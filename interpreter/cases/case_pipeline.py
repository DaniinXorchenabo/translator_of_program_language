from typing import Generator

from interpreter.cases.case_controller import CaseController
from interpreter.expressions.pipeline import expr_pipeline
from interpreter.io.pipeline import io_controller_pipe
from interpreter.utils.generator_wapper import reverse_gen_waper, WaperName, ReverseMessage
from interpreter.var_const_concatinator.var_const_pipline import var_const_pipline
from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.main_syntax_analyzer import SyntaxAnalyzer
from syntax_analyzer.rules.raw_rules import raw_rules_dict


def switch_case_pipeline(io_gen: Generator):
    case_controller = CaseController()
    # yield next(io_gen)
    # yield next(io_gen)
    # io_gen.send(ReverseMessage(WaperName.syntax, lambda i: i != ALL_LEXICAL.CASE and i != ALL_LEXICAL.END ))
    # yield next(io_gen)
    # yield next(io_gen)
    # for i in io_gen:
    #     res = yield i
    #     if res is not None:
    #         yield io_gen.send(res)
    # return

    for i in io_gen:
        buffer_item, message = case_controller.controller(i)
        if message is not None:
            io_gen.send(message)
        res = yield  i
        if res is not None:
            io_gen.send(res)

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
    cases_gen = reverse_gen_waper(
        switch_case_pipeline(io_gen),
        WaperName.switch_case
    )

    res = cases_gen
    for i in res:
        # print(i, sep='\n')
        pass


