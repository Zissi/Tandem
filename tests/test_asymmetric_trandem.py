from pytest import fixture

from tandem.humans import Human
from tandem.asymmetric_tandem import AsymmetricSeater


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


def test_prefer_small_groups(humans_matching_small_and_big_groups):
    target = AsymmetricSeater(humans_matching_small_and_big_groups,
                              max_table_size=4,
                              max_level_difference=0)
    actual = target.seat()
    (actual_first, actual_second), (unseated_first, unseated_second) = actual

    expected_unseated = []
    assert unseated_first == unseated_second == expected_unseated

    expected_table_size = 2
    assert len(actual_first) == len(actual_second) == expected_table_size


def test_finds_optimal_solution(humans_with_optimal_solution):
    humans, expected = humans_with_optimal_solution
    target = AsymmetricSeater(humans,
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
