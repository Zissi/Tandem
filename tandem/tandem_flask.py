import csv
from pathlib import Path

from flask import Flask, render_template, request
from celery import Celery

from tandem.humans import Human
from tandem.symmetric_tandem import SymmetricGurobiSeater
from tandem.asymmetric_tandem import AsymmetricGurobiSeater
from tandem.asymmetric_tandem import AsymmetricPulpSeater
from tandem.symmetric_tandem import SymmetricPulpSeater



file_path = Path(__file__).resolve()
base_path = file_path.parents[0].resolve()
backup_path = base_path / 'backup.tsv'
default_path = base_path / 'default.tsv'
template_path = file_path.parents[1] / 'templates'

app = Flask(__name__,
            template_folder=str(template_path))
app.config.update(
    CELERY_BROKER_URL='amqp://localhost',
    CELERY_RESULT_BACKEND='amqp://localhost'
)

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery


celery = make_celery(app)


def parse_learning_languages(langs_string):
    splitted = langs_string.split(',')

    langs = []
    for idx in range(0, len(splitted), 2):
        lang, level = splitted[idx:idx + 2]
        lang = normalize(lang)
        level = normalize(level)
        langs.append((lang, level))

    return langs


def parse_teaching_languages(langs_string):
    return [normalize(l) for l in langs_string.split(',')]


def normalize(string):
    return string.strip().lower()


def _human_from_csv(csv_dict):
    name = csv_dict['Name']
    learning_languages = parse_learning_languages(csv_dict['Learning Languages'])
    teaching_languages = parse_teaching_languages(csv_dict['Teaching Languages'])
    return Human(name, learning_languages, teaching_languages)


def _load_backup():
    load_path = backup_path if backup_path.exists() else default_path
    with load_path.open() as load_file:
        reader = csv.DictReader(load_file, delimiter='\t')
        for row in reader:
            yield _human_from_csv(row)


HUMANS = list(_load_backup())

MAX_TABLE_SIZE = 3
MAX_LEVEL_DIFFERENCE = 1


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


@app.route('/results_symmetric')
def show_symmetric_results():
    _save_backup()
    seater = SymmetricGurobiSeater(HUMANS, MAX_TABLE_SIZE, MAX_LEVEL_DIFFERENCE)
    task = async_seat.delay(seater)
    tables, unseated = task.wait()
    return render_template('result_symmetric.html', tables=tables, unseated=unseated)


@app.route('/results_asymmetric')
def show_asymmetric_results():
    _save_backup()
    seater = AsymmetricGurobiSeater(HUMANS, MAX_TABLE_SIZE, MAX_LEVEL_DIFFERENCE)
    task = async_seat.delay(seater)
    (round1, round2), (unseated_round_1, unseated_round_2) = task.wait()
    return render_template('result_asymmetric.html', round1=round1, round2=round2, unseated_round_1=unseated_round_1, unseated_round_2=unseated_round_2)


@celery.task(name='async_seat')
def async_seat(seater):
    return seater.seat()


def delete_all_humans():
    del HUMANS[:]
    return render_template('humans.html', humans=HUMANS)


def enter_new_human(r):
    name = r.form['name']
    learning_languages = r.form['learning']
    teaching_languages = r.form['teaching']

    learning_languages = parse_learning_languages(learning_languages)
    teaching_languages = parse_teaching_languages(teaching_languages)
    name = normalize(name)
    make_new_human(name, learning_languages, teaching_languages)
    return render_template('humans.html', humans=HUMANS)


def make_new_human(name, learning_languages, teaching_languages):
    human = Human(name=name, learning_languages=learning_languages, teaching_languages=teaching_languages)
    HUMANS.append(human)


def _save_backup():
    with backup_path.open('w') as backup_file:
        cols = ('Name', 'Learning Languages', 'Teaching Languages')
        writer = csv.DictWriter(backup_file, cols, delimiter='\t')
        writer.writeheader()
        for human in HUMANS:
            writer.writerow(human.to_dict())


if __name__ == '__main__':
    app.run(debug=True)
