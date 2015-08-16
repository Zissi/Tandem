from itertools import product
import pulp
from humans import Human

MAX_TABLE_SIZE = 4

humans = [Human(name='tim', learning_languages=[('german', 1), ('english', 2)], teaching_languages=['french']),
          Human(name='tom', learning_languages=[('english', 1), ('french', 2)], teaching_languages=['german']),
          Human(name='tum', learning_languages=[('german', 1), ('english', 2)], teaching_languages=['french']),
          Human(name='tam', learning_languages=[('german', 1), ('english', 2)], teaching_languages=['french'])]


max_tables = 5
max_table_size = 4

def table_languages(table):
    language_combinations = get_overlapping_languages(table)
    valid_languages = languages_with_teachers(table, language_combinations)
    return valid_languages


def languages_with_teachers(table, language_combinations):
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


def get_overlapping_languages(table):
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



def happiness(table):
    """
    Find the happiness of the table
    - by calculating the maximum distance between the letters
    """

    return 2

# create list of all possible tables
print('find allcombinations')
possible_tables = [table for table in pulp.allcombinations(humans, MAX_TABLE_SIZE) if len(table) > 1 and table_languages(table)]
print('found all combinations')

# create a binary variable to state that a table setting is used
x = pulp.LpVariable.dicts('table', possible_tables,
                            lowBound=0,
                            upBound=1,
                            cat=pulp.LpInteger)

seating_model = pulp.LpProblem("Tandem Seating Model", pulp.LpMinimize)

seating_model += sum([happiness(table) * x[table] for table in possible_tables])

# specify the maximum number of tables
seating_model += sum([x[table] for table in possible_tables]) <= max_tables, \
                            "Maximum_number_of_tables"
print('Have model')

# A guest must seated at one and only one table
for human in humans:
    seating_model += sum([x[table] for table in possible_tables
                                if human in table]) == 1, "Must_seat_%s" % human

print('done with model')

seating_model.solve()

print("The choosen tables are out of a total of %s:" % len(possible_tables))
for table in possible_tables:
    print(x[table].value())
    if x[table].value() == 1.0:
        print(table)
