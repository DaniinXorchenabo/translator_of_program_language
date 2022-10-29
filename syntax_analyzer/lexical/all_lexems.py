import enum

from syntax_analyzer.lexical.terminals import keywords, chars, numerals, unary, binary, special_chars
from syntax_analyzer.lexical.no_terminals import NO_TERMINALS

__all__ = [
    'ALL_LEXICAL'
]

ALL_LEXICAL = DynamicEnum = enum.Enum(
    'ALL_LEXICAL',
    {item: item
     for dict_ in [keywords, chars, numerals, unary, binary, special_chars, [i.name for i in NO_TERMINALS]]
     for item in dict_}
)