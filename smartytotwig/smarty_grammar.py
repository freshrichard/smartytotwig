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

# pyPEG:
#
#   basestring:     terminal symbol (characters)
#   keyword:        terminal symbol (keyword)
#   matchobj:       terminal symbols (regex, use for scanning symbols)
#   function:       named non-terminal symbol, recursive definition
#                   if you don't want naming in output, precede name with an underscore
#   tuple:          production sequence
#   integer:        count in production sequence:
#                    0: following element is optional
#                   -1: following element can be omitted or repeated endless
#                   -2: following element is required and can be repeated endless
#   list:           options, choose one of them
#   _not:           next element in production sequence is matched only if this would not
#   _and:           next element in production sequence is matched only if this would, too

# comment <- r"//.*" | r"/\*.**?\*/";

"""
Misc.
"""
def comment():              return [re.compile(r'//.*'), re.compile('/\*.*?\*/', re.S)]

def content():              return re.compile(r'[^{]+')

"""
Logical operators.
"""
def and_operator():         return [keyword('and'), '&&']

def operator():             return [and_operator]

"""
Smarty variables.
"""

def symbol():               return re.compile(r'\$\w+')

def array():                return symbol(), array_dereference

def array_dereference():    return "[", 0, expression, "]"

def expression():           return [array, symbol]

"""
Smarty statements.
"""
def if_statement():         return '{', keyword('if'), expression, -1, (operator, expression), '}', '{/', keyword('if'), '}'

"""
Finally, the actual language description.
"""
def smarty_language():      return -2, [if_statement, content]