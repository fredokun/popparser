'''Simple tests for Popy parser

Created on 24 august 2012

@author: F. Peschanski
'''

if __name__ == "__main__":
    import sys
    sys.path.append("../..")


import unittest


from popy import Tokenizer
from popy.grammar import Grammar
from popy.llparser import LLParsing
import popy.parsers as parse
import popy.tokens as tok


class TestTokens(unittest.TestCase):
    def test_char_token(self):
        tokens = Tokenizer()
        tokens.from_string("ab\nc")
        self.assertTrue(tokens.position.offset == 0)
        tokens.add_rule(tok.Char('char_a', 'a'))
        tokens.add_rule(tok.CharSet('charset_ab', 'a', 'b'))
        tokens.add_rule(tok.CharInterval('char_int_a_c', 'a', 'c'))
        token1 = tokens.next()
        self.assertTrue(token1.token_type == 'char_a')
        self.assertTrue(token1.value == 'a')
        self.assertTrue(tokens.position.offset == 1)

        token2 = tokens.next()
        self.assertTrue(token2.token_type == 'charset_ab')
        self.assertTrue(token2.value == 'b')
        self.assertTrue(tokens.position.offset == 2)

        token_err = tokens.next()
        #print(token_err)
        self.assertTrue(token_err.iserror)
        self.assertTrue(tokens.position.offset == 2)

        tokens.forward()
        self.assertTrue(tokens.position.offset == 3)
        self.assertTrue(tokens.position.line_pos == 2)

        token3 = tokens.next()
        self.assertTrue(token3.token_type == 'char_int_a_c')
        self.assertTrue(token3.value == 'c')
        self.assertTrue(tokens.position.offset == 4)

        eof_tok = tokens.next()
        self.assertTrue(eof_tok.iseof)


class TestSimpleParsers(unittest.TestCase):
    def test_token_parser(self):
        tokens = Tokenizer()
        tokens.add_rule(tok.Literal('hello', 'hello'))
        tokens.add_rule(tok.CharSet('space', ' ', '\t', '\r'))
        tokens.add_rule(tok.Literal('world', 'world'))

        grammar = Grammar()
        init_parser = parse.Tuple().element(parse.Token('hello'))\
                                   .element(parse.Token('space'))\
                                   .element(parse.Token('world'))\
                                   .element(parse.EOF())
        grammar.register('init', init_parser)
        llparser = LLParsing(grammar)
        llparser.tokenizer = tokens
        tokens.from_string("hello world")
        res = llparser.parse()
        self.assertTrue(len(res.content) == 4)
        self.assertTrue(res.content[0].content.value == 'hello')
        self.assertTrue(res.content[1].content.value == ' ')
        self.assertTrue(res.content[2].content.value == 'world')
        self.assertTrue(res.content[3].content.iseof)

if __name__ == '__main__':
    unittest.main()
