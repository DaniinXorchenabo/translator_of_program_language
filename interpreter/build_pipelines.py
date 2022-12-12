from interpreter.cases.case_pipeline import switch_case_pipeline
from interpreter.expressions.pipeline import expr_pipeline
from interpreter.io.pipeline import io_controller_pipe
from interpreter.utils.generator_wapper import reverse_gen_waper, WaperName
from interpreter.var_const_concatinator.var_const_pipline import var_const_pipline
from syntax_analyzer.main_syntax_analyzer import SyntaxAnalyzer


def build_interpreter_pipeline(text: str, raw_rules: dict, variables_dict: dict):
    syntax_analyzer = SyntaxAnalyzer(raw_rules)

    syntax_gen = reverse_gen_waper(
        syntax_analyzer.analyze_gen(text),
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

    return res
