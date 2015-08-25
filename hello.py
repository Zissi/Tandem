from humans import Human
from tandem import calculate_tables

from flask import Flask, render_template, request

app = Flask(__name__)

HUMANS = [Human(name='anna', learning_languages=[('german', 10)], teaching_languages=['french', 'english']),
          Human(name='bert', learning_languages=[('english', 2), ('french', 2)], teaching_languages=['german']),
          Human(name='clara', learning_languages=[('german', 2), ('english', 2)], teaching_languages=['french']),
          Human(name='dirk', learning_languages=[('german', 2), ('english', 2)], teaching_languages=['french']),
          Human(name='erik', learning_languages=[('greek', 2), ('french', 2)], teaching_languages=['german'])]

MAX_TABLE_SIZE = 4


@app.route('/')
def add_humans():
    return render_template('humans.html', humans=HUMANS)



@app.route('/', methods=['POST'])
def humans_post():
    if request.form.get('remove') is not None:
        return delete_human(request)

    if request.form.get('btn') == 'save':
        return enter_new_human(request)

    if request.form.get('btn') == 'delete_all':
        return delete_all_humans()

def delete_human(req):
    delete_name = req.form['remove']
    for idx, human in enumerate(HUMANS):
        if human.name == delete_name:
            HUMANS.pop(idx)
    return render_template('humans.html', humans=HUMANS)

@app.route('/results')
def show_results():
    return render_template('result.html', tables=calculate_tables(HUMANS, MAX_TABLE_SIZE))


def delete_all_humans():
    del HUMANS[:]
    return render_template('humans.html', humans=HUMANS)


def enter_new_human(r):
    name = r.form['name']
    learning_languages = r.form['learning']
    teaching_languages = r.form['teaching']

    learning_languages = parse_learning_languages(learning_languages)
    teaching_languages = prase_teaching_languages(teaching_languages)
    name = normalize(name)
    make_new_human(name, learning_languages, teaching_languages)
    return render_template('humans.html', humans=HUMANS)


def make_new_human(name, learning_languages, teaching_languages):
    human = Human(name=name, learning_languages=learning_languages, teaching_languages=teaching_languages)
    HUMANS.append(human)


def parse_learning_languages(langs_string):
    splitted = langs_string.split(',')

    langs = []
    for idx in range(0, len(splitted), 2):
        lang, level = splitted[idx:idx + 2]
        lang = normalize(lang)
        level = normalize(level)
        langs.append((lang, level))

    return langs


def prase_teaching_languages(langs_string):
    return [normalize(l) for l in langs_string.split(',')]


def normalize(string):
    return string.strip().lower()


if __name__ == '__main__':
    app.run(debug=True)
