import enum

from syntax_analyzer.lexical.terminals import keywords, chars, numerals, unary, binary, special_chars
from syntax_analyzer.lexical.no_terminals import get_no_terminals

__all__ = [
    'ALL_LEXICAL'
]

ALL_LEXICAL = enum.Enum(
    'ALL_LEXICAL',
    {item: item
     for dict_ in [keywords, chars, numerals, unary, binary, special_chars, [i.name for i in get_no_terminals()]]
     for item in dict_}
)