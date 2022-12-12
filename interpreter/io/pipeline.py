from interpreter.expressions.pipeline import expr_pipeline
from interpreter.io.io_controller import VarController
from interpreter.utils.generator_wapper import WaperName, reverse_gen_waper
from interpreter.var_const_concatinator.var_const_pipline import var_const_pipline
from syntax_analyzer.lexical.terminals import TERMINALS
from syntax_analyzer.main_syntax_analyzer import SyntaxAnalyzer
from syntax_analyzer.rules.raw_rules import raw_rules_dict


def io_controller_pipe(expression_gen, variables_dict):
    # variables_dict[(TERMINALS.t, TERMINALS.t, TERMINALS.x)] = 100

    var_controller = VarController()

    for i in expression_gen:
        changed_variables_dict = var_controller.controller(i, variables_dict)
        res = yield i
        if res is not None:
            yield expression_gen.send(res)


if __name__ == '__main__':

    with open("../program.txt", "r", encoding='utf-8') as f:
        data = f.read()

    variables_dict = dict()
    syntax_analyzer = SyntaxAnalyzer(raw_rules_dict)

    syntax_gen = reverse_gen_waper(
        syntax_analyzer.analyze_gen(data),
        WaperName.syntax
    )
    var_const_gen = reverse_gen_waper(var_const_pipline(syntax_gen), WaperName.v_c_concatenate)
    expr_gen = reverse_gen_waper(
        expr_pipeline(
            var_const_gen,
            variables_dict
        ),
        WaperName.expr_calc
    )
    io_gen = reverse_gen_waper(
        io_controller_pipe(
            expr_gen,
            variables_dict
        ),
        WaperName.var_controller
    )

    res = io_gen
    for i in res:
        print(i, sep='\n')
