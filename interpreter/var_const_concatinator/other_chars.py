from dataclasses import dataclass
from typing import Any

from interpreter.var_const_concatinator.abstract import BufferItem
from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.lexical.terminals import KEYWORDS_ENUM, NUMERALS_ENUM, OPTIONAL_BLANKS_ENUM, CHARS_ENUM


class UnaryBufferItem(BufferItem):
    def done(self):
        return True


class OtherChars(object):
    def __init__(self):
        pass

    @staticmethod
    def to_buffer(grammar_buffer: list[BufferItem],  lexeme: ALL_LEXICAL ) \
            -> list[BufferItem]:
        if any(i.name == lexeme.name for i in
               list(CHARS_ENUM) + list(NUMERALS_ENUM) + list(OPTIONAL_BLANKS_ENUM)
               ) is False:
            grammar_buffer += [UnaryBufferItem(result=lexeme)]
        return grammar_buffer
