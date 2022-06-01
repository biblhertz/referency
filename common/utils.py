# -*- coding: utf-8 -*-
import os
import re
import subprocess
from difflib import SequenceMatcher

import pandas
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
from pandas.core.frame import DataFrame

import common.misc as misc
from common.config import config
from common.logger import log
from common.misc import fields

PA_QUOTATION = r"“(.+?)”"
PA_ITALIC = r"<i>(.+?)<\/i>"

PA_MULTIPLE_PAGES = r"pp\.?\s+(([0-9]+.{1}[0-9]+)|(xx))"
PA_SINGLE_PAGE = r"p\.?\s+(([0-9]+)|(xx))"
PA_ALPHANUMERICAL = r"\W+"
PA_NAME_INITIAL = r"[A-Z]\."
PA_COMMA = r","

ET = "et"
AL = "al"
ET_AL = ET + ' ' + AL + '.'

TITLE_SIMILARITY_THREASHOLD = 0.6
AUTHOR_SIMILARITY_THREASHOLD = 0.49


class StopWordsSingleton(object):
    _instance = None
    _stopwords = None

    def __init__(self):
        raise RuntimeError("Call instance() instead!")

    @classmethod
    def get_instance(cls):
        if (cls._instance) is None:
            cls._instance = cls.__new__(cls)
            with open(config.STOPWORDS_FILE) as f:
                lines = f.readlines()

            trailed = list()
            for line in lines:
                temp = line.strip()
                temp = temp.strip("\n")
                trailed.append(temp.lower())

            cls._stopwords = trailed

        return cls._instance

    @classmethod
    def getStopWords(cls):
        return cls._stopwords


class NameDatasetSingleton(object):
    _instance = None
    _dataset = None
    _NAME_DETECTION_THRESHOLD = 0.03

    def __init__(self):
        raise RuntimeError("Call instance() instead!")

    @classmethod
    def get_instance(cls):
        if (cls._instance) is None:
            cls._instance = cls.__new__(cls)
            # from names_dataset import NameDatasetV1
            # cls._dataset = NameDatasetV1()
            log.info("Setting up name dataset. Please wait....")
            from names_dataset import NameDataset
            cls._dataset = NameDataset()
            log.info("Done.")

        return cls._instance

    @classmethod
    def get_dataset(cls):
        return cls._dataset

    @classmethod
    def is_firstname(cls, text: str):
        return cls._dataset.search_first_name(text) > cls._NAME_DETECTION_THRESHOLD

    @classmethod
    def is_lastname(cls, text: str):
        return cls._dataset.search_last_name(text) > cls._NAME_DETECTION_THRESHOLD


class CitiesLookupSingleton(object):
    _instance = None
    _cities_dataframe: DataFrame = None

    def __init__(cls):
        raise RuntimeError("Call instance() instead!")

    @classmethod
    def get_instance(cls):
        if (cls._instance) is None:
            cls._instance = cls.__new__(cls)
            cls._cities_dataframe = pandas.read_csv(
                config.WORLD_CITIES, usecols=["name"]
            )

            cls._cities_dataframe["name"] = (
                cls._cities_dataframe["name"]
                    # normalize all city names
                    # see unicode normalization
                    .str.normalize("NFKD")
                    # all cities names to lower letters
                    .str.lower()
                    .str.encode("ascii", errors="ignore")
                    .str.decode("utf-8")
            )

        return cls._instance

    @classmethod
    def is_city(cls, txt):
        return not cls._cities_dataframe.query('name == "' + txt + '"').empty


def tokenize(text: str, keep_single_letter_tokens=False, keep_stopwords=False):
    """
    TODO documentation
    """
    STOPWORDS = StopWordsSingleton.get_instance().getStopWords()

    # assert stopwords are loaded
    assert "in" in STOPWORDS

    multiple_fifo = []
    single_fifo = []
    name_initials_fifo = []

    # find all PA_NAME_INITIAL matches and save their values.
    # name initials are case-sensitive hence they are replaced before
    # transforming input to lower case
    for match in re.finditer(PA_NAME_INITIAL, text):
        name_initials_fifo.append(text[match.start(): match.end()])
    text = re.sub(PA_NAME_INITIAL, " ppnameinitial ", text)

    text = text.lower()

    # Since the text argument is going to be splitted using spaces, sentences
    # like pp. 138-150 and p. 50 can end up as two or more *seperate* sentences,
    # namely ["pp." , "138", 150"] and ["p.", "50"].
    # We DON'T want that. Instead we want them to be treated a single token
    # like any other word, so that when a function is consuming the output of
    # the function it can easily determine if token is a pp or p reference
    # by applying a regex to token.

    # find all PA_MULTIPLE_PAGES matches and save their values.
    for match in re.finditer(PA_MULTIPLE_PAGES, text):
        multiple_fifo.append(text[match.start(): match.end()])
    # replace all matches in the original string and place a non-sense value as a mark
    text = re.sub(PA_MULTIPLE_PAGES, " ppmultiple ", text)

    # find all PA_SINGLE_PAGE matches and save their values.
    for match in re.finditer(PA_SINGLE_PAGE, text):
        single_fifo.append(text[match.start(): match.end()])
    # replace all matches in the original string and place a non-sense value as a mark
    text = re.sub(PA_SINGLE_PAGE, " ppsingle ", text)

    # remove all non alphanumerical characters from text
    text = re.sub(PA_ALPHANUMERICAL, " ", text)

    # split input text to create sentences
    tokens = text.split(" ")

    FILTERS = [
        # remove and all stop words
        lambda token: (len(token) == 1 and keep_single_letter_tokens)
                      or keep_stopwords or token not in STOPWORDS,
        # remove all empty sentences
        lambda token: not len(token) == 0,
    ]

    for f in FILTERS:
        tokens = list(filter(f, tokens))

    # remove marks and replace them with the original values, now sentences contain things like p. 130
    tokens = list(
        map(lambda token: multiple_fifo.pop(0) if token == "ppmultiple" else token, tokens)
    )

    tokens = list(
        map(lambda token: single_fifo.pop(0) if token == "ppsingle" else token, tokens)
    )

    tokens = list(
        map(lambda token: name_initials_fifo.pop(0) if token == "ppnameinitial" else token, tokens)
    )

    # log.debug("normalized tokens {tokens}".format(tokens=tokens))
    return tokens


def keep_non_empty(text: str):
    return len(text.strip()) != 0


def is_valid_year(text: str):
    return re.compile("[1-2][0-9]{3}$").match(text) != None


# Wrapper for get_human_names to make code more readable
def get_authors(text: str, strict=False):
    return get_human_names(text, strict)


def get_human_names(sentence: str, strict=False):
    """
    Returns an array containing the strings that are likely names
    Function considers "et al." as a valid human name
    to ease crosschecking the of authors

    :param sentence: a text to extract a possible name from
    :param strict: if strict is set then the function returns false
        if text doesn't begin with a name

    :return: an array of strings or None if no name was found
    """

    namesLookup = NameDatasetSingleton.get_instance()

    if strict:
        tokens = tokenize(sentence, True, True)
    else:
        tokens = tokenize(sentence, True, False)

    names = list()

    log.debug("checking sentences for name(s) {tokens}".format(tokens=tokens))

    i = 0

    while i < len(tokens):

        initial = False
        lastname = False
        firstname = False
        et = False
        al = False
        name = ''

        while i < len(tokens):

            token = tokens[i]
            i = i + 1

            if len(token) == 2 and token[1] == '.':
                initial = True
                name += ' ' + token.title()
            elif namesLookup.is_firstname(token):
                if firstname:
                    lastname = True
                else:
                    firstname = True
                name += ' ' + token.title()
            elif namesLookup.is_lastname(token):
                if lastname:
                    firstname = True
                else:
                    lastname = True
                name += ' ' + token.title()
            elif token == ET:
                # we consider et al as a valid human name
                et = True
            elif token == AL:
                al = True
            else:
                break

        if (firstname and lastname) or (initial and lastname) or (initial and firstname):
            names.append(name.strip())

            if et and al:
                names.append(ET_AL)

        if strict:
            break

    if len(names):
        log.debug('found name(s) "{names}" in {s}'.format(names=names, s=sentence))
    else:
        if len(tokens):
            log.debug("no name(s) found in '{s}'".format(s=sentence))
            # log.debug("firstname_found: {found}".format(found=firstname))
            # log.debug("initial_found: {found}".format(found=initial))
            # log.debug("lastname_found: {found}".format(found=lastname))

    return names if len(names) else None


def author_paper_title_publishing_info(full_txt: str, sentences: list, strict=True):
    """
    Searches in sentences for a pattern like A paper title, Location Year

    :param full_txt: a string, see extract_from_full_txt()

    :param sentences: list of sentences that represent our splitted, untokenized input
                    e.g. ["A paper title here","Location Year"]

    :param strict: if strict is set then the algorithm will search for both publisher and publication year,
                else only one of the them is good enough

    :return:  a two item list with all the paper data found being the first element
           the index of the last token consumed being the second one.

    :rtype: list
    """
    if not sentences:
        return [None, None]

    # city object used to query for valid locations
    cities_singleton = CitiesLookupSingleton.get_instance()
    data = dict()
    # For each token, if token contains a city name and a year
    # search assumes it refers to publishing location and publishing year.
    # If token doesn't contain both, search proceeds to check the next token
    for idx, sentence in enumerate(sentences):

        has_location = False
        has_publication_year = False

        # e.g sentences[idx] is "Rome (2021)"
        # then subtokens will be ["rome","2021"]
        subtokens = tokenize(sentence)

        def title_and_publisher(data_, idx_):
            # check in the substring in between the assumed title and the publisher information
            # for possible journal and responsibility references
            assumed_title = extract_from_full_txt(full_txt, sentences, 0, idx_)
            collective_works, title = collective_works_pattern(assumed_title)

            data_ = {
                **data_,
                **collective_works,
                fields.TITLE: title,
                fields.PUBLISHER: extract_from_full_txt(full_txt, sentences, idx_, idx_)
            }

            log.debug("title found {title} ".format(title=data_[fields.TITLE]))
            log.debug("journal found {pub} ".format(pub=data_[fields.CONTENT]))
            log.debug("responsibility found {pub} ".format(pub=data_[fields.RESPONSIBILITY]))
            log.debug("publisher found {pub} ".format(pub=data_[fields.PUBLISHER]))

            return data_

        for token in subtokens:

            if not has_location and cities_singleton.is_city(token):
                log.debug("city found {city}".format(city=token))
                has_location = True
            elif not has_publication_year and is_valid_year(token):
                log.debug("publication year found {year}".format(year=token))
                has_publication_year = True
                data[fields.YEAR] = token
            # search now assumes that all sentences from start to idx - 1
            # represent a title and stops searching
            # idx > 0 checks that there is something in between
            # the assumed title and the publication info found
            if has_location and has_publication_year and idx > 0:
                return [title_and_publisher(data, idx), idx]
            elif not strict and (has_location or has_publication_year) and idx > 0:
                return [title_and_publisher(data, idx), idx]

    # nothing found
    return [None, None]


def extract_from_full_txt(full_txt: str, sentences: list, sentence_start_idx, sentence_end_idx):
    """
    Maps sentences to the original text using indices.

    When transforming input, we may split it using a variety of delimiters.
    In order to retrieve the unsplitted version we resort to using the splitted,
    but untokenized "sentences" and their indices to get any substring of the original
    we need.

    :param full_txt: a string
    :param sentences: the splitted version of full_txt
    :param sentence_start_idx: an index in the sentences list
    :param sentence_end_idx: an index in sentences list

    :return: a substring of full_txt
    :rtype: str
    """
    if sentence_start_idx == sentence_end_idx:
        return sentences[sentence_start_idx]
    else:
        start = full_txt.index(sentences[sentence_start_idx])
        end = full_txt.index(sentences[sentence_end_idx])

        res = full_txt[start:end]

        assert len(res) != 0

        return res


def author_paper_title_page_references(full_txt: str, sentence_tokens: list):
    """
    Searches in sentences for a pattern like A paper title, pp. page_no - page_no

    :param full_txt: a string, see extract_from_full_txt()

    :param sentence_tokens: list of strings that represent our splitted, untokenized
            sentence input, e.g. ["A paper title here","esp. pp. 256-258"]

    :return:  a two item list with all the paper data found being the first element
           the index of the last token consumed being the second one.

    :rtype: list
    """
    data = dict()

    if not sentence_tokens:
        return [None, None]

    for idx, sentence in enumerate(sentence_tokens):
        pages = get_pp(sentence)
        if pages and idx > 0:
            assumed_title = extract_from_full_txt(full_txt, sentence_tokens, 0, idx)
            collective_works, title = collective_works_pattern(assumed_title)

            data = {
                **data,
                **collective_works,
                fields.TITLE: title,
                fields.PAGES: pages,
            }

            log.debug("title found {title} ".format(title=data[fields.TITLE]))
            log.debug("journal found {pub} ".format(pub=data[fields.CONTENT]))
            log.debug("responsibility found {pub} ".format(pub=data[fields.RESPONSIBILITY]))

            return [data, idx]

    return [None, None]


def try_author_based_patterns(full_txt: str):
    """
    Searches in full_txt and tries to match as many of the known author patterns
    as it can.

    The function consumes all its input before returning.

    :param full_txt: a string representing a footnote or part of it

    :return: a list of all the papers found alongside their data

    :rtype: a list of dictionaries
    """
    sentences = list(re.split(PA_COMMA, full_txt))

    paper = dict()
    results = []

    def found_authors(res):
        return fields.AUTHORS in res and len(res[fields.AUTHORS]) != 0

    author_idx = 0

    # consume authors
    for i, sentence in enumerate(sentences):
        authors_relaxed = get_authors(sentence)
        authors_strict = get_authors(sentence, strict=True)
        if not found_authors(paper) and authors_relaxed:
            # relaxed search to find first author
            log.debug("Found author {name} using relaxed search".format(name=sentence))
            paper[fields.AUTHORS] = authors_relaxed
            author_idx = i
        elif found_authors(paper) and authors_strict:
            # if more than one exist, they should be listed consecutively
            # e.g. "see Günther Görz, Martin Smith, and Bernhard Schiemann"
            # then ["Günther Görz"] is found from the above if and
            # the rest separated only by stopwords and commas
            log.debug("Found author {name} using strict search".format(name=sentence))
            paper[fields.AUTHORS].extend(authors_strict)
            author_idx = i
        elif found_authors(paper) and not authors_strict:
            log.debug("Stopped author search. Sentence found {sentence}".format(sentence=sentence))
            break

    if found_authors(paper):
        KNOWN_AUTHOR_PATTERNS = [
            lambda: author_paper_title_page_references(full_txt, sentences[author_idx + 1:]),
            lambda: author_paper_title_publishing_info(full_txt, sentences[author_idx + 1:]),
            lambda: author_paper_title_publishing_info(full_txt, sentences[author_idx + 1:], False),
        ]

        for p in KNOWN_AUTHOR_PATTERNS:
            data, last_consumed = p()
            if data:
                # merge authors with title,publisher and pages data
                paper = {**paper, **data}
                break

        # consume the rest of input
        if last_consumed and i + last_consumed < len(sentences):
            rest = try_author_based_patterns(full_txt.split(sentences[i + last_consumed], 1)[1])
            if rest:
                rest.extend(results)
                results = rest

        results.append(paper)
        results = [misc.broom(result) for result in results]
        return results
    else:
        return None


def try_collective_works_pattern(sentence: str):
    data, leftovers = collective_works_pattern(sentence)
    if data[fields.RESPONSIBILITY] and data[fields.CONTENT]:
        return data
    else:
        return None


def collective_works_pattern(sentence: str):
    data = {
        fields.RESPONSIBILITY: None,
        fields.CONTENT: None
    }

    res = None

    PA_IN_ED = r',(\s*)(\bin\b)(.*)(\s*)(\bed(\.?)\b)(.*?)(,+)'
    PA_ED = r',(\s*)(\bed(\.?)\b)(.*?)(,+)'
    # less common, but possible
    PA_IN = r',(\s*)(\bin\b)(.*)(,+)'

    reg_in_ed = re.compile(PA_IN_ED)
    reg_ed = re.compile(PA_ED)
    reg_in = re.compile(PA_IN)

    if reg_in_ed.search(sentence):
        res = reg_in_ed.split(sentence)
        data[fields.CONTENT] = res[3]
        authors = get_authors(res[7])
        if not authors:
            # there is a chance that get_authors fails to identify
            # the names, in this case instead of ignoring the
            # data following "ed. ..." we manually insert them as a single name
            data[fields.RESPONSIBILITY] = [res[7]]
        else:
            data[fields.RESPONSIBILITY] = authors
    elif reg_ed.search(sentence):
        res = reg_ed.split(sentence)
        data[fields.CONTENT] = res[0]
        authors = get_authors(res[4])
        # see the explanation above to better understand the following
        if not authors:
            data[fields.RESPONSIBILITY] = [res[4]]
        else:
            data[fields.RESPONSIBILITY] = authors
    elif reg_in.search(sentence):
        res = reg_in.split(sentence)
        data[fields.CONTENT] = res[3]
    return [data, res[0] if res else sentence]


# Returns true if text doesn't contain substrings like pp. 56-68, p. 154, pp. xx and p. xx.
def keep_non_pp(text: str):
    return not get_pp(text)


def get_pp(text: str):
    text = text.lower()

    pp_re = re.compile(PA_MULTIPLE_PAGES)
    p_re = re.compile(PA_SINGLE_PAGE)

    if pp_re.search(text):
        return pp_re.search(text)[0]
    elif p_re.search(text):
        return p_re.search(text)[0]
    else:
        return None


def single_split_pattern(text: str, pattern: str):
    pa = re.compile(pattern)

    matches = pa.split(text, 1)

    return matches if len(matches) != 0 else [text]


def replace(pattern: str, repl, string: str):
    fifo = []

    for match in re.finditer(pattern, string):
        s = string[match.start():match.end()]
        fifo.append(s)

    string = re.sub(pattern, repl, string)

    return string, fifo


def sentence_tokenize(text: str):
    _ITALICS_PLACEHOLDER = r'ppitalic'
    _QUOTES_PLACEHOLDER = r'ppquote'

    text, quotes_fifo = replace(PA_QUOTATION, _QUOTES_PLACEHOLDER, text)
    text, italics_fifo = replace(PA_ITALIC, _ITALICS_PLACEHOLDER, text)

    italics_fifo = [string.replace('<i>', '').replace('</i>', '') for string in italics_fifo]
    quotes_fifo = [string.replace('<i>', '').replace('</i>', '') for string in quotes_fifo]

    punkt_param = PunktParameters()

    punkt_param.abbrev_types = set(
        ['dr', 'vs', 'mr', 'mrs', 'prof', 'inc', 'jr', 'ed', 'et', 'al', 'esp', 'p', 'pp', 'vol', 'vols', 'trans'])

    punkt_param.sent_starters = set(['see', 'see also'])

    sentence_splitter = PunktSentenceTokenizer(punkt_param)

    sentences = []
    for sentence in text.split(';'):
        sentences.extend(sentence_splitter.tokenize(sentence))

    sentences = [replace(_ITALICS_PLACEHOLDER, lambda m: italics_fifo.pop(0), sentence)[0] for sentence in sentences]
    sentences = [replace(_QUOTES_PLACEHOLDER, lambda m: quotes_fifo.pop(0), sentence)[0] for sentence in sentences]

    assert not italics_fifo
    assert not quotes_fifo

    return sentences


def extract_citations(footnotes: list):
    citations = dict()

    def citations_from(footnote: str):
        footnote_citations = list()

        sentences = sentence_tokenize(footnote)

        for sentence in sentences:
            author_based_data = try_author_based_patterns(sentence)
            collective_works_data = try_collective_works_pattern(sentence)
            if author_based_data:
                footnote_citations.extend(author_based_data)
            elif collective_works_data:
                log.debug('Data with collective works pattern {d}'.format(d=collective_works_data))
                footnote_citations.extend(collective_works_data)
        return footnote_citations

    for footnote in footnotes:
        citations[footnote] = citations_from(footnote)

    return citations


def create_workspace():
    try:
        if not os.path.exists(config.WORKSPACE):
            os.makedirs(config.WORKSPACE)
        if not os.path.exists(config.INPUT_FOLDER):
            os.makedirs(config.INPUT_FOLDER)
        if not os.path.exists(config.INTER_FOLDER):
            os.makedirs(config.INTER_FOLDER)
        if not os.path.exists(config.OUTPUT_FOLDER):
            os.makedirs(config.OUTPUT_FOLDER)
    except OSError:
        log.error("Workspace creation failed.")


# Run meTypeset
def meTypeset(filepath):
    filename,file_extension = os.path.splitext(os.path.basename(filepath))
    file_extension = file_extension.replace('.','')
    assert file_extension in {"docx", "doc", "odt","xml"}
    if file_extension == 'xml':
        file_extension = 'tei'

    intermediate = os.path.join(config.INTER_FOLDER, filename)

    jats_path = os.path.join(intermediate, config.JATS_FOLDER, filename + '.xml')
    tei_path = os.path.join(intermediate, config.TEI_FOLDER, filename + '.xml')

    cmd = 'python ' + config.METYPESET_BIN_PATH + ' {ext} '.format(ext=file_extension) + filepath + ' ' + intermediate
    log.info(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    p.communicate()

    is_tei = os.path.exists(tei_path)

    return [is_tei, tei_path if is_tei else jats_path]


def similar_authors(author_list_1: list, author_list_2: list):
    if not author_list_1 or not author_list_2:
        return False

    similar_lists = True

    temp = author_list_1
    list_1 = author_list_1 if len(author_list_1) < len(author_list_2) else author_list_2
    list_2 = author_list_2 if len(temp) < len(author_list_2) else temp

    for item_1 in list_1:
        if item_1 in ET_AL:
            continue

        similar = False
        for item_2 in list_2:
            if item_2 in ET_AL:
                continue

            similar |= SequenceMatcher(None, re.sub(r'[^\w]', '', item_1),
                                       re.sub(r'[^\w]', '', item_2)).ratio() >= AUTHOR_SIMILARITY_THREASHOLD

        similar_lists &= similar
    log.debug("partially similar authors? '{similar}', authors: {a1} , {a2}"
              .format(similar=similar_lists, a1=author_list_1, a2=author_list_2))

    return similar_lists


def similar_titles(title_1: str, title_2: str):
    similar = SequenceMatcher(None, misc.broom(title_1), misc.broom(title_2)).ratio() >= TITLE_SIMILARITY_THREASHOLD

    log.debug("similar titles ? '{similar}'\ntitles: '{title_1}' and '{title_2}'"
              .format(title_1=title_1, title_2=title_2, similar=similar))

    return similar


def in_contents(needle, haystack):
    if not needle or not haystack:
        return False

    matched = re.search(needle, misc.broom(haystack), re.IGNORECASE)

    log.debug("in contents ? '{found}'".format(found=matched[0] if matched else None))

    return matched


def similar_citations(data_local, data_retrieved):
    assert fields.AUTHORS in data_local and fields.AUTHORS in data_retrieved
    assert fields.TITLE in data_local and fields.TITLE in data_retrieved

    author_title = similar_authors(data_local[fields.AUTHORS], data_retrieved[fields.AUTHORS]) and similar_titles(
        data_local[fields.TITLE], data_retrieved[fields.TITLE])

    responsibilty_contents = in_contents(data_local[fields.TITLE], data_retrieved[fields.CONTENT]) and \
                             all(in_contents(author, data_retrieved[fields.CONTENT]) for author in
                                 data_local[fields.AUTHORS])

    return author_title or responsibilty_contents


def parse_tail(tail):
    """
    Tries to extract data from what is found at the 'tail' of a citation,
    which is typically the last token after a comma.
    """
    RE_TAIL = r"\((?P<when>[0-9\s\\-]+)?\)"
    RE_TAILPG = r"(:|pp?\.?)\s*(?P<pfrom>\d+)((-|—)(?P<pto>\d+))?"
    m = re.search(RE_TAIL, tail)
    d1 = m.groupdict() if m else {}
    m = re.search(RE_TAILPG, tail)
    d2 = m.groupdict() if m else {}
    return {**d1, **d2}

