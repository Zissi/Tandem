from itertools import product

import numpy as np
import pulp

from tandem import HUMANS, MAX_TABLE_SIZE, MAX_DIFFERENCE, Seater, \
    _acceptable_level_difference

class SymmetricSeater(Seater):

    def _valid_tables_with_languages(self, table):
        languages = _table_languages(table)
        for language_combination in languages:
            if _acceptable_level_difference(table,
                                            language_combination,
                                            self.max_level_difference):
                yield (table, frozenset(language_combination))

    def _optimal_seatings(self, possible_tables):
        is_seated = pulp.LpVariable.dicts('table',
                                          possible_tables,
                                          lowBound=0,
                                          upBound=1,
                                          cat=pulp.LpInteger)
        seating_model = _make_ilp_model(self.humans, is_seated, possible_tables)
        seating_model.solve()

        return _optimized_tables(possible_tables, is_seated)
    
    def _not_matched(self, seatings):
        seated_humans = set()
        for humans, _ in seatings:
            seated_humans.update(humans)
        not_matched = [human for human in self.humans if human not in seated_humans]
        return not_matched


def _table_languages(table):
    language_combinations = _get_overlapping_languages(table)
    valid_languages = _languages_with_teachers(table, language_combinations)
    return valid_languages


def _languages_with_teachers(table, language_combinations):
    possible_languages = set()

    for combination in language_combinations:
        if _combination_has_teachers(table, combination):
            possible_languages.add(combination)

    return possible_languages


def _combination_has_teachers(table, combination):
    has_teacher = {}

    for human in table:
        for language in human.teaching_languages:
            has_teacher[language] = True
            if _combination_has_enough_teachers(has_teacher, combination):
                return True

    return False


def _combination_has_enough_teachers(has_teacher, combination):
    for language in combination:
        if not has_teacher.get(language, False):
            return False

    return True


def _get_overlapping_languages(table):
    table_languages = _get_language_combinations(table[0])

    for human in table[1:]:
        table_languages &= _get_language_combinations(human)
        if not table_languages:
            break

    return table_languages


def _get_language_combinations(human):
    learning_languages = (language for language, _ in human.learning_languages)
    language_combinations = product(learning_languages, human.teaching_languages)
    return {frozenset(combination) for combination in language_combinations}


def _unhappiness(table, language_combination):
    ranking_unhappiness = 0
    levels = []

    for human in table:
        for idx, (learning_language, level) in enumerate(human.learning_languages):
            if learning_language in language_combination:
                ranking_unhappiness += idx
                levels.append(level)
                break
    levels = [int(i) for i in levels]
    levels = np.array(levels)
    levels = levels / max(levels)
    level_unhappiness = np.std(levels)
    total_unhappiness = ranking_unhappiness + level_unhappiness
    return total_unhappiness


def _optimized_tables(possible_tables, is_seated):
    optimized_tables = []
    print("The chosen tables are")
    for language_table in possible_tables:
        if is_seated[language_table].value() == 1.0:
            optimized_tables.append(language_table)
            print(language_table[0])
            print(language_table[1])
    return optimized_tables


def _make_ilp_model(humans, is_seated, possible_tables):
    seating_model = pulp.LpProblem("Tandem Seating Model", pulp.LpMinimize)
    seating_model += pulp.lpSum([_unhappiness(*language_table) * is_seated[language_table]
                                 for language_table in possible_tables])
    for human in humans:
        seating_model += (pulp.lpSum([is_seated[(table, languages)]
                                     for table, languages in possible_tables if human in table]) == 1,
                          "Must_seat_{}".format(human))

    return seating_model

if __name__ == '__main__':
    seater = SymmetricSeater(HUMANS, MAX_TABLE_SIZE, MAX_DIFFERENCE)
    print(seater.seat())
