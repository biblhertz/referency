# -*- coding: utf-8 -*-
"""
Query the Kubikat service for metadata.
"""
import bs4
import re
import urllib

from common.config import config
from common.logger import log
from common.misc import fields, fill_with_none

_KUBIKAT_SERVICE = 'https://aleph.mpg.de/F/'
_KUBIKAT_FILTERS = '&adjacent=N&filter_code_1=WSP&filter_request_1=&filter_code_2=WYR&filter_request_2=&filter_code_3' \
                   '=WYR&filter_request_3=&filter_code_4=WEF&filter_request_4=&local_base=KUB01&filter_code_7=WEM' \
                   '&filter_code_8=WAK&con_lng=eng '
SERVICE_URL = _KUBIKAT_SERVICE + '?func=find-b&find_code=WRD&request={title}' + _KUBIKAT_FILTERS


def book_parser(data):
    """
    Parses the html page of a title and returns all the relevant information

    :param: html data

    :return: all relevant info, if found, empty dict if an error occurs

    :rtype: a dict
    """
    book_data = {}

    soup = bs4.BeautifulSoup(data, features='html.parser')

    try:
        results = soup.find(id="Person(s)-tr").parent

        # Extract title
        book_data[fields.TITLE] = str(results.find('tr', id="Title-tr").find('a').text)

        # Extract subtitle if exists
        if results.find('tr', id="Remainder of title-tr"):
            book_data[fields.TITLE] += str(" ") + str(
                results.find('tr', id="Remainder of title-tr").find('span').text.replace('\\n', ''))

        log.debug('{name}: {value}'.format(name=fields.TITLE, value=book_data[fields.TITLE]))

        # Extract list of author(s)
        raw = results.find('tr', id="Person(s)-tr")
        names = list()
        names.append(str(raw.find('a').string))
        siblings = raw.find_next_siblings('tr')
        for sibling in siblings:
            if sibling['id'] != '-tr':
                break
            names.append(str(sibling.find('a').string))

        book_data[fields.AUTHORS] = names
        log.debug('{name}: {value}'.format(name=fields.AUTHORS, value=book_data[fields.AUTHORS]))

        # Extract publisher and year
        raw = results.find('tr', id='Publication-tr')
        if raw:
            book_data[fields.PUBLISHER] = str(raw.find('span').string)
            log.debug('{name}: {value}'.format(name=fields.PUBLISHER, value=book_data[fields.PUBLISHER]))

        raw = results.find('tr', id='Responsibility-tr')
        if raw:
            book_data[fields.RESPONSIBILITY] = str(raw.find('span').string)
            log.debug('{name}: {value}'.format(name=fields.RESPONSIBILITY, value=book_data[fields.RESPONSIBILITY]))

        raw = results.find('tr', id='ISBN-tr')
        if raw:
            raw = raw.find('span').string.split("(")
            book_data[fields.ISBN] = raw[0]
            log.debug('{name}: {value}'.format(name=fields.ISBN, value=book_data[fields.ISBN]))

        raw = results.find('tr', id='External File')
        if raw:
            for td in raw.find_all('td'):
                if td.find('span').find('a'):
                    raw = td.find('span').find('a', href=True)['href']
                    href = re.findall(r'\"(.+?)\"', raw)[0]
                    import ssl
                    context = ssl._create_unverified_context()
                    contents = urllib.request.urlopen(href, context=context).read()
                    contents = bs4.BeautifulSoup(contents, features='html.parser')
                    contents = urllib.request.urlopen(
                        urllib.request.Request(
                            contents.find('body')['onload'].split('\'')[1],
                            headers={
                                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
                            })).read()
                    contents = bs4.BeautifulSoup(contents, features='html.parser')
                    book_data[fields.CONTENT] = str(contents.find('body'))
                    log.debug('{name}: {value}'.format(name=fields.CONTENT, value=book_data[fields.CONTENT]))


    except (AttributeError, KeyError) as ex:
        log.error('Error parsing book page html in Kubikat. {ex}'.format(ex=ex))
        book_data = {}

    book_data[fields.RETRIEVED_WITH] = config.KUBIKAT_NAME
    return fill_with_none(book_data)


def results_parser(data, max_results):
    """
    Parses html data retrieved and returns a list of all the relevant hrefs
    """
    records = list()

    soup = bs4.BeautifulSoup(data, features='html.parser')

    try:
        result = soup.find_all('tr', {"valign": "baseline"})

        for i in range(min(max_results, len(result))):
            records.append(result[i].find('td').find('a', href=True)['href'])

    except (AttributeError, KeyError) as ex:
        log.error('Error parsing results html in Kubikat. {ex}'.format(ex=ex))
        records = []

    return records
