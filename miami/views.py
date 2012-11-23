from flask import render_template, abort, flash, request, redirect, url_for, jsonify
from miami import app, db
from miami.models import User, Task, TimeSlot, Team, NotPricing, NotEstimate, ReviewData
from flask.ext.login import login_user, logout_user, login_required, current_user
from datetime import datetime,timedelta
import simplejson as json


def now():
    return datetime.now()

def get_last_monday():
    ctime = now().replace(hour=0)
    td = timedelta(days=(ctime.weekday()+7))
    return ctime - td


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


@app.route('/tasks', methods=['POST'])
@login_required
def create_task():
    if current_user.teams.count() == 0:
        abort(403)
    jsons = json.loads(request.data)
    task = Task(jsons.get('title'), jsons.get('detail'), team=current_user.teams[0])
    db.session.add(task)
    db.session.commit()
    return jsonify(id=task.id), 201


@app.route('/planning', methods=['GET'])
@login_required
def planning():
    return render_template('planning.html', user=current_user)


@app.route('/tasks/<status>', methods=['GET'])
@login_required
def load_tasks(status):
    tasks = []
    for team in current_user.teams:
        [tasks.append(t) for t in Task.query.filter(Task.status == status, Task.team == team)]

    return render_template('task_card.html', tasks=tasks, user=current_user)


@app.route('/estimate/<tid>/<estimate>', methods=['PUT'])
@login_required
def estimate(tid, estimate):
    task = Task.query.get_or_404(tid)
    task.estimating(estimate)
    return render_template('task_card.html', tasks=[task], user=current_user)


@app.route('/pricing/<tid>/<price>', methods=['PUT'])
@login_required
def pricing(tid, price):
    task = Task.query.get_or_404(tid)
    task.pricing(price)
    return render_template('task_card.html', tasks=[task], user=current_user)


@app.route('/jointask/<tid>', methods=['PUT'])
@login_required
def join_task(tid):
    task = current_user.join(tid)
    return render_template('task_card.html', tasks=[task], user=current_user)


@app.route('/leavetask/<tid>', methods=['PUT'])
@login_required
def leave_task(tid):
    task = current_user.leave(tid)
    return render_template('task_card.html', tasks=[task], user=current_user)


@app.route('/tasks/<status>/<tid>', methods=['PUT'])
@login_required
def to_status(status, tid):
    task = Task.query.get_or_404(tid)
    try:
        task.changeTo(status)
        return render_template('task_card.html', tasks=[task], user=current_user)
    except NotPricing:
        return render_template('price.html', task=task), 400
    except NotEstimate:
        return render_template('estimate.html', task=task), 400


@app.route('/teams', methods=['GET'])
@login_required
def new_team():
    return render_template('teams.html', user=current_user)


@app.route('/load_teams', methods=['GET'])
@login_required
def load_teams():
    return render_template('team_card.html', teams=Team.query.all(), user=current_user)


@app.route('/teams/join/<team_id>', methods=['PUT'])
@login_required
def join_team(team_id):
    team = Team.query.get_or_404(team_id)
    team.members.append(current_user)
    db.session.commit()
    return render_template('team_card.html', teams=[team], user=current_user)


@app.route('/teams/leave/<team_id>', methods=['PUT'])
@login_required
def leave_team(team_id):
    team = Team.query.get_or_404(team_id)
    team.remove_member(current_user)
    db.session.commit()
    return render_template('team_card.html', teams=[team], user=current_user)


@app.route('/review', methods=['GET'])
@login_required
def review():
    time_slots = TimeSlot.query.filter(TimeSlot.start_time > get_last_monday())
    review_data = ReviewData()
    for ts in time_slots:
        review_data.merge(ts)

    return render_template('review.html', review_data=review_data, user=current_user)
