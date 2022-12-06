import dataclasses
import enum
import inspect
from typing import NamedTuple, Type

from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.rules.LL1_test import first_f, next_f
from syntax_analyzer.rules.raw_rules import raw_rules_dict
from syntax_analyzer.lexical.terminals import TERMINALS, OPTIONAL_BLANKS_ENUM, terminals, terminal_enums
from syntax_analyzer.lexical import no_terminals
from syntax_analyzer.rules.to_LL1_grammar import grammar_transform, grammar_factorization, RAW_RULES_TYPE, \
    GROUPED_RULES_TYPE

NO_TERMINALS, get_clone_unique_id = no_terminals.get_no_terminals()


class States(enum.Enum):
    start = 'start'
    finish = 'finish'


class ShopMarker(enum.Enum):
    shopHO = 'shopHO'


class InputAction(enum.Enum):
    read = 'read'
    empty = 'empty'


class ShopAction(enum.Enum):
    delete = 'delete'
    add = 'add'
    pass_ = 'pass_'


class Delta(NamedTuple):
    input_char: TERMINALS | Type[enum.Enum]
    shop: TERMINALS | no_terminals._first_NO_TERMINALS | ShopMarker | Type[enum.Enum]
    state: States = States.start

    def __hash__(self):
        return hash(
            str(self.input_char.name if hasattr(self.input_char, 'name') else self.input_char.__name__)
            + str(self.shop.name if hasattr(self.shop, 'name') else self.shop.__name__)
            + self.state.name
        )


@dataclasses.dataclass
class DeltaDisplay(object):
    input_action: InputAction
    shop_action: ShopAction
    shop_chain: list[TERMINALS | ALL_LEXICAL] | None = None
    state: States = States.start

    def __hash__(self):
        return hash(
            self.input_action.name
            + self.shop_action.name
            + str(self.shop_chain
                  and ''.join(
                (str(i.name) + str(i.value) if hasattr(i, 'name') else i.__name__) for i in self.shop_chain))
            + self.state.name

        )


SHOP_MACHINE_TYPE = dict[Delta, DeltaDisplay]

ARGS = NO_TERMINALS | ALL_LEXICAL | Type[enum.Enum]


def other_first_f(
        symbol: ARGS,
        rules: GROUPED_RULES_TYPE,
        symbol_buf_first: set[ARGS] | None = None,
        symbol_buf_second: set[ARGS] | None = None,
        is_calculated_first: dict[ARGS, set[ARGS]] | None = None,
        is_calculated_second: dict[ARGS, set[ARGS]] | None = None,
) -> set[TERMINALS | Type[enum.Enum]]:
    is_calculated_first = is_calculated_first or dict()
    is_calculated_second = is_calculated_second or dict()
    symbol_buf_first = symbol_buf_first or set()
    symbol_buf_second = symbol_buf_second or set()

    if symbol in is_calculated_first:
        return is_calculated_first[symbol]

    if (hasattr(symbol, "name") and symbol.name in terminals) \
            or (inspect.isclass(symbol) and issubclass(symbol, enum.Enum)):
        is_calculated_first[symbol] = {symbol}
        return {symbol}

    if symbol == OPTIONAL_BLANKS_ENUM(None):
        print('empty WARNING')
        is_calculated_first[symbol] = {symbol}
        return {symbol}

    symbol_buf_first.add(symbol)
    res: set[TERMINALS | Type[enum.Enum]] = set()
    # print(rules)
    for right_part in rules[symbol]:
        if right_part[0] not in symbol_buf_first:
            res |= other_first_f(
                right_part[0],
                rules,
                symbol_buf_first=symbol_buf_first.copy(),
                symbol_buf_second=symbol_buf_second,
                is_calculated_first=is_calculated_first,
                is_calculated_second=is_calculated_second,
            )
    # res -= {OPTIONAL_BLANKS_ENUM(None)}
    is_calculated_first[symbol] = res
    return res


def other_next_f(
        symbol: ARGS,
        rules: GROUPED_RULES_TYPE,
        symbol_buf_first: set[ARGS] | None = None,
        symbol_buf_second: set[ARGS] | None = None,
        is_calculated_first: dict[ARGS, set[ARGS]] | None = None,
        is_calculated_second: dict[ARGS, set[ARGS]] | None = None,
) -> set[TERMINALS | Type[enum.Enum]]:
    is_calculated_first = is_calculated_first or dict()
    is_calculated_second = is_calculated_second or dict()
    symbol_buf_first = symbol_buf_first or set()
    symbol_buf_second = symbol_buf_second or set()

    if symbol in is_calculated_second:
        return is_calculated_second[symbol]
    assert symbol != OPTIONAL_BLANKS_ENUM(None)

    symbol_buf_second.add(symbol)
    res: set[TERMINALS | Type[enum.Enum]] = set()
    for no_terminal, right_parts in rules.items():
        for right_part in right_parts:
            find = False
            for ind, char in enumerate(right_part):
                if find is True and char != OPTIONAL_BLANKS_ENUM(None):
                    find = False
                    _res = other_first_f(
                        char,
                        rules,
                        symbol_buf_first=symbol_buf_first,
                        symbol_buf_second=symbol_buf_second,
                        is_calculated_first=is_calculated_first,
                        is_calculated_second=is_calculated_second,
                    )
                    if OPTIONAL_BLANKS_ENUM(None) in _res:
                        _res -= {OPTIONAL_BLANKS_ENUM(None)}
                        _res |= other_next_f(
                            char,
                            rules,
                            symbol_buf_first=symbol_buf_first,
                            symbol_buf_second=symbol_buf_second,
                            is_calculated_first=is_calculated_first,
                            is_calculated_second=is_calculated_second,
                        )
                        # print()
                    res |= _res
                    # _res |= other_next_f(char, rules)
                    assert OPTIONAL_BLANKS_ENUM(None) not in res
                elif find is True and char == OPTIONAL_BLANKS_ENUM(None):
                    continue
                if char == symbol:
                    find = True
            if find is True and (no_terminal not in symbol_buf_second):
                res |= other_next_f(
                    no_terminal,
                    rules,
                    symbol_buf_first=symbol_buf_first,
                    symbol_buf_second=symbol_buf_second.copy(),
                    is_calculated_first=is_calculated_first,
                    is_calculated_second=is_calculated_second,
                )
    is_calculated_second[symbol] = res
    return res


def empty_rules_resolved(
        grouped_rules: dict[NO_TERMINALS, set[tuple[ALL_LEXICAL | NO_TERMINALS | OPTIONAL_BLANKS_ENUM]]]):
    shop_machine = dict()
    remove_rules: set[tuple[NO_TERMINALS, tuple[ALL_LEXICAL | NO_TERMINALS | OPTIONAL_BLANKS_ENUM]]] = set()
    grouped_rules_copy = dict()

    with_empty: set[tuple[NO_TERMINALS, tuple[ALL_LEXICAL | NO_TERMINALS | OPTIONAL_BLANKS_ENUM]]] = set()
    for no_term, rules in grouped_rules.items():
        grouped_rules_copy[no_term] = set()
        for rule in rules:
            grouped_rules_copy[no_term] |= {rule}
            if rule[0] == OPTIONAL_BLANKS_ENUM(None):
                with_empty.add((no_term, rule))

    remove_rules = with_empty.copy()
    while bool(with_empty):
        for no_term, rule in with_empty.copy():
            resolved_terminals = other_next_f(no_term, grouped_rules_copy)
            # while OPTIONAL_BLANKS_ENUM(None) in resolved_terminals:
            # resolved_terminals |=
            if OPTIONAL_BLANKS_ENUM(None) not in resolved_terminals:
                for item in resolved_terminals:
                    terminal = TERMINALS[item.name] if hasattr(item, 'name') else item
                    shop_machine[Delta(terminal, no_term)] = DeltaDisplay(
                        input_action=InputAction.empty,
                        shop_action=ShopAction.pass_,
                        shop_chain=None
                    )
                    with_empty -= {(no_term, rule)}

    return shop_machine


def deterministic_top_down_parsing_builder(rules_dict: RAW_RULES_TYPE) -> \
        tuple[SHOP_MACHINE_TYPE, Type[NO_TERMINALS], GROUPED_RULES_TYPE]:
    global NO_TERMINALS

    ll1_rules, NO_TERMINALS = grammar_transform(rules_dict)
    ll1_rules: GROUPED_RULES_TYPE

    first_f_dict = dict()
    next_f_dict = dict()
    for no_terminal, rules in ll1_rules.items():
        first_f_dict[no_terminal] = first_f(
            no_terminal,
            ll1_rules,
            # is_calculated_first=first_f_dict,
            # is_calculated_second=next_f_dict,
        )
        next_f_dict[no_terminal] = next_f(
            no_terminal,
            ll1_rules,
            # is_calculated_first=first_f_dict,
            # is_calculated_second=next_f_dict,
        )
        assert OPTIONAL_BLANKS_ENUM(None) not in next_f_dict[no_terminal], \
            f'Функция СЛЕД не должна выдавать пустой символ, однако для нетерминала {no_terminal} ' \
            f'оно его содержит {next_f_dict[no_terminal]} ' \
            f'Правила: {ll1_rules}'

    newer_first_terminals = set()
    _ = {
        newer_first_terminals.update(
            {ii for i in
             [(val.name if hasattr(val, 'name') else {v.name for v in val} | {val}) for val in values]
             for ii in (i if isinstance(i, set) else [i])}
        ) for key, values in first_f_dict.items()
    }

    newer_first_terminals = (terminals | terminal_enums) - newer_first_terminals
    # print('&-------------')
    # print(newer_first_terminals)

    shop_machine: SHOP_MACHINE_TYPE = dict()
    first_terminals = set()
    for no_terminal, rules in ll1_rules.items():
        for shop_chain in rules:
            if inspect.isclass(shop_chain[0]):
                first_terminals |= {shop_chain[0], *set(shop_chain[0])}
            else:
                first_terminals |= {shop_chain[0], shop_chain[0].__class__}

            # print(f"{str(no_terminal.name).ljust(50)} {str(shop_chain[0]).ljust(25)} {shop_chain}")
            if isinstance(shop_chain[0], no_terminals._first_NO_TERMINALS):
                for item in first_f_dict[shop_chain[0]]:
                    terminal = TERMINALS[item.name] if hasattr(item, 'name') else item
                    shop_machine[Delta(terminal, no_terminal)] = DeltaDisplay(
                        InputAction.empty,
                        ShopAction.add,
                        shop_chain[::-1]
                    )
            elif shop_chain[0] == OPTIONAL_BLANKS_ENUM(None):
                assert len(shop_chain) == 1, f"цепочка должна состоять только из одного пустого символа, " \
                                             f"а она {shop_chain}"
                for item in next_f_dict[no_terminal]:
                    # TODO: May be uncomment it
                    # terminal = TERMINALS[item.name] if hasattr(item, 'name') else item
                    # shop_machine[Delta(terminal, no_terminal)] = DeltaDisplay(
                    #     input_action=InputAction.empty,
                    #     shop_action=ShopAction.pass_,
                    #     shop_chain=None
                    # )
                    pass
            elif (hasattr(shop_chain[0], "name") and shop_chain[0].name in terminals) \
                    or (inspect.isclass(shop_chain[0]) and issubclass(shop_chain[0], enum.Enum)):
                # if inspect.isclass(shop_chain[0]):
                # print("^^")
                terminal = TERMINALS[shop_chain[0].name] if hasattr(shop_chain[0], 'name') else shop_chain[0]
                shop_machine[Delta(terminal, no_terminal)] = DeltaDisplay(
                    InputAction.read,
                    ShopAction.add,
                    shop_chain[:0:-1]
                )
            else:
                print("***")
                raise ValueError()

    shop_machine = empty_rules_resolved(ll1_rules) | shop_machine

    newer_first_terminals = (terminals | terminal_enums) - first_terminals - set(NO_TERMINALS)
    for terminal in newer_first_terminals:
        if terminal == OPTIONAL_BLANKS_ENUM(None).name:
            continue
        terminal = terminal if inspect.isclass(terminal) else TERMINALS[terminal]
        shop_machine[Delta(terminal, terminal)] = DeltaDisplay(
            InputAction.read,
            ShopAction.pass_,
            None
        )

    print(len(ll1_rules), len(shop_machine))
    return shop_machine, NO_TERMINALS, ll1_rules


if __name__ == '__main__':
    deterministic_top_down_parsing_builder(raw_rules_dict)
