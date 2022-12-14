import enum
import inspect
from typing import Type, Any
from uuid import uuid4, UUID

from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.lexical.terminals import OPTIONAL_BLANKS_ENUM, BLANKS_ENUM, CHARS_ENUM, NUMERALS_ENUM, \
    BINARY_ENUM
from syntax_analyzer.lexical import no_terminals

NO_TERMINALS, get_clone_unique_id = NO_T, _ = no_terminals.get_no_terminals()


def recourse_gen(*data: list[Any] | str | enum.Enum | Type[enum.Enum], _const_data_prefix=None):
    _const_data_prefix = _const_data_prefix or []

    if len(data) == 1:

        if isinstance(data[0], (list, set, frozenset, tuple)) \
                or (inspect.isclass(data[0]) and issubclass(data[0], enum.Enum)):
            for i in data[0]:
                yield _const_data_prefix + [i]
        else:
            yield _const_data_prefix + [data[0]]
    else:
        if isinstance(data[0], (list, set, frozenset, tuple)) \
                or (inspect.isclass(data[0]) and issubclass(data[0], enum.Enum)):
            for i in data[0]:
                yield from recourse_gen(*data[1:], _const_data_prefix=_const_data_prefix[:] + [i])
        else:
            yield from recourse_gen(*data[1:], _const_data_prefix=_const_data_prefix[:] + [data[0]])


def recourse_optional_gen(*data: list[Any] | str | enum.Enum | Type[enum.Enum], _const_data_prefix=None):
    _const_data_prefix = _const_data_prefix or []

    if len(data) == 1:

        if isinstance(data[0], (list, set, frozenset, tuple)) \
                or (inspect.isclass(data[0]) and issubclass(data[0], OPTIONAL_BLANKS_ENUM)):
            if data[0] == OPTIONAL_BLANKS_ENUM:
                yield _const_data_prefix
                yield _const_data_prefix + [BLANKS_ENUM]
                # yield _const_data_prefix + [OPTIONAL_BLANKS_ENUM]
            else:
                for i in data[0]:
                    yield _const_data_prefix + [i]
        else:
            yield _const_data_prefix + [data[0]]
    else:
        if isinstance(data[0], (list, set, frozenset, tuple)) \
                or (inspect.isclass(data[0]) and issubclass(data[0], OPTIONAL_BLANKS_ENUM)):
            if data[0] == OPTIONAL_BLANKS_ENUM:
                yield from recourse_optional_gen(*data[1:], _const_data_prefix=_const_data_prefix[:] + [BLANKS_ENUM])
                yield from recourse_optional_gen(*data[1:], _const_data_prefix=_const_data_prefix[:] + [])
                # yield from recourse_optional_gen(*data[1:],
                #                                  _const_data_prefix=_const_data_prefix[:] + [OPTIONAL_BLANKS_ENUM])
            else:
                for i in data[0]:
                    yield from recourse_optional_gen(*data[1:], _const_data_prefix=_const_data_prefix[:] + [i])
        else:
            yield from recourse_optional_gen(*data[1:], _const_data_prefix=_const_data_prefix[:] + [data[0]])


A = ALL_LEXICAL
O_BL = OPTIONAL_BLANKS_ENUM
BL = BLANKS_ENUM

D_V_TYPE = dictionary_value_type = list[ALL_LEXICAL | Type[enum.Enum]]

raw_rules_dict: dict[str, dict[tuple[UUID, NO_TERMINALS], D_V_TYPE]] = dict(

    tM_dict={
        (uuid4(), NO_T.tM): [NO_T.tD, O_BL, NO_T.tB, BL],  # , O_BL
    },

    tD_dict={
        (uuid4(), NO_T.tD): [A.VAR, BL, NO_T.tDv, A(":"), O_BL, A.INTEGER, O_BL, A(';')],  # , O_BL
    },

    tDv_dict={
        (uuid4(), NO_T.tDv): [NO_T.tV, O_BL],  # , O_BL
        (uuid4(), NO_T.tDv): [NO_T.tV, O_BL, A(','), O_BL, NO_T.tDv],
    },
    tV_dict={
        (uuid4(), NO_T.tV): [CHARS_ENUM, NO_T.tV],
        (uuid4(), NO_T.tV): [CHARS_ENUM],
    },
    tB_dict={
        (uuid4(), NO_T.tB): [A.BEGIN, BL, NO_T.tBr, A.END],
    },
    tBr_dict={
        (uuid4(), NO_T.tBr): [A.PASS, O_BL, A(';'), O_BL, ],
        (uuid4(), NO_T.tBr): [NO_T.tA, O_BL, A(';'), O_BL, ],
        (uuid4(), NO_T.tBr): [NO_T.tR, O_BL, A(';'), O_BL, ],
        (uuid4(), NO_T.tBr): [NO_T.tW, O_BL, A(';'), O_BL, ],
        (uuid4(), NO_T.tBr): [NO_T.tSc, O_BL, A(';'), O_BL, ],
        (uuid4(), NO_T.tBr): [NO_T.tA, O_BL, A(';'), O_BL, NO_T.tBr],
        (uuid4(), NO_T.tBr): [NO_T.tR, O_BL, A(';'), O_BL, NO_T.tBr],
        (uuid4(), NO_T.tBr): [NO_T.tW, O_BL, A(';'), O_BL, NO_T.tBr],
        (uuid4(), NO_T.tBr): [NO_T.tSc, O_BL, A(';'), O_BL, NO_T.tBr],
    },
    tR_dict={
        (uuid4(), NO_T.tR): [A.READ, O_BL, A('('), O_BL, NO_T.tV, O_BL, A(')')],

    },
    tW_dict={
        (uuid4(), NO_T.tW): [A.WRITE, O_BL, A('('), O_BL, NO_T.tE, O_BL, A(')')],
    },
    tA_dict={
        (uuid4(), NO_T.tA): [NO_T.tV, O_BL, A('='), O_BL, NO_T.tE],
    },
    tSc_dict={
        (uuid4(), NO_T.tSc): [A.SWITCH, BL, NO_T.tE, BL, NO_T.tCes, A.END],
    },
    tCes_dict={
        (uuid4(), NO_T.tCes): [A.CASE, BL, NO_T.tE, BL, A.OF, BL, NO_T.tBr, A.END, A(';'), O_BL, ],
        (uuid4(), NO_T.tCes): [A.CASE, BL, NO_T.tE, BL, A.OF, BL, NO_T.tBr, A.END, A(';'), O_BL, NO_T.tCes],
    },
    tE_dict={
        # (uuid4(), NO_T.tE): [NO_T.tUo, NO_T.tSe],
        (uuid4(), NO_T.tE): [NO_T.tUo, O_BL, NO_T.tSe],
        (uuid4(), NO_T.tE): [NO_T.tSe],
    },
    tSe_dict={
        (uuid4(), NO_T.tSe): [A('('), O_BL, NO_T.tE, O_BL, A(')')],
        (uuid4(), NO_T.tSe): [NO_T.tNum],
        (uuid4(), NO_T.tSe): [NO_T.tV],
        (uuid4(), NO_T.tSe): [NO_T.tSe, NO_T.tBo, O_BL, NO_T.tSe],
    },
    # tSe_dict={
    #     (uuid4(), NO_T.tSe): [A('('), NO_T.tE,  A(')')],
    #     (uuid4(), NO_T.tSe): [NO_T.tNum],
    #     (uuid4(), NO_T.tSe): [NO_T.tV],
    #     (uuid4(), NO_T.tSe): [NO_T.tSe, NO_T.tBo,  NO_T.tSe],
    # },
    tNum_dict={
        (uuid4(), NO_T.tNum): [NUMERALS_ENUM, NO_T.tNum],
        (uuid4(), NO_T.tNum): [NUMERALS_ENUM],
    },
    tUo_dict={
        (uuid4(), NO_T.tUo): [BINARY_ENUM("-")],
    },
    tBo_dict={
        (uuid4(), NO_T.tBo): [BINARY_ENUM],
    },

)

old_raw_rule_len = sum(len(v) for v in raw_rules_dict.values())

# raw_rules_dict: dict[str, dict[tuple[UUID, NO_TERMINALS], list[ALL_LEXICAL]]] = {
#     dict_name: {
#         (uuid4(), key): list(filter(lambda i: i != O_BL(None), new_rule))
#         for [_, key], rule in rules.items()
#         for new_rule in recourse_gen(*rule)
#     }
#     for dict_name, rules in raw_rules_dict.items()
# }

# TODO: Uncommented
# assert len(raw_rules_dict) == len(NO_T), f'''??????????????????????
#     {set([i.name for i in NO_T]) - set([i.removesuffix('_dict') for i in raw_rules_dict])},
#      ???????????????????????? ????????????
#      {set([i.removesuffix('_dict') for i in raw_rules_dict]) - set([i.name for i in NO_T])}'''
# key_num = None
# assert all([all(j[1].name == key.removesuffix('_dict') for j in values)
#             for key, values in raw_rules_dict.items() if (key_num := key)]), \
#     f'?? ?????????????? {key_num} ?????? ?????????????? ???????? ???? ???????????? ?????????? ???????????????? ?????????????? ????????????????'
raw_rules_dict: dict[tuple[UUID, NO_TERMINALS], list[ALL_LEXICAL]] = {
    key: val for values in raw_rules_dict.values() for key, val in values.items()
}
# print(*raw_rules_dict.items(), sep='\n')
START_STATES = {NO_TERMINALS.tM}

if __name__ == '__main__':
    # print(*[(key, str(val).replace("\n", '\\n'.replace('\r', '\\r'))) for key, val in raw_rules_dict.items()], sep="\n")
    print(f'???????????? ???????? ?????????? {old_raw_rule_len} ????????????,\n?????????? ???????????? -- {len(raw_rules_dict)}')
