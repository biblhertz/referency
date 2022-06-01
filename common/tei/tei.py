import os
from xml.dom.minidom import parse as xml_parser

import bs4

from common.config import config
from common.misc import fields as f


def return_xml_new_lines(sentence):
    cleaned = ''

    for word in sentence.split(" "):
        if word != '':
            cleaned += word.strip() + ' '

    return cleaned


def recursive_node_value(root):
    if len(root.childNodes) == 0:
        if root.nodeValue and root.nodeType == root.TEXT_NODE and root.nodeValue.strip() != '':
            return return_xml_new_lines(root.nodeValue)
        else:
            # ignore empty non text nodes
            return ""

    contents = ''

    for child in root.childNodes:
        if child.nodeType == child.ELEMENT_NODE and child.tagName == config.TEI_ITALICS_NODE_TAG:
            contents += '<i>{value}</i>'.format(value=recursive_node_value(child))
        else:
            contents += recursive_node_value(child)

    return contents


def parse(filename):
    """

    """
    tei_xml = xml_parser(filename)

    citations = list()

    for i, elem in enumerate(tei_xml.getElementsByTagName(config.TEI_FOOTNOTE_TAG)):
        contents = ''
        for child_node in elem.childNodes:
            # ignore empty nodes
            if child_node.nodeType == child_node.TEXT_NODE and child_node.nodeValue.strip() == '':
                continue

            assert child_node.nodeType == child_node.TEXT_NODE or child_node.nodeType == child_node.ELEMENT_NODE
            contents += recursive_node_value(child_node)

        citations.append(contents)

    return citations


def update(file, references):
    """
    Create a new updated xml, containing information for all the bibliographic references.
    As per TEI standards, all bibliographic references are added under `teiHeader`

    https://www.tei-c.org/release/doc/tei-p5-doc/en/html/CO.html#COBICOL
    """
    with open(file, "r") as fd:
        soup = bs4.BeautifulSoup(fd, "xml")
        # x3ml will fail if the following is present
        soup.find('TEI').attrs.clear()
        tei_header = soup.find("teiHeader")

        listBibl = tei_header.find("listBibl")
        if not listBibl:
            listBibl = soup.new_tag("listBibl")

        for ref in references:

            biblStruct = soup.new_tag("biblStruct")
            if ref[f.URI]:
                biblStruct['uri'] = ref[f.URI]
                
            analytic = soup.new_tag("analytic")

            for author in ref[f.AUTHORS]:
                author_tag = soup.new_tag("author")
                author_tag['level'] = 'a'  # `a` for analytic
                author_tag.string = author
                analytic.append(author_tag)

            title_tag = soup.new_tag("title")
            title_tag['level'] = 'a'
            title_tag.string = ref[f.TITLE]
            analytic.append(title_tag)

            if ref[f.LANG]:
                lang_tag = soup.new_tag('textLang')
                lang_tag.string = ref[f.LANG]
                analytic.append(lang_tag)

            biblStruct.append(analytic)

            monogr = soup.new_tag('monogr')

            if ref[f.PUBLISHER]:
                mono_title_tag = soup.new_tag("title")
                mono_title_tag['level'] = 'm'
                mono_title_tag.string = ref[f.PUBLISHER]
                monogr.append(mono_title_tag)

            imprint_tag = soup.new_tag("imprint")

            if ref[f.YEAR]:
                date_tag = soup.new_tag("date")
                date_tag.string = ref[f.YEAR]
                imprint_tag.append(date_tag)

            monogr.append(imprint_tag)

            if ref[f.PAGES]:
                biblScope_tag = soup.new_tag("biblScope")
                biblScope_tag.string = ref[f.PAGES]
                monogr.append(biblScope_tag)

            for editor in (ref[f.RESPONSIBILITY] or []):
                editor_tag = soup.new_tag("editor")
                editor_tag.string = editor
                monogr.append(editor_tag)

            if ref[f.ISBN]:
                isbn_tag = soup.new_tag('idno')
                isbn_tag['type'] = 'ISBN'
                isbn_tag.string = ref[f.ISBN]
                monogr.append(isbn_tag)

            if ref[f.OCLC]:
                oclc_tag = soup.new_tag('idno')
                oclc_tag['type'] = 'OCLC'
                oclc_tag.string = ref[f.OCLC]
                monogr.append(oclc_tag)

            biblStruct.append(monogr)
            listBibl.append(biblStruct)
            tei_header.append(listBibl)

    filename = os.path.basename(file)
    inter_dirs = file.split(os.sep)

    outpath = os.path.join(config.WORKSPACE, config.OUTPUT_FOLDER, inter_dirs[-3], inter_dirs[-2])
    os.makedirs(outpath, exist_ok=True)

    outfile = os.path.join(outpath, filename)
    with open(file=outfile, mode="w", encoding="utf-8") as fd:
        fd.write(soup.prettify())

    return outfile
