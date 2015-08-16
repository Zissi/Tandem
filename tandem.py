from itertools import product
import pulp

TEACHING_LANGUAGES = 'teaching_languages'
LEARNING_LANGUAGES = 'learning_languages'

humans = [{'name': 'tim', LEARNING_LANGUAGES: [('german', 1), ('english', 2)], TEACHING_LANGUAGES: ['french']},
          {'name': 'tom', LEARNING_LANGUAGES: [('german', 1), ('english', 2)], TEACHING_LANGUAGES: ['french']},
          {'name': 'tum', LEARNING_LANGUAGES: [('french', 1), ('english', 2)], TEACHING_LANGUAGES: ['german']}]

max_tables = 5
max_table_size = 4
guests = 'A B C D E F G'.split()

def table_languages(table):
    language_combinations = get_overlapping_languages(table)
    valid_languages = languages_with_teachers(table, language_combinations)
    return valid_languages


def languages_with_teachers(table, language_combinations):
    possible_languages = set()

    for combination in language_combinations:
        if _combination_has_teachers(table, combination):
            possible_languages += combination

    return possible_languages


def _combination_has_teachers(table, combination):
    has_teacher = {}

    for human in table:
        for language in human[TEACHING_LANGUAGES]:
            has_teacher[language] = True
            if _combination_has_enough_teachers(has_teacher, combination):
                return True

    return False


def _combination_has_enough_teachers(has_teacher, combination):
    for language in combination:
        if not has_teacher.get(language, False):
            return False

    return True


def get_overlapping_languages(table):
    table_languages = _get_language_combinations(table[0])

    for human in table[1:]:
        table_languages &= _get_language_combinations(human)
        if not table_languages:
            break

    return table_languages


def _get_language_combinations(human):
    learning_languages = (language for language, _ in human[LEARNING_LANGUAGES])
    language_combinations = product(learning_languages, human[TEACHING_LANGUAGES])
    return {frozenset(combination) for combination in language_combinations}



def happiness(table):
    """
    Find the happiness of the table
    - by calculating the maximum distance between the letters
    """
    return abs(ord(table[0]) - ord(table[-1]))

# create list of all possible tables
print('find allcombinations')
possible_tables = [tuple(c) for c in pulp.allcombinations(guests,
                                        max_table_size) if len(c) > 1]
print('found all combinations')

# create a binary variable to state that a table setting is used
x = pulp.LpVariable.dicts('table', possible_tables,
                            lowBound=0,
                            upBound=1,
                            cat=pulp.LpInteger)

seating_model = pulp.LpProblem("Wedding Seating Model", pulp.LpMinimize)

seating_model += sum([happiness(table) * x[table] for table in possible_tables])

# specify the maximum number of tables
seating_model += sum([x[table] for table in possible_tables]) <= max_tables, \
                            "Maximum_number_of_tables"

seating_model += sum([x[table] for table in possible_tables]) == sum([x[table] for table in possible_tables]), \
                            "test"
print('Have model')

# A guest must seated at one and only one table
for guest in guests:
    seating_model += sum([x[table] for table in possible_tables
                                if guest in table]) == 1, "Must_seat_%s" % guest

print('done with model')

seating_model.solve()

print("The choosen tables are out of a total of %s:" % len(possible_tables))
for table in possible_tables:
    if x[table].value() == 1.0:
        print(table)
