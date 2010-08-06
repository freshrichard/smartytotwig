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
from smartytotwig.pyPEG import parse
from smartytotwig.pyPEG import keyword, _and, _not, ignore

"""
Misc.
"""
def content():              return re.compile(r'[^{]+')

def comment():              return re.compile("{\*.*?\*}", re.S)

def literal():              return '{', keyword('literal'), '}', re.compile(".*{/literal}", re.S)

def junk():                 return -1, [' ', '\n', '\t']

"""
Logical operators.
"""
def and_operator():         return [keyword('and'), '&&']

def or_operator():          return [keyword('or'), '||']

def equals_operator():      return ['==', keyword('eq')]

def ne_operator():          return ['!=', keyword('ne'), keyword('neq')]

def gt_operator():          return ['>', 'gt']

def lt_operator():          return ['<', 'gt']

def lte_operator():         return ['<=']

def gte_operator():         return ['>=']

def operator():             return 0, ' ', [and_operator, equals_operator, gte_operator, lte_operator, lt_operator, gt_operator, ne_operator, or_operator]

"""
Smarty variables.
"""
def string():               return 0, ' ', [(re.compile(r'"'), -1, [re.compile(r'[^$`"\\]'), re.compile(r'\\.')], re.compile(r'"')), (re.compile(r'\''), -1, [re.compile(r'[^\'\\]'), re.compile(r'\\.')], re.compile(r'\''))]

def text():                 return -2, [re.compile(r'[^$`"\\]'), re.compile(r'\\.')]

def variable_string():      return '"', -2, [text, ('`', expression, '`'), ('$', expression)], '"'

def dollar():               return '$'

def not_operator():         return '!'

def symbol():               return -1, [' ', '\n', '\t'], 0, not_operator, 0, dollar, re.compile(r'[\w\-\+]+')

def array():                return symbol, "[", 0, expression, "]"

def modifier():             return [object_dereference, array, symbol, variable_string, string], -2, modifier_right, 0, ' '

def expression():           return [modifier, object_dereference, array, symbol, string, variable_string]

def object_dereference():   return [array, symbol], '.', expression

def exp_no_modifier():      return [object_dereference, array, symbol, variable_string, string]

def modifier_right():       return ('|', symbol, -1, (':', exp_no_modifier),)

"""
Smarty statements.
"""
def else_statement():       return '{', keyword('else'), '}', -1, smarty_language

def foreachelse_statement():return '{', keyword('foreachelse'), '}', -1, smarty_language

def print_statement():      return '{', 0, 'e ', expression, '}'

def function_parameter():   return symbol, '=', expression, junk

def function_statement():   return '{', symbol, -2, function_parameter, '}'

def for_from():             return junk, keyword('from'), '=', 0, ['"', '\''], expression, 0, ['"', '\''], junk

def for_item():             return junk, keyword('item'), '=', 0, ['"', '\''], symbol, 0, ['"', '\''], junk

def for_name():             return junk, keyword('name'), '=', 0, ['"', '\''], symbol, 0, ['"', '\''], junk

def for_key():              return junk, keyword('key'), '=', 0, ['"', '\''], symbol, 0, ['"', '\''], junk

def elseif_statement():     return '{', keyword('elseif'), expression, -1, (operator, expression), '}', -1, smarty_language

def if_statement():         return '{', keyword('if'), expression, -1, (operator, expression), '}', -1, smarty_language, -1, [else_statement, elseif_statement], '{/', keyword('if'), '}'

def for_statement():        return '{', keyword('foreach'), -1, [for_from, for_item, for_name, for_key], '}', -1, smarty_language, 0, foreachelse_statement, '{/', keyword('foreach'), '}'

"""
Finally, the actual language description.
"""
def smarty_language():      return -2, [if_statement, for_statement, function_statement, comment, literal, print_statement, content]