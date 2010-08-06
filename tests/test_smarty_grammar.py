from smartytotwig.tree_walker import TreeWalker
import unittest, time, smartytotwig

class TestSmartyGrammar(unittest.TestCase):
    """
    """

    def test_symbol(self):
           """
           """
           ast = smartytotwig.parse_file('examples/sample.tpl')
           print ast
           tree_walker = TreeWalker(ast)
           print tree_walker.code
           #self.assertEqual(1, 1)
   
    def test_if(self):
        """
        """
        
        # Test an an if with an else and a single logical operation.
        ast = smartytotwig.parse_string("{if foo}\nbar\n{else}\nfoo{/if}")
        #tree_walker = TreeWalker(ast)
        #self.assertEqual(tree_walker.code, "{% if foo %}\nbar\n{% else %}\nfoo{% endif %}")

        # Test an an if with an else and an elseif and two logical operations.
       # ast = smartytotwig.parse_string("{if foo and awesome.string|banana:\"foo\ $a\"}\nbar\n{elseif awesome.sauce[1] and blue and 'hello'}\nfoo{/if}")
       # tree_walker = TreeWalker(ast)
       # self.assertEqual(tree_walker.code, "{% if foo %}\nbar\n{% else %}\nfoo{% endif %}")


if __name__ == '__main__':
    unittest.main()