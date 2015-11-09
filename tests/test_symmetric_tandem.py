from pytest import fixture, mark

from tandem.humans import Human
from tandem.symmetric_tandem import SymmetricPulpSeater, SymmetricGurobiSeater


@fixture
def humans_with_optimal_solution():
    anna = Human(name='anna', learning_languages=[('english', 1), ('german', 10)], teaching_languages=['arabic', 'greek'])
    bert = Human(name='bert', learning_languages=[('french', 1), ('german', 10)], teaching_languages=['arabic', 'spanish'])
    clara = Human(name='clara', learning_languages=[('spanish', 1), ('arabic', 2)], teaching_languages=['german', 'english'])
    dirk = Human(name='dirk', learning_languages=[('greek', 1), ('arabic', 2)], teaching_languages=['german', 'french'])

    humans = [anna, bert, clara, dirk]
    solution = [((anna, clara), frozenset(['english', 'arabic'])),
                ((bert, dirk), frozenset(['french', 'arabic']))]

    return humans, solution


@mark.parametrize("seater_class", [SymmetricPulpSeater, SymmetricGurobiSeater])
def test_finds_optimal_solution(seater_class, humans_with_optimal_solution):
    humans, expected = humans_with_optimal_solution
    target = seater_class(humans,
                          max_table_size=4,
                          max_level_difference=0)

    actual = target.seat()
    actual, unseated = actual

    expected_unseated = []
    assert unseated == expected_unseated

    assert len(actual) == len(expected)

    for expected_table in expected:
        assert expected_table in actual


@fixture
def unsolvable_humans():
    anna = Human(name='anna', learning_languages=[('english', 1), ('german', 10)], teaching_languages=['arabic', 'greek'])
    bert = Human(name='bert', learning_languages=[('french', 1), ('german', 10)], teaching_languages=['arabic', 'spanish'])
    return [anna, bert]


@mark.parametrize("seater_class", [SymmetricPulpSeater, SymmetricGurobiSeater])
def test_unsolvable(seater_class, unsolvable_humans):
    target = seater_class(unsolvable_humans,
                          max_table_size=4,
                          max_level_difference=0)

    solution = target.seat()
    actual_seated, actual_unseated = solution
    
    expected_seated = []
    assert actual_seated == expected_seated

    expected_unseated = unsolvable_humans
    assert actual_unseated == expected_unseated
    
    
@fixture
def only_teacher_humans():
    anna = Human(name='anna', learning_languages=[('english', 1)], teaching_languages=['arabic', 'greek'])
    bert = Human(name='bert', learning_languages=[('french', 1)], teaching_languages=['english'])
    return [anna, bert]


@mark.parametrize("seater_class", [SymmetricPulpSeater, SymmetricGurobiSeater])
def test_only_teacher(seater_class, only_teacher_humans):
    target = seater_class(only_teacher_humans,
                          max_table_size=4,
                          max_level_difference=0)

    solution = target.seat()
    actual_seated, actual_unseated = solution
    
    expected_seated = []
    assert actual_seated == expected_seated

    expected_unseated = only_teacher_humans
    assert actual_unseated == expected_unseated
