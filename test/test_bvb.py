import unittest
from common.bvb_sparql import bvb


class TestBVBSparqlMethods(unittest.TestCase):
    _TITLE = "Deep maps and spatial narratives"

    _RESULTS = [
        {
            'uri': {'type': 'uri', 'value': 'http://lod.b3kat.de/title/BV042483444'},
            'isbn': {'type': 'literal', 'value': '9780253015556'},
            'oclc': {'type': 'literal', 'value': '904466461'},
            'authors': {'type': 'uri', 'value': 'http://d-nb.info/gnd/1027282482'},
            'year': {'type': 'literal', 'value': '2015'},
            'responsibility': {'type': 'literal', 'value': 'ed by David J Bodenhamer'},
            'publisher': {'type': 'literal', 'value': 'Indiana Univ. Press'},
            'description': {'type': 'literal', 'value': 'ed by David J Bodenhamer'}
        },
        {
            'uri': {'type': 'uri', 'value': 'http://lod.b3kat.de/title/BV042483444'},
            'isbn': {'type': 'literal', 'value': '9780253015600'},
            'oclc': {'type': 'literal', 'value': '904466461'},
            'authors': {'type': 'uri', 'value': 'http://d-nb.info/gnd/1027282482'},
            'year': {'type': 'literal', 'value': '2015'},
            'responsibility': {'type': 'literal', 'value': 'ed by David J Bodenhamer'},
            'publisher': {'type': 'literal', 'value': 'Indiana Univ. Press'},
            'description': {'type': 'literal', 'value': 'ed by David J Bodenhamer'}
        },
        {
            'uri': {'type': 'uri', 'value': 'http://lod.b3kat.de/title/BV042483444'},
            'isbn': {'type': 'literal', 'value': '9780253015679'},
            'oclc': {'type': 'literal', 'value': '904466461'},
            'authors': {'type': 'uri', 'value': 'http://d-nb.info/gnd/1027282482'},
            'year': {'type': 'literal', 'value': '2015'},
            'responsibility': {'type': 'literal', 'value': 'ed by David J Bodenhamer'},
            'publisher': {'type': 'literal', 'value': 'Indiana Univ. Press'},
            'description': {'type': 'literal', 'value': 'ed by David J Bodenhamer'}
        },
        {
            'uri': {'type': 'uri', 'value': 'http://lod.b3kat.de/title/BV044061842'},
            'isbn': {'type': 'literal', 'value': '9780253015556'},
            'oclc': {'type': 'literal', 'value': '959595752'}, 'year': {'type': 'literal', 'value': '2015'},
            'responsibility': {'type': 'literal',
                               'value': 'edited by David J Bodenhamer, John Corrigan, and Trevor M Harris'},
            'publisher': {'type': 'literal', 'value': 'Indiana University Press'},
            'description': {'type': 'literal',
                            'value': 'edited by David J Bodenhamer, John Corrigan, and Trevor M Harris'}
        },
        {
            'uri': {'type': 'uri', 'value': 'http://lod.b3kat.de/title/BV044061842'},
            'isbn': {'type': 'literal', 'value': '9780253015600'},
            'oclc': {'type': 'literal', 'value': '959595752'}, 'year': {'type': 'literal', 'value': '2015'},
            'responsibility': {'type': 'literal',
                               'value': 'edited by David J Bodenhamer, John Corrigan, and Trevor M Harris'},
            'publisher': {'type': 'literal', 'value': 'Indiana University Press'},
            'description': {'type': 'literal',
                            'value': 'edited by David J Bodenhamer, John Corrigan, and Trevor M Harris'}
        },
        {
            'uri': {'type': 'uri', 'value': 'http://lod.b3kat.de/title/BV044061842'},
            'isbn': {'type': 'literal', 'value': '9780253015679'},
            'oclc': {'type': 'literal', 'value': '959595752'}, 'year': {'type': 'literal', 'value': '2015'},
            'responsibility': {'type': 'literal',
                               'value': 'edited by David J Bodenhamer, John Corrigan, and Trevor M Harris'},
            'publisher': {'type': 'literal', 'value': 'Indiana University Press'},
            'description': {'type': 'literal',
                            'value': 'edited by David J Bodenhamer, John Corrigan, and Trevor M Harris'}
        }
    ]

    def test_results_parser(self):
        results = bvb.results_parser(self._RESULTS, self._TITLE)
        self.assertTrue(results)