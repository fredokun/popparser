'''Calculator parsing examples.

Created on 27 august 2012

@author: F. Peschanski
'''

if __name__ == "__main__":
    import sys
    sys.path.append("../src")

from popparser import Grammar, ParseResult, ParseError,\
                 parsers, tokens, expr
from popparser.llparser import LLParsing
from popparser.tokenizer import Tokenizer


class CalculatorEval:
    def __init__(self):
        self.grammar = CalculatorEval.calculator_grammar()

    @staticmethod
    def calculator_tokenizer():
        tokenizer = Tokenizer()

        # punctuation
        tokenizer.add_rule(tokens.Char('lparen', '('))
        tokenizer.add_rule(tokens.Char('rparen', ')'))

        # operators
        tokenizer.add_rule(tokens.Char('add', '+'))
        tokenizer.add_rule(tokens.Char('sub', '-'))
        tokenizer.add_rule(tokens.Char('mult', '*'))
        tokenizer.add_rule(tokens.Char('mult', '×'))
        tokenizer.add_rule(tokens.Char('div', '/'))
        tokenizer.add_rule(tokens.Char('div', '÷'))

        # spaces
        tokenizer.add_rule(tokens.CharSet('space', ' ', '\t', '\r'))
        tokenizer.add_rule(tokens.Char('newline', '\n'))

        # numbers
        tokenizer.add_rule(tokens.Char('number', '0'))
        tokenizer.add_rule(tokens.Regexp('number',
                                         '[1-9][0-9]*(\\.[0-9]*[1-9]+)?',
                                         lookups={str(i) for i in range(10)}))

        return tokenizer

    @staticmethod
    def calculator_grammar():
        grammar = Grammar()

        grammar.entry = parsers.Tuple().element(grammar.ref('expr'))\
                                       .skip(grammar.ref('spaces'))\
                                       .skip(parsers.EOF())

        spaces_parser = parsers.Repeat(parsers.Token('space'), minimum=0)
        grammar.register('spaces', spaces_parser)

        expr_parser = expr.ExprParser()\
            .skip_token('space')\
            .register('add', CalculatorEval.AddOperator())\
            .register('sub', CalculatorEval.SubOperator())\
            .register('mult', CalculatorEval.MultOperator())\
            .register('div', CalculatorEval.DivOperator())\
            .register('lparen', CalculatorEval.Parentheses())\
            .register('number', CalculatorEval.Number())

        grammar.register('expr', expr_parser)

        return grammar

    class AddOperator(expr.Mixfix):
        def __init__(self):
            expr.Mixfix.__init__(self, prefix_prio=100,
                                 infix_assoc="LEFT", infix_prio=40)

        def on_prefix(self, token, argument):
            return ParseResult(argument.content,
                               token.start_pos,
                               argument.end_pos)

        def on_infix(self, left, _, right):
            return ParseResult(left.content + right.content,
                               left.start_pos,
                               right.start_pos)

    class SubOperator(expr.Mixfix):
        def __init__(self):
            expr.Mixfix.__init__(self, prefix_prio=100,
                                 infix_assoc="LEFT", infix_prio=40)

        def on_prefix(self, token, argument):
            return ParseResult(-argument.content,
                               token.start_pos,
                               argument.end_pos)

        def on_infix(self, left, _, right):
            return ParseResult(left.content - right.content,
                               left.start_pos,
                               right.start_pos)

    class MultOperator(expr.Infix):
        def __init__(self):
            expr.Infix.__init__(self, 'LEFT', 80)

        def on_infix(self, left, _, right):
            return ParseResult(left.content * right.content,\
                               left.start_pos, right.end_pos)

    class DivOperator(expr.Infix):
        def __init__(self):
            expr.Infix.__init__(self, 'LEFT', 80)

        def on_infix(self, left, token, right):
            if right.content == 0:
                return ParseError("Division by zero",\
                                  token.start_pos,\
                                  right.end_pos)
            return ParseResult(left.content / right.content,\
                               left.start_pos, right.end_pos)

    class Number(expr.Atom):
        def on_atom(self, token):
            return ParseResult(float(token.value),\
                               token.start_pos, token.end_pos)

    class Parentheses(expr.Bracket):
        def __init__(self):
            expr.Bracket.__init__(self, 'lparen', 'rparen')

    def parse_from_string(self, string):
        tokenizer = CalculatorEval.calculator_tokenizer()
        parser = LLParsing(self.grammar)
        parser.tokenizer = tokenizer
        tokenizer.from_string(string)
        return parser.parse()


# test functions
def show_eval(parser, input_):
    result = parser.parse_from_string(input_)
    return "{0} = {1}".format(input_, result.content.content)


def show_error(parser, input_):
    result = parser.parse_from_string(input_)
    return "> {0}\n==> {1}".format(input_, result)

# entrypoint
if __name__ == '__main__':
    parser = CalculatorEval()
    print(show_eval(parser, '3×6'))
    print(show_eval(parser, '3 * 6'))
    print(show_eval(parser, '3 × 6/2 × 3'))
    print(show_eval(parser, '(3 × 6) / (2 × 3)'))
    print(show_error(parser, '2 / 0'))
    print(show_eval(parser, '3 + 4 × 6'))
    print(show_eval(parser, '3 + 4 × -6'))
    print(show_eval(parser, '3 + + 4'))
