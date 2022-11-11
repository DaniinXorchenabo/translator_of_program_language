
from syntax_analyzer.lexical import no_terminals
from syntax_analyzer.parsing.top_down import deterministic_top_down_parsing_builder
from syntax_analyzer.rules.raw_rules import raw_rules_dict
from syntax_analyzer.rules.to_LL1_grammar import RAW_RULES_TYPE

NO_TERMINALS = no_terminals.get_no_terminals()


class SyntaxAnalyzer(object):
    def __init__(self, raw_rules: RAW_RULES_TYPE):
        global NO_TERMINALS
        self.grammar, NO_TERMINALS = deterministic_top_down_parsing_builder(raw_rules)


if __name__ == '__main__':

    syntax_analyzer = SyntaxAnalyzer(raw_rules_dict)
    with open("program.txt", "r", encoding='utf-8') as f:
        data = f.read()