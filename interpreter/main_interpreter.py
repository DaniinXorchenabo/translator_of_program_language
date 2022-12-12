from __future__ import annotations
from typing import Any

from interpreter.build_pipelines import build_interpreter_pipeline
from interpreter.var_const_concatinator.variables import VarActions, VariablesController
from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.main_syntax_analyzer import SyntaxAnalyzer
from syntax_analyzer.rules.raw_rules import raw_rules_dict

Var = tuple[ALL_LEXICAL, ...]
VarActionType = tuple[Var, VarActions]


def interpreter(text: str, raw_rules: dict, variables_dict: dict):
    res = build_interpreter_pipeline(text, raw_rules, variables_dict)
    for i in res:
        # print(i, sep='\n')
        yield i


if __name__ == '__main__':
    with open("program.txt", "r", encoding='utf-8') as f:
        data = f.read()

    variables_dict = dict()
    for i in interpreter(data, raw_rules_dict, variables_dict):
        pass
