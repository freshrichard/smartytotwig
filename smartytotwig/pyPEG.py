# YPL parser 0.34

# written by VB.

import re

class keyword(str): pass
class code(str): pass
class ignore(object):
    def __init__(self, regex_text):
        self.regex = re.compile(regex_text)

class _and(object):
    def __init__(self, something):
        self.obj = something

class _not(_and): pass

word_regex = re.compile(r"\w+")
rest_regex = re.compile(r".*")
ignoring = ignore("")

def skip(skipper, text, pattern, skipWS, skipComments):
    if skipWS:
        t = text.strip()
    else:
        t = text
    if skipComments:
        try:
            while True:
                skip, t = skipper.parseLine(t, skipComments, [], skipWS, None, 0)
                if skipWS:
                    t = t.strip()
        except: pass
    return t

class parser(object):
    def __init__(self, another = False):
        self.restlen = -1 
        if not(another):
            self.skipper = parser(True)
        else:
            self.skipper = self

    # parseLine():
    #   textline:       text to parse
    #   pattern:        pyPEG language description
    #   resultSoFar:    parsing result so far (default: blank list [])
    #   skipWS:         Flag if whitespace should be skipped (default: True)
    #   skipComments:   Python functions returning pyPEG for matching comments
    #   inputLength:    len of text to parse, how it was originally
    #   
    #   returns:        pyAST, textrest
    #
    #   raises:         SyntaxError(reason) if textline is detected not being in language
    #                   described by pattern
    #
    #                   SyntaxError(reason) if pattern is an illegal language description

    def parseLine(self, textline, pattern, resultSoFar = [], skipWS = True,
            skipComments = None, inputLength = 0):
        name = None
        position = 0

        def R(result, text):
            if self.restlen == -1:
                self.restlen = len(text)
            else:
                self.restlen = min(self.restlen, len(text))
            # if skipComments:
            #     if name:
            #         if name[:7]=="comment":
            #             return resultSoFar, text
            res = resultSoFar
            if name and result:
                if inputLength: res.append(position)
                res.append((name, result))
            elif name:
                if inputLength: res.append(position)
                res.append((name, []))
            elif result:
                if type(result) is type([]):
                    res.extend(result)
                else:
                    if inputLength: res.append(position)
                    res.extend([result])
            return res, text

        if type(pattern) is type(lambda x: 0):
            if pattern.__name__[0] != "_":
                name = pattern.__name__
            pattern = pattern()
            if type(pattern) is type(lambda x: 0):
                pattern = (pattern,)

        text = skip(self.skipper, textline, pattern, skipWS, skipComments)

        if inputLength:
            position = inputLength - len(text) - 1

        pattern_type = type(pattern)

        if pattern_type is type(""):
            if text[:len(pattern)] == pattern:
                text = skip(self.skipper, text[len(pattern):], pattern, skipWS, skipComments)
                return R(None, text)
            else:
                raise SyntaxError()

        elif pattern_type is type(keyword("")):
            m = word_regex.match(text)
            if m:
                if m.group(0) == pattern:
                    text = skip(self.skipper, text[len(pattern):], pattern, skipWS, skipComments)
                    return R(None, text)
                else:
                    raise SyntaxError()
            else:
                raise SyntaxError()

        elif pattern_type is type(_not("")):
            try:
                r, t = self.parseLine(text, pattern.obj, [], skipWS, skipComments, inputLength)
            except:
                return resultSoFar, textline
            raise SyntaxError()

        elif pattern_type is type(_and("")):
            r, t = self.parseLine(text, pattern.obj, [], skipWS, skipComments, inputLength)
            return resultSoFar, textline

        elif pattern_type is type(word_regex) or pattern_type is type(ignoring):
            if pattern_type is type(ignoring):
                pattern = pattern.regex
            m = pattern.match(text)
            if m:
                text = skip(self.skipper, text[len(m.group(0)):], pattern, skipWS, skipComments)
                if pattern_type is type(ignoring):
                    return R(None, text)
                else:
                    return R(m.group(0), text)
            else:
                raise SyntaxError()

        elif pattern_type is type((None,)):
            result = []
            n = 1
            for p in pattern:
                if type(p) is type(0):
                    n = p
                else:
                    if n>0:
                        for i in range(n):
                            result, text = self.parseLine(text, p, result, skipWS, skipComments, inputLength)
                    elif n==0:
                        if text == "":
                            pass
                        else:
                            try:
                                newResult, newText = self.parseLine(text, p, result, skipWS, skipComments, inputLength)
                                result, text = newResult, newText
                            except SyntaxError:
                                pass
                    elif n<0:
                        found = False
                        while True:
                            try:
                                newResult, newText = self.parseLine(text, p, result, skipWS, skipComments, inputLength)
                                result, text, found = newResult, newText, True
                            except SyntaxError:
                                break
                        if n == -2 and not(found):
                            raise SyntaxError()
                    n = 1
            return R(result, text)

        elif pattern_type is type([]):
            result = []
            found = False
            for p in pattern:
                try:
                    result, text = self.parseLine(text, p, result, skipWS, skipComments, inputLength)
                    found = True
                except SyntaxError:
                    pass
                if found:
                    break
            if found:
                return R(result, text)
            else:
                raise SyntaxError()

        else:
            raise SyntaxError("illegal type in grammar: " + str(pattern_type))

# plain module API

def parseLine(textline, pattern, resultSoFar = [], skipWS = True, skipComments = None, outputPos = False):
    p = parser()
    if outputPos:
        length = len(textline)
    else:
        length = 0
    text = skip(p.skipper, textline, pattern, skipWS, skipComments)
    ast, text = p.parseLine(text, pattern, resultSoFar, skipWS, skipComments, length)
    return ast, text

# parse():
#   language:       pyPEG language description
#   lineSource:     a fileinput.FileInput object
#   skipWS:         Flag if whitespace should be skipped (default: True)
#   skipComments:   Python function which returns pyPEG for matching comments
#   outputPos:      Flag wether to insert position information into pyAST
#   
#   returns:        pyAST
#
#   raises:         SyntaxError(reason), if a parsed line is not in language
#                   SyntaxError(reason), if the language description is illegal

def parse(language, lineSource, skipWS = True, skipComments = None, outputPos = False):
    lines, textlen, lineNo = [], 0, 0

    while type(language) is type(lambda x: 0):
        language = language()

    orig, ld = "", 0
    for line in lineSource:
        if lineSource.isfirstline():
            ld = 1
        else:
            ld += 1
        lines.append((len(orig), ld))
        orig += line
    textlen = len(orig)

    try:
        p = parser()
        if outputPos:
            length = len(orig)
        else:
            length = 0
        text = skip(p.skipper, orig, language, skipWS, skipComments)
        result, text = p.parseLine(text, language, [], skipWS, skipComments, length)
        if text:
            raise SyntaxError()
        textlen = 0
    except SyntaxError, msg:
        parsed = textlen - p.restlen
        textlen = 0
        for n, ld in lines:
            if n >= parsed:
                if n == parsed:
                    lineNo += 1
                break
            else:
                lineNo = ld

        lineCont = orig.splitlines()[lineNo-1]
        raise SyntaxError("syntax error in " + lineSource.filename() + ":" + str(lineNo) + ": " + lineCont)

    return result

