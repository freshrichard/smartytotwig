from smartytotwig.tree_walker import TreeWalker
import unittest, time, smartytotwig

class TestSmartyGrammar(unittest.TestCase):
    """
    It's easy to screw up other rules when modifying the underlying grammar.
    These unit tests test various smarty statements, to make refactoring the grammar more sane.
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
        ast = smartytotwig.parse_string("{if !foo or foo.bar or foo|bar:foo['hello']}\nfoo\n{/if}")
        tree_walker = TreeWalker(ast)
        self.assertEqual(tree_walker.code, "{% if not foo or foo.bar or foo|bar(foo['hello']) %}\nfoo\n{% endif %}")
        
        # Test an an if with an else and a single logical operation.
        ast = smartytotwig.parse_string("{if foo}\nbar\n{else}\nfoo{/if}")
        tree_walker = TreeWalker(ast)
        self.assertEqual(tree_walker.code, "{% if foo %}\nbar\n{% else %}\nfoo{% endif %}")

        # Test an an if with an else and an elseif and two logical operations.
        ast = smartytotwig.parse_string("{if foo and awesome.string|banana:\"foo\\\" $a\"}\nbar\n{elseif awesome.sauce[1] and blue and 'hello'}\nfoo{/if}")
        tree_walker = TreeWalker(ast)
        self.assertEqual(tree_walker.code, "{% if foo and awesome.string|banana(\"foo\\\" %s\"|format(a)) %}\nbar\n{% elseif awesome.sauce[1] and blue and \'hello\' %}\nfoo{% endif %}")

        # Test an if with an elseif and else clause.
        ast = smartytotwig.parse_string("{if foo|bar:3 or !foo[3]}\nbar\n{elseif awesome.sauce[1] and blue and 'hello'}\nfoo\n{else}bar{/if}")
        tree_walker = TreeWalker(ast)
        self.assertEqual(tree_walker.code, "{% if foo|bar(3) or not foo[3] %}\nbar\n{% elseif awesome.sauce[1] and blue and 'hello' %}\nfoo\n{% else %}bar{% endif %}")
        
    def test_function_statement(self):
        """
        Test Smarty's function? statement:
        
        {foo arg=bar}
        """
        # Test a a simple function statement.
        ast = smartytotwig.parse_string("{foo arg1=bar arg2=3}")
        tree_walker = TreeWalker(ast)
        self.assertEqual(tree_walker.code, "{{['arg1': bar, 'arg2': 3]|foo}}")
        
        # Test a a simple function statement with object and array arguments.
        ast = smartytotwig.parse_string("{foo arg1=bar[1] arg2=foo.bar.foo arg3=foo.bar[3] arg4=foo.bar.awesome[3] }")
        tree_walker = TreeWalker(ast)
        self.assertEqual(tree_walker.code, "{{['arg1': bar[1], 'arg2': foo.bar.foo, 'arg3': foo.bar[3], 'arg4': foo.bar.awesome[3]]|foo}}")
        
        # Test a function statement with modifiers in in the parameters.
        ast = smartytotwig.parse_string("{foo arg1=bar[1]|modifier arg2=foo.bar.foo arg3=foo.bar[3]|modifier:array[0]:\"hello $foo \" arg4=foo.bar.awesome[3]|modifier2:7:'hello':\"hello\":\"`$apple.banana`\"}")
        tree_walker = TreeWalker(ast)
        self.assertEqual(tree_walker.code, "{{[\'arg1\': bar[1]|modifier, \'arg2\': foo.bar.foo, \'arg3\': foo.bar[3]|modifier(array[0], \"hello %s \"|format(foo)), \'arg4\': foo.bar.awesome[3]|modifier2(7, \'hello\', \"hello\", \"%s\"|format(apple.banana))]|foo}}")
        
    def test_for_statement(self):
        """
        Test Smarty's for statement:
        
        {foreach foo}
        {foreachelse}
        {/foreach}
        """
        # Test a a simple foreach statement.
        ast = smartytotwig.parse_string("{foreach item=bar from=foo }{/foreach}")
        tree_walker = TreeWalker(ast)
        self.assertEqual(tree_walker.code, "{% for bar in foo %}{% endfor %}")
        
        # Test a more complex foreach statement.
        ast = smartytotwig.parse_string("{foreach item='bar'    name=snuh key=\"foobar\" from=foo[5].bar[2]|hello:\"world\":\" $hey \" }bar{/foreach}")
        tree_walker = TreeWalker(ast)
        self.assertEqual(tree_walker.code, "{% for bar in foo[5].bar[2]|hello(\"world\", \" %s \"|format(hey)) %}bar{% endfor %}")
        
        # Test a for statement with a foreachelse clause.
        ast = smartytotwig.parse_string("{foreach item='bar'    name=snuh key=\"foobar\" from=foo.bar[2]|hello:\"world\":\" $hey \" }bar{foreachelse}{if !foo}bar{/if}hello{/foreach}")
        tree_walker = TreeWalker(ast)
        self.assertEqual(tree_walker.code, "{% for bar in foo.bar[2]|hello(\"world\", \" %s \"|format(hey)) %}bar{% foreachelse %}{% if not foo %}bar{% endif %}hello{% endfor %}")

if __name__ == '__main__':
    unittest.main()