import enum

__all__ = [
    'get_no_terminals',
    'no_terminals_dict'
]

from typing import Type

no_terminals_dict = dict(
    tM='Start_state',
    tD="Define_all_variables_with_syntax",
    tB='Body',
    tDv='Define_all_variables',
    tV='variable',
    tBr='Real program body',
    tA='Assigment',
    tR='Read from stdin',
    tW='Write to stdout',
    tSc='Switch case',
    tCes='Cases',
    tUo='Unary operator',
    tSe='Subexpression',
    tE='Expression',
    tBo='Binary operator',
    tNum='Number',
)


def eq_enum_decorator(default_eq):
    def no_terminals_eq(self, item):
        global _first_NO_TERMINALS
        if _first_NO_TERMINALS and isinstance(item, _first_NO_TERMINALS):
            return item.name == self.name and item.value == self.value
        else:
            return default_eq(self, item)

    return no_terminals_eq


def ne_enum_decorator(default_ne):
    def no_terminals_no_eq(self, item):
        global _first_NO_TERMINALS
        if _first_NO_TERMINALS and isinstance(item, _first_NO_TERMINALS):
            return item.name != self.name or item.value != self.value
        else:
            return default_ne(self, item)

    return no_terminals_no_eq


def get_no_terminals():
    global _NO_TERMINALS, _first_NO_TERMINALS, no_terminals_dict

    NO_TERMINALS = enum.unique(enum.Enum('NO_TERMINALS', no_terminals_dict))
    if _NO_TERMINALS is None:
        _NO_TERMINALS = NO_TERMINALS
        _first_NO_TERMINALS = NO_TERMINALS
        _first_NO_TERMINALS.__eq__ = eq_enum_decorator(_first_NO_TERMINALS.__eq__)
        _first_NO_TERMINALS.__ne__ = ne_enum_decorator(_first_NO_TERMINALS.__ne__)
        NO_TERMINALS = enum.Enum('NO_TERMINALS', no_terminals_dict)
        NO_TERMINALS.__bases__ = (_first_NO_TERMINALS, enum.Enum)
        NO_TERMINALS = enum.unique(NO_TERMINALS)
    else:
        NO_TERMINALS.__bases__ = (_first_NO_TERMINALS, enum.Enum)
        NO_TERMINALS = enum.unique(NO_TERMINALS)
        _NO_TERMINALS = NO_TERMINALS

    def get_clone_unique_id():
        global id_counter
        id_counter += 1
        return str(id_counter).rjust(4, "0")

    return NO_TERMINALS, get_clone_unique_id


_first_NO_TERMINALS: Type[enum.Enum] | None = None
_NO_TERMINALS = None
id_counter = 0
