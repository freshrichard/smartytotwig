import unittest, time, smartytotwig

class TestSmartyGrammar(unittest.TestCase):
    """
    """
    def test_symbol(self):
        """
        """
        print smartytotwig.parse_file('examples/sample.tpl')
        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()