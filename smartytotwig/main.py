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
import optparse, sys, smartytotwig
from smartytotwig.tree_walker import TreeWalker

def main():
    
    opt1 = optparse.make_option(
        "-s",
        "--smarty-file",
        action="store",
        dest="source",
        help="Path to the source Smarty file."
    )

    opt2 = optparse.make_option(
        "-t",
        "--twig-file",
        action="store",
        dest="target",
        help="Location of the Twig output file."
    )
    
    opt3 = optparse.make_option(
        "-p",
        "--twig-path",
        action="store",
        dest="path",
        help="The path used in Twig include tags."
    )
    
    opt4 = optparse.make_option(
        "-e",
        "--twig-extension",
        action="store",
        dest="extension",
        help="The extension that should be used when including files in Twig."
    )
    
    parser = optparse.OptionParser(usage='smartytotwig --smarty-file=<SOURCE TEMPLATE> --twig-file=<OUTPUT TEMPLATE>')
    parser.add_option(opt1)
    parser.add_option(opt2)
    parser.add_option(opt3)
    parser.add_option(opt4)
    (options, args) = parser.parse_args(sys.argv)
            
    if options.source and options.target:
                
        ast = smartytotwig.parse_file(options.source)
        tree_walker = TreeWalker(ast, twig_path = options.path, twig_extension = options.extension)
            
        f = open(options.target, 'w+')
        f.write(tree_walker.code)
        f.close()
    
        print 'Template outputted to %s' % options.target
                
if __name__ == "__main__":
    main()