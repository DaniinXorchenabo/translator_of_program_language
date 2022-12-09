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


def var_const_pipline(raw_rules, text: str):
    syntax_analyzer = SyntaxAnalyzer(raw_rules)
    lexemes_iterator = syntax_analyzer.analyze_gen(text)

    grammar_buffer: list[BufferItem] = []
    var_action_stack: list[VarBufferItem] = []

    var_controller = VariablesController()
    num_controller = NumController()
    other_lexemes_controller = OtherChars()

    for lexeme in lexemes_iterator:
        # print(lexeme)
        grammar_buffer, var_action_stack = var_controller.builder(grammar_buffer, lexeme, var_action_stack)
        var_action_stack = var_controller.action_identifier(var_action_stack, lexeme)

        grammar_buffer = num_controller.concatenate(grammar_buffer, lexeme)
        grammar_buffer = other_lexemes_controller.to_buffer(grammar_buffer, lexeme)

        for _ in range(len(grammar_buffer)):
            if grammar_buffer[0].done():
                # print("^^---=")
                yield grammar_buffer.pop(0)
            else:
                break
    print('**********************')
    yield from grammar_buffer


if __name__ == '__main__':

    with open("../program.txt", "r", encoding='utf-8') as f:
        data = f.read()

    res = var_const_pipline(raw_rules_dict, data)
    for i in res:
        print(i, sep='\n')

    # ddd = list(res)
    # print(*ddd, sep='\n')
