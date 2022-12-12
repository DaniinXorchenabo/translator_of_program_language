from typing import Iterator, Generator

from interpreter.expressions.expressions import ExpressionController
from interpreter.var_const_concatinator.var_const_pipline import var_const_pipline
from syntax_analyzer.lexical.terminals import TERMINALS
from syntax_analyzer.main_syntax_analyzer import SyntaxAnalyzer
from syntax_analyzer.rules import raw_rules
from syntax_analyzer.rules.raw_rules import raw_rules_dict


def expr_pipeline(var_const_gen: Generator, variables_dict):
    expr_controller = ExpressionController()
    # variables_dict[(TERMINALS.t, TERMINALS.t, TERMINALS.x)] = 200

    # variables_dict = dict()
    for buffer_item in var_const_gen:
        res = expr_controller.expressions_tree_builder(buffer_item, variables_dict)
        for i in res:
            if i is not None:
                res = yield i
                if res is not None:
                    yield var_const_gen.send(res)
    print("")
    # return []


if __name__ == '__main__':

    with open("../program.txt", "r", encoding='utf-8') as f:
        data = f.read()
    variables_dict = dict()
    syntax_analyzer = SyntaxAnalyzer(raw_rules_dict)
    syntax_gen = syntax_analyzer.analyze_gen(data)
    res = expr_pipeline(var_const_pipline(syntax_gen), variables_dict)
    for i in res:
        print(i, sep='\n')
        # pass