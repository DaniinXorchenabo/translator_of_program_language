from typing import Iterator

from interpreter.expressions.expressions import ExpressionController
from interpreter.var_const_concatinator.var_const_pipline import var_const_pipline
from syntax_analyzer.rules.raw_rules import raw_rules_dict


def expr_pipeline(var_const_gen: Iterator):
    expr_controller = ExpressionController()
    for buffer_item in var_const_gen:
        expr_controller.expressions_tree_builder(buffer_item)
    print("")
    return []


if __name__ == '__main__':

    with open("../program.txt", "r", encoding='utf-8') as f:
        data = f.read()

    res = expr_pipeline(var_const_pipline(raw_rules_dict, data))
    for i in res:
        print(i, sep='\n')