import os
import unittest

import bs4

import common.tei as tei
from common.config import config


class TestTeiMethods(unittest.TestCase):
    TEST_FILE = os.path.join(config.INTER_FOLDER,
                             'Guckelsberger-Geus_Biondo-Measurements_maps_material_V4_la_corr-KGkg_la_GO_style_clean',
                             config.TEI_FOLDER, 'out.xml')
    TEST_REFS = [
        {
            'Title': 'Italia illustrata',
            'Authors': ['Flavius Blondus', 'Paolo Pontari'],
            'Language': 'it',
            'Publisher': 'Roma Ist Storico Italiano per il Medio Evo',
            'Year': '2014',
            'ISBN': '8898079184',
            'OCLC': '891917573',
            'Responsibility': ['Paolo Pontari'],
            'RetrievedWith': 'WorldCat',
            'UniqueID': None,
            'Pages': "198-200",
            'Content': None
        },
        {
            'Title': 'Scritti inediti e rari di Biondo Flavio',
            'Authors': ['Flavio Biondo', 'Bartolomeo Nogara'],
            'Language': 'it',
            'Publisher': 'Roma Biblioteca apostolica Vaticana',
            'Year': '1973',
            'OCLC': '442279842',
            'Responsibility': ['Bartolomeo Nogara'],
            'RetrievedWith': 'WorldCat',
            'ISBN': "8898079184",
            'UniqueID': None,
            'Pages': "15",
            'Content': None
        },
    ]

    def test_parse(self):
        citations = tei.parse(self.TEST_FILE)
        self.assertEqual(len(citations), 56)

        self.assertEqual(
            ("On the genesis of the Italia Illustrata , see esp. Bartolomeo Nogara, Scritti inediti e rari di Biondo "
             "Flavio , Rome 1927, Studi e Testi 48, p. 241; Sebastiano Gentile, Firenze e la scoperta dell’America. "
             "Umanesimo e geografia nel ’400 Fiorentino , Firenze 1992; Giovanni Salmeri, “Tra politica e antiquaria. "
             "Letture di Strabone nel XV e XVI secolo”, in Strabone e l’Italia antica , ed. Gianfranco Maddoli, "
             "Naples 1988, pp. 303–305; Paolo Pontari’s introduction, in Blondus Flavius, Italia illustrata (1453), "
             "ed. Paolo Pontari, 3 vols., Rome 2011–2017 (Edizione nazionale delle opere di Biondo Flavio 4/1–3), "
             "vol. 1, 2011, pp. 25–63; and Patrick Gautier Dalché, “Strabo ’ s Reception in the West "
             "(Fifteenth–Sixteenth Centuries)”, in The Routledge Companion to Strabo , ed. Daniela Dueck, "
             "Abingdon and New York 2017, esp. p. 370. "),
            citations[0].replace('<i>', '').replace('</i>', ''))

    def test_update(self):
        update_file = tei.update(self.TEST_FILE, self.TEST_REFS)

        with open(update_file, "r") as file:
            soup = bs4.BeautifulSoup(file, "xml")

            self.assertIsNotNone(soup.find("teiHeader"))
            self.assertIsNotNone(soup.find("listBibl"))
            self.assertEqual(len(self.TEST_REFS), len(soup.findAll("biblStruct")))
