import unittest
import urllib.request

from common import kubikat
from common.misc import broom, fields as f


class TestKubikatMethods(unittest.TestCase):
    _TITLE = 'Italy Illuminated (1453)'
    _JOURNAL_TITLE = 'Cartography in prehistoric ancient and medieval Europe and the Mediterranean'

    def test_search_results_parser(self):
        results = urllib.request.urlopen(kubikat.SERVICE_URL.format(title=self._TITLE.replace(' ', '+'))).read()
        self.assertTrue(results)

        results = kubikat.results_parser(results, 5)
        self.assertTrue(results)

        data = urllib.request.urlopen(results[0]).read()
        self.assertTrue(data)

        book_info = kubikat.book_parser(data)
        book_info = broom(book_info)
        self.assertIn('Biondo, Flavio', book_info[f.AUTHORS])
        self.assertIn('White, Jeffrey A', book_info[f.AUTHORS])
        self.assertEqual('Italy illuminated', book_info[f.TITLE])
        self.assertEqual('Cambridge, Mass. [u.a.] : Harvard Univ. Press', book_info[f.PUBLISHER])
        self.assertEqual('Biondo Flavio. Ed. and transl. by Jeffrey A. White', book_info[f.RESPONSIBILITY])

        results = urllib.request.urlopen(kubikat.SERVICE_URL.format(title=self._JOURNAL_TITLE.replace(' ', '+'))).read()
        self.assertTrue(results)

        results = kubikat.results_parser(results, 5)
        self.assertTrue(results)

        data = urllib.request.urlopen(results[0]).read()
        self.assertTrue(data)

        book_info = kubikat.book_parser(data)
        book_info = broom(book_info)
        self.assertIn('Harley, J. B', book_info[f.AUTHORS])
        self.assertIn('Woodward, David', book_info[f.AUTHORS])
        self.assertEqual('Cartography in prehistoric, ancient and medieval Europe and the Mediterranean',
                         book_info[f.TITLE])
        self.assertEqual('1987', book_info[f.PUBLISHER])
        self.assertEqual('ed. by J. B. Harley and David Woodward', book_info[f.RESPONSIBILITY])
        self.assertIn('Regional Cartography in Medieval Europe', book_info[f.CONTENT])
