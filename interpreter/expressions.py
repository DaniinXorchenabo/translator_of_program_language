from syntax_analyzer.lexical import no_terminals
from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.lexical.terminals import OPTIONAL_BLANKS_ENUM, CHARS_ENUM, NUMERALS_ENUM, BINARY_ENUM, \
    SPECIAL_CHARS_ENUM
from syntax_analyzer.main_syntax_analyzer import NO_TERMINALS


SC_ENUM = SPECIAL_CHARS_ENUM


class ExprTreeList(object):
    def __init__(self, value, parent):
        self.value = value
        self.parent = parent


class ExprTreeNode(object):
    def __init__(self, value, parent, left=None, right=None, priority=None):
        self.value = value
        self.parent = parent
        self.left = left
        self.right = right
        self.priority = priority or (2 if value in [ALL_LEXICAL("/")] else 1)


class ExpressionController(object):

    def __init__(self):
        self.expr_continue = False

    def expressions_tree_builder(self, lexeme: ALL_LEXICAL):
        if lexeme == NO_TERMINALS.tE:
            self.expr_continue = True

        if isinstance(lexeme, no_terminals._first_NO_TERMINALS) is False \
                and any(i.name == lexeme.name for i in
                        list(OPTIONAL_BLANKS_ENUM)
                        + list(BINARY_ENUM)
                        + [SC_ENUM("("), SC_ENUM(")")]
                        + list(CHARS_ENUM)
                        + list(NUMERALS_ENUM)
                        ) is False:
            self.expr_continue = False

        if self.expr_continue:
            # Формирование дерева
            pass
