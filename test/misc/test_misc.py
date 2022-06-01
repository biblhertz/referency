import string
import unittest


class TestMisc(unittest.TestCase):

    def test_broom(self):
        from common.misc import fields
        from common.misc import broom
        import random

        data = dict()

        for f in fields.ALL:
            data[f] = '  ,;.; ' + ''.join(random.choice(string.ascii_letters) for i in range(10)) + ' ,.. ,'

        data = broom(data)

        for key, value in data.items():
            self.assertIn(key, fields.ALL)
            self.assertTrue(value[0] != ' ')
            self.assertTrue(value[0] != ',')
            self.assertTrue(value[0] != ';')

            self.assertTrue(value[-1] != ' ')
            self.assertTrue(value[-1] != ',')
            self.assertTrue(value[-1] != ';')

        for f in fields.ALL:
            data[f] = list()
            for i in range(0, 5):
                data[f].append('  ,;.; ' + ''.join(random.choice(string.ascii_letters) for j in range(10)) + ' ,.. ,')

        data = broom(data)

        for key, d in data.items():
            for value in d:
                self.assertIn(key, fields.ALL)
                self.assertTrue(value[0] != ' ')
                self.assertTrue(value[0] != ',')
                self.assertTrue(value[0] != ';')

                self.assertTrue(value[-1] != ' ')
                self.assertTrue(value[-1] != ',')
                self.assertTrue(value[-1] != ';')

        self.assertIsNone(broom(None))
