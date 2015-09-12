class Human(object):

    def __init__(self, name, learning_languages, teaching_languages):
        self.name = name
        self.learning_languages = learning_languages
        self.teaching_languages = teaching_languages

    def __repr__(self):
        return self.name
    
    def all_languages(self):
        return set(self.teaching_languages + self.learning_languages)