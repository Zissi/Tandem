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
def hello_world():
    return 'Hello World!'


@app.route('/tandem/')
def hello():
    return render_template('humans.html', humans=HUMANS)



@app.route('/tandem/', methods=['POST'])
def my_form_post():
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
    text = r.form['name'], r.form['learning'], r.form['teaching']
    learning_languages = get_learning_languages(text)
    teaching_languages = get_teaching_languages(text)
    make_new_human(text[0], learning_languages, teaching_languages)
    return render_template('humans.html', humans=HUMANS)


def make_new_human(name, learning_languages, teaching_languages):
    human = Human(name=name, learning_languages=learning_languages, teaching_languages=teaching_languages)
    HUMANS.append(human)


def get_learning_languages(text):
    no_white = text[1].replace(" ", "")
    learning_languages = no_white.split(',')
    it = iter(learning_languages)
    return list(zip(it, it))


def get_teaching_languages(text):
    no_white = text[2].replace(" ", "")
    return no_white.split(',')

if __name__ == '__main__':
    app.run(debug=True)
