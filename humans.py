class Human(object):

    def __init__(self, name, learning_languages, teaching_languages):
        self.name = name
        self.learning_languages = learning_languages
        self.teaching_languages = teaching_languages

    def __repr__(self):
        return self.name

    def all_languages(self):
        learning_languages = [language_with_level[0] for language_with_level in self.learning_languages]
        return set(self.teaching_languages + learning_languages)