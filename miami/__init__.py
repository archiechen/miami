from flask import Flask, render_template
import flask.ext.sqlalchemy
import flask.ext.restless


# Create the Flask application and the Flask-SQLAlchemy object.
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

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
    status = db.Column(db.String(10),default = 'NEW')


# Create the database tables.
db.create_all()

@app.route('/', methods=['GET'])
def index():
    return render_template('dashborad.html')

@app.route('/new_task', methods=['GET'])
def new_task():
    return render_template('new_task.html')

@app.route('/planning', methods=['GET'])
def planning():
    return render_template('planning.html')

# Create the Flask-Restless API manager.
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(Task, methods=['GET', 'POST','PUT', 'DELETE'])


