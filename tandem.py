
import pulp

humans = [{'name': 'tim', 'learning_languages': [('german', 1), ('english', 2)], 'teaching_languages': ['french']},
          {'name': 'tom', 'learning_languages': [('german', 1), ('english', 2)], 'teaching_languages': ['french']},
          {'name': 'tum', 'learning_languages': [('french', 1), ('english', 2)], 'teaching_languages': ['german']}]

max_tables = 5
max_table_size = 4
guests = 'A B C D E F G'.split()

def fittness(table):
    pass

def no_teacher(table):
    for human in table:

        return 0

def disjunct_humans():
    return 0

def happiness(table):
    """
    Find the happiness of the table
    - by calculating the maximum distance between the letters
    """
    return abs(ord(table[0]) - ord(table[-1]))

#create list of all possible tables
print('find allcombinations')
possible_tables = [tuple(c) for c in pulp.allcombinations(guests,
                                        max_table_size) if len(c)>1]
print('found all combinations')

#create a binary variable to state that a table setting is used
x = pulp.LpVariable.dicts('table', possible_tables,
                            lowBound = 0,
                            upBound = 1,
                            cat = pulp.LpInteger)

seating_model = pulp.LpProblem("Wedding Seating Model", pulp.LpMinimize)

seating_model += sum([happiness(table) * x[table] for table in possible_tables])

#specify the maximum number of tables
seating_model += sum([x[table] for table in possible_tables]) <= max_tables, \
                            "Maximum_number_of_tables"

seating_model += sum([x[table] for table in possible_tables]) == sum([x[table] for table in possible_tables]), \
                            "test"
print('Have model')

#A guest must seated at one and only one table
for guest in guests:
    seating_model += sum([x[table] for table in possible_tables
                                if guest in table]) == 1, "Must_seat_%s"%guest

print('done with model')

seating_model.solve()

print("The choosen tables are out of a total of %s:"%len(possible_tables))
for table in possible_tables:
    if x[table].value() == 1.0:
        print(table)