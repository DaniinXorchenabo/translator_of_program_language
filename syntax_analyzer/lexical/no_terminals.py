import enum

__all__ = [
    'NO_TERMINALS',
    "NO_T"
]


class NO_TERMINALS(enum.Enum):
    tM = 'Start_state'
    tD = "Define_all_variables_with_syntax"
    tB = 'Body'
    tDv = 'Define_all_variables'
    tV = 'variable'
    tBr = 'Real program body'
    tA = 'Assigment'
    tR = 'Read from stdin'
    tW = 'Write to stdout'
    tSc = 'Switch case'
    tCes = 'Cases'
    tUo = 'Unary operator'
    tSe = 'Subexpression'
    tE = 'Expression'
    tBo = 'Binary operator'
    tNum = 'Number'


NO_T = NO_TERMINALS
