import os
from xml.dom.minidom import parse as xml_parser

import bs4

from common.config import config
from common.misc import fields as f


def parse(filepath):
    """

    """
    jats_xml = xml_parser(filepath)
    # iterate footnotes
    citations = list()
    for i, elem in enumerate(jats_xml.getElementsByTagName(config.JATS_FOOTNOTE_TAG)):
        if len(elem.getElementsByTagName(config.JATS_PARAGRAPH_TAG)[0].getElementsByTagName(
                config.JATS_EXT_LINK_TAG)) > 0:

            if elem.getElementsByTagName(config.JATS_PARAGRAPH_TAG)[0].firstChild != None:
                p = elem.getElementsByTagName(config.JATS_PARAGRAPH_TAG)[0].firstChild.nodeValue
            else:
                p = ""

            if elem.getElementsByTagName(config.JATS_PARAGRAPH_TAG)[0]. \
                    getElementsByTagName(config.JATS_EXT_LINK_TAG)[0].firstChild != None:
                ext = elem.getElementsByTagName(config.JATS_PARAGRAPH_TAG)[0]. \
                    getElementsByTagName(config.JATS_EXT_LINK_TAG)[0].firstChild.nodeValue
            else:
                ext = ""

            citations.append(str(p) + " " + str(ext))
        else:
            p = elem.getElementsByTagName(config.JATS_PARAGRAPH_TAG)[0].firstChild.nodeValue
            citations.append(p)

    return citations


def update(file, references):
    """
    Create a new updated xml, containing information for all the bibliographic references.
    As per JATS standards, all bibliographic references are added under `back`

    https://jats.nlm.nih.gov/archiving/tag-library/1.1d3/chapter/tag-citation.html
    """

    def get_ref_id():
        i = 0
        while True:
            yield "ref-" + str(i)
            i += 1
    ids = get_ref_id()
    with open(file, "r") as fd:
        soup = bs4.BeautifulSoup(fd, "xml")
        jats_back = soup.find("back")

        if not jats_back:
            jats_back = soup.new_tag("back")

        ref_list_tag = soup.new_tag("ref-list")

        for ref in references:
            ref_tag = soup.new_tag("ref")
            ref_tag['id'] = next(ids)
            if ref[f.URI]:
                ref_tag['uri'] = ref[f.URI]

            ref_list_tag.append(ref_tag)

            mixed_citation_tag = soup.new_tag("mixed-citation")
            ref_tag.append(mixed_citation_tag)

            article_title_tag = soup.new_tag("article-title")
            if ref[f.LANG]:
                article_title_tag['xml:lang'] = ref[f.LANG]

            article_title_tag.string = ref[f.TITLE]
            mixed_citation_tag.append(article_title_tag)

            person_group_tag_authors = soup.new_tag("person-group")
            person_group_tag_authors['person-group-type'] = 'author'

            for author in (ref[f.AUTHORS] or []):
                if "et al" in author:
                    et_al_tag = soup.new_tag("etal")
                    person_group_tag_authors.append(et_al_tag)
                else:
                    name_tag = soup.new_tag("name")
                    surname_tag = soup.new_tag("surname")
                    surname_tag.string = author.rsplit(" ", 1)[1]
                    name_tag.append(surname_tag)

                    given_game_tag = soup.new_tag("given-names")
                    given_game_tag.string = author.rsplit(" ", 1)[0]
                    name_tag.append(given_game_tag)

                    person_group_tag_authors.append(name_tag)

            mixed_citation_tag.append(person_group_tag_authors)

            person_group_tag_editors = soup.new_tag("person-group")
            person_group_tag_editors['person-group-type'] = 'editor'

            for editor in (ref[f.RESPONSIBILITY] or []):
                name_tag = soup.new_tag("name")
                surname_tag = soup.new_tag("surname")
                surname_tag.string = editor.rsplit(" ", 1)[1]
                name_tag.append(surname_tag)

                given_game_tag = soup.new_tag("given-names")
                given_game_tag.string = editor.rsplit(" ", 1)[0]
                name_tag.append(given_game_tag)

                person_group_tag_editors.append(name_tag)

            mixed_citation_tag.append(person_group_tag_editors)

            year_tag = soup.new_tag("year")
            if ref[f.YEAR]:
                year_tag.string = ref[f.YEAR]
            mixed_citation_tag.append(year_tag)

            if ref[f.PAGES]:
                fpage_tag = soup.new_tag("fpage")
                fpage_tag.string = ref[f.PAGES].split('-')[0] if '-' in ref[f.PAGES] else ref[f.PAGES]
                mixed_citation_tag.append(fpage_tag)

                lpage_tag = soup.new_tag("lpage")
                lpage_tag.string = ref[f.PAGES].split('-')[1] if '-' in ref[f.PAGES] else ref[f.PAGES]
                mixed_citation_tag.append(lpage_tag)

            if ref[f.ISBN]:
                isbn_tag = soup.new_tag("isbn")
                isbn_tag.string = ref[f.ISBN]
                mixed_citation_tag.append(isbn_tag)

            if ref[f.PUBLISHER]:
                publisher_tag = soup.new_tag("publisher-name")
                publisher_tag.string = ref[f.PUBLISHER]
                mixed_citation_tag.append(publisher_tag)

            ref_list_tag.append(ref_tag)
        jats_back.append(ref_list_tag)

    filename = os.path.basename(file)
    inter_dirs = file.split(os.sep)

    outpath = os.path.join(config.WORKSPACE, config.OUTPUT_FOLDER, inter_dirs[-3], inter_dirs[-2])
    os.makedirs(outpath,exist_ok=True)

    outfile = os.path.join(outpath, filename)
    with open(outfile, "w") as fd:
        fd.write(soup.prettify())

    return outfile
