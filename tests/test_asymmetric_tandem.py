from pytest import fixture, mark

from tandem.humans import Human
from tandem.asymmetric_tandem import AsymmetricPulpSeater,\
    AsymmetricGurobiSeater


@fixture
def humans_matching_small_and_big_groups():
    humans = [Human(name='anna', learning_languages=[('german', 10)], teaching_languages=['arabic']),
              Human(name='bert', learning_languages=[('german', 10)], teaching_languages=['arabic']),
              Human(name='clara', learning_languages=[('arabic', 2)], teaching_languages=['german']),
              Human(name='dirk', learning_languages=[('arabic', 2)], teaching_languages=['german'])]
    return humans


@fixture
def humans_with_optimal_solution():
    anna = Human(name='anna', learning_languages=[('english', 1), ('german', 10)], teaching_languages=['arabic', 'greek'])
    bert = Human(name='bert', learning_languages=[('french', 1), ('german', 10)], teaching_languages=['arabic', 'spanish'])
    clara = Human(name='clara', learning_languages=[('spanish', 1), ('arabic', 2)], teaching_languages=['german', 'english'])
    dirk = Human(name='dirk', learning_languages=[('greek', 1), ('arabic', 2)], teaching_languages=['german', 'french'])

    humans = [anna, bert, clara, dirk]
    solution = [((anna, clara), frozenset(['english'])),
                ((anna, dirk), frozenset(['greek'])),
                ((bert, dirk), frozenset(['french'])),
                ((bert, clara), frozenset(['spanish']))]

    return humans, solution


@mark.parametrize("seater_class", [AsymmetricPulpSeater, AsymmetricGurobiSeater])
def test_prefer_small_groups(seater_class, humans_matching_small_and_big_groups):
    target = seater_class(humans_matching_small_and_big_groups,
                          max_table_size=4,
                          max_level_difference=0)
    actual = target.seat()
    (actual_first, actual_second), (unseated_first, unseated_second) = actual

    expected_unseated = []
    assert unseated_first == unseated_second == expected_unseated

    expected_table_size = 2
    assert len(actual_first) == len(actual_second) == expected_table_size


@mark.parametrize("seater_class", [AsymmetricPulpSeater, AsymmetricGurobiSeater])
def test_finds_optimal_solution(seater_class, humans_with_optimal_solution):
    humans, expected = humans_with_optimal_solution
    target = seater_class(humans,
                          max_table_size=4,
                          max_level_difference=0)

    actual = target.seat()
    (actual_first, actual_second), (unseated_first, unseated_second) = actual
    actual_tables = actual_first + actual_second

    expected_unseated = []
    assert unseated_first == unseated_second == expected_unseated

    assert len(actual_tables) == len(expected)

    for expected_table in expected:
        assert expected_table in actual_tables


@fixture
def unsolvable_humans():
    anna = Human(name='anna', learning_languages=[('english', 1), ('german', 10)], teaching_languages=['arabic', 'greek'])
    bert = Human(name='bert', learning_languages=[('french', 1), ('german', 10)], teaching_languages=['arabic', 'spanish'])
    return [anna, bert]


@mark.parametrize("seater_class", [AsymmetricPulpSeater, AsymmetricGurobiSeater])
def test_unsolvable(seater_class, unsolvable_humans):
    target = seater_class(unsolvable_humans,
                          max_table_size=4,
                          max_level_difference=0)

    solution = target.seat()
    actual_seated, actual_unseated = solution
    
    expected_seated = ([], [])
    assert actual_seated == expected_seated

    expected_unseated = (unsolvable_humans, unsolvable_humans)
    assert actual_unseated == expected_unseated
    
    
@fixture
def only_teacher_humans():
    anna = Human(name='anna', learning_languages=[('english', 1)], teaching_languages=['arabic', 'greek'])
    bert = Human(name='bert', learning_languages=[('french', 1)], teaching_languages=['english'])
    return [anna, bert]


@mark.parametrize("seater_class", [AsymmetricPulpSeater, AsymmetricGurobiSeater])
def test_only_teacher(seater_class, only_teacher_humans):
    target = seater_class(only_teacher_humans,
                          max_table_size=4,
                          max_level_difference=0)

    solution = target.seat()
    actual_seated, actual_unseated = solution
    
    expected_seated = ([], [])
    assert actual_seated == expected_seated

    expected_unseated = (only_teacher_humans, only_teacher_humans)
    assert actual_unseated == expected_unseated
    
    
@fixture
def too_small_tables_humans():
    anna = Human(name='anna', learning_languages=[('english', 1)], teaching_languages=['french'])
    bert = Human(name='bert', learning_languages=[('french', 1)], teaching_languages=['english'])
    clara = Human(name='clara', learning_languages=[('french', 1)], teaching_languages=['english'])
    table_size = 2
    return [anna, bert, clara], table_size


@mark.parametrize("seater_class", [AsymmetricPulpSeater, AsymmetricGurobiSeater])
def test_too_small_tables(seater_class, too_small_tables_humans):
    humans, table_size = too_small_tables_humans
    target = seater_class(humans,
                          max_table_size=table_size,
                          max_level_difference=0)

    solution = target.seat()
    actual_seated, actual_unseated = solution
    
    expected_seated = ([], [])
    assert actual_seated == expected_seated

    expected_unseated = (humans, humans)
    assert actual_unseated == expected_unseated