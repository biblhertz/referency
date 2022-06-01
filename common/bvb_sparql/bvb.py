import copy
import bs4
import io

import common.utils as utils
from common.logger import log
from urllib import request
from common.misc import fields, fill_with_none, misc
from SPARQLWrapper import SPARQLWrapper, JSON
from common.config import config
from time import time as timestamp


class AuthorNameRetrievalError(RuntimeError):
    pass


def merge_records(records: list, fields_to_merge: list):
    """
    Merge individual records to one

    :param records: list of records to merge
    :param fields_to_merge: fields containing the information to merge

    :return : a single record
    :rtype : dict
    """
    merged = copy.deepcopy(records[0])

    for field in fields_to_merge:
        merged_field_data = set()

        data = [record[field] for record in records if field in record]

        for d in data:
            merged_field_data.update(
                filter(
                    lambda token: len(token),
                    # common prefixes added by bvb
                    # running any query against the endpoint
                    # should explain the following
                    d.replace("edited by", "").replace("ed by", "").replace(" and", ",").split(",")
                )
            )

        merged = {**merged, **{field: list(merged_field_data)}}

    return merged


def get_author_details_from_iri(author_uri: str):
    """
    Retrieve any author's name using its iri.

    :param author_uri: an author's iri

    :return: authors full name
    :rtype: str
    """
    author_uri = author_uri + '/about/marcxml'
    raw = bs4.BeautifulSoup(io.BytesIO(request.urlopen(author_uri).read()), 'xml')

    try:
        author_name = raw.find("datafield", {"tag": "100"}).find("subfield", {"code": "a"}).string
    except:
        log.error("Error retrieving marcxml for {}".format(author_uri))
        raise AuthorNameRetrievalError()

    return author_name


def flat_map_json_bindings(bindings: list):
    flat_mapped = list()

    # flat map json values
    for binding in bindings['results']['bindings']:
        d = dict()
        for key, value in binding.items():
            d[key] = value['value']
        flat_mapped.append(d)

    return flat_mapped


def merge(using: str, what: list, in_list: list):
    """
    In case the are more than one editors, or authors, the sparql endpoint
    will return more than one rows for the same result, representing all the
    possible combinations of the above.
    (e.g. two authors will result in two rows that share the same data in all
    columns expect the one holding author iri)

    Thus we need to reconstruct the information.

    :param using: the sparql variable shared among all rows representing the same data.(e.g. a uri)
    :param what: the sparql variables to merge their data
    :param in_list: the list containing the data to merge

    :return : list of records merged
    :rtype : list of dicts
    """
    merged_records = list()
    unique_ = set([result[using] for result in in_list])

    for uri in unique_:
        merged_records.append(
            merge_records(list(filter(lambda res: res[using] == uri, in_list)), what)
        )

    return merged_records


def results_parser(bindings: list, title: str):
    sparql_results = flat_map_json_bindings(bindings)

    sparql_results = merge(using="uri",
                           what=['responsibility', 'authors', 'description', 'isbn', 'oclc', 'year', 'publisher'],
                           in_list=sparql_results)

    records = list()

    for sparql_result in sparql_results:
        record = dict()

        record[fields.TITLE] = title
        record[fields.PUBLISHER] = sparql_result['publisher'][0] if sparql_result['publisher'] else None
        record[fields.RESPONSIBILITY] = sparql_result['responsibility'] or sparql_result['description']
        record[fields.OCLC] = sparql_result['oclc'][-1] if sparql_result['oclc'] else None
        record[fields.ISBN] = sparql_result['isbn'][-1] if sparql_result['isbn'] else None
        record[fields.YEAR] = sparql_result['year'][0] if sparql_result['year'] else None
        record[fields.AUTHORS] = list()
        record[fields.URI] = sparql_result['uri']

        if 'authors' in sparql_result:
            for author_iri in sparql_result['authors']:
                try:
                    record[fields.AUTHORS].append(get_author_details_from_iri(author_iri))
                except AuthorNameRetrievalError:
                    record[fields.AUTHORS] = list()
                    break;

        if 'responsibility' in sparql_result:
            record[fields.AUTHORS] = sparql_result['responsibility']
        elif 'description' in sparql_result:
            record[fields.AUTHORS] = sparql_result['description']
        else:
            log.error("Failed to find any author/editor/description in {}".format(sparql_result['uri']))
            record = {}

        if record:
            records.append(record)

    return [fill_with_none(r) for r in records]


def run(citation, sparql_query, title_sparql_var_name):
    start = timestamp()

    title = citation[fields.TITLE].strip()
    log.info('Querying: {q}'.format(q=title))

    sparql_query = sparql_query.replace(title_sparql_var_name, "\"" + title + "\"")

    if fields.YEAR in citation:
        sparql_query = sparql_query.replace("?issued", "\"" + citation[fields.YEAR].strip() + "\"^^xsd:gYear")

    sparql = SPARQLWrapper(config.BVB_ENDPOINT)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)

    sparql_results = sparql.query().convert()

    if sparql_results['results']['bindings']:
        log.info("Successfully retrieved results for: '{t}'".format(t=title))
    else:
        log.info("No results for: '{t}'".format(t=title))

    records = results_parser(sparql_results, title)

    for book_data in records:
        if utils.similar_citations(citation, book_data):
            log.info('Found similar data.')
            log.debug("Similar {data} == {l_data}".format(data=book_data, l_data=citation))
            log.info("Finished in {time}s".format(time=(int(timestamp() - start))))
            book_data[fields.RETRIEVED_WITH] = config.BVB_NAME
            return misc.fill_with_none(book_data)

    log.info("Finished in {time}s".format(time=(int(timestamp() - start))))

    return None
