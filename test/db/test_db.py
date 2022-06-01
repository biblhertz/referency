import unittest
from common.config import config
from common.misc import fields
from common.db import db


class TestDb(unittest.TestCase):
    REF = {
        "cit_key": [
            {
                fields.TITLE: 'Italy Illuminated 1453',
                fields.AUTHORS: ["Biondo Flavio", "LinkWhite Jeffrey A."]
            }
        ]
    }

    BVB_REF = {
        "cit_key": [
            {
                fields.TITLE: "Deep maps and spatial narratives",
                fields.AUTHORS: ["David J Bodenhamer", "John Corrigan", "Trevor M Harris"]
            }
        ]
    }

    REF_NONSENSE = {
        "cit_key": [
            {
                fields.TITLE: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus varius ante ac pretium mattis.',
                fields.AUTHORS: [
                    'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus varius ante ac pretium mattis.']
            }
        ]
    }

    def test_check(self):
        import copy

        refs = copy.deepcopy(self.REF)
        ret = db.check(config.ENDPOINTS['Worldcat'], refs)
        self.assertNotEqual(ret['cit_key'], [])

        refs = copy.deepcopy(self.REF)
        ret = db.check(config.ENDPOINTS['Kubikat'], refs)
        self.assertNotEqual(ret['cit_key'], [])

        refs = copy.deepcopy(self.BVB_REF)
        ret = db.check(config.ENDPOINTS['BVB'], refs)
        self.assertNotEqual(ret['cit_key'], [])

        refs = copy.deepcopy(self.REF_NONSENSE)
        ret = db.check(config.ENDPOINTS['Worldcat'], refs)
        self.assertEqual(ret['cit_key'], [])

        refs = copy.deepcopy(self.REF_NONSENSE)
        ret = db.check(config.ENDPOINTS['Kubikat'], refs)
        self.assertEqual(ret['cit_key'], [])

        refs = copy.deepcopy(self.REF_NONSENSE)
        ret = db.check(config.ENDPOINTS['BVB'], refs)
        self.assertEqual(ret['cit_key'], [])
