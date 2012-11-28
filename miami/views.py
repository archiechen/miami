from flask import render_template, abort, flash, request, redirect, url_for, jsonify
from miami import app, db
from miami.models import User, Task, TimeSlot, Team, NotPricing, NotEstimate, ReviewData
from flask.ext.login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import or_
import simplejson as json

price_colors = {1: 'btn-success', 2: 'btn-info', 5: 'btn-primary', 10: 'btn-warning'}


def now():
    return datetime.now()


def get_last_monday():
    ctime = now().replace(hour=0, minute=0, second=0, microsecond=0)
    td = timedelta(days=(ctime.weekday() + 7))
    return ctime - td


def get_current_monday():
    ctime = now().replace(hour=0, minute=0, second=0, microsecond=0)
    td = timedelta(days=ctime.weekday())
    return ctime - td


def get_next_monday():
    td = timedelta(days=7)
    return get_current_monday() + td


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


@app.route('/tasks', methods=['POST'])
@login_required
def create_task():
    if current_user.teams.count() == 0:
        abort(403)
    jsons = json.loads(request.data)
    status = jsons.get('status', 'NEW')
    if status not in ['NEW', 'READY']:
        abort(403)
    task = Task(jsons.get('title'), jsons.get('detail'), status=status, team=current_user.teams[0])
    db.session.add(task)
    db.session.commit()
    return jsonify(id=task.id), 201


@app.route('/planning', methods=['GET'])
@login_required
def planning():
    return render_template('planning.html', user=current_user)


@app.route('/tasks/page/<page>', methods=['GET'])
@login_required
def load_tasks_page(page):
    team_conditions = [Task.team is None]
    for team in current_user.teams:
        team_conditions.append(Task.team == team)

    tasks = Task.query.filter(or_(*team_conditions)).order_by(Task.created_time.desc()).paginate(int(page), per_page=15, error_out=True)
    return render_template('tasks.html', pagination=tasks, user=current_user)


@app.route('/tasks/<status>', methods=['GET'])
@login_required
def load_tasks(status):
    team_conditions = [Task.team is None]
    for team in current_user.teams:
        team_conditions.append(Task.team == team)
    if status == 'DONE':
        return render_template('task_card.html', tasks=Task.query.filter(Task.start_time > get_current_monday(), Task.status == status, or_(*team_conditions)), user=current_user)
    return render_template('task_card.html', tasks=Task.query.filter(Task.status == status, or_(*team_conditions)), user=current_user)


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


@app.route('/review/<team_id>', methods=['GET'])
@login_required
def review(team_id):
    team = Team.query.get(team_id)
    return render_template('review.html', review_data=team.review_data(get_last_monday()), user=current_user)


@app.route('/review/<team_id>/member/<member_id>', methods=['GET'])
@login_required
def review_member(team_id, member_id):
    member = User.query.get(member_id)

    return render_template('review_personal.html', review_data=member.review_data(get_last_monday(), team_id), personal_card=member.personal_card())


@app.route('/burning/<team_id>', methods=['GET'])
@login_required
def burning(team_id):
    return render_template('burning.html',team = Team.query.get(team_id),user=current_user)