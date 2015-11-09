from itertools import product

import numpy as np

from tandem.base_tandem import HUMANS, Seater, _acceptable_level_difference
from tandem.pulp_tandem import PulpMixin
from tandem.gurobi_tandem import GurobiMixin

class BaseSymmetricSeater(Seater):

    def _valid_tables_with_languages(self, table):
        languages = _table_languages(table)
        for language_combination in languages:
            if _acceptable_level_difference(table,
                                            language_combination,
                                            self.max_level_difference):
                yield (table, frozenset(language_combination))

    def _optimal_seatings(self, possible_tables):
        possible_tables = list(possible_tables)
        is_seated, seating_model = self._solved_variables_and_model(possible_tables)

        return self._optimized_tables(is_seated, seating_model)

    def _not_matched(self, seatings):
        seated_humans = set()
        for humans, _ in seatings:
            seated_humans.update(humans)
        not_matched = [human for human in self.humans if human not in seated_humans]
        return not_matched
    
    def _make_ilp_model(self, seating_model, is_seated, possible_tables):
        total_unhappiness = self._solver_sum(_unhappiness(*language_table) * is_seated[language_table]
                                             for language_table in possible_tables)
        seating_model = self._add_objective_function(total_unhappiness, seating_model)

        for human in self.humans:
            total_seatings = self._solver_sum(is_seated[(table, languages)]
                                              for table, languages in possible_tables if human in table)
            seating_model = self._add_constraint(total_seatings == 1, "Must_seat_{}".format(human), seating_model)
    
        return seating_model
    
    def _optimized_tables(self, is_seated, seating_model):
        chosen_tables = self._chosen_tables(is_seated, seating_model)
        chosen_tables = list(chosen_tables)
        print(chosen_tables)
        return chosen_tables
    

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


class SymmetricPulpSeater(BaseSymmetricSeater, PulpMixin):
    pass


class SymmetricGurobiSeater(BaseSymmetricSeater, GurobiMixin):
    pass


if __name__ == '__main__':
    seater = SymmetricPulpSeater(HUMANS, 4, 1)
    print(seater.seat())
