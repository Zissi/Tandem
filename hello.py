from humans import Human

__author__ = 'franziska'
from flask import Flask, render_template, request

app = Flask(__name__)

HUMANS = []


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/hello/')
def hello():
    return render_template('hello.html', humans=HUMANS)


@app.route('/hello/', methods=['POST'])
def my_form_post():
    text = request.form['name'], request.form['learning'], request.form['teaching']
    learning_languages = get_learning_languages(text)
    teaching_languages = get_teaching_languages(text)
    human = Human(name=text[0], learning_languages=learning_languages, teaching_languages=teaching_languages)
    HUMANS.append(human)
    print(teaching_languages, learning_languages)
    return render_template('hello.html', humans=HUMANS)


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