from typing import Type
from uuid import UUID, uuid4

from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.rules.raw_rules import raw_rules_dict
from syntax_analyzer.lexical import no_terminals

NO_TERMINALS = no_terminals.get_no_terminals()

RAW_RULES_TYPE = dict[tuple[UUID, NO_TERMINALS], list[ALL_LEXICAL | NO_TERMINALS]]
RULES_SET_TYPE = set[tuple[tuple[NO_TERMINALS, UUID, tuple[ALL_LEXICAL | NO_TERMINALS]], ...]]


def find_left_loops(raw_rules: RAW_RULES_TYPE, not_change: RAW_RULES_TYPE) \
        -> tuple[RULES_SET_TYPE, RULES_SET_TYPE, RULES_SET_TYPE]:
    """
    Преобразование правил с первым терминальным символом в правой части
    в цепочки из последовательностей правил,
    заканчивающейся правилом с терминальным первым символом в правой части.
    Разделение этих цепочек на циклические, не циклические
    и те, которые невозможно вычислить, не вычислив циклические цепочки.

    :param raw_rules:
    :param not_change:
    :return:
    """
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
                    # print('************', *target, '************', sep='\n')
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
    # print('^^^^^^^^', len(closed_chains))
    # print(*closed_chains, sep='\n')
    closed_chains: RULES_SET_TYPE = {
        tuple([
            tuple([(tuple(ii) if isinstance(ii, list) else ii) for ii in j])
            for j in i
        ])
        for i in closed_chains
    }
    # print("___________________", *resolve_after_loop, "___________", sep='\n')

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
    # print("___________________", *resolve_after_loop, "___________", sep='\n')

    # print(*closed_chains, sep='\n')
    # print("----")
    # print(*loop_chains, sep='\n')
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
        if isinstance(right_part[0], no_terminals._first_NO_TERMINALS):
            changing[(uuid, key)] = right_part
        else:
            no_changing[(uuid, key)] = right_part

    return changing, no_changing


def transform_no_looping_rules(no_looping_rules: RULES_SET_TYPE) -> RAW_RULES_TYPE:
    """
    Преобразование цепочки из правил, начинающихся с нетерминала
    в правило с терминальным первым символом в правой части.
    :param no_looping_rules:
    :return:
    """
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


def resolved_yourself_recursion(
        yourself_recursion: RAW_RULES_TYPE,
        resolved_rules: RAW_RULES_TYPE,
) -> tuple[RAW_RULES_TYPE, Type[NO_TERMINALS]]:
    """
    Преобразование правил с саморекурсией
    (терминальный символ в левой части равен первому символу в правой части)
    :param yourself_recursion:
    :param resolved_rules:
    :return:
    """
    global NO_TERMINALS
    new_no_terminals = dict()
    new_rules: RAW_RULES_TYPE = dict()
    for [uuid, no_terminal], right_part in yourself_recursion.items():
        new_no_terminals[_new_name := str(no_terminal.name) + '_clone_' + str(uuid4())] = 'cloned from ' + str(
            no_terminal.name) + ' - ' + str(no_terminal.value)
        no_terminals.no_terminals_dict.update(new_no_terminals)
        NO_TERMINALS = no_terminals.get_no_terminals()
        new_rules[(uuid4(), NO_TERMINALS[_new_name])] = right_part[1:]
        new_rules[(uuid4(), NO_TERMINALS[_new_name])] = right_part[1:] + [NO_TERMINALS[_new_name]]
        for [uuid_, no_terminal_], right_part_ in resolved_rules.items():
            if no_terminal == no_terminal_ and right_part_[0] != no_terminal:
                new_rules[(uuid4(), no_terminal)] = right_part_ + [new_no_terminals[_new_name]]

    no_terminals.no_terminals_dict.update(new_no_terminals)
    NO_TERMINALS = no_terminals.get_no_terminals()
    return new_rules, NO_TERMINALS


def transform_left_recursion_rules(
        looped_rules: RULES_SET_TYPE,
        # not_looped_with_no_terminal: RULES_SET_TYPE,
        # no_change: RAW_RULES_TYPE,
        # all_rules: RAW_RULES_TYPE
) -> tuple[RAW_RULES_TYPE, set[tuple[UUID, NO_TERMINALS]]]:
    """
    Преобразование циклических цепочек правил в правила с саморекурсией.
    :param looped_rules:
    :param not_looped_with_no_terminal:
    :param no_change:
    :param all_rules:
    :return:
    """
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
    # current_new_right_parts: list[tuple[NO_TERMINALS, list[ALL_LEXICAL | NO_TERMINALS]]] = new_other_right_parts
    # next_new_right_parts = []
    # while bool(current_new_right_parts):
    #     for [left, new_right_part] in current_new_right_parts:
    #         new_right_part: list[ALL_LEXICAL | NO_TERMINALS]
    #         # TODO: ещё учесть случай, когда мы приходим в саморекурсию
    #         while isinstance(new_right_part[0], no_terminals._first_NO_TERMINALS):
    #             for [uuid, no_terminal], right_part in (all_rules | new_rules).items():
    #                 if new_right_part[0] != no_terminal \
    #                         or (uuid, no_terminal) in old_rules \
    #                         or (no_terminal, uuid, tuple(right_part)) in new_other_right_parts_resolved:
    #                     continue
    #
    #     current_new_right_parts = next_new_right_parts
    #     next_new_right_parts = []

    # print(*new_rules.items(), sep='\n')
    return new_rules, old_rules


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

def grammar_transform(raw_rules):
    global NO_TERMINALS

    middle_rules = raw_rules.copy()
    transform_all_rules = raw_rules.copy()
    will_change, not_change = first_no_terminal_division(middle_rules)
    loop_counter = 0
    while bool(will_change) and loop_counter < 10:
        loop_counter += 1
        print("------------", len(will_change), len(not_change))
        assert len(will_change) + len(not_change) == len(middle_rules), "Ошибка в функции разделения на правила, " \
                                                                        "которые нужно изменять и те, которые не нужно"
        looped, not_looped, resolving_after_loop = find_left_loops(will_change, not_change)
        assert len(looped) + len(not_looped) + len(resolving_after_loop) >= len(will_change), \
            "количество зацикленных цепочек, не зацикленных цепочек и нерешённых цепочек в сумме не должно превышать " \
            "количество цепочек, которое должно быть изменено"

        transformed_not_looped_rules = transform_no_looping_rules(not_looped)
        assert len(not_looped) == len(
            transformed_not_looped_rules), "Количество незацикленных цепочек и преобразованных " \
                                           "незацикленных цепочек должно совпадать"
        # print(*transformed_not_looped_rules.items(), sep='\n')
        # print("===================", len(transformed_not_looped_rules))

        yourself_recursions, remove_rules = transform_left_recursion_rules(looped)
        assert len(looped) == len(yourself_recursions), "количество циклов должно совпадать " \
                                                        "с количеством полученных саморекурсий"
        # print("*******************", len(yourself_recursions))
        # print(*yourself_recursions.items(), sep='\n')
        resolved_yourself_recursions, NO_TERMINALS = resolved_yourself_recursion(
            yourself_recursions, transformed_not_looped_rules | not_change)
        # print("-------------------", len(resolved_yourself_recursions))
        # print(*resolved_yourself_recursions.items(), sep='\n')
        # print("*******************")

        # print(*ff.items(), sep='\n')
        # print("--------------")

        looped_after_resolution, not_looped_after_resolution, resolving_after_loop_after_resolution = find_left_loops(
            _resolving_after_loop := {
                (uuid, no_terminal): list(right_rule_part)
                for rule_path in resolving_after_loop
                for [no_terminal, uuid, right_rule_part] in rule_path
                if right_rule_part is not None and (uuid, no_terminal) not in remove_rules

            },
            {
                key: val
                for key, val in
                (not_change | transformed_not_looped_rules | resolved_yourself_recursions).items()
                if key not in remove_rules
            }
        )
        assert len(looped_after_resolution) == 0, "После второй итерации не должно оставаться зацикленных цепочек," \
                                                  f" а их обнаружено {len(looped_after_resolution)}. " \
                                                  f"Скорее всего какая-то ошибка в формировании грамматики"
        assert len(resolving_after_loop_after_resolution) == 0, "После второй итерации не должно оставаться" \
                                                                " не решённых цепочек," \
                                                                f" а их обнаружено " \
                                                                f"{len(resolving_after_loop_after_resolution)}. " \
                                                                f"Скорее всего какая-то ошибка в формировании грамматики"
        transformed_rules_after_resolve = transform_no_looping_rules(not_looped_after_resolution)
        # print("===================",
        #       len(looped_after_resolution),
        #       len(not_looped_after_resolution),
        #       len(resolving_after_loop_after_resolution),
        #       len(raw_rules_dict))
        # print(*looped_after_resolution, sep="\n")
        # print("--------------")
        # print(*not_looped_after_resolution, sep="\n")
        # print("--------------")
        # print(*resolving_after_loop_after_resolution, sep="\n")
        # print("--------------")
        transform_all_rules = {
            key: val
            for key, val in
            (not_change | transformed_not_looped_rules
             | resolved_yourself_recursions | transformed_rules_after_resolve).items()
            if key not in remove_rules
        }
        middle_rules = transform_all_rules
        will_change, not_change = first_no_terminal_division(middle_rules)

    print("------------", len(will_change), len(not_change))
    print(*will_change.items(), sep='\n')
    print("------------")
    print(*not_change.items(), sep='\n')
    assert loop_counter < 10, "Похоже грамматика зациклилась"

    return transform_all_rules, NO_TERMINALS


if __name__ == '__main__':
    grammar_transform(raw_rules_dict)
