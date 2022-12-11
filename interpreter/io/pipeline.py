from interpreter.expressions.pipeline import expr_pipeline
from interpreter.io.io_controller import VarController
from interpreter.var_const_concatinator.var_const_pipline import var_const_pipline
from syntax_analyzer.lexical.terminals import TERMINALS
from syntax_analyzer.main_syntax_analyzer import SyntaxAnalyzer
from syntax_analyzer.rules.raw_rules import raw_rules_dict


def io_controller_pipe(expression_gen, variables_dict):
    # variables_dict[(TERMINALS.t, TERMINALS.t, TERMINALS.x)] = 100

    var_controller = VarController()

    for i in expression_gen:
        changed_variables_dict = var_controller.controller(i, variables_dict)
        yield i


if __name__ == '__main__':

    with open("../program.txt", "r", encoding='utf-8') as f:
        data = f.read()

    variables_dict = dict()
    syntax_analyzer = SyntaxAnalyzer(raw_rules_dict)
    syntax_gen = syntax_analyzer.analyze_gen(data)
    res = io_controller_pipe(
        expr_pipeline(
            var_const_pipline(syntax_gen),
            variables_dict
        ),
        variables_dict
    )
    for i in res:
        print(i, sep='\n')
