import enum
from typing import Type
from uuid import uuid4, UUID

from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.lexical.no_terminals import NO_TERMINALS, NO_T
from syntax_analyzer.lexical.terminals import OPTIONAL_BLANKS_ENUM, BLANKS_ENUM, CHARS_ENUM, NUMERALS_ENUM

A = ALL_LEXICAL
O_BL = OPTIONAL_BLANKS_ENUM
BL = BLANKS_ENUM

D_V_TYPE = dictionary_value_type = list[ALL_LEXICAL | Type[enum.Enum]]

raw_rules_dict: dict[str, dict[tuple[UUID, NO_TERMINALS], D_V_TYPE]] = dict(

    tM_dict={
        (uuid4(), NO_T.tM): [NO_T.tD, O_BL, NO_T.tB, O_BL],
    },

    tD_dict={
        (uuid4(), NO_T.tD): [A.VAR, BL, NO_T.tDv, O_BL, A(":"), O_BL, A.INTEGER, O_BL, A(';'), O_BL],
    },

    tDv_dict={
        (uuid4(), NO_T.tDv): [NO_T.tV, O_BL],
        (uuid4(), NO_T.tDv): [NO_T.tV, O_BL, A(','), O_BL, NO_T.tDv],
    },
    tV_dict={
        (uuid4(), NO_T.tV): [CHARS_ENUM, NO_T.tV],
        (uuid4(), NO_T.tV): [CHARS_ENUM],
    },
    tB_dict={
        (uuid4(), NO_T.tB): [A.BEGIN, BL, NO_T.tBr, BL, A.END],
    },
    tBr_dict={
        (uuid4(), NO_T.tBr): [NO_T.tA, O_BL, A(';'), O_BL, NO_T.tBr],
        (uuid4(), NO_T.tBr): [O_BL('')],
        (uuid4(), NO_T.tBr): [NO_T.tR, O_BL, A(';'), O_BL, NO_T.tBr],
        (uuid4(), NO_T.tBr): [NO_T.tW, O_BL, A(';'), O_BL, NO_T.tBr],
        (uuid4(), NO_T.tBr): [NO_T.tSc, O_BL, A(';'), O_BL, NO_T.tBr],
    },
    tR_dict={
        (uuid4(), NO_T.tR): [A.READ, O_BL, A('('), O_BL, NO_T.tDv, O_BL, A(')')],
    },
    tW_dict={
        (uuid4(), NO_T.tW): [A.WRITE, O_BL, A('('), O_BL, NO_T.tDv, O_BL, A(')')],
    },
    tA_dict={
        (uuid4(), NO_T.tA): [NO_T.tV, O_BL, A('='), O_BL, NO_T.tE],
    },
    tSc_dict={
        (uuid4(), NO_T.tSc): [A.SWITCH, BL, NO_T.tCes, O_BL, A.END],
    },
    tCes_dict={
        (uuid4(), NO_T.tCes): [A.CASE, BL, NO_T.tE, BL, A.OF, BL, NO_T.tBr, BL, A.END, O_BL, A(';')],
        (uuid4(), NO_T.tCes): [A.CASE, BL, NO_T.tE, BL, A.OF, BL, NO_T.tBr, BL, A.END, O_BL, A(';'), O_BL, NO_T.tCes],
    },
    tE_dict={
        (uuid4(), NO_T.tE): [NO_T.tUo, O_BL, NO_T.tSe],
        (uuid4(), NO_T.tE): [NO_T.tSe],
    },
    tSe_dict={
        (uuid4(), NO_T.tSe): [A('('), O_BL, NO_T.tE, O_BL, A(')')],
        (uuid4(), NO_T.tSe): [NO_T.tNum],
        (uuid4(), NO_T.tSe): [NO_T.tSe, O_BL, NO_T.tBo, O_BL, NO_T.tSe],
    },

    tNum_dict={
        (uuid4(), NO_T.tNum): [NUMERALS_ENUM],
        (uuid4(), NO_T.tNum): [NUMERALS_ENUM, NO_T.tNum],
    },

)
