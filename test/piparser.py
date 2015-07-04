
if __name__ == "__main__":
    import sys
    sys.path.append("../src")

from popparser import (Grammar, tokens, parsers, expr, ParseResult)
from popparser.llparser import LLParsing
from popparser.tokenizer import Tokenizer

import pisyntax

'''{

The pi-calculus grammar is given below :

<process> ::= <term>
              | <restriction>
              | <gc>
              | <call>
              | <choice-process>
              | <process> <parallel> <process>
              | '(' <process> ')'

<choice-process> ::= <prefixed-process>
                     | <prefixed-process> <choice> <choice-process>

<prefixed-process> ::=  <guard>? <action> <process>

<guard> ::= '[' <conditions> ']'

<conditions> ::= <cond>
                 | <cond>  <et-cond> <conditions>

<cond> ::= <name> <eq> <name>
          | <name> <neq> <name>
          | 'true'


<action> ::= <tau> | <output> | <input>

<output> ::= <name> ! <name>

<input> ::= <name> ? (<name>)


<restriction> ::= <new> ( <name> ) <process>

<call> ::= <name> ( <args> )

<args> ::= <name>
           | <name> ',' <args>

}'''

class PiParser:
    def __init__(self):
        pass

    @staticmethod
    def pi_tokenizer():
        tokenizer = Tokenizer()

        # punctuation
        tokenizer.add_rule(tokens.CharSet('space', ' ', '\t', '\r'))
        tokenizer.add_rule(tokens.Char('lparen', '('))
        tokenizer.add_rule(tokens.Char('rparen', ')'))
        tokenizer.add_rule(tokens.Char('lbracket', '['))
        tokenizer.add_rule(tokens.Char('rbracket', ']'))
        tokenizer.add_rule(tokens.Char('bang', '!'))
        tokenizer.add_rule(tokens.Char('what', '?'))

        # identifiers
        tokenizer.add_rule(tokens.Regexp('name',
                                         r'[a-zA-Z_][a-zA-Z0-9_]*'))

        # process elements
        tokenizer.add_rule(tokens.LiteralSet('term', '0', 'nil', 'end'))
        tokenizer.add_rule(tokens.LiteralSet('new', 'new', 'res'))
        tokenizer.add_rule(tokens.Literal('gc', '<gc>'))
        tokenizer.add_rule(tokens.LiteralSet('tau', 'tau', 'skip'))

        tokenizer.add_rule(tokens.Regexp('output',
                                         r'([a-zA-Z_][a-zA-Z0-9_]*)!([a-zA-Z_][a-zA-Z0-9_]*)'))
        tokenizer.add_rule(tokens.Regexp('input',
                                         r'([a-zA-Z_][a-zA-Z0-9_]*)?\(([a-zA-Z_][a-zA-Z0-9_]*)\)'))

        return tokenizer

    @staticmethod
    def pi_grammar():
        grammar = Grammar()

        # spaces
        spaces_parser = parsers.Repeat(parsers.Token('space'), minimum=0)
        grammar.register('spaces', spaces_parser)
        
        # end of process
        grammar.register('term', parsers.Token('term'))

        # restricted process
        restrict_parser = parsers.Tuple().skip(parsers.Token('new'))\
                                         .skip(parsers.Token('lparen'))\
                                         .element(parsers.Token('name'))\
                                         .skip(parsers.Token('rparen'))\
                                         .skip(grammar.ref('spaces'))\
                                         .element(grammar.ref('expr'))

        def restrict_xform_content(result):
            ncontent = pisyntax.Restriction(result.content[0].content.value,
                                            result.content[1].content)
            return ncontent
        
        restrict_parser.xform_content = restrict_xform_content

        # GC process
        gc_parser = parsers.Tuple().skip(parsers.Token('gc'))\
                                   .skip(grammar.ref('spaces'))\
                                   .element(grammar.ref('expr'))

        def gc_xform_content(result):
            ncontent = pisyntax.GC(result.content.content)
            return ncontent

        gc_parser.xform_content = gc_xform_content
        
        # process expression parser
        expr_parser = expr.ExprParser()\
                          .skip_token('space')\
                          .register('term', PiParser.TermAtom())\
                          .register('new', expr.parsers.Embed(restrict_parser))\
                          .register('gc', expr.parsers.Embed(gc_parser))

        grammar.register('expr', expr_parser)

        grammar.entry = parsers.Tuple().element(grammar.ref('expr'))\
                                       .skip(grammar.ref('spaces'))\
                                       .skip(parsers.EOF())
        
        return grammar

    class TermAtom(expr.Atom):
        def on_atom(self, token):
            return ParseResult(pisyntax.Term(), token.start_pos, token.end_pos)

    @staticmethod
    def parse_from_string(string):
        tokenizer = PiParser.pi_tokenizer()
        parser = LLParsing(PiParser.pi_grammar())
        parser.tokenizer = tokenizer
        tokenizer.from_string(string)
        return parser.parse()


if __name__ == "__main__":
    parse_str = "  end  "
    print("Parsing: '{}'".format(parse_str))
    result = PiParser.parse_from_string(parse_str)
    print("Gives: {}".format(repr(result.content.content)))

    print("----")
    
    parse_str = "  new(a) end  "
    print("Parsing: '{}'".format(parse_str))
    #import pdb ; pdb.set_trace()
    result = PiParser.parse_from_string(parse_str)
    print("Gives: {}".format(repr(result.content.content)))

    print("----")

    parse_str = "  new(a) new(bla_bAla9) end  "
    print("Parsing: '{}'".format(parse_str))
    #import pdb ; pdb.set_trace()
    result = PiParser.parse_from_string(parse_str)
    print("Gives: {}".format(repr(result.content.content)))

    print("----")

    parse_str = "  new(a) <gc> end  "
    print("Parsing: '{}'".format(parse_str))
    #import pdb ; pdb.set_trace()
    result = PiParser.parse_from_string(parse_str)
    print("Gives: {}".format(repr(result.content.content)))

    print("----")

    parse_str = "  new(a) <gc> new(b) <gc> new(c) end  "
    print("Parsing: '{}'".format(parse_str))
    #import pdb ; pdb.set_trace()
    result = PiParser.parse_from_string(parse_str)
    print("Gives: {}".format(repr(result.content.content)))
