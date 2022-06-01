import unittest

from common import utils
from common.misc import fields as f, broom


class TestUtilsMethods(unittest.TestCase):
    _RED_FOX = "The quick brown fox jumps over the lazy dog"

    _CITATION = (
        "Features of Common Sense Geography: Implicit Knowledge Structures in Ancient Geographical Texts, "
        "ed. Klaus Geus and Martin Thiering, "
        "Münster 2014 (Antike Kultur und Geschichte 16)"
    )

    _CITATION_AUTHOR_PAPER_PUBLISHER = (
        " For example,"
        " Werner Kuhn,"
        " “Cognitive and Linguistic Ideas in Geographic Information Semantics”,"
        " in Cognitive and Linguistic Aspects of Geographic Space: New Perspectives on Geographic Information Research"
        " (conference proceedings, Castillo-Palacio Magalia 1990/2010), "
        " ed. Martin Raubal et al.,"
        " Berlin and Heidelberg 2013, "
        " pp. 159-174;"
    )

    _CITATION_AUTHOR_PAPER_ONLY = (
        "See Ronald. W. Langacker, Cognitive Grammar: A Basic Introduction"
    )

    _CITATION_AUTHOR_PAPER_PUBLISHER_MULTIPLE = (
        " On the genesis of the Italia Illustrata, "
        " see esp. Bartolomeo Nogara,"
        " Scritti inediti e rari di Biondo Flavio, "
        " Rome 1927, "
        " Studi e Testi 48, "
        " p. 241; Sebastiano Gentile, "
        " <i>Florence e la scoperta dell’America. Umanesimo e geografia nel ’400 Fiorentino,</i> "
        " Florence 1992; Giovanni Salmeri,"
        " “Tra politica e antiquaria. Letture di Strabone nel XV e XVI secolo” ,"
        " in Strabone e l’Italia antica,"
        " ed. Gianfranco Maddoli,"
        " Naples 1988,"
        " pp. 303–305; Paolo Pontari’s introduction,"
        " in Blondus Flavius,"
        " Italia illustrata (1453),"
        " ed. Paolo Pontari,"
        " 3 vols., "
        " Rome 2011–2017 (Edizione nazionale delle opere di Biondo Flavio 4/1–3), "
        " vol. 1, "
        " 2011, "
        " pp. 25–63; and Patrick Gautier Dalché, "
        " “Strabo’s Reception in the West (Fifteenth–Sixteenth Centuries)”, "
        " in The Routledge Companion to Strabo, "
        " ed. Daniela Dueck, "
        " Abingdon and New York 2017, "
        " esp. p. 370."
    )

    _CITATION_PAPER_TITLE_AUTHORS_PUBLISHER = 'Grammars of Space, ed. Stephen C. Levinson and David Wilkins, Cambridge 2006 '

    _MULTIPLE_AUTHORS = ("see Günther Görz, Martin Smith, and Bernhard Schiemann, An Implementation "
                         "of the CIDOC Conceptual Reference Model (4.2.4) in OWL-DL, in Proceedings CIDOC "
                         "2008 – The Digital Curation of Cultural Heritage (conference proceedings, Athens 2008), "
                         "Athens 2008, pp. 1–14")

    _THREE_CITATIONS = " See Pablo Abend and Francis Harvey, “Maps as Geomedial Action Spaces: Considering the Shift \
    from Logocentric to Egocentric Engagements”, in <i>Geographic Journal</i>, 82, 1 (2017), pp. 171–183, see Martin \
    Thiering, <i>Spatial Semiotics and Spatial Mental Models Figure-Ground Asymmetries in Language</i>, Berlin 2015 \
    (Applied Cognitive Linguistics 27); <i>Grammars of Space: Explorations in Cognitive Diversity</i>, ed. Stephen C. \
    Levinson and David P. Wilkins, Cambridge 2006."

    _PP_P = "pp. 159-174, p. 168,pp. xx,p. xx, pp.   xx., p.    xx."

    def test_tokenize(self):
        results = utils.tokenize(self._RED_FOX)

        self.assertTrue("the" not in results)
        self.assertTrue("quick" in results)
        self.assertTrue("brown" in results)
        self.assertTrue("fox" in results)
        self.assertTrue("jumps" in results)
        self.assertTrue("over" not in results)
        self.assertTrue("the" not in results)
        self.assertTrue("lazy" in results)
        self.assertTrue("dog" in results)

        results = utils.tokenize(self._CITATION)

        self.assertTrue("features" in results)
        self.assertTrue("of" not in results)
        self.assertTrue("common" in results)
        self.assertTrue("sense" in results)
        self.assertTrue("geography" in results)
        self.assertTrue("implicit" in results)
        self.assertTrue("knowledge" in results)
        self.assertTrue("structures" in results)
        self.assertTrue("in" not in results)
        self.assertTrue("ancient" in results)
        self.assertTrue("geographical" in results)
        self.assertTrue("texts" in results)
        self.assertTrue("ed" in results)
        self.assertTrue("klaus" in results)
        self.assertTrue("geus" in results)
        # We don't consider 'and' a stop word.
        # This way conceptually different words
        # don't end up as a single one
        self.assertTrue("and" in results)
        self.assertTrue("martin" in results)
        self.assertTrue("thiering" in results)
        self.assertTrue("münster" in results)
        self.assertTrue("2014" in results)
        self.assertTrue("antike" in results)
        self.assertTrue("kultur" in results)
        self.assertTrue("und" in results)
        self.assertTrue("geschichte" in results)
        self.assertTrue("16" in results)

        results = utils.tokenize(self._PP_P)

        # assert no pp. or p. footnotes are removed
        self.assertEqual(len(results), 6)

    def test_is_valid_year(self):
        self.assertTrue(utils.is_valid_year("1920"))

        # assert non year input fails
        self.assertFalse(utils.is_valid_year("seven"))
        self.assertFalse(utils.is_valid_year("19 20"))

        # assert that string is a valid year not that it only contains one
        self.assertFalse(utils.is_valid_year("1920 "))
        self.assertFalse(utils.is_valid_year(" 1920"))

    def test_get_human_names(self):
        # check valid human names
        self.assertIn("John Doe", utils.get_human_names("John Doe"))
        self.assertEqual(len(utils.get_human_names("John Doe")), 1)

        self.assertIn("Winston Churchill", utils.get_human_names("Winston Churchill"))
        self.assertEqual(len(utils.get_human_names("Winston Churchill")), 1)

        self.assertIn("Rafael Nadal", utils.get_human_names("Rafael Nadal"))
        self.assertEqual(len(utils.get_human_names("Rafael Nadal")), 1)

        self.assertIn("Gerald Hiebel", utils.get_human_names("and Gerald Hiebel", strict=False))
        self.assertEqual(len(utils.get_human_names("and Gerald Hiebel", strict=False)), 1)

        self.assertIsNone(utils.get_human_names("and Gerald Hiebel", strict=True))

        self.assertIn("Ioannis Kapodistrias", utils.get_human_names("Ioannis Kapodistrias"))
        self.assertEqual(len(utils.get_human_names("Ioannis Kapodistrias")), 1)

        self.assertIn("Matthew H. Edney", utils.get_human_names("Matthew H. Edney"))
        self.assertEqual(len(utils.get_human_names("Matthew H. Edney")), 1)

        # check a valid lastname with name initials
        self.assertIn("L. S. Churchill", utils.get_human_names("L. S. Churchill"))
        self.assertEqual(len(utils.get_human_names("L. S. Churchill")), 1)

        # check with a valid firstname, name initials and lastname
        self.assertIn("Winston L. S. Churchill", utils.get_human_names("Winston L. S. Churchill"))
        self.assertEqual(len(utils.get_human_names("Winston L. S. Churchill")), 1)

        # Nice edge case I stumbled upon.
        # Bartolomeo is both a common firstname and a common lastname
        # Nogara is a rare lastname and an even rarer firstname
        self.assertIn("Bartolomeo Nogara", utils.get_human_names("Bartolomeo Nogara"))
        self.assertEqual(len(utils.get_human_names("Bartolomeo Nogara")), 1)

        # check with a valid firstname with a non valid lastname
        self.assertIsNone(utils.get_human_names("Michael Computer"))
        self.assertIsNone(utils.get_human_names("Computer Michael"))

        # check with a valid lastname and a non valid firstname
        self.assertIsNone(utils.get_human_names("Smith Computer"))
        self.assertIsNone(utils.get_human_names("Computer Smith"))

        # non-sense strings
        self.assertIsNone(utils.get_human_names("Sense Geography"))
        self.assertIsNone(utils.get_human_names("Computer Science"))

        self.assertIn('Anderson Silva', utils.get_human_names("Anderson Silva and Mike Tyson"))
        self.assertIn('Mike Tyson', utils.get_human_names("Anderson Silva and Mike Tyson"))

        self.assertIn('John Smith', utils.get_human_names("John Smith et al."))
        self.assertIn('et al.', utils.get_human_names("John Smith et al."))

        self.assertIn("Winston Churchill",
                      utils.get_human_names(
                          "I no longer listen to what people say, I just watch what they do. \
                          Behavior never lies. \
                          Winston Churchill"))

    def test_author_paper_title_publising_info(self):
        tokens = self._CITATION_AUTHOR_PAPER_PUBLISHER.split(",")
        data, last_consumed = utils.author_paper_title_publishing_info(self._CITATION_AUTHOR_PAPER_PUBLISHER,
                                                                       tokens[2:])

        self.assertIsNotNone(data)
        self.assertEqual(type(data), type({}))
        self.assertIn("Cognitive and Linguistic Ideas in Geographic Information Semantics", data[f.TITLE])
        self.assertIn("Berlin and Heidelberg 2013", data[f.PUBLISHER])
        self.assertEqual(last_consumed, 4)

        tokens = self._CITATION_AUTHOR_PAPER_ONLY.split(",")

        data, last_consumed = utils.author_paper_title_publishing_info(self._CITATION_AUTHOR_PAPER_ONLY, tokens[1:])

        self.assertIsNone(data)
        self.assertIsNone(last_consumed)

        tokens = self._CITATION_PAPER_TITLE_AUTHORS_PUBLISHER.split(',')
        data, last_consumed = utils.author_paper_title_publishing_info(
            self._CITATION_PAPER_TITLE_AUTHORS_PUBLISHER.replace(tokens[1], ""),
            tokens[:1] + tokens[2:])

        self.assertIsNotNone(data)
        self.assertEqual(type(data), type({}))
        self.assertIn("Grammars of Space", data[f.TITLE])
        self.assertIn("Cambridge 2006", data[f.PUBLISHER])
        self.assertEqual(last_consumed, 1)

    def test_author_paper_title_page_references(self):
        tokens = self._CITATION_AUTHOR_PAPER_PUBLISHER.split(",")

        data, last_consumed = utils.author_paper_title_page_references(self._CITATION_AUTHOR_PAPER_PUBLISHER,
                                                                       tokens[2:])

        self.assertIsNotNone(data)
        self.assertEqual(type(data), type({}))
        self.assertIn("Cognitive and Linguistic Ideas in Geographic Information Semantics", data[f.TITLE])
        self.assertIn("pp. 159-174", data[f.PAGES])
        self.assertEqual(last_consumed, 5)

        tokens = self._CITATION_AUTHOR_PAPER_PUBLISHER_MULTIPLE.split(",")

        data, last_consumed = utils.author_paper_title_page_references(self._CITATION_AUTHOR_PAPER_PUBLISHER_MULTIPLE,
                                                                       tokens[2:])

        self.assertIsNotNone(data)
        self.assertEqual(type(data), type({}))
        self.assertIn("Scritti inediti e rari di Biondo Flavio", data[f.TITLE])
        self.assertIn("p. 241", data[f.PAGES])
        self.assertEqual(last_consumed, 3)

        data, last_consumed = utils.author_paper_title_page_references(self._CITATION_AUTHOR_PAPER_PUBLISHER_MULTIPLE,
                                                                       tokens[8:])

        self.assertIsNotNone(data)
        self.assertEqual(type(data), type({}))
        self.assertIn("Tra politica e antiquaria. Letture di Strabone nel XV e XVI secolo", data[f.TITLE])
        self.assertIn("pp. 303–305", data[f.PAGES])
        self.assertEqual(last_consumed, 4)

        tokens = self._CITATION_AUTHOR_PAPER_ONLY.split(",")

        data, last_consumed = utils.author_paper_title_publishing_info(self._CITATION_AUTHOR_PAPER_ONLY, tokens[1:])

        self.assertIsNone(data)
        self.assertIsNone(last_consumed)

    def test_try_author_based_patterns(self):
        results = utils.try_author_based_patterns(self._CITATION_AUTHOR_PAPER_PUBLISHER)

        self.assertEqual(len(results), 1)
        self.assertEqual("Cognitive and Linguistic Ideas in Geographic Information Semantics", results[0][f.TITLE])
        self.assertEqual("Cognitive and Linguistic Aspects of Geographic Space: New Perspectives on Geographic "
                         "Information Research (conference proceedings, Castillo-Palacio Magalia 1990/2010)",
                         results[0][f.CONTENT])
        self.assertIn("Martin Raubal et al", results[0][f.RESPONSIBILITY])
        self.assertEqual("pp. 159-174", results[0][f.PAGES])

        results = list()

        sentences = utils.sentence_tokenize(self._CITATION_AUTHOR_PAPER_PUBLISHER_MULTIPLE)
        for sentence in sentences:
            results.extend(utils.try_author_based_patterns(sentence))

        self.assertEqual(6, len(results))

        self.assertEqual(len(results[0][f.AUTHORS]), 1)
        self.assertEqual("Esp Bartolomeo Nogara", results[0][f.AUTHORS][0])
        self.assertIn("Scritti inediti e rari di Biondo Flavio", results[0][f.TITLE])
        # MISSING PUBLISHER INFO
        self.assertEqual("p. 241", results[0][f.PAGES])

        self.assertEqual(len(results[1][f.AUTHORS]), 1)
        self.assertEqual("Sebastiano Gentile", results[1][f.AUTHORS][0])
        self.assertEqual(broom("Florence e la scoperta dell’America. Umanesimo e geografia nel ’400 Fiorentino"),
                         results[1][f.TITLE])
        self.assertEqual("Florence 1992", results[1][f.PUBLISHER])

        self.assertEqual(len(results[2][f.AUTHORS]), 1)
        self.assertEqual("Giovanni Salmeri", results[2][f.AUTHORS][0])
        self.assertEqual("Tra politica e antiquaria. Letture di Strabone nel XV e XVI secolo", results[2][f.TITLE])
        self.assertEqual(broom("Strabone e l’Italia antica"), results[2][f.CONTENT])
        self.assertIn("Gianfranco Maddoli", results[2][f.RESPONSIBILITY])
        # MISSING PUBLISHER INFO
        self.assertEqual("pp. 303-305", results[2][f.PAGES])

        self.assertEqual(len(results[3][f.AUTHORS]), 1)
        self.assertEqual("Paolo Pontari", results[3][f.AUTHORS][0])
        self.assertIn("Blondus Flavius, Italia illustrata (1453)", results[3][f.TITLE])
        self.assertIn("Blondus Flavius, Italia illustrata (1453)", results[3][f.CONTENT])
        self.assertIn("Paolo Pontari", results[3][f.RESPONSIBILITY])
        # MISSING PUBLISHER INFO
        self.assertEqual("pp. 25-63", results[3][f.PAGES])

        self.assertEqual(len(results[4][f.AUTHORS]), 1)
        self.assertEqual(broom("Patrick Gautier Dalché"), results[4][f.AUTHORS][0])
        self.assertEqual(broom("Strabo’s Reception in the West (Fifteenth–Sixteenth Centuries)"), results[4][f.TITLE])
        self.assertEqual("The Routledge Companion to Strabo", results[4][f.CONTENT])
        self.assertIn("Daniela Dueck", results[4][f.RESPONSIBILITY])
        # MISSING PUBLISHER INFO
        self.assertEqual("p. 370", results[4][f.PAGES])

        results = utils.try_author_based_patterns(self._MULTIPLE_AUTHORS)

        self.assertIn("An Implementation of the CIDOC Conceptual Reference Model (4.2.4) in OWL-DL",
                      results[0][f.TITLE])
        self.assertIn(
            "Proceedings CIDOC 2008 - The Digital Curation of Cultural Heritage",
            results[0][f.CONTENT])

        results = utils.try_author_based_patterns(self._MULTIPLE_AUTHORS + ',' + self._MULTIPLE_AUTHORS)
        self.assertEqual(len(results), 2)
        self.assertDictEqual(results[0], results[1])

    def test_sentence_tokenize(self):
        tokens = utils.sentence_tokenize(self._THREE_CITATIONS)
        self.assertEqual(3, len(tokens))

    def test_try_collective_works_pattern(self):
        result, ignore = utils.collective_works_pattern(self._CITATION_AUTHOR_PAPER_PUBLISHER)
        self.assertIn(
            "Cognitive and Linguistic Aspects of Geographic Space: New Perspectives on Geographic Information Research",
            result[f.CONTENT])
        self.assertIn('Martin Raubal et al', result[f.RESPONSIBILITY])

        result, ignore = utils.collective_works_pattern(self._CITATION_PAPER_TITLE_AUTHORS_PUBLISHER)
        self.assertEqual('Grammars of Space', result[f.CONTENT])
        self.assertIn('Stephen C. Levinson', result[f.RESPONSIBILITY])
        self.assertIn('David Wilkins', result[f.RESPONSIBILITY])

    def test_get_pp(self):
        self.assertEqual('pp. 198-200', utils.get_pp('see pp. 198-200'))
        self.assertEqual('pp. xx', utils.get_pp('see pp. xx'))
        self.assertEqual('pp 198-200', utils.get_pp('pp 198-200'))
        self.assertEqual('pp xx', utils.get_pp('see pp xx'))

        self.assertEqual('p. 198', utils.get_pp('see p. 198'))
        self.assertEqual('p. xx', utils.get_pp('see p. xx'))
        self.assertEqual('p 198', utils.get_pp('p 198'))
        self.assertEqual('p xx', utils.get_pp('see p xx'))

    def test_similar_authors(self):
        self.asssertTrue(utils.similar_authors(['Ottavio Clavuot'], ['Clavuot, Ottavio']))
        
    _TAILS = (
        { "text": "(2013): 88-99", "data": {"when": "2013", "pfrom":"88", "pto":"99"} },
        { "text": " (2013) p. 88", "data": {"when": "2013", "pfrom":"88", "pto":None} },
        { "text": " v13 n3 (198505): 208-217", "data": {"when": "198505", "pfrom":"208", "pto":"217"} },
        { "text": " v28 n6 (2014 01 01) pp. 1272-1293", "data": {"when": "2014 01 01", "pfrom":"1272", "pto":"1293"} }
    )
    
    def test_tail(self):
        for tail in self._TAILS:
            self.assertEqual(tail['data'], utils.parse_tail(tail['text']))
