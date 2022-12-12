from typing import Any

from interpreter.var_const_concatinator.abstract import BufferItem
from interpreter.var_const_concatinator.numbers import NumController
from interpreter.var_const_concatinator.other_chars import OtherChars
from interpreter.var_const_concatinator.variables import VarActions, VariablesController, VarBufferItem
from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.main_syntax_analyzer import SyntaxAnalyzer
from syntax_analyzer.rules.raw_rules import raw_rules_dict

Var = tuple[ALL_LEXICAL, ...]
VarActionType = tuple[Var, VarActions]


def var_const_pipline(syntax_gen):
    # syntax_analyzer = SyntaxAnalyzer(raw_rules)
    # lexemes_iterator = syntax_analyzer.analyze_gen(text)

    grammar_buffer: list[BufferItem] = []
    var_action_stack: list[VarBufferItem] = []

    var_controller = VariablesController()
    num_controller = NumController()
    other_lexemes_controller = OtherChars()

    for lexeme in syntax_gen:
        # print(lexeme)
        grammar_buffer, var_action_stack = var_controller.builder(grammar_buffer, lexeme, var_action_stack)
        var_action_stack = var_controller.action_identifier(var_action_stack, lexeme)

        grammar_buffer = num_controller.concatenate(grammar_buffer, lexeme)
        grammar_buffer = other_lexemes_controller.to_buffer(grammar_buffer, lexeme)

        for _ in range(len(grammar_buffer)):
            if grammar_buffer[0].done():
                # print("^^---=")
                res = yield grammar_buffer.pop(0)
                if res is not None:
                    yield syntax_gen.send(res)

            else:
                break
    # print('**********************')
    if bool(grammar_buffer):
        raise ValueError()
    for i in grammar_buffer:
        res = yield i
        if res is not None:
            yield syntax_gen.send(res)


if __name__ == '__main__':

    with open("../program.txt", "r", encoding='utf-8') as f:
        data = f.read()
    syntax_analyzer = SyntaxAnalyzer(raw_rules_dict)
    syntax_gen = syntax_analyzer.analyze_gen(data)
    res = var_const_pipline(syntax_gen)
    for i in res:
        print(i, sep='\n')

    # ddd = list(res)
    # print(*ddd, sep='\n')
