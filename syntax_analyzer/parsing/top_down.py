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

NO_TERMINALS = no_terminals.get_no_terminals()


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
                  and ''.join((i.name + i.value if hasattr(i, 'name') else i.__name__) for i in self.shop_chain))
            + self.state.name

        )


SHOP_MACHINE_TYPE = dict[Delta, DeltaDisplay]


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
    print('&-------------')
    print(newer_first_terminals)

    shop_machine: SHOP_MACHINE_TYPE = dict()
    first_terminals = set()
    for no_terminal, rules in ll1_rules.items():
        for shop_chain in rules:
            if inspect.isclass(shop_chain[0]):
                first_terminals |= {shop_chain[0], *set(shop_chain[0])}
            else:
                first_terminals |= {shop_chain[0], shop_chain[0].__class__}

            print(f"{str(no_terminal.name).ljust(50)} {str(shop_chain[0]).ljust(25)} {shop_chain}")
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
                    terminal = TERMINALS[item.name] if hasattr(item, 'name') else item
                    shop_machine[Delta(terminal, no_terminal)] = DeltaDisplay(
                        input_action=InputAction.empty,
                        shop_action=ShopAction.pass_,
                        shop_chain=None
                    )
            elif (hasattr(shop_chain[0], "name") and shop_chain[0].name in terminals) \
                    or (inspect.isclass(shop_chain[0]) and issubclass(shop_chain[0], enum.Enum)):
                if inspect.isclass(shop_chain[0]):
                    print("^^")
                terminal = TERMINALS[shop_chain[0].name] if hasattr(shop_chain[0], 'name') else shop_chain[0]
                shop_machine[Delta(terminal, no_terminal)] = DeltaDisplay(
                    InputAction.read,
                    ShopAction.add,
                    shop_chain[:0:-1]
                )
            else:
                print("***")
                raise ValueError()

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
