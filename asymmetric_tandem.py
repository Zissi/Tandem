import pulp

from tandem import Seater, HUMANS, MAX_DIFFERENCE, MAX_TABLE_SIZE
import pprint


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
        is_teacher = pulp.LpVariable.dicts('teacher_table',
                                           possible_tables,
                                           lowBound=0,
                                           upBound=1,
                                           cat=pulp.LpInteger)

        is_pupil = pulp.LpVariable.dicts('pupil_table',
                                          possible_tables,
                                          lowBound=0,
                                          upBound=1,
                                          cat=pulp.LpInteger)

        seating_model = _make_ilp_model(self.humans, is_teacher,
                                        is_pupil, possible_tables)
        seating_model.writeLP("test.txt")
        seating_model.solve()

        return _optimized_tables(possible_tables, is_teacher, is_pupil)


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


def _unhappiness(table, language_combination):
    ranking_unhappiness = 0

    for human in table:
        for idx, (learning_language, _) in enumerate(human.learning_languages):
            if learning_language in language_combination:
                ranking_unhappiness += idx
                break

    return 10 #ranking_unhappiness


def _make_ilp_model(humans, is_teacher_ilp, is_pupil_ilp, possible_tables):
    seating_model = pulp.LpProblem("Tandem Seating Model", pulp.LpMinimize)
    seating_model += pulp.lpSum([_unhappiness(*language_table) * is_pupil_ilp[language_table]
                                 for language_table in possible_tables])
    for human in humans:
        seating_model += (pulp.lpSum([is_teacher_ilp[(table, languages)]
                                     for table, languages in possible_tables
                                     if ((human in table) and _is_teacher(human, languages))]) == 1,
                          "Must_seat_as_teacher_{}".format(human))

        seating_model += (pulp.lpSum([is_pupil_ilp[(table, languages)]
                                     for table, languages in possible_tables
                                     if ((human in table) and _is_pupil(human, languages))]) == 1,
                          "Must_seat_as_pupil_{}".format(human))

#        seating_model += (pulp.lpSum([(is_pupil_ilp[language_table] + is_teacher_ilp[language_table])
#                                     for language_table in possible_tables]) == 2,
#                          "Must_seat_as_pupil_and_teacher_twice_{}".format(human))

#        seating_model += (pulp.lpSum([is_teacher_ilp[(table, languages)]
#                                      for table, languages in possible_tables
#                                      if ((human in table) and _is_teacher(human, languages))]
#                                     +
#                                     [is_pupil_ilp[(table, languages)]
#                                      for table, languages in possible_tables
#                                      if ((human in table) and _is_pupil(human, languages))]
#                                     ) == 2,
#                          "Must_seat_as_whatever_{}".format(human))

    return seating_model


def _is_teacher(human, table_language_combination):
    for language in table_language_combination:
        if language in human.teaching_languages:
            return True

    return False


def _is_pupil(human, table_language_combination):
    return not _is_teacher(human, table_language_combination)


def _optimized_tables(possible_tables, is_teacher_ilp, is_pupil_ilp):
    teacher_tables = []
    pupil_tables = []
    print("The chosen tables are")
    for language_table in possible_tables:
        if is_teacher_ilp[language_table].value() == 1.0:
            teacher_tables.append(language_table)
        if is_pupil_ilp[language_table].value() == 1.0:
            pupil_tables.append(language_table)

    print("TEACHER")
    pprint.pprint(teacher_tables)

    print("PUPILS")
    pprint.pprint(pupil_tables)

    return optimized_tables


if __name__ == '__main__':
    seater = AsymmetricSeater(HUMANS, MAX_TABLE_SIZE, MAX_DIFFERENCE)
    seater.seat()







