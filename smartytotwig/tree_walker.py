"""
The MIT License

Copyright (c) 2010 FreshBooks

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
class TreeWalker(object):
    """
    Takes an AST of a parsed smarty program
    and returns the parsed Twig template. This
    is meant as a helper it does not understand 100%
    of the Smarty synatx.
    """
    def __init__(self, ast):
        """
        The AST structure is created by pyPEG.
        """
                
        # Top level handler for walking the tree.
        self.code = self.smarty_language(ast, '', 0)
        print self.code
        
    def smarty_language(self, ast, code, tab_depth):
        """
        The entry-point for the parser.
        contains a set of top-level smarty
        statements.
        """
        
        code = self.__walk_tree (
            {
                'if_statement': self.if_statement,
                'content': self.content,
                'print_statement': self.print_statement,
                'for_statement': self.for_statement,
                'function_statement': self.function_statement,
                'comment': self.function_statement,
                'literal': self.literal
            },
            ast,
            code,
            tab_depth
        )
            
        return code
        
    def literal(self, ast, code, tab_depth):
        """
        A literal block in smarty, we can just
        drop the {literal} tags because Twig
        is less ambiguous.
        """
        literal_string = ast[0]
        literal_string = literal_string.replace('{/literal}', '')
        
        code = "%s%s\n" % (
            code,
            literal_string
        )
        
        return code
        
    def variable_string(self, ast, code, tab_depth):
        """
        A complex string containing variables, e.x.,
        
            "`$foo.bar` Hello World $bar"
        
        """
        
        code = "%s\"" % code
        
        # Crawl through the ast snippet and create a
        # string in the format "%s%s%s"
        # and a set of the parameters that will be
        # outputted with this string.
        variables = []
        string_contents = ''
        for k, v in ast:
            
            # Plain-text.
            if k == 'text':
                string_contents = "%s%s" % (
                    string_contents,
                    v
                )
            else: # An exprssion.
                string_contents = "%s%s " % (
                    string_contents,
                    '%s'
                )
                
                expression = self.__walk_tree (
                    {
                        'expression': self.expression,
                    },
                    [('expression', v)],
                    "",
                    tab_depth
                )
                variables.append(expression)
                
        # Now insert all the parameters
        function_params_string = ''
        i = 0
        size = len(variables)
        for v in variables:
            function_params_string = "%s%s" % (
                function_params_string,
                v
            )
            
            i += 1
            if not i == size:
                function_params_string = "%s, " % function_params_string
    
        # The final string outputted is in the format:
        #   
        #   "%s text %s"|format(foo, bar)
        #
        # format is a Twig modifier similar to sprintf.
        code = "%s%s\"|format(%s)" % (
            code,
            string_contents,
            function_params_string
        )
        
        return code
    
    def function_statement(self, ast, code, tab_depth):
        """
        Smarty functions are mapped to a 
        """
        
        # The variable that starts a function statement.
        function_name = self.__walk_tree (
            {
                'symbol': self.symbol
            },
            ast,
            "",
            tab_depth
        )
        
        # Cycle through the function_parameters and store them
        # these will be passed into the modifier as a dictionary.
        function_params = {}
        for k, v in ast[1:]:
            symbol = self.__walk_tree (
                {
                    'symbol': self.symbol
                },
                v,
                "",
                0
            )
            
            expression = self.__walk_tree (
                {
                    'expression': self.expression
                },
                v,
                "",
                0
            )
            
            function_params[symbol] = expression
            
        # Now create a dictionary string from the paramters.
        function_params_string = '['
        i = 0
        size = len(function_params.items())
        for k, v in function_params.items():
            function_params_string = "%s'%s': %s" % (
                function_params_string,
                k,
                v
            )
            
            i += 1
            if not i == size:
                function_params_string = "%s, " % function_params_string
                
        function_params_string = "%s]" % function_params_string
        
        code = "%s{{%s|%s}}\n" % (
            code,
            function_params_string,
            function_name
        )
        return code
        
    def print_statement(self, ast, code, tab_depth):
        """
        """
        code = "%s%s{{" % (
            code,
            self.__print_tabs(tab_depth)
        )
                
        # Walking the expression that starts a
        # modifier statement.
        code = self.__walk_tree (
            {
                'expression': self.expression,
            },
            ast,
            code,
            tab_depth
        )
        
        code = "%s}}" % code
        return code
        
    def modifier(self, ast, code, tab_depth):
        """
        """
                
        # Walking the expression that starts a
        # modifier statement.
        code = self.__walk_tree (
            {
                'symbol': self.symbol,
                'string': self.string,
                'variable_string': self.variable_string,
                'modifier_right': self.modifier_right
            },
            ast,
            code,
            tab_depth
        )
        
        return code        
        
    def modifier_right(self, ast, code, tab_depth):
        """
        """
        code = "%s|" % code
                
        code = self.__walk_tree (
            {
                'symbol': self.symbol,
                'string': self.string,
                'variable_string': self.variable_string
            },
            ast,
            code,
            tab_depth
        )
        
        # We must have parameters being passed
        # in to the modifier.
        if len(ast) > 1:
            code = "%s(" % code
            i = 0
            for k, v in ast[1:]:
                code = self.expression(v, code, tab_depth)
                
                # Put commas in if needed.
                i += 1
                if not i == len(ast) - 1:
                    code = "%s, " % code
                    
            code = "%s)" % code
        
        return code
        
    def content(self, ast, code, tab_depth):
        """
        """
        code = "%s%s" % (
            code,
            ast
        )
        
        return code
        
    def for_statement(self, ast, code, tab_depth):
        """

        """ 

        code = "%s%s{%s for " % (
            code,
            self.__print_tabs(tab_depth),
            '%'
        )
        
        for_parts = {}
        for k, v in ast:
            for_parts[k] = v
        
        # What variable is the for data being stored as.
        if for_parts.has_key('for_item'):
            code = self.__walk_tree (
                {
                    'symbol': self.symbol,
                },
                for_parts['for_item'],
                code,
                tab_depth
            )
            code = "%s " % code
        
        # What is the for statement reading from?
        if for_parts.has_key('for_from'):
            code = "%sin " % code
            code = self.__walk_tree (
                {
                    'expression': self.expression,
                },
                for_parts['for_from'],
                code,
                tab_depth
            )
        
        code = "%s %s}\n" % (
            code,
            '%'
        )

        # The content inside the if statement.
        code = self.__walk_tree (
            {
                'smarty_language': self.smarty_language,
            },
            ast,
            code,
            tab_depth + 1
        )

        # Else and elseif statements.
        code = self.__walk_tree (
            {
                'foreachelse_statement': self.else_statement,
            },
            ast,
            code,
            tab_depth
        )

        code = '%s%s{%s endfor %s}\n' % (
            code,
            self.__print_tabs(tab_depth),
            '%',
            '%'
        )

        return code

                
    def if_statement(self, ast, code, tab_depth):
        """
        
        """ 
                   
        code = "%s%s{%s if " % (
            code,
            self.__print_tabs(tab_depth),
            '%'
        )

        # Walking the expressions in an if statement.
        code = self.__walk_tree (
            {
                'expression': self.expression,
                'operator': self.operator
            },
            ast,
            code,
            tab_depth
        )
        
        code = "%s %s}\n" % (
            code,
            '%'
        )
         
        # The content inside the if statement.
        code = self.__walk_tree (
            {
                'smarty_language': self.smarty_language,
            },
            ast,
            code,
            tab_depth + 1
        )
        
        # Else and elseif statements.
        code = self.__walk_tree (
            {
                'elseif_statement': self.elseif_statement,
                'else_statement': self.else_statement
            },
            ast,
            code,
            tab_depth
        )
        
        code = '%s%s{%s endif %s}\n' % (
            code,
            self.__print_tabs(tab_depth),
            '%',
            '%'
        )
                        
        return code
        
    def elseif_statement(self, ast, code, tab_depth):
        """

        """        
        code = "%s%s{%s elseif " % (
            code,
            self.__print_tabs(tab_depth),
            '%'
        )

        # Walking the expressions in an if statement.
        code = self.__walk_tree (
            {
                'expression': self.expression,
                'operator': self.operator
            },
            ast,
            code,
            tab_depth
        )

        code = "%s %s}\n" % (
            code,
            '%'
        )

        # The content inside the if statement.
        code = self.__walk_tree (
            {
                'smarty_language': self.smarty_language,
            },
            ast,
            code,
            tab_depth + 1
        )
        
        return code
        
    def else_statement(self, ast, code, tab_depth):
        """
        """
             
        code = "%s%s{%s else %s}\n" % (
            code,
            self.__print_tabs(tab_depth),
            '%',
            '%'
        )
        
        # The content inside the if statement.
        code = self.__walk_tree (
            {
                'smarty_language': self.smarty_language,
            },
            ast,
            code,
            tab_depth + 1
        )
                        
        return code
        
    def operator(self, ast, code, tab_depth):
        """
        """
        
        # Evaluate the different types of expressions.
        code = self.__walk_tree (
            {
                'and_operator': self.and_operator,
                'equals_operator': self.equals_operator,
                'gte_operator': self.gte_operator,
                'lte_operator': self.lte_operator,
                'lt_operator': self.lt_operator,
                'gt_operator': self.gt_operator,
                'ne_operator': self.ne_operator,
                'or_operator': self.or_operator
            },
            ast,
            code,
            tab_depth
        )
            
        return code
            
    def gte_operator(self, ast, code, tab_depth):
        """
        """
        code = '%s >= ' % (
            code
        )
        
        return code
        
    def lte_operator(self, ast, code, tab_depth):
        """
        """
        code = '%s <= ' % (
            code
        )

        return code
        
    def lt_operator(self, ast, code, tab_depth):
        """
        """
        code = '%s < ' % (
            code
        )

        return code
        
    def gt_operator(self, ast, code, tab_depth):
        """
        """
        code = '%s > ' % (
            code
        )

        return code
        
    def ne_operator(self, ast, code, tab_depth):
        """
        """
        code = '%s != ' % (
            code
        )

        return code
    
    def and_operator(self, ast, code, tab_depth):
        """
        """
        code = '%s and ' % (
            code
        )
        
        return code
        
    def or_operator(self, ast, code, tab_depth):
        """
        """
        code = '%s or ' % (
            code
        )

        return code
        
    def equals_operator(self, ast, code, tab_depth):
        """
        """
        code = '%s == ' % (
            code
        )

        return code
    
    def expression(self, ast, code, tab_depth):
        """
        """
        # Evaluate the different types of expressions.
        code = self.__walk_tree (
            {
                'symbol': self.symbol,
                'string': self.string,
                'variable_string': self.variable_string,
                'object_dereference': self.object_dereference,
                'array': self.array,
                'modifier': self.modifier
            },
            ast,
            code,
            tab_depth
        )
            
        return code
        
    def object_dereference(self, ast, code, tab_depth):
        """
        """
        handlers = {
            'expression': self.expression,
            'symbol': self.symbol,
            'string': self.string,
            'variable_string': self.variable_string,
            'array': self.array
        }
        
        code = handlers[ast[0][0]](ast[0][1], code, tab_depth)
        
        code = "%s.%s" % (
            code, 
            handlers[ast[1][0]](ast[1][1], "", tab_depth)
        )
        
        return code
        
    def array(self, ast, code, tab_depth):
        """
        """
        handlers = {
            'expression': self.expression,
            'array': self.array,
            'symbol': self.symbol,
            'string': self.string,
            'variable_string': self.variable_string
        }

        code = handlers[ast[0][0]](ast[0][1], code, tab_depth)

        if (len(ast) > 1):
            code = "%s[%s]" % (
                code, 
                handlers[ast[1][0]](ast[1][1], "", tab_depth)
            )
        else:
            code = "%s[]" % code

        return code
    
    def string(self, ast, code, tab_depth):
        """
        """
        return "%s%s" % (code, ast[0])
        
    def symbol(self, ast, code, tab_depth):
        """
        
        """
        
        # Assume no $ on the symbol.
        variable = ast[0]
        
        # Is there a ! operator.
        if len(ast[0]) > 0:
            if ast[0][0] == 'not_operator':
                code = "%snot " % (
                    code
                )
        
        # Maybe there was a $ on the symbol?.
        if len(ast) > 1:
            variable = ast[len(ast) - 1]
            
        code = "%s%s" % (code, variable)    
        
        return code
        
    def __walk_tree(self, handlers, ast, code, tab_depth):
        """
        """
        for k, v in ast:
            if handlers.has_key(k):
                if k == 'comment':
                    code = "%s%s\n" % (
                        code,
                        v
                    )
                else:
                    code = handlers[k](v, code, tab_depth)
                
        return code
        
    def __print_tabs(self, tab_depth):
        """
        """
        tabs = ''
        for i in range(0, tab_depth):
            tabs = "%s\t" % tabs
        return tabs