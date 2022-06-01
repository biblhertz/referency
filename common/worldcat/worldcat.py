# -*- coding: utf-8 -*-
'''Query the WorldCat service for metadata. '''
import re
import urllib

import bs4
import pycountry

from common.config import config
from common.logger import log
from common.misc import fill_with_none
import common.misc as fields
from common.utils import parse_tail

SERVICE_URL = 'https://www.worldcat.org/search?qt=worldcat_org_all&q={title}&lang=en'
_WORLDCAT_URL = 'https://www.worldcat.org'

_re1 = re.compile(r'(?<=[A-Z])(\s)(?![A-z]{2,})')
_re2 = re.compile(r'(?<=[A-Z])(\s)(?=[A-z]{2,})')


def book_parser(data):
    """
    Parses the html page of a title and returns all the relevant information

    :param: html data

    :return: all relevant info, if found, empty dict if an error occurs

    :rtype: a dict
    """
    book_data = dict()

    soup = bs4.BeautifulSoup(data, features='html.parser')

    try:
        result = soup.find(id="bibdata")

        # Extract title
        raw = result.find('h1', class_='title').contents[0]

        book_data[fields.TITLE] = str(raw.replace(' :', ':'))  # Fix a error in title markup
        log.debug('{name}: {value}'.format(name=fields.TITLE, value=book_data[fields.TITLE]))

        # Extract list of author(s)
        raw = result.find('td', id="bib-author-cell").contents
        # Split and fix another common error
        # use 'string' attribute instead of contents[0] in case raw is NavigableString
        names = [authorTag.string for authorTag in raw if authorTag != '; ']
        names = [s for name in names for s in name.split(';')]

        def fix_punctuation(name):  # Fix missing punctuation in author initials (WorldCat issues...)
            step = re.sub(_re1, r'.', str(name))
            return re.sub(_re2, r'. ', step)

        book_data[fields.AUTHORS] = [fix_punctuation(name).split(':')[0] for name in names]
        log.debug('{name}: {value}'.format(name=fields.AUTHORS, value=book_data[fields.AUTHORS]))

        # Extract language
        raw = [i.replace(":", " ").replace(",", " ") for i in
               result.find('td', id='bib-itemType-cell').find('span')
               # Catch things like ": English". Keep in mind that language is not inside a
               # span therefore it has *no* contents attribute
               if not hasattr(i, 'contents') and ":" in i]
        langs = []

        for rawItem in raw:
            for lang in rawItem.split(" "):
                langs.append(lang.strip())

        lang_codes = []

        for lang in langs:
            # swallow the exception
            try:
                country_code = pycountry.languages.lookup(str(lang))
                if country_code:
                    lang_codes.append(country_code.alpha_2.lower())
            except:
                pass

        if len(lang_codes) == 1:
            book_data[fields.LANG] = str(lang_codes[0])
        elif len(lang_codes) > 1:
            book_data[fields.LANG] = str(', '.join(lang_codes))
        else:
            book_data[fields.LANG] = ''

        log.debug('{name}: {value}'.format(name=fields.LANG, value=book_data[fields.LANG]))

        # Extract publisher and year
        raw = result.find(lambda tag:tag.name == "td" and
            'id' in tag.attrs and tag.attrs['id'] in ('bib-journalTitle-cell', 'bib-publisher-cell'))
        if raw:
            raw = raw.contents[0]
            raw = raw.rsplit(',', 1)
            
            publisher = raw[0]
            book_data[fields.PUBLISHER] = str(publisher)
            log.debug('{name}: {value}'.format(name=fields.PUBLISHER, value=book_data[fields.PUBLISHER]))

            if len(raw) > 1:
                tail_data = parse_tail(str(raw[1]))
                year = tail_data['when'] if 'when' in tail_data and tail_data['when'] else str(raw[1])
                book_data[fields.YEAR] = year
                log.debug('{name}: {value}'.format(name=fields.YEAR, value=year))

        raw = soup.find('tr', id="details-unique-id")  # retrieve inique identifier if it exits
        if raw and raw.find('td'):
            book_data[fields.UNIQUE_ID] = raw.find('td').contents[0]  # set the last one as UniqueID
            log.debug('{name}: {value}'.format(name=fields.UNIQUE_ID, value=book_data[fields.UNIQUE_ID]))

        raw = soup.find('tr', id="details-standardno")  # retrive isbn if it exists
        if raw and raw.find('td'):
            book_data[fields.ISBN] = raw.find('td').contents[0].split(' ')[-1]  # set the last one as ISBN
            log.debug('{name}: {value}'.format(name=fields.ISBN, value=book_data[fields.ISBN]))

        raw = soup.find('tr', id="details-oclcno")  # retrieve oclc if it exists
        if raw and raw.find('td'):
            book_data[fields.OCLC] = raw.find('td').contents[0].split(' ')[-1]  # set the last one as OCLC
            log.debug('{name}: {value}'.format(name=fields.OCLC, value=book_data[fields.OCLC]))

        raw = soup.find('tr', id='details-respon')
        if raw and raw.find('td'):
            book_data[fields.RESPONSIBILITY] = str(raw.find('td').string).split(',;')
            log.debug('{name}: {value}'.format(name=fields.RESPONSIBILITY, value=book_data[fields.RESPONSIBILITY]))

        raw = soup.find('tr', id='details-moreinfo')
        if raw and raw.find('td'):
            for li in raw.find('td').find('ul').find_all('li'):
                if re.search('contents', str(li.find('a').string), re.IGNORECASE):
                    contents_page = urllib.request.urlopen(_WORLDCAT_URL + li.find('a', href=True)['href']).read()
                    book_data[fields.CONTENT] = str(
                        bs4.BeautifulSoup(contents_page, features='html.parser').find('body'))
                    log.debug('{name}: {value}'.format(name=fields.CONTENT, value=book_data[fields.CONTENT]))

        raw = soup.find('tr', id='details-contents')
        if raw and raw.find('td'):
            book_data[fields.CONTENT] = str(raw.find('td'))
            log.debug('{name}: {value}'.format(name=fields.CONTENT, value=book_data[fields.CONTENT]))

    except (AttributeError, KeyError) as ex:
        log.error('Error parsing book page html in WorldCat. {ex}'.format(ex=ex))
        book_data = {}

    book_data[fields.RETRIEVED_WITH] = config.WORLDCAT_NAME
    return fill_with_none(book_data)


def results_parser(data, max_results):
    """
    Parses html data retrieved and returns a list of all the relevant hrefs
    """
    records = list()

    soup = bs4.BeautifulSoup(data, features='html.parser')

    try:
        result = soup.find_all('td', class_='result details')

        for i in range(min(max_results, len(result))):
            records.append(_WORLDCAT_URL + result[i].find('a', href=True)['href'])

    except (AttributeError, KeyError) as ex:
        log.error('Error parsing results html in WorldCat. {ex}'.format(ex=ex))
        records = []

    return records
