from flask import Flask, render_template, abort, flash, request, redirect, url_for
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
    created_time = db.Column(db.DateTime, default=datetime.now)
    start_time = db.Column(db.DateTime)
    time_slots = db.relationship('TimeSlot', backref='task',
                                 lazy='dynamic')
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship("User", primaryjoin='User.id==Task.owner_id')
    partner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    partner = db.relationship("User", primaryjoin='User.id==Task.partner_id')

    def __init__(self, title, detail, estimate=0, price=0, status='NEW', start_time=datetime.now()):
        self.title = title
        self.detail = detail
        self.price = price
        self.estimate = estimate
        self.status = status
        self.start_time = start_time

    def __getattr__(self, name):
        if name == 'consuming':
            return math.fsum([ts.consuming for ts in self.time_slots])

        return db.Model.__getattr__(self.name)


class TimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    start_time = db.Column(db.DateTime, default=datetime.now)
    consuming = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", primaryjoin='User.id==TimeSlot.user_id')
    partner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    partner = db.relationship("User", primaryjoin='User.id==TimeSlot.partner_id')

    def __init__(self, start_time, consuming, user, partner=None):
        self.consuming = consuming
        self.start_time = start_time
        self.user = user
        self.partner = partner


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    active = db.Column(db.Boolean)

    def __init__(self, name, active=True):
        self.name = name
        self.active = active

    def is_active(self):
        return self.active


class Anonymous(AnonymousUser):
    name = u"Anonymous"


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


@app.errorhandler(401)
def unauthorized(e):
    return render_template('login.html', message='please login.'), 401


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST" and "username" in request.form:
        user = User.query.filter_by(name=request.form["username"]).first()
        if user:
            if login_user(user):
                flash("Logged in!")
                return redirect(request.args.get("next") or url_for("index"))
            else:
                flash("Sorry, but you could not log in.")
        else:
            flash(u"Invalid username.")
    return render_template("login.html", error=error)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route('/', methods=['GET'])
@login_required
def index():
    return render_template('dashborad.html', user=current_user)


@app.route('/tasks', methods=['GET'])
@login_required
def new_task():
    return render_template('tasks.html', user=current_user)


@app.route('/planning', methods=['GET'])
@login_required
def planning():
    return render_template('planning.html', user=current_user)


@app.route('/tasks/PROGRESS/<tid>/<estimate>', methods=['PUT'])
@login_required
def estimate(tid, estimate):
    task = Task.query.get_or_404(tid)
    if task.status == 'READY' or task.status == 'DONE':
        task.estimate = estimate
        task.status = 'PROGRESS'
        task.start_time = now()
        task.owner = current_user
        db.session.commit()
        return render_template('task_card.html', task=task)

    abort(400)


@app.route('/jointask/<tid>', methods=['PUT'])
@login_required
def join_task(tid):
    task = Task.query.get_or_404(tid)
    task.partner = current_user
    current_time = now()
    task.time_slots.append(TimeSlot(task.start_time, (current_time - task.start_time).total_seconds(), task.owner))
    task.start_time = current_time
    db.session.commit()
    return render_template('task_card.html', task=task)


@app.route('/tasks/<status>/<tid>', methods=['PUT'])
@login_required
def to_status(status, tid):
    task = Task.query.get_or_404(tid)
    if task.owner and task.owner.id != current_user.id:
        abort(401)
    if task.status == 'PROGRESS' and (status == 'READY' or status == 'DONE'):
        task.time_slots.append(TimeSlot(task.start_time, (now() - task.start_time).total_seconds(), current_user, partner=task.partner))
        task.partner = None
    if status == 'READY' and task.price == 0:
        return render_template('price.html', task=task), 400
    if status == 'PROGRESS':
        if Task.query.filter_by(owner=current_user, status='PROGRESS').count() > 0:
            abort(403)

        if task.estimate == 0:
            return render_template('estimate.html', task=task), 400
        else:
            task.start_time = datetime.now()

    task.status = status
    db.session.commit()

    return render_template('task_card.html', task=task)


# Create the Flask-Restless API manager.
auth_func = lambda: current_user.is_authenticated()
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Task, methods=['GET', 'POST', 'PUT', 'DELETE'], authentication_required_for=['POST', 'PUT'],
                   authentication_function=auth_func)
