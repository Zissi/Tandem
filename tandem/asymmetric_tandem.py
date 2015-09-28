import pulp

from tandem.tandem import Seater, HUMANS, MAX_DIFFERENCE, MAX_TABLE_SIZE
import pprint
from itertools import permutations


class AsymmetricSeater(Seater):

    @staticmethod
    def _valid_tables_with_languages(table):
        common_languages = table[0].all_languages()
        for human in table[1:]:
            common_languages &= human.all_languages()
            if not common_languages:
                return False

        languages = _languages_with_teachers_and_pupils(table, common_languages)
        for language in languages:
            language_combination = frozenset((language,))
            yield table, language_combination


    def _optimal_seatings(self, possible_tables):
        possible_tables = list(set(possible_tables))
        impossible_humans = set()
        for human in self.humans:
            is_teacher = False
            is_pupil = False
            for table in possible_tables:
                if human in table[0] and _is_pupil(human, table):
                    is_pupil = True

                if human in table[0] and _is_teacher(human, table[1]):
                    is_teacher = True

            if not (is_pupil and is_teacher):
                impossible_humans.add(human)

        possible_tables = [(table, langs) for (table, langs) in possible_tables if not set(table) & impossible_humans]

        possible_tables = list(permutations(possible_tables, 2))

        is_seated = pulp.LpVariable.dicts('table',
                                          possible_tables,
                                          lowBound=0,
                                          upBound=1,
                                          cat=pulp.LpInteger)

        seating_model = _make_ilp_model(self.humans, is_seated, possible_tables)
        seating_model.solve()

        return _optimized_tables(possible_tables, is_seated)

    def _not_matched(self, seatings):
        seated_humans_round_1 = set()
        seated_humans_round_2 = set()
        for (humans_1, _), (humans_2, _) in zip(*seatings):
            seated_humans_round_1.update(humans_1)
            seated_humans_round_2.update(humans_2)
        not_matched_round_1 = [human for human in self.humans if human not in seated_humans_round_1]
        not_matched_round_2 = [human for human in self.humans if human not in seated_humans_round_2]
        return not_matched_round_1, not_matched_round_2


def _languages_with_teachers_and_pupils(table, common_languages):
    for language in common_languages:
        has_teachers = False
        has_pupils = False
        for human in table:
            if language in human.teaching_languages:
                has_teachers = True
            else:
                has_pupils = True
            if has_pupils and has_teachers:
                yield language


def _unhappiness(table1, table2):
    total_unhappiness = _ranking_unhappiness(*table1)
    total_unhappiness += _ranking_unhappiness(*table2)

    total_unhappiness += 3 ** len(table1[0])
    total_unhappiness += 3 ** len(table2[0])

    return total_unhappiness

def _ranking_unhappiness(table, language_combination):
    ranking_unhappiness = 0
    for human in table:
        for idx, (learning_language, _) in enumerate(human.learning_languages):
            if learning_language in language_combination:
                ranking_unhappiness += idx * 100
                break
    return ranking_unhappiness


def _make_ilp_model(humans, is_seated_ilp, possible_tables):
    seating_model = pulp.LpProblem("Tandem Seating Model", pulp.LpMinimize)
    seating_model += pulp.lpSum([_unhappiness(*language_table) * is_seated_ilp[language_table]
                                 for language_table in possible_tables])


    for human in humans:
        round1_variables = []
        for table_1, table_2 in possible_tables:
            if human in table_1[0]:
                round1_variables.append(is_seated_ilp[(table_1, table_2)])

        seating_model += (pulp.lpSum(round1_variables) == 1,
                          "Must_seat_exatcly_once_round1_{}".format(human))


        round2_variables = []
        for table_1, table_2 in possible_tables:
            if human in table_2[0]:
                round2_variables.append(is_seated_ilp[(table_1, table_2)])

        seating_model += (pulp.lpSum(round2_variables) == 1,
                          "Must_seat_exatcly_once_round2_{}".format(human))


        pupil_variables = []
        for table_1, table_2 in possible_tables:
            if human in table_1[0] and _is_pupil(human, table_1[1]) or human in table_2[0] and _is_pupil(human, table_2[1]):
                pupil_variables.append(is_seated_ilp[(table_1, table_2)])

        seating_model += (pulp.lpSum(pupil_variables) == 1,
                          "Must_seat_as_pupil_{}".format(human))


        teacher_variables = []
        for table_1, table_2 in possible_tables:
            if human in table_1[0] and _is_teacher(human, table_1[1]) or human in table_2[0] and _is_teacher(human, table_2[1]):
                teacher_variables.append(is_seated_ilp[(table_1, table_2)])

        seating_model += (pulp.lpSum(teacher_variables) == 1,
                          "Must_seat_as_teacher_{}".format(human))

    return seating_model


def _is_teacher(human, table_language_combination):
    for language in table_language_combination:
        if language in human.teaching_languages:
            return True

    return False


def _is_pupil(human, table_language_combination):
    return not _is_teacher(human, table_language_combination)


def _optimized_tables(possible_tables, is_seated_ilp):
    tables = []
    print("The chosen tables are")
    for language_table in possible_tables:
        if is_seated_ilp[language_table].value() == 1.0:
            tables.append(language_table)

    all_round1 = []
    all_round2 = []
    for round1, round2 in tables:
        all_round1.append(round1)
        all_round2.append(round2)

    print("ROUND I")
    pprint.pprint(all_round1)

    print("ROUND II")
    pprint.pprint(all_round2)

    return all_round1, all_round2


if __name__ == '__main__':
    seater = AsymmetricSeater(HUMANS, MAX_TABLE_SIZE, MAX_DIFFERENCE)
    print(seater.seat())







