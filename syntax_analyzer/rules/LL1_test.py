import enum
import inspect
from typing import Type

from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.lexical.terminals import TERMINALS, terminals, OPTIONAL_BLANKS_ENUM
from syntax_analyzer.rules.raw_rules import raw_rules_dict
from syntax_analyzer.rules.to_LL1_grammar import grammar_factorization, RAW_RULES_TYPE, GROUPED_RULES_TYPE
from syntax_analyzer.lexical import no_terminals

NO_TERMINALS = no_terminals.get_no_terminals()

__all__ = ['ll1_test']

ARGS = NO_TERMINALS | ALL_LEXICAL | Type[enum.Enum]


def first_f(
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
            res |= first_f(
                right_part[0],
                rules,
                symbol_buf_first=symbol_buf_first.copy(),
                symbol_buf_second=symbol_buf_second,
                is_calculated_first=is_calculated_first,
                is_calculated_second=is_calculated_second,
            )
    res -= {OPTIONAL_BLANKS_ENUM(None)}
    is_calculated_first[symbol] =  res
    return res


def next_f(
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
                    res |= first_f(
                        char,
                        rules,
                        symbol_buf_first=symbol_buf_first,
                        symbol_buf_second=symbol_buf_second,
                        is_calculated_first=is_calculated_first,
                        is_calculated_second=is_calculated_second,
                    )
                    assert OPTIONAL_BLANKS_ENUM(None) not in res
                elif find is True and char == OPTIONAL_BLANKS_ENUM(None):
                    continue
                if char == symbol:
                    find = True
            if find is True and (no_terminal not in symbol_buf_second ):
                res |= next_f(
                    no_terminal,
                    rules,
                    symbol_buf_first=symbol_buf_first,
                    symbol_buf_second=symbol_buf_second.copy(),
                    is_calculated_first=is_calculated_first,
                    is_calculated_second=is_calculated_second,
                )
    is_calculated_second[symbol] = res
    return res


def ll1_test(raw_rules: RAW_RULES_TYPE):
    global NO_TERMINALS

    testing_rules, NO_TERMINALS = grammar_factorization(raw_rules)
    print(testing_rules)
    print('LL1 test start')
    res_1 = dict()
    for no_terminal, rules in testing_rules.items():
        print(no_terminal)
        res_1[no_terminal] = dict()
        for rule in rules:
            res_1[no_terminal][rule] = first_f(no_terminal, testing_rules | {no_terminal: {rule}})
            print('\t', res_1[no_terminal][rule])

    print("-"*20)
    correct = True
    for no_terminal, first_symbols in res_1.items():
        # print(no_terminal)
        if len(first_symbols) > 1:
            for rule1, item1 in first_symbols.items():
                for rule2, item2 in first_symbols.items():
                    if rule1 == rule2:
                        continue
                    if len(item1 & item2) != 0:
                        correct = False
                        print(no_terminal, f"{item1} & {item2} =  {item1 & item2}")
                        print(no_terminal, f"ПЕРВ({rule1}) & ПЕРВ({rule2}) = {item1 & item2} not empty!")
    assert correct is True, "Грамматика не может быть LL1 по первому правилу"
    print("Грамматика удовлетворяет первому правилу LL1")
    first_f_dict = dict()
    next_f_dict = dict()
    for no_terminal, rules in testing_rules.items():
        first_f_dict[no_terminal] = first_f(
            no_terminal,
            testing_rules,
            # is_calculated_first=first_f_dict,
            # is_calculated_second=next_f_dict,
        )
        next_f_dict[no_terminal] = next_f(
            no_terminal,
            testing_rules,
            # is_calculated_first=first_f_dict,
            # is_calculated_second=next_f_dict,
        )
    correct_2 = 0
    print(first_f_dict.keys())
    print(next_f_dict.keys())
    print(set(first_f_dict.keys()) - set(next_f_dict.keys()))
    print(set(next_f_dict.keys()) - set(first_f_dict.keys()))
    for no_terminal,  rules in testing_rules.items():
        if len(first_f_dict[no_terminal] & next_f_dict[no_terminal]) > 0:
            correct_2 += 1
            print(f"{no_terminal.name}, {no_terminal.value}",
                  f"ПЕРВ({no_terminal}) = {first_f_dict[no_terminal]}",
                  f"СЛЕД({no_terminal}) = {next_f_dict[no_terminal]}",
                  f"ПЕРВ() & СЛЕД() = {first_f_dict[no_terminal] & next_f_dict[no_terminal]}",
                  sep='\n\t')

    assert correct_2 == 0, f"Грамматика не LL1 по второму правилу. Обнаружено {correct_2} конфликтов"
    print("Грамматика удовлетворяет второму правилу LL1")


if __name__ == '__main__':
    ll1_test(raw_rules_dict)