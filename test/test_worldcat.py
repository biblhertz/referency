import unittest
import urllib.request

from common import worldcat
from common.misc import broom, fields as f


class TestWorldcatMethods(unittest.TestCase):
    _TITLE_UNIQUE_IDENTIFIER = "Automated Geocoding of Textual Documents: A Survey of Current Approaches Automated Geocoding of Textual Documents"
    _TITLE_ISBN_OCLC = "The power of maps"
    _CHAPTER_TITLE = "Regional Cartography in Medieval Europe"

    def test_book_parser(self):
        _DATA = '''
<html><body>

    <div id="bibdata">
        <h1 class="title">Granularity of locations referred to by place descriptions</h1>
        <table cellspacing="0" cellpadding="0" border="0"><tbody>
            <tr id="bib-author-row"><th>Author:</th>
                <td id="bib-author-cell"><a href="/search?q=au%3AD+Richter&amp;qt=hot_author" title="Search for more by this author">D Richter</a>; <a href="/search?q=au%3AS+Winter&amp;qt=hot_author" title="Search for more by this author">S Winter</a>; <a href="/search?q=au%3AK++F+Richter&amp;qt=hot_author" title="Search for more by this author">K  F Richter</a>; <a href="/search?q=au%3AL+Stirling&amp;qt=hot_author" title="Search for more by this author">L Stirling</a></td>
            </tr>
            <tr id="bib-itemType-row"><th>Edition/Format:</th>
                <td id="bib-itemType-cell"><span class="art" id="editionFormatType"><img src="/wcpa/images/icon-art.gif" alt="Article" width="16" height="16" border="0" align="absmiddle"> <span class="itemType">Article</span> : English</span></td>
            </tr>
            <tr id="bib-journalTitle-row"><th>Publication:</th>
                <td id="bib-journalTitle-cell">COMPUTERS ENVIRONMENT AND URBAN SYSTEMS, 41, (2013): 88-99</td>
            </tr>
            <tr id="bib-otherDatabases-row"><th>Other Databases:</th>
                <td id="bib-otherDatabases-cell"><a title="WorldCat" href="/oclc/851500171">WorldCat</a></td>
            </tr>
            <tr><th>Rating:</th>
                <td><p class="rating"><span class="star0">(not yet rated)</span><a class="downpage" href="#reviews" title="Jump down this page to read user reviews">0 with reviews - Be the first.</a></p></td>
            </tr>
        </tbody></table>
    </div>
        
</body></html>
'''
        parsed = worldcat.book_parser(_DATA)
        self.assertEquals('2013', parsed['Year'])

    def test_query(self):
        results = urllib.request.urlopen(
            worldcat.SERVICE_URL.format(title=self._TITLE_UNIQUE_IDENTIFIER.replace(' ', '+'))).read()
        self.assertTrue(results)

        results = worldcat.results_parser(results, 5)
        self.assertTrue(results)

        data = urllib.request.urlopen(results[0]).read()
        self.assertTrue(data)

        book_info = worldcat.book_parser(data)
        book_info = broom(book_info)

        self.assertIn('Fernando Melo', book_info[f.AUTHORS][0])
        self.assertIn('Bruno Martins', book_info[f.AUTHORS][1])
        self.assertIn('en', book_info[f.LANG])
        self.assertEqual('6227032738', book_info[f.UNIQUE_ID])
        self.assertEqual(self._TITLE_UNIQUE_IDENTIFIER, book_info[f.TITLE])

        results = urllib.request.urlopen(
            worldcat.SERVICE_URL.format(title=self._TITLE_ISBN_OCLC.replace(' ', '+'))).read()
        self.assertTrue(results)

        results = worldcat.results_parser(results, 5)
        self.assertTrue(results)

        data = urllib.request.urlopen(results[0]).read()
        self.assertTrue(data)

        book_info = worldcat.book_parser(data)
        book_info = broom(book_info)

        self.assertIn('Denis Wood', book_info[f.AUTHORS])
        self.assertIn('John Fels', book_info[f.AUTHORS])
        self.assertIn('en', book_info[f.LANG])
        self.assertEqual(self._TITLE_ISBN_OCLC, book_info[f.TITLE])
        self.assertEqual("9780415096669", book_info[f.ISBN])
        self.assertEqual("1055155227", book_info[f.OCLC])

        results = urllib.request.urlopen(
            worldcat.SERVICE_URL.format(title=self._CHAPTER_TITLE.replace(' ', '+'))).read()
        self.assertTrue(results)

        results = worldcat.results_parser(results, 5)
        self.assertTrue(results)

        data = urllib.request.urlopen(results[0]).read()
        self.assertTrue(data)

        book_info = worldcat.book_parser(data)
        book_info = broom(book_info)

        self.assertIn('J.B. Harley', book_info[f.AUTHORS])
        self.assertIn('David Woodward', book_info[f.AUTHORS])
        self.assertIn('en', book_info[f.LANG])
        self.assertEqual('Cartography in prehistoric, ancient, and medieval Europe and the Mediterranean',
                         book_info[f.TITLE])
        self.assertEqual("9780226316338", book_info[f.ISBN])
        self.assertEqual("781786112", book_info[f.OCLC])

        self.assertIn('ed. by J.B. Harley and David Woodward', book_info[f.RESPONSIBILITY])
        self.assertIn(self._CHAPTER_TITLE, book_info[f.CONTENT])
        
