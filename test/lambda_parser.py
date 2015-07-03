'''A simplistic LL(1) parser for lambda-terms

@author: F. Peschanski
'''

if __name__ == "__main__":
    import sys
    sys.path.append("../src")

from popparser import Grammar, parsers, tokens
from popparser.llparser import LLParsing
from popparser.tokenizer import Tokenizer


class Term:
    def __init__(self, start_pos, end_pos):
        self.start_pos = start_pos
        self.end_pos = end_pos


class Var(Term):
    def __init__(self, var_name, var_type, start_pos, end_pos):
        Term.__init__(self, start_pos, end_pos)
        self.var_name = var_name
        self.var_type = var_type

    def __repr__(self):
        return "Var({0}, {1})".format(repr(self.var_name), repr(self.var_type))


class App(Term):
    def __init__(self, rator, rand, start_pos, end_pos):
        Term.__init__(self, start_pos, end_pos)
        self.rator = rator
        self.rand = rand

    def __repr__(self):
        return "App({0}, {1})".format(repr(self.rator), repr(self.rand))


class Lambda(Term):
    def __init__(self, bind_name, bind_type, body, start_pos, end_pos):
        Term.__init__(self, start_pos, end_pos)
        self.bind_name = bind_name
        self.bind_type = bind_type
        self.body = body

    def __repr__(self):
        return "Lambda({0}, {1}, {2})".format(repr(self.bind_name),
                                             repr(self.bind_type),
                                             repr(self.body))


class LambdaParser:
    def __init__(self):
        self.grammar = Grammar()
        self.prepare_grammar(self.grammar)

    def prepare_tokenizer(self, tokenizer):
        # reserved symbols
        tokenizer.add_rule(tokens.Char('dot', '.'))
        tokenizer.add_rule(tokens.Char('column', ':'))
        tokenizer.add_rule(tokens.Char('lparen', '('))
        tokenizer.add_rule(tokens.Char('rparen', ')'))
        tokenizer.add_rule(tokens.CharSet('space', ' ', '\t', '\r', '\n'))

        # lambdas
        tokenizer.add_rule(tokens.CharSet('lambda', 'λ', '\\'))
        tokenizer.add_rule(tokens.Literal('lambda', '\\lambda '))

        # identifiers
        tokenizer.add_rule(tokens.Regexp('identifier',
                                         "[a-zA-Z_][a-zA-Z_0-9]*'*"))

    def prepare_grammar(self, grammar):
        # punctuation
        grammar.register('column', parsers.Token('column'))
        grammar.register('dot', parsers.Token('dot'))
        grammar.register('lparen', parsers.Token('lparen'))
        grammar.register('rparen', parsers.Token('rparen'))

        grammar.register('spaces', parsers.Repeat(parsers.Token('space'),
                                                  minimum=1))

        # constructions
        grammar.register('lambda', parsers.Token('lambda'))
        grammar.register('identifier', parsers.Token('identifier'))

        ref_parser = parsers.Tuple().element(grammar.ref('identifier'))\
                                    .skip(grammar.ref('spaces'))\
                                    .skip(grammar.ref('column'))\
                                    .element(grammar.ref('identifier'))

        def ref_xform(result):
            var_ident = result.content[0]
            var_type = result.content[1]
            return Var(var_ident.content.value, var_type.content.value,
                       result.start_pos, result.end_pos)

        ref_parser.xform_content = ref_xform

        grammar.register('ref', ref_parser)

        app_parser = parsers.Tuple().skip(grammar.ref('lparen'))\
                                    .skip(grammar.ref('spaces'))\
                                    .element(grammar.ref('expr'))\
                                    .skip(grammar.ref('spaces'))\
                                    .element(grammar.ref('expr'))\
                                    .skip(grammar.ref('spaces'))\
                                    .skip(grammar.ref('rparen'))

        def app_xform(result):
            rator = result.content[0]
            rand = result.content[1]
            return App(rator.content, rand.content,
                       result.start_pos, result.end_pos)

        app_parser.xform_content = app_xform

        grammar.register('app', app_parser)

        lam_parser = parsers.Tuple().skip(grammar.ref('lambda'))\
                                    .element(grammar.ref('ref'))\
                                    .skip(grammar.ref('spaces'))\
                                    .skip(grammar.ref('dot'))\
                                    .skip(grammar.ref('spaces'))\
                                    .element(grammar.ref('expr'))

        def lam_xform(result):
            var_name = result.content[0].content.var_name
            var_type = result.content[0].content.var_type
            return Lambda(var_name, var_type, result.content[1].content,
                          result.start_pos, result.end_pos)

        lam_parser.xform_content = lam_xform

        grammar.register('lam', lam_parser)

        expr_parser = parsers.Choice().either(grammar.ref('ref'))\
                                      .orelse(grammar.ref('app'))\
                                      .orelse(grammar.ref('lam'))

        grammar.register('expr', expr_parser)

        grammar.entry = grammar.ref('expr')

    def parse_from_string(self, string):
        tokenizer = Tokenizer()
        self.prepare_tokenizer(tokenizer)
        parser = LLParsing(self.grammar)
        parser.tokenizer = tokenizer
        tokenizer.from_string(string)
        return parser.parse()

# entrypoint
if __name__ == '__main__':
    parser = LambdaParser()
    input_ = '(λx:Bool. x:Bool y:Bool)'
    result = parser.parse_from_string(input_)
    print("{0}\n==> {1}".format(input_, result))
