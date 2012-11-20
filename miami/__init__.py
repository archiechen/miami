from flask import Flask
import flask.ext.sqlalchemy
import flask.ext.restless
from datetime import datetime
import math
from flask.ext.login import LoginManager, UserMixin, AnonymousUser, login_user, logout_user, login_required, current_user


DATABASE = '/tmp/test.db'
SECRET_KEY = "yeah, not actually a secret"
DEBUG = True

# Create the Flask application and the Flask-SQLAlchemy object.
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % DATABASE
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://miami:miami@localhost:3306/miami'


db = flask.ext.sqlalchemy.SQLAlchemy(app)
global db
import miami.models
from miami.models import User, Task, TimeSlot, Anonymous


# Create your Flask-SQLALchemy models as usual but with the following two
# (reasonable) restrictions:
#   1. They must have an id column of type Integer.
#   2. They must have an __init__ method which accepts keyword arguments for
#      all columns (the constructor in flask.ext.sqlalchemy.SQLAlchemy.Model
#      supplies such a method, so you don't need to declare a new one).
login_manager = LoginManager()
login_manager.anonymous_user = Anonymous


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

login_manager.setup_app(app)
# Create the database tables.

def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()

def now():
    return datetime.now()


def zeroing():
    tasks = Task.query.filter_by(status='PROGRESS')

    for task in tasks:
        task.status = 'READY'
        end_time = now()
        if end_time.hour > 18:
            end_time = end_time.replace(hour=18, minute=0, second=0)
        task.time_slots.append(TimeSlot(task.start_time, (end_time - task.start_time).total_seconds(), task.owner))

    db.session.commit()


import miami.views


# Create the Flask-Restless API manager.
auth_func = lambda: current_user.is_authenticated()
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Task, methods=['GET', 'POST', 'PUT', 'DELETE'], authentication_required_for=['POST', 'PUT'],
                   authentication_function=auth_func)
