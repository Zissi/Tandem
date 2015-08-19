from humans import Human
from tandem import calculate_tables

__author__ = 'franziska'
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


@app.route('/hello/')
def hello():
    return render_template('hello.html', humans=HUMANS)


@app.route('/hello/', methods=['POST'])
def my_form_post():
    if request.form['btn'] == 'Submit':
        return enter_new_human(request)
    elif request.form['btn'] == 'DeleteAll':
        return delete_all_humans(request)
    elif request.form['btn'] == 'Calculate':
        return render_template('result.html', tables=calculate_tables(HUMANS, MAX_TABLE_SIZE))


def delete_all_humans(request):
    del HUMANS[:]
    return render_template('hello.html', humans=HUMANS)


def enter_new_human(request):
    text = request.form['name'], request.form['learning'], request.form['teaching']
    learning_languages = get_learning_languages(text)
    teaching_languages = get_teaching_languages(text)
    make_new_human(text[0], learning_languages, teaching_languages)
    print(teaching_languages, learning_languages)
    return render_template('hello.html', humans=HUMANS)


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