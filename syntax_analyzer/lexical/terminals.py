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


def eq_enum_decorator(default_eq):
    def no_terminals_eq(self, item):
        if isinstance(item, enum.Enum):
            return item.name == self.name and item.value == self.value
        else:
            return default_eq(self, item)

    return no_terminals_eq


def ne_enum_decorator(default_ne):
    def no_terminals_no_eq(self, item):
        if isinstance(item, enum.Enum):
            return item.name != self.name or item.value != self.value
        else:
            return default_ne(self, item)

    return no_terminals_no_eq


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
    "PASS"
}

chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_")
numerals = set("01233456789")
unary = set('-')
binary = set('-+/')
blanks = set(' \n\t\r')
special_chars = set('():;,=')
optional_blanks = special_chars | {'<empty>'}
terminals = keywords | chars | numerals | unary | binary | blanks | special_chars | optional_blanks

KEYWORDS_ENUM = enum.Enum('KEYWORDS_ENUM', {i: i for i in keywords})
CHARS_ENUM = enum.Enum('CHARS_ENUM', {i: i for i in chars})
NUMERALS_ENUM = enum.Enum('NUMERALS_ENUM', {i: i for i in numerals})
UNARY_ENUM = enum.Enum('UNARY_ENUM', {i: i for i in unary})
BINARY_ENUM = enum.Enum('BINARY_ENUM', {i: i for i in binary})
SPECIAL_CHARS_ENUM = enum.Enum('SPECIAL_CHARS_ENUM', {i: i for i in special_chars})
BLANKS_ENUM = enum.Enum('BLANKS_ENUM', {i: i for i in blanks})
OPTIONAL_BLANKS_ENUM = enum.Enum('OPTIONAL_BLANKS_ENUM', {i: i for i in list(blanks)} | {'<empty>': None})

terminal_enums = {KEYWORDS_ENUM, CHARS_ENUM, NUMERALS_ENUM, UNARY_ENUM, BINARY_ENUM, SPECIAL_CHARS_ENUM, BLANKS_ENUM}



for enum_cls in terminal_enums:
    enum_cls.__eq__ = eq_enum_decorator(enum_cls.__eq__)
    enum_cls.__ne__ = ne_enum_decorator(enum_cls.__ne__)

TERMINALS = DynamicEnum = enum.Enum(
    'TERMINALS',
    {item: item
     for dict_ in [keywords, chars, numerals, unary, binary, special_chars, blanks]
     for item in dict_}
)

# class TERMINALS(enum.Enum):
#     pass
TERMINALS.__bases__ = (*terminal_enums, TERMINALS.__bases__[0],)

assert all(map(lambda i: i[0], [(issubclass(TERMINALS, i), i) for i in [*terminal_enums, enum.Enum]]))
