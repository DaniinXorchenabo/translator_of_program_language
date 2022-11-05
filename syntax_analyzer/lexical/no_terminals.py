import enum

__all__ = [
    'get_no_terminals',
    'no_terminals_dict'
]

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
    tZ = 'tZ',
)


def get_no_terminals():
    global _NO_TERMINALS, _first_NO_TERMINALS, no_terminals_dict

    NO_TERMINALS = enum.unique(enum.Enum('NO_TERMINALS', no_terminals_dict))
    if _NO_TERMINALS is None:
        _NO_TERMINALS = NO_TERMINALS
        _first_NO_TERMINALS = NO_TERMINALS
        NO_TERMINALS = enum.Enum('NO_TERMINALS', no_terminals_dict)
        NO_TERMINALS.__bases__ = (_first_NO_TERMINALS, enum.Enum)
        NO_TERMINALS = enum.unique(NO_TERMINALS)
    else:
        NO_TERMINALS.__bases__ = (_first_NO_TERMINALS, enum.Enum)
        NO_TERMINALS = enum.unique(NO_TERMINALS)
        _NO_TERMINALS = NO_TERMINALS
    return NO_TERMINALS


_first_NO_TERMINALS = None
_NO_TERMINALS = None
