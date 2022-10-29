import enum

__all__ = [
    'keywords',
    'chars',
    'numerals'
    'unary',
    'binary',
    'special_chars',
    'TERMINALS'

]

keywords = {
    "BEGIN",
    "END",
    "VAR",
    "INTEGER",
    "READ",
    "CASE",
    "OF",
    "WRITE",
    "SWITCH",
    "END",
}



chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
numerals = "01233456789"
unary = '-'
binary = '-+/'
blanks = ' \n\t\r'
special_chars = '():;,='

KEYWORDS_ENUM = enum.Enum('KEYWORDS_ENUM', {i: i for i in keywords})
CHARS_ENUM = enum.Enum('KEYWORDS_ENUM', {i: i for i in chars})
NUMERALS_ENUM = enum.Enum('NUMERALS_ENUM', {i: i for i in numerals})
UNARY_ENUM = enum.Enum('UNARY_ENUM', {i: i for i in unary})
BINARY_ENUM = enum.Enum('BINARY_ENUM', {i: i for i in binary})
SPECIAL_CHARS_ENUM = enum.Enum('SPECIAL_CHARS_ENUM', {i: i for i in special_chars})
BLANKS_ENUM = enum.Enum('BLANKS_ENUM', {i: i for i in blanks})
OPTIONAL_BLANKS_ENUM =  enum.Enum('OPTIONAL_BLANKS_ENUM', {i: i for i in list(blanks) + ['']})


TERMINALS = DynamicEnum = enum.Enum(
    'TERMINALS',
    {item: item
     for dict_ in [keywords, chars, numerals, unary, binary, special_chars, blanks]
     for item in dict_}
)

# class TERMINALS(enum.Enum):
#     pass
TERMINALS.__bases__ = ( KEYWORDS_ENUM, CHARS_ENUM, NUMERALS_ENUM, UNARY_ENUM, BINARY_ENUM, SPECIAL_CHARS_ENUM, BLANKS_ENUM, TERMINALS.__bases__[0],)
print(TERMINALS, type(TERMINALS), [(issubclass(TERMINALS, i), i) for i in [KEYWORDS_ENUM, CHARS_ENUM, NUMERALS_ENUM, UNARY_ENUM, BINARY_ENUM, SPECIAL_CHARS_ENUM, BLANKS_ENUM, enum.Enum]])
print(list(TERMINALS))