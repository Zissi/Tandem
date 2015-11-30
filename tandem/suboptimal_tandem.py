from itertools import product

import numpy as np

from tandem.base_tandem import HUMANS, Seater
from tandem.pulp_tandem import PulpMixin
from tandem.gurobi_tandem import GurobiMixin
from tandem.asymmetric_tandem import _languages_with_teachers_and_pupils,\
    _is_teacher, _is_pupil
from tandem.humans import Human

class BaseSuboptimalSeater(Seater):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.already_teacher = set()
        self.already_pupil = set()
    
    def seat(self):
        seatings_round1, not_matched_round1 = super().seat()
        self.already_pupil, self.already_teacher = _fill_already_seated(seatings_round1)
        seatings_round2, not_matched_round2 = super().seat()
        return (seatings_round1, seatings_round2), (not_matched_round1, not_matched_round2)
        

    def _valid_tables_with_languages(self, table):
        common_languages = table[0].all_languages()
        for human in table[1:]:
            common_languages &= human.all_languages()
            if not common_languages:
                return

        languages = _languages_with_teachers_and_pupils(table, common_languages)
        for language in languages:
            language_combination = frozenset((language,))
            yield table, language_combination

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
        total_unhappiness = self._solver_sum(self._unhappiness(*language_table) * is_seated[language_table]
                                             for language_table in possible_tables)
        seating_model = self._add_objective_function(total_unhappiness, seating_model)

        for human in self.humans:
            total_seatings = self._solver_sum(is_seated[(table, languages)]
                                              for table, languages in possible_tables if human in table)
            seating_model = self._add_constraint(total_seatings == 1, "Must_seat_{}".format(human), seating_model)
    
        return seating_model
    
    def _unhappiness(self, table, language_combination):
        ranking_unhappiness = 0
        previous_round_unhappiness = 0
        levels = []
        
        for human in table:
            if (_is_teacher(human, language_combination) and human in self.already_teacher or
                _is_pupil(human, language_combination) and human in self.already_pupil):
                previous_round_unhappiness += 9999
            
            for idx, (learning_language, level) in enumerate(human.learning_languages):
                if learning_language in language_combination:
                    ranking_unhappiness += idx
                    levels.append(level)
                    break
        levels = [int(i) for i in levels]
        levels = np.array(levels)
        maximum = (max(levels))
        if maximum:
            levels = levels / maximum
        level_unhappiness = np.std(levels)
        total_unhappiness = ranking_unhappiness + level_unhappiness
        return total_unhappiness + previous_round_unhappiness
    
    def _optimized_tables(self, is_seated, seating_model):
        chosen_tables = self._chosen_tables(is_seated, seating_model)
        chosen_tables = list(chosen_tables)
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


def _fill_already_seated(seated):
    already_teacher = set()
    already_pupil = set()

    for table, languages in seated:
        for human in table:
            if _is_teacher(human, languages):
                already_teacher.add(human)
            else:
                already_pupil.add(human)
    
    return already_pupil, already_teacher


class SuboptimalPulpSeater(BaseSuboptimalSeater, PulpMixin):
    pass


class SuboptimalGurobiSeater(BaseSuboptimalSeater, GurobiMixin):
    pass


if __name__ == '__main__':
    from pathlib import Path
    import csv
    
    file_path = Path(__file__).resolve()
    base_path = file_path.parents[0].resolve()
    backup_path = base_path / 'backup.tsv'
    default_path = base_path / 'default.tsv'
    
    def parse_learning_languages(langs_string):
        splitted = langs_string.split(',')
    
        langs = []
        for idx in range(0, len(splitted), 2):
            lang, level = splitted[idx:idx + 2]
            lang = normalize(lang)
            level = normalize(level)
            langs.append((lang, level))
    
        return langs
    
    def parse_teaching_languages(langs_string):
        return [normalize(l) for l in langs_string.split(',')]
    
    
    def normalize(string):
        return string.strip().lower()
    
    def _human_from_csv(csv_dict):
        name = csv_dict['Name']
        learning_languages = parse_learning_languages(csv_dict['Learning Languages'])
        teaching_languages = parse_teaching_languages(csv_dict['Teaching Languages'])
        return Human(name, learning_languages, teaching_languages)
    
    def _load_backup():
        load_path = backup_path if backup_path.exists() else default_path
        with load_path.open() as load_file:
            reader = csv.DictReader(load_file, delimiter='\t')
            for row in reader:
                yield _human_from_csv(row)
            
            
    HUMANS = list(_load_backup())
    seater = SuboptimalGurobiSeater(HUMANS,
                                    max_table_size=4,
                                    max_level_difference=10)
    (round1, round2), (unseated1, unseated2) = seater.seat()
    
    sorted_round1 = []
    for (table, language) in round1:
        sorted_table = sorted(table, key=lambda human: human.name)
        sorted_round1.append((sorted_table, language))
        
    sorted_round2 = []
    for (table, language) in round2:
        sorted_table = sorted(table, key=lambda human: human.name)
        sorted_round2.append((sorted_table, language))
        
    print(sorted(sorted_round1, key=lambda x: x[0][0].name))
    print(sorted(sorted_round2, key=lambda x: x[0][0].name))
