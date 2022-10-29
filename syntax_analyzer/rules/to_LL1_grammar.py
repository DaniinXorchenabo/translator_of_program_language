from uuid import UUID, uuid4

from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.lexical.no_terminals import NO_TERMINALS
from syntax_analyzer.rules.raw_rules import raw_rules_dict

RAW_RULES_TYPE = dict[tuple[UUID, NO_TERMINALS], list[ALL_LEXICAL | NO_TERMINALS]]


def sort_no_terminal_rules(raw_rules: RAW_RULES_TYPE) -> RAW_RULES_TYPE:
    # raw_rules_list: list[tuple[UUID, NO_TERMINALS, list[ALL_LEXICAL | NO_TERMINALS]]] = [
    #     (*key, val) for key, val in raw_rules.items()]
    closed_chains = []
    used = set()
    for [uuid, trigger_target], trigger_target_right in raw_rules.items():
        if trigger_target in used:
            continue
        used.add(trigger_target)
        current_targets = [[[trigger_target, uuid, trigger_target_right]]]
        next_targets = []

        while bool(current_targets):
            for target in current_targets:
                used.add(target[-1][0])
                if target[-1][0] == trigger_target and len(target) > 1:
                    closed_chains.append(target)
                    continue
                elif any(i[0] == target[-1][0] for ind, i in enumerate(target[:-1]) if (_ind := ind)):
                    closed_chains.append(target[_ind:])
                    continue
                target_variants = []
                for target_variant, rules in raw_rules.items():
                    if target_variant[1] == target[-1][0]:
                        target_variants.append([rules[0], target_variant[0], rules])
                if bool(target_variants):
                    for i in target_variants:
                        next_target = [i[:] for i in target]
                        next_target[-1][1] = i[1]
                        next_target[-1][2] = i[2]
                        i[1] = None
                        i[2] = None
                        next_targets.append(next_target + [i])
                else:
                    # добавляем символ завершения к текущей цепочке
                    closed_chains.append(target)

            current_targets = next_targets
            next_targets = []
    closed_chains = {
        tuple([
            tuple([(tuple(ii) if isinstance(ii, list) else ii ) for ii in j])
            for j in i
        ])
        for i in closed_chains
    }
    loop_chains = [i for i in closed_chains if i[0][0] == i[-1][0]]
    print(*closed_chains, sep='\n')
    print("----")
    print(*loop_chains, sep='\n')


def first_no_terminal_division(raw_rules: RAW_RULES_TYPE) -> tuple[RAW_RULES_TYPE, RAW_RULES_TYPE]:
    """
    Разделяет правила на те, которые надо преобразовывать
    (с нетерминальным первым символом в правой части правила),
    и те, которые не надо (с терминальным первым символом в правой части правила).
    :param raw_rules:
    :return:
    """

    no_changing: RAW_RULES_TYPE = dict()
    changing: RAW_RULES_TYPE = dict()
    for [uuid, key], right_part in raw_rules.items():
        if isinstance(right_part[0], NO_TERMINALS):
            changing[(uuid, key)] = right_part
        else:
            no_changing[(uuid, key)] = right_part

    return changing, no_changing


# def sort_no_terminal_rules(raw_rules: dict[tuple[UUID, int], list[int]]) -> RAW_RULES_TYPE:
#     closed_chains = []
#     used = set()
#     for [uuid, trigger_target] in raw_rules:
#         if trigger_target in used:
#             continue
#         used.add(trigger_target)
#         current_targets = [[trigger_target]]
#         next_targets = []
#
#         while bool(current_targets):
#             for target in current_targets:
#                 used.add(target[-1])
#                 if target[-1] == trigger_target and len(target) > 1:
#                     target.append(-1)
#                     closed_chains.append(target)
#                     continue
#                 elif target[-1] in target[:-1]:
#                     closed_chains.append(target[target.index(target[-1]):] + [-1])
#                     continue
#                 target_variants = []
#                 for target_variant, rules in raw_rules.items():
#                     if target_variant[1] == target[-1]:
#                         target_variants.append(rules[0])
#                 if bool(target_variants):
#                     next_targets += [target + [i] for i in target_variants]
#                 else:
#                     # добавляем символ завершения к текущей цепочке
#                     target += [-1]
#                     closed_chains.append(target)
#
#             current_targets = next_targets
#             next_targets = []
#
#     print(*closed_chains, sep='\n')

if __name__ == '__main__':
    will_change, not_change = first_no_terminal_division(raw_rules_dict)
    sort_no_terminal_rules(will_change)

    # sort_no_terminal_rules({
    #     (uuid4(), 10): [11, *list('10df')],
    #     (uuid4(), 1): [2, *list('12df')],
    #     (uuid4(), 1): [3, *list('13df')],
    #     (uuid4(), 2): [4, *list('24df')],
    #     (uuid4(), 2): [5, *list('25df')],
    #     (uuid4(), 2): [6, *list('26df')],
    #     (uuid4(), 3): [6, *list('36df')],
    #     (uuid4(), 3): [5, *list('35df')],
    #     # 4: [],
    #     (uuid4(), 5): [7, *list('57df')],
    #     (uuid4(), 7): [1, *list('71df')],
    #     (uuid4(), 6): [8, *list('68df')],
    #     (uuid4(), 6): [9, *list('69df')],
    #
    #     (uuid4(), 1): [10, *list('110df')],
    #     (uuid4(), 1): [13, *list('113df')],
    #
    #     (uuid4(), 10): [12, *list('1013df')],
    #     (uuid4(), 11): [13, *list('1113df')],
    #     (uuid4(), 11): [14, *list('1114df')],
    #     (uuid4(), 13): [15, *list('1315df')],
    #     (uuid4(), 14): [10, *list('1410df')],
    # })
