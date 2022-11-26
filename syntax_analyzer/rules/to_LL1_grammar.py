from __future__ import annotations

import enum
import inspect
from typing import Type
from uuid import UUID, uuid4

from syntax_analyzer.lexical.all_lexems import ALL_LEXICAL
from syntax_analyzer.lexical.terminals import OPTIONAL_BLANKS_ENUM, TERMINALS, terminals
from syntax_analyzer.rules.raw_rules import raw_rules_dict, recourse_optional_gen, START_STATES
from syntax_analyzer.lexical import no_terminals

NO_TERMINALS, get_clone_unique_id = no_terminals.get_no_terminals()

RAW_RULES_TYPE = dict[tuple[UUID, NO_TERMINALS], list[ALL_LEXICAL | NO_TERMINALS]]
RULES_SET_TYPE = set[tuple[tuple[NO_TERMINALS, UUID, tuple[ALL_LEXICAL | NO_TERMINALS]], ...]]
GROUP_TREE_TYPE = dict[NO_TERMINALS, set[tuple[ALL_LEXICAL | NO_TERMINALS, ...]]]
GROUP_TREE_TYPE = dict[NO_TERMINALS, GROUP_TREE_TYPE | set[tuple[ALL_LEXICAL | NO_TERMINALS]]]
GROUPED_RULES_TYPE = dict[NO_TERMINALS, set[tuple[NO_TERMINALS | ALL_LEXICAL | OPTIONAL_BLANKS_ENUM, ...]]]


def find_left_loops(raw_rules: RAW_RULES_TYPE, not_change: RAW_RULES_TYPE, StartStates: set[NO_TERMINALS]) \
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

    for [uuid, trigger_target], trigger_target_right in {
        key: val for key, val in raw_rules.items() if key[1] in StartStates
    }.items():
        # if trigger_target in used:
        #     continue

        #
        used.add(trigger_target)
        current_targets: list[list[tuple[NO_TERMINALS, UUID, list[ALL_LEXICAL | NO_TERMINALS]]]] \
            = [[(trigger_target, uuid, trigger_target_right)]]
        next_targets: list[list[tuple[NO_TERMINALS, UUID, list[ALL_LEXICAL | NO_TERMINALS]]]] = []
        # Происходит поиск в ширину по графу
        while bool(current_targets):
            for target in current_targets:
                used.add(target[-1][0])
                if target[-1][0] == trigger_target and len(target) > 1:
                    # Если цепочка начинается и заканчивается одним и тем же нетерминалом
                    # ? то считаем, что мы дошли до конца этой цепочки.
                    # Это цикл
                    target[-1] = target[-1][0], None, None
                    closed_chains.append(target)
                    continue
                elif any(i[0] == target[-1][0] for ind, i in enumerate(target[:-1]) if (_ind := ind)):
                    # Если один и тот же нетерминал встречается в одной последовательности,
                    # То эта цепочка содержит цикл и должна будет решена после решения всех циклов.
                    target[-1] = target[-1][0], None, None
                    closed_chains.append(target[_ind:])
                    resolve_after_loop.append(target[:])
                    continue
                else:
                    # смотрим, имеет ли цепочка продолжение
                    target_variants: list[
                        list[tuple[ALL_LEXICAL | NO_TERMINALS, UUID, list[ALL_LEXICAL | NO_TERMINALS]]]] = []
                    for target_variant, rules in (raw_rules | not_change).items():
                        if target_variant[1] == target[-1][0]:
                            next_target = [i[:] for i in target]
                            next_target[-1] = next_target[-1][0], target_variant[0], rules[:]
                            # next_target[-1][2] = i[2]

                            target_variants.append(next_target + [(
                                rules[0],  # Переходим к следующему элементу в дереве графа
                                target_variant[0],
                                # Это неправильные данные, их необходимо заменить (Это произойдёт на следёющей итерации цикла, когда только что созданный next_target станат target и когда для него выполнится  target_variant[1] == target[-1][0])
                                rules[:]  # Это неправильные данные, их необходимо заменить
                            )])
                    if bool(target_variants):
                        for i in target_variants:
                            next_targets.append(i)

                    else:
                        # добавляем символ завершения к текущей цепочке
                        # TODO: проверить правильность этой строки
                        next_target = [i[:] for i in target]
                        # Исправляем некорректные данные, которые были записаны при добавлении.
                        next_target[-1] = next_target[-1][0], None, None
                        # next_targets.append(next_target)
                        closed_chains.append(next_target)

            current_targets = next_targets
            next_targets = []

    # print('^^^^^^^^', len(closed_chains))
    # print(*closed_chains, sep='\n')
    # Делим цепочки по типу завершения: loops завершаются циклом (первый терминал равен последнему),
    # а no_loops заканчивается терминалом, либо перечислением терминалов
    loops = []
    no_loops = []
    for chain in closed_chains:
        if len(chain) != 1 and chain[0][0] == chain[-1][0]:
            chain = tuple(((i[0], i[1], tuple(i[2])) if i[2] is not None else i) for i in chain)
            loops.append(chain)
        else:
            chain = tuple(((i[0], i[1], tuple(i[2])) if i[2] is not None else i) for i in chain)
            no_loops.append(chain)
    loops = set(loops)
    print()
    # closed_chains: RULES_SET_TYPE = {
    #     tuple([
    #         tuple([(tuple(ii) if isinstance(ii, list) else ii) for ii in j])
    #         for j in i
    #     ])
    #     for i in closed_chains
    # }
    # # print("___________________", *resolve_after_loop, "___________", sep='\n')
    #
    # resolve_after_loop: RULES_SET_TYPE = {
    #     tuple([
    #         tuple([(tuple(ii) if isinstance(ii, list) else ii) for ii in j])
    #         for j in i
    #     ])
    #     for i in resolve_after_loop
    # }
    # loop_chains = {i[:-1] for i in closed_chains if i[0][0] == i[-1][0]}
    # no_looping_chains = {i[:] for i in closed_chains if i[0][0] != i[-1][0]}
    # resolve_after_loop: set = {i[:] for i in resolve_after_loop}
    # print("___________________", *resolve_after_loop, "___________", sep='\n')

    # print(*closed_chains, sep='\n')
    # print("----")
    # print(*loop_chains, sep='\n')
    return loops, no_loops, resolve_after_loop


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
    global get_clone_unique_id, NO_TERMINALS
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
    old_rules: set[tuple[UUID, NO_TERMINALS]] = set()

    no_term_to_name: dict[tuple[UUID, NO_TERMINALS], str] = dict()

    for [uuid, no_terminal], right_part in yourself_recursion.items():
        _new_name = str(no_terminal.name) + '_rec_clone_' + get_clone_unique_id()
        _new_val = 'cloned from ' + str(no_terminal.name) + ' - ' + str(no_terminal.value)
        new_no_terminals[_new_name] = _new_val
        no_term_to_name[(uuid, no_terminal)] = _new_name

    no_terminals.no_terminals_dict.update(new_no_terminals)
    NO_TERMINALS, get_clone_unique_id = no_terminals.get_no_terminals()

    for [uuid, no_terminal], right_part in yourself_recursion.items():
        _new_name = no_term_to_name[(uuid, no_terminal)]

        # new_rules[(uuid4(), NO_TERMINALS[_new_name])] = right_part[1:]
        new_rules[(uuid4(), NO_TERMINALS[_new_name])] =(OPTIONAL_BLANKS_ENUM(None),)
        new_rules[(uuid4(), NO_TERMINALS[_new_name])] = list(right_part[1:]) + [NO_TERMINALS[_new_name]]
        for [uuid_, no_terminal_], right_part_ in resolved_rules.items():
            if no_terminal == no_terminal_ and right_part_[0] != no_terminal:
                new_rules[(uuid4(), no_terminal)] = right_part_ + [NO_TERMINALS[_new_name]]
                old_rules.add((uuid_, no_terminal_))
            elif no_terminal == no_terminal_ and right_part_[0] == no_terminal:
                old_rules.add((uuid_, no_terminal_))
                # new_rules[(uuid_, no_terminal)] = right_part_

    return new_rules, old_rules, NO_TERMINALS


def transform_left_recursion_rules(
        looped_rules: set[tuple[tuple[NO_TERMINALS, UUID, tuple[NO_TERMINALS | ALL_LEXICAL, ...]], ...]],
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
    self_recursion = dict()
    new_other_right_parts: list[tuple[NO_TERMINALS, list[ALL_LEXICAL | NO_TERMINALS]]] = []
    new_other_right_parts_resolved: dict[
        tuple[NO_TERMINALS, tuple[ALL_LEXICAL | NO_TERMINALS]], tuple[NO_TERMINALS, UUID]] = dict()
    for loop_chain in looped_rules:
        if len(loop_chain) > 2:
            old_rules.add((loop_chain[-2][1], loop_chain[-2][0]))
            # FIXME: Возможно не учитывается сценарий,
            #  когда правила не из петли для нетерминала, запускающего рекурсию
            new_right_part = [loop_chain[-2][2][0]] \
                             + [ii for i in reversed([i[2][1:] for i in loop_chain[:-2]]) for ii in i] \
                             + list(loop_chain[-2][2][1:])

            # for ind, [rule_key, uuid, right_part] in enumerate(loop_chain[:-1]):
            #     new_other_right_parts.append((loop_chain[-1][0], list(right_part) + new_right_part[:]))
            #     new_other_right_parts_resolved[(loop_chain[-1][0], tuple(list(right_part) + new_right_part[:]))] = tuple(
            #         loop_chain[ind + 1][:2])
            #     new_right_part = list(right_part[1:]) + new_right_part
            #
            # new_right_part = [loop_chain[-1][0]] + new_right_part
            # new_rules[(uuid4(), loop_chain[-1][0])] = [loop_chain[-1][0]] + new_right_part
            new_rules[(uuid4(), loop_chain[-1][0])] = new_right_part
        elif len(loop_chain) == 2:
            # Саморекурсия
            self_recursion[(loop_chain[0][1], loop_chain[0][0])] = loop_chain[0][2]
        else:
            raise ValueError("Такого быть не должно, так как даже саморекурсия имеет две составляющих")
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
    return new_rules, old_rules, self_recursion


def grammar_transform(raw_rules: RAW_RULES_TYPE) -> tuple[RAW_RULES_TYPE, Type[NO_TERMINALS]]:
    """
    Построение LL1-грамматики из контекстно-свободной грамматики без правил с пустыми цепочками.
    Для большей информации по разрешению рекурсий смотреть: https://lektsii.org/15-77737.html
    :param raw_rules:
    :return:
    """
    global NO_TERMINALS

    middle_rules = raw_rules.copy()
    transform_all_rules = raw_rules.copy()
    will_change, not_change = first_no_terminal_division(middle_rules)
    loop_counter = 0
    while bool(will_change) and loop_counter < 10:
        # print(middle_rules)
        loop_counter += 1
        print("------------", len(will_change), len(not_change))
        assert len(will_change) + len(not_change) == len(middle_rules), "Ошибка в функции разделения на правила, " \
                                                                        "которые нужно изменять и те, которые не нужно"
        looped, not_looped, resolving_after_loop = find_left_loops(will_change, not_change, START_STATES)
        # assert len(looped) + len(not_looped) + len(resolving_after_loop) >= len(will_change), \
        #     "количество зацикленных цепочек, не зацикленных цепочек и нерешённых цепочек в сумме не должно превышать " \
        #     "количество цепочек, которое должно быть изменено"

        # transformed_not_looped_rules = transform_no_looping_rules(not_looped)
        # assert len(not_looped) == len(
        #     transformed_not_looped_rules), "Количество незацикленных цепочек и преобразованных " \
        #                                    "незацикленных цепочек должно совпадать"
        # print(*transformed_not_looped_rules.items(), sep='\n')
        # print("===================", len(transformed_not_looped_rules))

        new_yourself_recursions, remove_rules, old_yourself_recursions = transform_left_recursion_rules(looped)
        new_factorization_recursion_rules: GROUPED_RULES_TYPE
        new_factorization_recursion_rules, NO_TERMINALS = grammar_factorization(
            new_yourself_recursions | old_yourself_recursions)

        remove_rules |= set(new_yourself_recursions) | set(old_yourself_recursions)
        new_factorization_rules: RAW_RULES_TYPE = dict()
        new_self_recursion_rules: RAW_RULES_TYPE = dict()
        for no_terminal, rules_set in new_factorization_recursion_rules.items():
            for rule in rules_set:
                if rule[0] == no_terminal:
                    new_self_recursion_rules[(uuid4(), no_terminal)] = rule
                else:
                    new_factorization_rules[(uuid4(), no_terminal)] = rule

        print()
        # assert len(looped) == len(yourself_recursions), "количество циклов должно совпадать " \
        #                                                 "с количеством полученных саморекурсий"
        # print("*******************", len(yourself_recursions))
        # print(*yourself_recursions.items(), sep='\n')

        # TODO: По-хорошему, перед решением саморекурсии
        #  (т.е. перед созданием новых нетерминалов)
        #  необходимо произвести факторизацию грамматики
        middle_rules = {key: val for key, val in (middle_rules | new_factorization_rules).items() if
                        key not in remove_rules}
        resolved_yourself_recursions, old_recursion_rules, NO_TERMINALS = resolved_yourself_recursion(new_self_recursion_rules, middle_rules)

        remove_rules |= old_recursion_rules

        middle_rules = middle_rules | {
            (_good_uuid, no_term): rule
            for [uuid, no_term], rule in resolved_yourself_recursions.items()
            if any(
                no_term == old_no_term and tuple(rule) == tuple(old_rule)
                for [good_uuid, old_no_term], old_rule in middle_rules.items()
                if (_good_uuid := good_uuid)

            ) or (_good_uuid := uuid)
        }
        remove_rules |= set(new_self_recursion_rules)
        middle_rules = {key: val for key, val in middle_rules.items() if key not in remove_rules}

        # print("-------------------", len(resolved_yourself_recursions))
        # print(*resolved_yourself_recursions.items(), sep='\n')
        # print("*******************")

        # print(*ff.items(), sep='\n')
        # print("--------------")

        # looped_after_resolution, not_looped_after_resolution, resolving_after_loop_after_resolution = find_left_loops(
        #     _resolving_after_loop := {
        #         (uuid, no_terminal): list(right_rule_part)
        #         for rule_path in resolving_after_loop
        #         for [no_terminal, uuid, right_rule_part] in rule_path
        #         if right_rule_part is not None and (uuid, no_terminal) not in remove_rules
        #
        #     },
        #     {
        #         key: val
        #         for key, val in
        #         (not_change | transformed_not_looped_rules | resolved_yourself_recursions).items()
        #         if key not in remove_rules
        #     }
        # )
        # assert len(looped_after_resolution) == 0, "После второй итерации не должно оставаться зацикленных цепочек," \
        #                                           f" а их обнаружено {len(looped_after_resolution)}. " \
        #                                           f"Скорее всего какая-то ошибка в формировании грамматики"
        # assert len(resolving_after_loop_after_resolution) == 0, "После второй итерации не должно оставаться" \
        #                                                         " не решённых цепочек," \
        #                                                         f" а их обнаружено " \
        #                                                         f"{len(resolving_after_loop_after_resolution)}. " \
        #                                                         f"Скорее всего какая-то ошибка в формировании грамматики"
        # transformed_rules_after_resolve = transform_no_looping_rules(not_looped_after_resolution)
        # # print("===================",
        # #       len(looped_after_resolution),
        # #       len(not_looped_after_resolution),
        # #       len(resolving_after_loop_after_resolution),
        # #       len(raw_rules_dict))
        # # print(*looped_after_resolution, sep="\n")
        # # print("--------------")
        # # print(*not_looped_after_resolution, sep="\n")
        # # print("--------------")
        # # print(*resolving_after_loop_after_resolution, sep="\n")
        # # print("--------------")
        # transform_all_rules = {
        #     key: val
        #     for key, val in
        #     (not_change | transformed_not_looped_rules
        #      | resolved_yourself_recursions | transformed_rules_after_resolve).items()
        #     if key not in remove_rules
        # }
        # middle_rules = transform_all_rules
        will_change, not_change = first_no_terminal_division(middle_rules)
        # looped, not_looped, resolving_after_loop = find_left_loops(will_change, not_change, START_STATES)
        print("------------", len(will_change), len(not_change), len(middle_rules))
        # print(*will_change.items(), sep='\n')
        # print("------------")
        # print(*not_change.items(), sep='\n')
        assert loop_counter < 10, "Похоже грамматика зациклилась"
        if len(looped) == 0 and len(resolving_after_loop) == 0:
            break


    factorized_rules, NO_TERMINALS = grammar_factorization(middle_rules)

    new_factorized_rules = {
        NO_TERMINALS[key.name]: {
            tuple(
                (NO_TERMINALS[lexeme.name] if isinstance(lexeme, no_terminals._first_NO_TERMINALS) else lexeme)
                for lexeme in rule
            )
            for rule in val}
                            for key, val in factorized_rules.items()
    }
    assert len(new_factorized_rules) == len(factorized_rules)
    factorized_rules = new_factorized_rules

    return factorized_rules, NO_TERMINALS


def group_factorization(
        key: NO_TERMINALS,
        grouped_rules: set[tuple[ALL_LEXICAL | NO_TERMINALS, ...]],
        global_new_rules: GROUP_TREE_TYPE | None = None,
        old_rules: GROUP_TREE_TYPE | None = None,
        _deep: int = 0
) -> tuple[GROUP_TREE_TYPE, GROUP_TREE_TYPE, Type[NO_TERMINALS]]:
    global NO_TERMINALS, get_clone_unique_id

    if bool(grouped_rules) is False:
        return global_new_rules, old_rules, NO_TERMINALS

    global_new_rules: GROUP_TREE_TYPE = global_new_rules or dict()
    old_rules: GROUP_TREE_TYPE = old_rules or dict()

    local_new_rules = dict()

    new_dict: dict[tuple[ALL_LEXICAL | NO_TERMINALS], set[tuple[ALL_LEXICAL | NO_TERMINALS, ...]]] = dict()
    last_new_dict = dict()
    ind = 0
    break_flag = False
    while len(new_dict) < 2 and break_flag is False:
        assert len(grouped_rules) > 1, "Такие правила должны отсекаться на более раннем этапе: " \
                                       f"{key}, {grouped_rules}"
        last_new_dict = new_dict
        ind += 1
        new_dict = dict()
        for rule in grouped_rules:
            # print(rule)
            new_left_part = rule[:ind]
            raw_remains = rule[ind:]
            if bool(raw_remains):
                # assert len(rule[ind:]) > 0, "Отдельно рассмотреть этот случай"
                new_dict[new_left_part] = new_dict.get(new_left_part, set()) | {tuple(raw_remains)}
            else:
                break_flag = True
                new_dict[new_left_part] = new_dict.get(new_left_part, set()) | {(OPTIONAL_BLANKS_ENUM(None),)}
    if len(last_new_dict) == 1 and len(new_dict) > 1:
        new_dict = last_new_dict

    new_dict_with_raw_rules = dict()
    new_dict_with_hot_rules = dict()
    for new_dict_key, val in new_dict.items():
        if len(val) > 1:
            new_dict_with_raw_rules[new_dict_key] = val
        else:
            new_dict_with_hot_rules[new_dict_key] = val
    # print("+" * 10 + str(key), *[f"{len(k)} {k}    {v}" for k, v in new_dict.items()], "=" * 10, sep='\n')

    for problem_trigger, val in new_dict_with_hot_rules.items():
        local_new_rules[key] = local_new_rules.get(key, set()) | {tuple([*list(problem_trigger), *(list(val)[0])])}

    new_no_terminals = dict()
    nt_to_names = dict()
    for problem_trigger, val in new_dict_with_raw_rules.items():
        _new_name = f'{key.name}_clone_{get_clone_unique_id()}'
        nt_to_names[_new_name] = problem_trigger
        new_no_terminals[_new_name] = f'cloned from {key.name} - {key.value} ' \
                                      f'resolve the ||{"".join([str(i or i.name) for i in problem_trigger])}|| trigger'

    no_terminals.no_terminals_dict.update(new_no_terminals)
    NO_TERMINALS, get_clone_unique_id = no_terminals.get_no_terminals()

    for trigger_name, problem_trigger in nt_to_names.items():
        val = new_dict_with_raw_rules[problem_trigger]  # - {(OPTIONAL_BLANKS_ENUM(None),)}
        # val = new_dict[problem_trigger]
        no_terminal = NO_TERMINALS[trigger_name]
        local_new_rules[key] = local_new_rules.get(key, set()) | {tuple([*list(problem_trigger), no_terminal])}
        if len(val) == 1:
            local_new_rules[no_terminal] = local_new_rules.get(no_terminal, set()) | val
        elif len(val) > 1:
            unary_val = []
            plural_vals = []
            first_lexeme = [i[0] for i in val]
            for i in set(first_lexeme):
                if first_lexeme.count(i) == 1:
                    unary_val += [lexemes for lexemes in val if lexemes[0] == i]
                else:
                    plural_vals.append([lexemes for lexemes in val if lexemes[0] == i])
            local_new_rules[no_terminal] = local_new_rules.get(no_terminal, set()) | set(unary_val)
            for plural_val in plural_vals:
                res_new_rules, old_rules, NO_TERMINALS = group_factorization(
                    no_terminal,
                    set(plural_val),
                    global_new_rules=global_new_rules,
                    old_rules=old_rules,
                    _deep=_deep + 1
                )
                local_new_rules = res_new_rules | {key: val | res_new_rules.get(key, set()) for key, val in
                                                   local_new_rules.items()}
        else:
            local_new_rules[no_terminal] = local_new_rules.get(no_terminal, set()) | {(OPTIONAL_BLANKS_ENUM(None),)}
            print(key, trigger_name, problem_trigger, val, no_terminal)

            # raise ValueError("Подумать, что делать, если оно пустое")

    global_new_rules = local_new_rules | {key: val | local_new_rules.get(key, set()) for key, val in
                                          global_new_rules.items()}
    return global_new_rules, old_rules, NO_TERMINALS


def dict_chain(rules: GROUP_TREE_TYPE, aggregate_dict=None, _deep=0) -> GROUPED_RULES_TYPE:
    aggregate_dict: GROUPED_RULES_TYPE = aggregate_dict or dict()
    for key, val in rules.items():
        if isinstance(val, dict):
            aggregate_dict |= dict_chain(val, aggregate_dict=aggregate_dict, _deep=_deep + 1)
        else:
            val: set
            print(key, val)
            aggregate_dict[key] = aggregate_dict.get(key, set()) | val
    return aggregate_dict


def grammar_factorization(raw_rules: RAW_RULES_TYPE) -> tuple[GROUPED_RULES_TYPE, Type[NO_TERMINALS]]:
    """
    После того, как решены все рекурсии, грамматику надо факторизировать
    (делать так, чтобы для каждого нетерминала в левой части правила первый правый терминал был уникален)
    Этот процесс может провалиться, уйдя в бесконечную рекурсию.

    :param raw_rules:
    :return:
    """
    global NO_TERMINALS

    # middle_rules, NO_TERMINALS = grammar_transform(raw_rules)
    # print(middle_rules)

    middle_rules = {(uuid4(), no_terminal): {
        tuple(right_part) for right_part in recourse_optional_gen(*val)
    }
        for (_, no_terminal), val in raw_rules.items()}
    # print("^"*20 + ' ' + str(len(middle_rules)), *[f"{type(v)} {k}\t\t {v}" for (_, k), v in middle_rules.items()], "^"*20, sep='\n')
    # print('---------------------------------------------')
    grouped_rules: GROUP_TREE_TYPE = dict()
    for [uuid, no_terminal], right_rule_pat in middle_rules.items():
        grouped_rules[no_terminal] = grouped_rules.get(no_terminal, set()) | right_rule_pat
    # print(sum(len(val) for val in grouped_rules.values()))
    # print(*grouped_rules.items(), sep='\n')
    new_rules = dict()
    old_rules = dict()
    for key, rules in grouped_rules.items():
        if len(rules) == 1:
            new_rules[key] = rules
            # print(key)
        else:
            data, old_rules, NO_TERMINALS = group_factorization(key, rules, new_rules, old_rules)
            new_rules |= data
    print('*' * 20)
    new_rules: GROUPED_RULES_TYPE = dict_chain(new_rules)

    return transform_longer_first_empty_rules(new_rules), NO_TERMINALS


def transform_longer_first_empty_rules(rules: GROUPED_RULES_TYPE) -> GROUPED_RULES_TYPE:
    global NO_TERMINALS
    for no_term, right_parts in rules.items():
        for rule in right_parts:
            if rule[0] == OPTIONAL_BLANKS_ENUM(None) and len(rule) > 1:
                rules[no_term] -= {rule}
                rules[no_term] |= {rule[1:]}
    return rules


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






if __name__ == '__main__':
    dict_, NO_TERMINALS = grammar_factorization(raw_rules_dict)
    print(*[str(k) + '\n\t' + '\n\t'.join(map(lambda i: f"{i}", v)) for k, v in dict_.items()], sep='\n')
    print(len(dict_))
