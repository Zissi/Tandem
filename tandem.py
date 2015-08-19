from itertools import product

import numpy as np
import pulp

from humans import Human

MAX_TABLE_SIZE = 4
MAX_DIFFERENCE = 1

HUMANS = [Human(name='anna', learning_languages=[('german', 10)], teaching_languages=['french', 'english']),
          Human(name='bert', learning_languages=[('english', 2), ('french', 2)], teaching_languages=['german']),
          Human(name='clara', learning_languages=[('german', 2), ('english', 2)], teaching_languages=['french']),
          Human(name='dirk', learning_languages=[('german', 2), ('english', 2)], teaching_languages=['french']),
          Human(name='erik', learning_languages=[('greek', 2), ('french', 2)], teaching_languages=['german'])]


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


def unhappiness(table, language_combination):
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


def language_tables(humans, max_table_size):
    for table in pulp.allcombinations(humans, max_table_size):
        if len(table) <= 1:
            continue
        languages = _table_languages(table)
        for language_combination in languages:
            if _acceptable_level_difference(table, language_combination):
                yield (table, frozenset(language_combination))


def _acceptable_level_difference(table, language_combination):
    for language in language_combination:
        levels = _learning_levels(table, language)
        if _max_difference(levels) > MAX_DIFFERENCE:
            return False

    return True


def _learning_levels(table, language):
    levels = []
    for human in table:
        for learning_language, level in human.learning_languages:
            if learning_language == language:
                levels.append(level)
                break
    return levels


def _max_difference(levels):
    levels = [int(i) for i in levels]
    return max(levels) - min(levels)


def calculate_tables(humans, max_table_size):
    possible_tables = list(language_tables(humans, max_table_size))

    x = pulp.LpVariable.dicts('table', possible_tables,
                                lowBound=0,
                                upBound=1,
                                cat=pulp.LpInteger)

    seating_model = pulp.LpProblem("Tandem Seating Model", pulp.LpMinimize)
    seating_model += pulp.lpSum([unhappiness(*language_table) * x[language_table] for language_table in possible_tables])
    for human in humans:
        seating_model += pulp.lpSum([x[(table, languages)] for table, languages in possible_tables if human in table]) == 1, "Must_seat_{}".format(human)

    #solver = pulp.solvers.CPLEX()
    #seating_model.solve(solver)
    seating_model.solve()

    final_tables = []
    print("The choosen tables are")
    for language_table in possible_tables:
        if x[language_table].value() == 1.0:
            final_tables.append(language_table)
            print(language_table[0])
            print(language_table[1])
    return final_tables

