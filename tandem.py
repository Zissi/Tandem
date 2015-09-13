import abc
import pulp

from humans import Human



HUMANS = [Human(name='anna', learning_languages=[('german', 10)], teaching_languages=['french', 'english']),
          Human(name='bert', learning_languages=[('english', 2), ('french', 2)], teaching_languages=['german']),
          Human(name='clara', learning_languages=[('german', 2), ('english', 2)], teaching_languages=['french']),
          Human(name='dirk', learning_languages=[('german', 2), ('english', 2)], teaching_languages=['french']),
          Human(name='erik', learning_languages=[('greek', 2), ('french', 2)], teaching_languages=['german']),
          Human(name='francisca', learning_languages=[('arabic', 2), ('hausa', 2)], teaching_languages=['turkish']),
          ]

MAX_TABLE_SIZE = 4
MAX_DIFFERENCE = 1

class Seater(abc.ABC):

    def __init__(self, humans, max_table_size, max_level_difference):
        self.humans = humans
        self.max_table_size = max_table_size
        self.max_level_difference = max_level_difference

    def seat(self):
        possible_tables = list(self._filtered_tables())
        seatings = self._optimal_seatings(possible_tables)
        not_matched = self._not_matched(seatings)

        return seatings, not_matched

    @abc.abstractmethod
    def _optimal_seatings(self, possible_tables):
        ...
        
    @abc.abstractmethod
    def _not_matched(self, seatings):
        ...

    def _tables(self):
        tables = pulp.allcombinations(self.humans, self.max_table_size)
        return [table for table in tables if len(table) > 1]

    def _filtered_tables(self):
        for table in self._tables():
            tables_with_languages = self._valid_tables_with_languages(table)
            for table, language_combination in tables_with_languages:
                if _acceptable_level_difference(table,
                                                language_combination,
                                                self.max_level_difference):
                    yield table, language_combination

    @abc.abstractstaticmethod
    def _valid_tables_with_languages(table):
        ...


def _acceptable_level_difference(table, languages, max_difference):
    for language in languages:
        levels = _learning_levels(table, language)
        if _max_difference(levels) > max_difference:
            return False

    return True


def _learning_levels(table, language):
    levels = []
    for human in table:
        for learning_language, level in human.learning_languages:
            if learning_language == language:
                levels.append(level)
                break
    return levels


def _max_difference(levels):
    levels = [int(i) for i in levels]
    return max(levels) - min(levels)
