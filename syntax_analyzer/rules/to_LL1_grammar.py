from uuid import UUID, uuid4

from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.lexical.no_terminals import NO_TERMINALS
from syntax_analyzer.rules.raw_rules import raw_rules_dict

RAW_RULES_TYPE = dict[tuple[UUID, NO_TERMINALS], list[ALL_LEXICAL | NO_TERMINALS]]
RULES_SET_TYPE = set[tuple[tuple[NO_TERMINALS, UUID, tuple[ALL_LEXICAL | NO_TERMINALS]], ...]]


def find_left_loops(raw_rules: RAW_RULES_TYPE, not_change: RAW_RULES_TYPE) -> tuple[
    RULES_SET_TYPE, RULES_SET_TYPE, RULES_SET_TYPE]:
    # raw_rules_list: list[tuple[UUID, NO_TERMINALS, list[ALL_LEXICAL | NO_TERMINALS]]] = [
    #     (*key, val) for key, val in raw_rules.items()]
    closed_chains: list = []
    resolve_after_loop: list = []
    used = set()
    for [uuid, trigger_target], trigger_target_right in raw_rules.items():
        # if trigger_target in used:
        #     continue
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
                    print('************', *target, '************', sep='\n')
                    closed_chains.append(target[_ind:])
                    resolve_after_loop.append(target[:])
                    continue
                target_variants = []
                for target_variant, rules in (raw_rules | not_change).items():
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
    closed_chains: RULES_SET_TYPE = {
        tuple([
            tuple([(tuple(ii) if isinstance(ii, list) else ii) for ii in j])
            for j in i
        ])
        for i in closed_chains
    }
    print("___________________", *resolve_after_loop, "___________", sep='\n')

    resolve_after_loop: RULES_SET_TYPE = {
        tuple([
            tuple([(tuple(ii) if isinstance(ii, list) else ii) for ii in j])
            for j in i
        ])
        for i in resolve_after_loop
    }
    loop_chains = {i[:-1] for i in closed_chains if i[0][0] == i[-1][0]}
    no_looping_chains = {i[:] for i in closed_chains if i[0][0] != i[-1][0]}
    resolve_after_loop = {i[:] for i in resolve_after_loop}
    print("___________________", *resolve_after_loop, "___________", sep='\n')

    print(*closed_chains, sep='\n')
    print("----")
    print(*loop_chains, sep='\n')
    return loop_chains, no_looping_chains, resolve_after_loop


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


def transform_no_looping_rules(no_looping_rules: RULES_SET_TYPE) -> RAW_RULES_TYPE:
    new_rules: RAW_RULES_TYPE = dict()
    for old_rules_chain in no_looping_rules:
        left_part = (uuid4(), old_rules_chain[0][0])
        right_part = []
        # print(*old_rules_chain, sep="\n")
        for ind, [no_terminal, old_rule_uuid, old_right_part] in enumerate(old_rules_chain):
            if old_right_part is not None or ind + 1 != len(old_rules_chain):
                right_part = list(old_right_part)[1:] + right_part
        right_part = [old_rules_chain[-1][0]] + right_part
        new_rules[left_part] = right_part
    return new_rules


def resolved_yourself_recursion():
    pass


def transform_left_recursion_rules(
        looped_rules: RULES_SET_TYPE,
        not_looped_with_no_terminal: RULES_SET_TYPE,
        no_change,
        all_rules
):
    new_rules = dict()
    old_rules: set[tuple[UUID, NO_TERMINALS]] = set()
    new_other_right_parts: list[tuple[NO_TERMINALS, list[ALL_LEXICAL | NO_TERMINALS]]] = []
    new_other_right_parts_resolved: dict[
        tuple[NO_TERMINALS, tuple[ALL_LEXICAL | NO_TERMINALS]], tuple[NO_TERMINALS, UUID]] = dict()
    for loop_chain in looped_rules:
        old_rules.add((loop_chain[-1][1], loop_chain[-1][0]))
        # FIXME: Возможно не учитывается сценарий,
        #  когда правила не из петли для нетерминала, запускающего рекурсию
        new_right_part = [*loop_chain[-1][-1][1:]]

        for ind, [rule_key, uuid, right_part] in enumerate(loop_chain[:-1]):
            new_other_right_parts.append((loop_chain[-1][0], list(right_part) + new_right_part[:]))
            new_other_right_parts_resolved[(loop_chain[-1][0], tuple(list(right_part) + new_right_part[:]))] = tuple(
                loop_chain[ind + 1][:2])
            new_right_part = list(right_part[1:]) + new_right_part

        new_right_part = [loop_chain[-1][0]] + new_right_part
        new_rules[(uuid4(), loop_chain[-1][0])] = [loop_chain[-1][0]] + new_right_part
    # TODO: после того, как все левые рекурсии будут пофикшены,
    #  необходимо проверить для каждой подцепочки циклов
    #  наличие альтернативных выходов из цикла
    #  и потом добавить их в new_other_right_parts.
    #  Отдельно стоит рассмотреть сценарий,
    #  когда такая цепочка может "наткнуться" на ещё один цикл.
    #  В этом случае надо дойти по циклу до нового правила и использовать его
    #  (одна цепочка на каждую модификацию правила).
    #  Для каждого цикла надо хранить,
    #  обработали ли мы для него все побочные цепочки или нет.
    #  Если цепочка в процессе спуска натыкается на "ещё не обработанный цикл",
    #  то она должна уйти в очередь ожидания
    current_new_right_parts: list[tuple[NO_TERMINALS, list[ALL_LEXICAL | NO_TERMINALS]]] = new_other_right_parts
    next_new_right_parts = []
    while bool(current_new_right_parts):
        for [left, new_right_part] in current_new_right_parts:
            new_right_part: list[ALL_LEXICAL | NO_TERMINALS]
            # TODO: ещё учесть случай, когда мы приходим в саморекурсию
            while isinstance(new_right_part[0], NO_TERMINALS):
                for [uuid, no_terminal], right_part in (all_rules | new_rules).items():
                    if new_right_part[0] != no_terminal \
                            or (uuid, no_terminal) in old_rules \
                            or (no_terminal, uuid, tuple(right_part)) in new_other_right_parts_resolved:
                        continue

        current_new_right_parts = next_new_right_parts
        next_new_right_parts = []

    print(*new_rules.items(), sep='\n')


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
    will_change, not_change = first_no_terminal_division(all_rules := raw_rules_dict)

    looped, not_looped, resolving_after_loop = find_left_loops(will_change, not_change)
    # transform_left_recursion_rules(looped,not_looped, not_change)
    # looped, not_looped = find_left_loops(all_rules := {
    #     (uuid4(), 10): [11, ('10df')],
    #     (uuid4(), 1): [2, ('12df')],
    #     (uuid4(), 1): [3, ('13df')],
    #     (uuid4(), 2): [4, ('24df')],
    #     (uuid4(), 2): [5, ('25df')],
    #     (uuid4(), 2): [6, ('26df')],
    #     (uuid4(), 3): [6, ('36df')],
    #     (uuid4(), 3): [5, ('35df')],
    #     # 4: [],
    #     (uuid4(), 5): [7, ('57df')],
    #     (uuid4(), 7): [1, ('71df')],
    #     (uuid4(), 6): [8, ('68df')],
    #     (uuid4(), 6): [9, ('69df')],
    #
    #     (uuid4(), 1): [10, ('110df')],
    #     (uuid4(), 1): [13, ('113df')],
    #
    #     (uuid4(), 10): [12, ('1013df')],
    #     (uuid4(), 11): [13, ('1113df')],
    #     (uuid4(), 11): [14, ('1114df')],
    #     (uuid4(), 13): [15, ('1315df')],
    #     (uuid4(), 14): [10, ('1410df')],
    # })
    print("===================", len(not_looped), len(looped), len(resolving_after_loop), len(raw_rules_dict),
          len(will_change), len(not_change))

    new_rules = transform_no_looping_rules(not_looped)

    print(*new_rules.items(), sep='\n')
    print("===================", len(new_rules))
    # transform_left_recursion_rules(looped, not_looped, [], all_rules)
