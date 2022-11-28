import enum
import inspect
from typing import Type

from syntax_analyzer.lexical.lexical_analyzer import get_lexical_analyzer
from syntax_analyzer.lexical import no_terminals
from syntax_analyzer.lexical.terminals import TERMINALS, OPTIONAL_BLANKS_ENUM
from syntax_analyzer.parsing.top_down import deterministic_top_down_parsing_builder, States, ShopMarker, InputAction, \
    ShopAction, SHOP_MACHINE_TYPE, Delta, DeltaDisplay
from syntax_analyzer.rules.raw_rules import raw_rules_dict
from syntax_analyzer.rules.to_LL1_grammar import RAW_RULES_TYPE

NO_TERMINALS, get_clone_unique_id = no_terminals.get_no_terminals()


class SyntaxAnalyzer(object):
    def __init__(self, raw_rules: RAW_RULES_TYPE):
        global NO_TERMINALS
        self._grammar: SHOP_MACHINE_TYPE
        self._grammar, NO_TERMINALS, self.ll1_rules = deterministic_top_down_parsing_builder(raw_rules)
        self.grammar_predicates: SHOP_MACHINE_TYPE = dict()  # input_char - всегда  TERMINALS
        self.grammar_predicates_finder:  dict[TERMINALS, dict[TERMINALS| NO_TERMINALS, set[DeltaDisplay]] ]= dict()
        # input_char - всегда  TERMINALS ; shop - всегда Type[enum.Enum]
        self.grammar_predicates_shop_enum: dict[TERMINALS, dict[Type[enum.Enum], set[DeltaDisplay]]] = dict()

        self.grammar_enums: SHOP_MACHINE_TYPE = dict()  # input_char - всегда  Type[enum.Enum]
        # input_char - всегда  Type[enum.Enum] ; shop - всегда TERMINALS | NO_TERMINALS
        self.grammar_enums_finder: dict[Type[enum.Enum], dict[TERMINALS | NO_TERMINALS, set[DeltaDisplay]]] = dict()
        # input_char - всегда  Type[enum.Enum] ; shop - всегда Type[enum.Enum]
        self.grammar_enums_finder_shop_enum: dict[Type[enum.Enum], dict[Type[enum.Enum], set[DeltaDisplay]]] = dict()

        for key, val in self._grammar.items():
            if inspect.isclass(key.input_char):
                self.grammar_enums[key] = val
                if inspect.isclass(key.shop):
                    self.grammar_enums_finder_shop_enum[key.input_char] = w_dict = \
                        self.grammar_enums_finder_shop_enum.get(key.input_char, dict())
                    self.grammar_enums_finder_shop_enum[key.input_char][key.shop] = w_dict.get(key.shop, set()) | {val}
                else:
                    self.grammar_enums_finder[key.input_char] = w_dict = \
                        self.grammar_enums_finder.get(key.input_char, dict())
                    self.grammar_enums_finder[key.input_char][key.shop] = w_dict.get(key.shop, set()) | {val}

                    # self.grammar_enums_finder_shop_enum[key.input_char] = w_dict = \
                    #     self.grammar_enums_finder_shop_enum.get(key.input_char, dict())
                    # self.grammar_enums_finder_shop_enum[key.input_char][key.shop.__class__] = w_dict.get(key.shop.__class__, set()) | {val}
            else:
                self.grammar_predicates[key] = val
                if inspect.isclass(key.shop):
                    self.grammar_predicates_shop_enum[key.input_char] = w_dict = \
                        self.grammar_predicates_shop_enum.get(key.input_char, dict())
                    self.grammar_predicates_shop_enum[key.input_char][key.shop] = w_dict.get(key.shop, set()) | {val}
                else:
                    # print(key)
                    self.grammar_predicates_finder[key.input_char] = w_dict = \
                        self.grammar_predicates_finder.get(key.input_char, dict())
                    self.grammar_predicates_finder[key.input_char][key.shop] = w_dict.get(key.shop, set()) | {val}

    def analyze(self, text: str):
        global NO_TERMINALS
        current: Delta
        shop: list = [ShopMarker.shopHO, NO_TERMINALS['tM']]
        next_state: DeltaDisplay = DeltaDisplay(
            InputAction.empty,
            ShopAction.pass_,
            [ShopMarker.shopHO, NO_TERMINALS['tM']],
            States.start
        )
        current: Delta
        for lexeme in get_lexical_analyzer(text):
            lexeme: TERMINALS
            next_state = DeltaDisplay(
                InputAction.empty,
                next_state.shop_action,
                next_state.shop_chain,
                next_state.state
            )
            # next_state.input_action = InputAction.empty
            print("\n" + f"{[str(lexeme)]}", end=': - ')
            # print("%%--", next_state)
            while next_state.input_action != InputAction.read:
                if shop[-1] == OPTIONAL_BLANKS_ENUM(None):
                    shop.pop(-1)
                current, next_state = self.get_next_state(lexeme, shop[-1], next_state.state)
                print(current.shop, end=', ')
                # print(current)
                # print(next_state)
                # print(shop)
                assert next_state is not None
                _del = shop.pop(-1)
                if next_state.shop_action == ShopAction.add:
                    shop.extend(next_state.shop_chain)
                    if  OPTIONAL_BLANKS_ENUM(None) in shop:
                        print()
                        raise ValueError()
                # print("%%--", next_state)

    def terminal_eq(self, tested: TERMINALS, terminal_value: TERMINALS | Type[enum.Enum]):
        if isinstance(tested, TERMINALS) is False:
            tested = TERMINALS[tested]
        if inspect.isclass(terminal_value):
            return tested == terminal_value
        terminal_value: Type[enum.Enum]
        return any(i == tested for i in terminal_value)

    def get_next_state(
            self,
            input_char: TERMINALS,
            shop_symbol: NO_TERMINALS | TERMINALS | Type[enum.Enum],
            current_state: States
    ) -> tuple[Delta, DeltaDisplay]:
        current: Delta
        next_state: DeltaDisplay | None
        if next_state := self.grammar_predicates.get(current := Delta(input_char, shop_symbol, current_state)):
            return current, next_state
        elif inspect.isclass(shop_symbol) \
                and (w_dict := self.grammar_predicates_shop_enum.get(input_char)) is not None \
                and (possible_v := w_dict.get(shop_symbol)) is not None:

            test_res = [i for i in possible_v if i.state == current_state]
            if len(test_res) != 1:
                raise SyntaxError("Ошибка недетерминированности")

            return current, test_res[0]

        elif inspect.isclass(input_char) is False and inspect.isclass(shop_symbol):
            # в правилах указаны только конкретные случаи для магазина, однако в магазине находится множество
            # possible = self.grammar_predicates[input_char]
            for key, values in self.grammar_predicates_finder[input_char].items():
                if isinstance(key, shop_symbol):
                    test_res = [i for i in values if i.state == current_state]
                    if len(test_res) != 1:
                        raise SyntaxError("Ошибка недетерминированности")
                    return current, test_res[0]

        enums = {i.input_char for i in self.grammar_enums.keys()}
        for tested_enum in enums:
            if any(i == input_char for i in tested_enum):
                input_char_type: Type[enum.Enum] = tested_enum

                break
        else:
            if inspect.isclass(input_char):
                input_char_type: Type[enum.Enum] = input_char
            else:
                raise ValueError()
        # if (possible_v := self.grammar_enums_finder.get(input_char)) is not None:
        #     pass
        # else:
        #     possible_v = self.grammar_enums_finder_shop_enum.get(input_char)
        #     assert possible_v is not None
        if inspect.isclass(shop_symbol):
            variants = self.grammar_enums_finder_shop_enum[input_char_type][shop_symbol]
        else:
            if (variants := self.grammar_enums_finder.get(input_char_type, dict()).get(shop_symbol)) is not None:
                pass
            else:
                for shop_enum in set(self.grammar_enums_finder_shop_enum.get(input_char_type, dict()).keys()):
                    if any(i == shop_symbol for i in shop_enum):
                        variants = shop_enum
                        break
                else:
                    print()
                    raise ValueError()
        test_res = [i for i in variants if i.state == current_state]
        if len(test_res) != 1:
            raise SyntaxError("Ошибка недетерминированности")
        return current, test_res[0]



if __name__ == '__main__':
    syntax_analyzer = SyntaxAnalyzer(raw_rules_dict)
    with open("program.txt", "r", encoding='utf-8') as f:
        data = f.read()
    syntax_analyzer.analyze(data)
