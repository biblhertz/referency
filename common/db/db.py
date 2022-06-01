import tqdm

import common.worldcat as worldcat
import common.kubikat as kubikat

from functools import lru_cache
from common.config import config
from common import query
from common.logger import log
from common.misc import fields, freeze
from common.bvb_sparql import bvb


def _mapper(refs, function):
    filtered_dict = {k: list() for k, v in refs.items()}
    pbar = tqdm.tqdm(total=len(refs))
    for key, value in refs.items():
        #pbar2 = tqdm.tqdm(total=len(refs),desc='Items',position=0)
        for item in value:
            if fields.RETRIEVED_WITH in item:
                filtered_dict[key].append(item)
            elif fields.TITLE in item:
                try:
                    data = function(freeze(item))
                    if data:
                        log.info("For ref {ref} retrieved {data}".format(ref=item, data=data))
                        filtered_dict[key].append(data)
                except Exception as ex:
                    import traceback
                    log.error('Caught error: {err}'.format(err=ex))
                    traceback.print_exc()
                    continue
        pbar.update(1)

    return filtered_dict


@lru_cache(config.CACHE_SIZE)
def _worldcat_wrapper(reference):
    return query.run(reference, worldcat.SERVICE_URL, worldcat.results_parser, worldcat.book_parser)


@lru_cache(config.CACHE_SIZE)
def _kubikat_wrapper(reference):
    return query.run(reference, kubikat.SERVICE_URL, kubikat.results_parser, kubikat.book_parser)


@lru_cache(config.CACHE_SIZE)
def _bvb_wrapper(reference):
    return bvb.run(
        reference,
        """    
            PREFIX  rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX  rdfs:<http://www.w3.org/2000/01/rdf-schema#>
            PREFIX  owl:<http://www.w3.org/2002/07/owl#>
            PREFIX  dc:<http://purl.org/dc/elements/1.1/>
            PREFIX  dct:<http://purl.org/dc/terms/>
            PREFIX  dcmitype:<http://purl.org/dc/dcmitype/>
            PREFIX  bibo:<http://purl.org/ontology/bibo/>
            PREFIX  frbr:<http://purl.org/vocab/frbr/core#>
            PREFIX  event:<http://purl.org/NET/c4dm/event.owl#>
            PREFIX  foaf:<http://xmlns.com/foaf/0.1/>
            PREFIX  skos:<http://w3.org/2004/02/skos/core#>
            PREFIX  geonames:<http://www.geonames.org/ontology#>
            PREFIX  marcrel:<http://id.loc.gov/vocabulary/relators/>
            PREFIX  rdagr1:<http://rdvocab.info/Elements/>
            PREFIX  umbel: <http://umbel.org/umbel#>
            PREFIX  b3kat: <http://bsb-muenchen.de/ont/b3katOntology#>
            
            SELECT DISTINCT ?uri ?isbn ?oclc ?authors ?year ?responsibility ?publisher ?description WHERE {
              ?uri dc:title ?title .
              ?uri <http://purl.org/dc/terms/issued> ?issued.
              ?uri <http://purl.org/dc/terms/publisher> ?publisher .
              OPTIONAL {
                ?uri <http://purl.org/dc/terms/description> ?description .
              }
              OPTIONAL {
                ?uri <http://purl.org/dc/terms/contributor> ?authors .
              }
              OPTIONAL {
                 ?uri <http://purl.org/dc/terms/description> ?responsibility .
              }
              OPTIONAL {
                ?uri bibo:isbn ?isbn
              }
              OPTIONAL {
                ?uri bibo:oclcnum ?oclc
              }
              FILTER(?responsibility != "Includes index")
              FILTER(?responsibility != "Description based on print version record")
              FILTER(?description != "Includes index")
              FILTER(?description != "Description based on print version record")
              BIND(str(?issued) as ?year)
            }
        """,
        "?title")


def _opencitations_wrapper(reference):
    _Q = "  PREFIX cito: <http://purl.org/spar/cito/> \
            PREFIX dcterms: <http://purl.org/dc/terms/> \
            PREFIX datacite: <http://purl.org/spar/datacite/> \
            PREFIX literal: <http://www.essepuntato.it/2010/06/literalreification/> \
            PREFIX biro: <http://purl.org/spar/biro/> \
            PREFIX frbr: <http://purl.org/vocab/frbr/core#> \
            PREFIX c4o: <http://purl.org/spar/c4o/> \
            PREFIX prism: <http://prismstandard.org/namespaces/basic/2.0/> \
            PREFIX pro: <http://purl.org/spar/pro/> \
            PREFIX foaf: <http://xmlns.com/foaf/0.1/> \
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> \
            \
            SELECT ?doi WHERE { \
              ?paper dcterms:title ?title . \
              OPTIONAL { \
                ?paper datacite:hasIdentifier [ \
                    datacite:usesIdentifierScheme datacite:doi ; \
                    literal:hasLiteralValue ?doi \
                  ] \
              } \
            }"

    # s = sparql.Service(config.OPENCITATIONS_ENDPOINT)
    # titleQuery = query.replace("\n", " ").replace(config.TITLE, '"' + reference[fields.TITLE] + '"')
    # res = s.query(titleQuery)
    # for row in res:
    #    raise NotImplementedError()
    # else:
    #    raise NotImplementedError()


# Check against Database
def check(database, references: list):
    if database in config.ENDPOINTS.values():
        _db_wrapper = globals()['_' + database + '_wrapper']
        return _mapper(references, _db_wrapper)
    else:
        log.error("Endpoint with name '{name}' not found in endpoint list '{endlist}'". \
                  format(name=database, endlist=config.ENDPOINTS))
        raise RuntimeError()
