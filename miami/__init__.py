from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import flask.ext.restless
from datetime import datetime
import math
import os
from flask.ext.login import LoginManager, UserMixin, AnonymousUser, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config.from_object('miami.default_config')
app.config["DEBUG"] = False

# Dev run mode
if os.getenv('MIAMI_ENV') == 'dev':
    app.config["DEBUG"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"

# Test run mode
elif os.getenv('MIAMI_ENV') == 'test':
    app.config["DEBUG"] = True
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

# Production run mode
elif os.getenv('MIAMI_ENV') == 'prod':
    # Get port number from Heroku environment variable
    app_run_args['port'] = 5000
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://miami:miami@localhost:3306/miami'

db = SQLAlchemy(app)
import miami.models
from miami.models import Anonymous, Task, TimeSlot, User

login_manager = LoginManager()
login_manager.anonymous_user = Anonymous


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

login_manager.setup_app(app)

# Create the Flask-Restless API manager.
auth_func = lambda: current_user.is_authenticated()
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Task, methods=['GET', 'POST', 'DELETE'], authentication_required_for=['POST', 'DELETE'],
                   authentication_function=auth_func)

import miami.views


def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()


def now():
    return datetime.now()


def zeroing():
    app.logger.debug('zeroing')
    tasks = Task.query.filter_by(status='PROGRESS')

    for task in tasks:
        task.status = 'READY'
        end_time = now()
        if end_time.hour > 18:
            end_time = end_time.replace(hour=18, minute=0, second=0)
        task.time_slots.append(TimeSlot(task.start_time, (end_time - task.start_time).total_seconds(), task.owner))

    db.session.commit()
