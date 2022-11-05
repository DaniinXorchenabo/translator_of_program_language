import enum
from typing import NamedTuple, Type

from syntax_analyzer.rules.raw_rules import raw_rules_dict
from syntax_analyzer.lexical.terminals import TERMINALS
from syntax_analyzer.lexical import no_terminals
from syntax_analyzer.rules.to_LL1_grammar import grammar_transform, grammar_factorization

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


class Delta(NamedTuple):
    input_char: TERMINALS | Type[enum.Enum]
    shop: TERMINALS | no_terminals._first_NO_TERMINALS | ShopMarker
    state: States = States.start


class DeltaDisplay(NamedTuple):
    input_action: InputAction
    shop_action: ShopAction
    state: States = States.start


def deterministic_top_down_parsing_builder(rules_dict):
    global NO_TERMINALS
    ll1_rules, NO_TERMINALS = grammar_factorization(rules_dict)
    shop_machine: dict[Delta, DeltaDisplay] = dict()
    for [uuid, no_terminal], shop_chain in ll1_rules.items():
        print(f"{str(no_terminal.name).ljust(50)} {str(shop_chain[0]).ljust(25)} {shop_chain}")
        terminal = TERMINALS[shop_chain[0].name] if hasattr(shop_chain[0], 'name') else shop_chain[0]
        shop_machine[Delta(terminal, no_terminal)] = DeltaDisplay(InputAction.read, ShopAction.add)
    print(len(ll1_rules), len(shop_machine))


if __name__ == '__main__':
    deterministic_top_down_parsing_builder(raw_rules_dict)
