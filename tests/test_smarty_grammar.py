from smartytotwig.tree_walker import TreeWalker
import unittest, time, smartytotwig

class TestSmartyGrammar(unittest.TestCase):
    """
    """

    def test_sample(self):
           """
           Runs and prints out the sample.tpl file, this is used
           during debugging.
           """
           ast = smartytotwig.parse_file('examples/sample.tpl')
           print ast
           tree_walker = TreeWalker(ast)
           print tree_walker.code
   
    def test_if_statement(self):
        """
        Test several different types of if statements.
        """
        # Test an if statement (no else or elseif)
        ast = smartytotwig.parse_string("{if foo or foo.bar or foo|bar:foo['hello']}\nfoo\n{/if}")
        tree_walker = TreeWalker(ast)
        self.assertEqual(tree_walker.code, "{% if foo or foo.bar or foo|bar(foo['hello']) %}\nfoo\n{% endif %}")
        
        # Test an an if with an else and a single logical operation.
        ast = smartytotwig.parse_string("{if foo}\nbar\n{else}\nfoo{/if}")
        tree_walker = TreeWalker(ast)
        self.assertEqual(tree_walker.code, "{% if foo %}\nbar\n{% else %}\nfoo{% endif %}")

        # Test an an if with an else and an elseif and two logical operations.
        ast = smartytotwig.parse_string("{if foo and awesome.string|banana:\"foo\\\" $a\"}\nbar\n{elseif awesome.sauce[1] and blue and 'hello'}\nfoo{/if}")
        tree_walker = TreeWalker(ast)
        self.assertEqual(tree_walker.code, "{% if foo and awesome.string|banana(\"foo\\\" %s\"|format(a)) %}\nbar\n{% elseif awesome.sauce[1] and blue and \'hello\' %}\nfoo{% endif %}")

        # Test an if with an elseif and else clause.
        ast = smartytotwig.parse_string("{if foo|bar:3 or foo[3]}\nbar\n{elseif awesome.sauce[1] and blue and 'hello'}\nfoo\n{else}bar{/if}")
        tree_walker = TreeWalker(ast)
        self.assertEqual(tree_walker.code, "{% if foo|bar(3) or foo[3] %}\nbar\n{% elseif awesome.sauce[1] and blue and 'hello' %}\nfoo\n{% else %}bar{% endif %}")
        
    def test_for_statement(self):
        """
        """

if __name__ == '__main__':
    unittest.main()