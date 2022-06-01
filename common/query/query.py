# -*- coding: utf-8 -*-
import re
import urllib
from time import time as timestamp

import common.utils as utils
from common.logger import log
import common.misc as misc
from common.misc import fields

MAX_RESULTS_TO_VISIT = 4


def get_search_results(search_term: str, service_url, results_parser):
    """
    Return the first MAX_RESULTS_TO_VISIT number of results for the given search term

    :param: a term to search for in the service

    :return: a list of links

    :rtype: list of strings or empty list
    """
    title = urllib.parse.quote_plus(search_term)
    search_results = urllib.request.urlopen(service_url.format(title=title)).read()

    return results_parser(search_results, MAX_RESULTS_TO_VISIT)


def run(citation, service_url, results_parser, book_parser):
    """
    Query service 'service' for metadata about the citation.

    :param citation: citation to search for
    :param service_url:
    :param results_parser:
    :param book_parser:
    """
    search_term = citation[fields.TITLE]

    start = timestamp()

    # create shorter versions of the original title alongside the original one,
    # so that in case the original one yields no results, we can try searching for
    # some permutations of it before giving up
    alternative_titles = list()
    # alternative_titles.append(search_term)

    for i in range(1, int(len([word for word in re.findall(r' ', search_term)]) / 2) + 1):
        alternative_titles.append(search_term.rsplit(' ', i)[0])

    alternative_titles = alternative_titles[-2:]
    alternative_titles.insert(0, search_term)

    alternative_titles = misc.broom(alternative_titles)
    assert alternative_titles

    for title in alternative_titles:
        log.info('Querying: {q}'.format(q=title))
        search_results = get_search_results(title, service_url, results_parser)
        if search_results:
            log.info("Successfully retrieved results for: '{t}'".format(t=title))

            for idx, result in enumerate(search_results):
                log.debug("checking result #{idx}/{sres}".format(idx=idx+1,sres=len(search_results)))

                data_from_service = urllib.request.urlopen(result).read()

                parsed_data = book_parser(data_from_service)
                parsed_data[fields.URI] = result

                if parsed_data and utils.similar_citations(citation, parsed_data):
                    log.info('Found similar data.')
                    log.debug("Similar {data} == {l_data}".format(data=parsed_data, l_data=citation))

                    log.info("Finished in {time}s".format(time=(int(timestamp() - start))))

                    return misc.fill_with_none(parsed_data)
                else:
                    log.debug(
                        "Not similar {data} != {l_data}".format(data=parsed_data, l_data=citation))
        else:
            log.info("No results for: '{t}'".format(t=title))

    log.info("Finished in {time}s".format(time=(int(timestamp() - start))))
    return None
