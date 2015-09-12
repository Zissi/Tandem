from tandem import Seater

class AsymmetricSeater(Seater):
    
    @staticmethod
    def _valid_table(table):
        common_languages = table[0].all_languages()
        for human in table[1:]:
            common_languages &= human.all_languages()
            if not common_languages:
                return False
            
        languages = _languages_with_teachers_and_pupils(table, common_languages)
        yield from ((language, table) for language in languages)
        
        
def _languages_with_teachers_and_pupils(table, common_languages):
    has_teachers = False
    has_pupils = False
    for language in common_languages:
        for human in table:
            if language in human.teaching_languages:
                has_teachers = True
            else:
                has_pupils = True
            if has_pupils and has_teachers:
                yield language
            

            
            
            
    
    
