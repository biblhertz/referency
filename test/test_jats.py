import os
import unittest

import bs4

import common.jats as jats
from common.config import config


class TestJatsMethods(unittest.TestCase):
    TEST_FILE = os.path.join(config.INTER_FOLDER,
                             'HistoricalMeaningInMaps_2020_V4_la-FH_la_GO_style_clean',
                             config.JATS_FOLDER, 'out.xml')

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
            'Authors': ['Flavio Biondo', 'Bartolomeo Nogara', "et al."],
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
        citations = jats.parse(self.TEST_FILE)
        self.assertEqual(len(citations), 20)

        self.assertEqual(' See Matthew H. Edney, Cartography: The Ideal and Its History, Chicago 2019. ', citations[0])

    def test_update(self):
        updated_file = jats.update(self.TEST_FILE, self.TEST_REFS)

        with open(updated_file, "r") as file:
            soup = bs4.BeautifulSoup(file, "xml")

            self.assertIsNotNone(soup.find("back"))
            self.assertIsNotNone(soup.find("ref-list"))
            self.assertEqual(len(self.TEST_REFS), len(soup.findAll("ref")))
