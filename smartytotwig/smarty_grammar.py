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

"""
Logical operators.
"""
def and_operator():         return [keyword('and'), '&&']

def equals_operator():      return [keyword('=='), 'eq']

def operator():             return [and_operator, equals_operator]

"""
Smarty variables.
"""
def string():               return [re.compile(r'"[^"]+"'), re.compile(r'\'[^\']+\'')]

def dollar():               return '$'

def symbol():               return 0, dollar, re.compile(r'\w+')

def array():                return symbol, "[", 0, expression, "]"

def expression():           return [object_dereference, array, symbol, string]

def object_dereference():   return [array, symbol], '.', expression

"""
Smarty statements.
"""
def else_statement():       return '{', keyword('else'), '}', -1, smarty_language

def if_statement():         return '{', keyword('if'), expression, -1, (operator, expression), '}', -1, smarty_language, -1, [else_statement, elseif_statement], '{/', keyword('if'), '}'

def elseif_statement():     return '{', keyword('elseif'), expression, -1, (operator, expression), '}', -1, smarty_language, 0, ('{/', keyword('if'), '}')

def modifier_right():    return ('|', symbol, -1, (':', expression), )

def modifier_statement():   return '{', expression, -2, modifier_right, '}'

"""
Finally, the actual language description.
"""
def smarty_language():      return -2, [modifier_statement, if_statement, content]