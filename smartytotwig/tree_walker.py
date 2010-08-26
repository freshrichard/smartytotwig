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

import re

class TreeWalker(object):
    """
    Takes an AST of a parsed smarty program
    and returns the parsed Twig template. This
    is meant as a helper it does not understand 100%
    of the Smarty synatx.
    """
    
    # Lookup tables for performing some token
    # replacements not addressed in the grammar.
    replacements = {
        'smarty\.foreach.*\.index': 'loop.index0',
        'smarty\.foreach.*\.iteration': 'loop.index'
    }
    
    keywords = {
        'foreachelse': '{% else %}',
        'else': '{% else %}',
    }
    
    def __init__(self, ast, twig_extension="", twig_path=""):
        """
        The AST structure is created by pyPEG.
        """
        self.twig_extension = 'twig'
        self.twig_path = ''
        
        if twig_extension:
           self.twig_extension = twig_extension
           
        if twig_path:
            self.twig_path = twig_path
        
        # Top level handler for walking the tree.
        self.code = self.smarty_language(ast, '')        
                
    def smarty_language(self, ast, code):
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
            code
        )
            
        return code
        
    def literal(self, ast, code):
        """
        A literal block in smarty, we can just
        drop the {literal} tags because Twig
        is less ambiguous.
        """
        literal_string = ast
        literal_string = literal_string.replace('{/literal}', '')
        literal_string = literal_string.replace('{literal}', '')
        
        code = "%s%s" % (
            code,
            literal_string
        )
        
        return code
        
    def variable_string(self, ast, code):
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
                for text in v:
                
                    string_contents = "%s%s" % (
                        string_contents,
                        text
                    )
                
            else: # An exprssion.
                string_contents = "%s%s" % (
                    string_contents,
                    '%s'
                )
                
                expression = self.__walk_tree (
                    {
                        'expression': self.expression,
                    },
                    [('expression', v)],
                    ""
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
        if len(function_params_string):
            code = "%s%s\"|format(%s)" % (
                code,
                string_contents,
                function_params_string
            )
        else: # Deal with parsing error on double-quoted strings.
            code = "%s%s\"" % (
                code,
                string_contents
            )
        
        return code
    
    def function_statement(self, ast, code):
        """
        Smarty functions are mapped to a modifier in
        Twig with a hash as input.
        """        
        # The variable that starts a function statement.
        function_name = self.__walk_tree (
            {
                'symbol': self.symbol
            },
            ast,
            ""
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
                ""
            )
            
            expression = self.__walk_tree (
                {
                    'expression': self.expression
                },
                v,
                ""
            )
            
            function_params[symbol] = expression
        
        # Deal with the special case of an include function in
        # smarty this should be mapped onto Twig's include tag.
        if function_name == 'include' and function_params.has_key('file'):
            tokens = function_params['file'].split('/')
            file_name = tokens[len(tokens) - 1]
            file_name = "%s/%s.%s" % (
                self.twig_path,
                re.sub(r'\..*$', '', file_name),
                self.twig_extension
            )
            code = "%s{%s include \"%s\" %s}" % (
                code,
                '%',
                file_name,
                '%'
            )
            return code
            
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
        
        code = "%s{{%s|%s}}" % (
            code,
            function_params_string,
            function_name
        )
        return code
        
    def print_statement(self, ast, code):
        """
        A print statement in smarty includes:
        
        {foo}
        {foo|bar:parameter}
        """
                        
        # Walking the expression that starts a
        # modifier statement.
        expression = self.__walk_tree (
            {
                'expression': self.expression,
            },
            ast,
            ""
        )
        
        # Perform any keyword replacements if found.        
        if self.keywords.has_key(expression):
            return "%s%s" % (
                code,
                self.keywords[expression]
            )
        
        code = "%s{{%s}}" % (
            code,
            expression
        )
                
        return code
        
    def modifier(self, ast, code):
        """
        A modifier statement:
        
        foo|bar:a:b:c
        """
                
        # Walking the expression that starts a
        # modifier statement.
        code = self.__walk_tree (
            {
                'symbol': self.symbol,
                'array': self.array,
                'string': self.string,
                'variable_string': self.variable_string,
                'modifier_right': self.modifier_right
            },
            ast,
            code
        )
        
        return code        
        
    def modifier_right(self, ast, code):
        """
        The right-hand side of the modifier
        statement:
        
        bar:a:b:c
        """
        code = "%s|" % code
                
        code = self.__walk_tree (
            {
                'symbol': self.symbol,
                'string': self.string,
                'variable_string': self.variable_string
            },
            ast,
            code
        )
        
        # We must have parameters being passed
        # in to the modifier.
        if len(ast) > 1:
            code = "%s(" % code
            i = 0
            for k, v in ast[1:]:
                code = self.expression(v, code)
                
                # Put commas in if needed.
                i += 1
                if not i == len(ast) - 1:
                    code = "%s, " % code
                    
            code = "%s)" % code
        
        return code
        
    def content(self, ast, code):
        """
        Raw content, e.g.,
        
        <html>
            <body>
                <b>Hey</b>
            </body>
        </html>
        """
        code = "%s%s" % (
            code,
            ast
        )
        
        return code
        
    def for_statement(self, ast, code):
        """
        A foreach statement in smarty:
        
        {foreach from=expression item=foo}
        {foreachelse}
        {/foreach}
        """ 

        code = "%s{%s for " % (
            code,
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
                code
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
                code
            )
        
        code = "%s %s}" % (
            code,
            '%'
        )

        # The content inside the if statement.
        code = self.__walk_tree (
            {
                'smarty_language': self.smarty_language,
            },
            ast,
            code
        )

        # Else and elseif statements.
        code = self.__walk_tree (
            {
                'foreachelse_statement': self.else_statement,
            },
            ast,
            code
        )

        code = '%s{%s endfor %s}' % (
            code,
            '%',
            '%'
        )

        return code

                
    def if_statement(self, ast, code):
        """
        An if statement in smarty:
        
        {if expression (operator expression)}
        {elseif expression (operator expression)}
        {else}
        {/if}
        """ 
                   
        code = "%s{%s if " % (
            code,
            '%'
        )

        # Walking the expressions in an if statement.
        code = self.__walk_tree (
            {
                'expression': self.expression,
                'operator': self.operator,
                'right_paren': None,
                'left_paren': None
            },
            ast,
            code
        )
        
        code = "%s %s}" % (
            code,
            '%'
        )
         
        # The content inside the if statement.
        code = self.__walk_tree (
            {
                'smarty_language': self.smarty_language,
            },
            ast,
            code
        )
        
        # Else and elseif statements.
        code = self.__walk_tree (
            {
                'elseif_statement': self.elseif_statement,
                'else_statement': self.else_statement
            },
            ast,
            code
        )
        
        code = '%s{%s endif %s}' % (
            code,
            '%',
            '%'
        )
                        
        return code
        
    def elseif_statement(self, ast, code):
        """
        The elseif part of an if statement, essentially
        this is the same as an if statement but without
        the elseif or else part.
        
        {elseif expression (operator expression)}
        """        
        code = "%s{%s elseif " % (
            code,
            '%'
        )

        # Walking the expressions in an if statement.
        code = self.__walk_tree (
            {
                'expression': self.expression,
                'operator': self.operator,
                'right_paren': None,
                'left_paren': None
            },
            ast,
            code
        )

        code = "%s %s}" % (
            code,
            '%'
        )

        # The content inside the if statement.
        code = self.__walk_tree (
            {
                'smarty_language': self.smarty_language,
            },
            ast,
            code
        )
        
        return code
        
    def else_statement(self, ast, code):
        """
        The else part of an if statement.
        """
             
        code = "%s{%s else %s}" % (
            code,
            '%',
            '%'
        )
        
        # The content inside the if statement.
        code = self.__walk_tree (
            {
                'smarty_language': self.smarty_language,
            },
            ast,
            code
        )
        return code
        
    def operator(self, ast, code):
        """
        Operators in smarty.
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
            code
        )
            
        return code
            
    def gte_operator(self, ast, code):
        """
        >= operator in Smarty.
        """
        code = '%s >= ' % (
            code
        )
        
        return code
        
    def lte_operator(self, ast, code):
        """
        <= operator in smarty.
        """
        code = '%s <= ' % (
            code
        )

        return code
        
    def lt_operator(self, ast, code):
        """
        < operator in smarty.
        """
        code = '%s < ' % (
            code
        )

        return code
        
    def gt_operator(self, ast, code):
        """
        > operator in smarty.
        """
        code = '%s > ' % (
            code
        )

        return code
        
    def ne_operator(self, ast, code):
        """
        ne, neq, != opeartor in Smarty.
        """
        code = '%s != ' % (
            code
        )

        return code
    
    def and_operator(self, ast, code):
        """
        &&, and operator in Smarty.
        """
        code = '%s and ' % (
            code
        )
        
        return code
        
    def or_operator(self, ast, code):
        """
        ||, or, operator in Smarty.
        """
        code = '%s or ' % (
            code
        )

        return code
        
    def equals_operator(self, ast, code):
        """
        eq, == opeartor in Smarty.
        """
        code = '%s == ' % (
            code
        )

        return code
    
    def expression(self, ast, code):
        """
        A top level expression in Smarty that statements
        are built out of mostly expressions and/or symbols (which are
        encompassed in the expression type.
        """
        # Evaluate the different types of expressions.
        expression = self.__walk_tree (
            {
                'symbol': self.symbol,
                'string': self.string,
                'variable_string': self.variable_string,
                'object_dereference': self.object_dereference,
                'array': self.array,
                'modifier': self.modifier
            },
            ast,
            ""
        )
        
        # Should we perform any replacements?
        for k, v in self.replacements.items():
            if re.match(k, expression):
                expression = v
                break
                    
        code = "%s%s" % (
            code,
            expression
        )
        
        return code
        
    def object_dereference(self, ast, code):
        """
        An object dereference expression in Smarty:
        
        foo.bar
        """
        handlers = {
            'expression': self.expression,
            'symbol': self.symbol,
            'string': self.string,
            'variable_string': self.variable_string,
            'array': self.array
        }
        
        code = handlers[ast[0][0]](ast[0][1], code)
        
        code = "%s.%s" % (
            code, 
            handlers[ast[1][0]](ast[1][1], "")
        )
        
        return code
        
    def array(self, ast, code):
        """
        An array expression in Smarty:
        
        foo[bar]
        """
        handlers = {
            'expression': self.expression,
            'array': self.array,
            'symbol': self.symbol,
            'string': self.string,
            'variable_string': self.variable_string
        }

        code = handlers[ast[0][0]](ast[0][1], code)

        if (len(ast) > 1):
            code = "%s[%s]" % (
                code, 
                handlers[ast[1][0]](ast[1][1], "")
            )
        else:
            code = "%s[]" % code

        return code
    
    def string(self, ast, code):
        """
        A string in Smarty.
        """
        return "%s%s" % (code, ''.join(ast))
        
    def symbol(self, ast, code):
        """
        A symbol (variable) in Smarty, e.g,
        
        !foobar
        foo_bar
        foo3
        """
        
        # Assume no $ on the symbol.
        variable = ast[0]
        
        # Is there a ! operator.
        if len(ast[0]) > 0:
            if ast[0][0] == 'not_operator':
                code = "%snot " % (
                    code
                )
            elif ast[0][0] == 'at_operator':
              pass # Nom nom, at operators are not supported in Twig
        
        # Maybe there was a $ on the symbol?.
        if len(ast) > 1:
            variable = ast[len(ast) - 1]
            
        code = "%s%s" % (code, variable)    
        
        return code
        
    def __walk_tree(self, handlers, ast, code):
        """
        Tree walking helper function.
        """
        for k, v in ast:
            if handlers.has_key(k):
                if k == 'right_paren':
                    code = "%s)" % (
                        code
                    )
                elif k == 'left_paren':
                    code = "%s(" % (
                        code
                    )
                elif k == 'comment':
                    
                    # Comments in Twig have {# not {*
                    code = "%s{#%s#}" % (
                        code,
                        v[2:len(v) - 2]
                    )
                else:
                    code = handlers[k](v, code)
                
        return code