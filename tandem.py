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
    
    def __init__(self, humans, max_table_size):
        self.humans = humans
        self.max_table_size = max_table_size
        
    def seat(self):
        seatings = self._optimal_seatings()
        seated_humans = set()
        for humans, _ in seatings:
            seated_humans.update(humans)
        not_matched = [human for human in self.humans if human not in seated_humans]
        return seatings, not_matched
    
    @abc.abstractmethod
    def _optimal_seatings(self):
        ...

    def _tables(self):
        tables = pulp.allcombinations(self.humans, self.max_table_size)
        return [table for table in tables if len(table) > 1]
    
    def _filtered_tables(self):
        for table in self._tables():
            if self._valid_table(table):
                yield table
                
    @abc.abstractstaticmethod
    def _valid_table(table):
        ...
            