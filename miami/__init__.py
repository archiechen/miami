from flask import Flask, render_template, abort
import flask.ext.sqlalchemy
import flask.ext.restless
from datetime import datetime


DATABASE = '/tmp/test.db'

# Create the Flask application and the Flask-SQLAlchemy object.
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % DATABASE

db = flask.ext.sqlalchemy.SQLAlchemy(app)

# Create your Flask-SQLALchemy models as usual but with the following two
# (reasonable) restrictions:
#   1. They must have an id column of type Integer.
#   2. They must have an __init__ method which accepts keyword arguments for
#      all columns (the constructor in flask.ext.sqlalchemy.SQLAlchemy.Model
#      supplies such a method, so you don't need to declare a new one).


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    detail = db.Column(db.Text)
    status = db.Column(db.String(10), default='NEW')
    price = db.Column(db.Integer, default=0)
    estimate = db.Column(db.Integer, default=0)
    consuming = db.Column(db.Integer, default=0)
    created_time = db.Column(db.DateTime, default=datetime.now)
    start_time = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, title, detail, estimate=0, price=0 ,status='NEW', start_time=datetime.now()):
        self.title = title
        self.detail = detail
        self.price=price
        self.estimate = estimate
        self.status = status
        self.start_time = start_time


# Create the database tables.
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()


def now():
    return datetime.now()


@app.route('/', methods=['GET'])
def index():
    return render_template('dashborad.html')


@app.route('/new_task', methods=['GET'])
def new_task():
    return render_template('new_task.html')


@app.route('/tasks', methods=['GET'])
def new_task():
    return render_template('tasks.html')


@app.route('/planning', methods=['GET'])
def planning():
    return render_template('planning.html')


@app.route('/tasks/<status>/<tid>', methods=['PUT'])
def to_status(status, tid):
    task = Task.query.get_or_404(tid)
    if task.status == 'PROGRESS' and (status == 'READY' or status == 'DONE'):
        task.consuming += (now() - task.start_time).total_seconds()

    if status == 'READY' and task.price == 0:
        return render_template('price.html', task=task), 400
    elif status == 'PROGRESS':
        if task.estimate == 0:
            return render_template('estimate.html', task=task), 400
        else:
            task.status = status
            task.start_time = datetime.now()
    else:
        task.status = status

    db.session.commit()

    return render_template('task_card.html', task=task)


# Create the Flask-Restless API manager.
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Task, methods=['GET', 'POST', 'PUT', 'DELETE'])
