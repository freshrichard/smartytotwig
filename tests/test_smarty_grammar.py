from smartytotwig.tree_walker import TreeWalker
import unittest, time, smartytotwig

class TestSmartyGrammar(unittest.TestCase):
    """
    """
    def test_symbol(self):
        """
        """
        ast = smartytotwig.parse_file('examples/sample.tpl')
        tree_walker = TreeWalker(ast)
        
        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()