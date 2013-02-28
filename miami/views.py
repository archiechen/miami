from flask import render_template, abort, flash, request, redirect, url_for, jsonify
from miami import app, db, utils
from miami.models import User, Task, TimeSlot, Team, NotPricing, NotEstimate, ReviewData, Category
from flask.ext.login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import or_
import simplejson as json

price_colors = {1: 'btn-success', 2: 'btn-info', 5: 'btn-primary', 10: 'btn-warning'}


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


@app.route('/current_user', methods=['GET'])
@login_required
def get_current_user():
    return jsonify(object=current_user.toJSON())


@app.route('/categories', methods=['GET'])
@login_required
def load_categories():
    return jsonify(objects=[c.toJSON() for c in Category.query.all()])


@app.route('/tasks', methods=['POST', 'PUT'])
@login_required
def create_task():
    if current_user.teams.count() == 0:
        abort(403)
    jsons = json.loads(request.data)
    if jsons.get('id', 0):
        task = Task.query.get_or_404(jsons.get('id'))
        task.title = jsons.get('title', '')
        db.session.commit()
        return jsonify(object=task.toJSON()), 200
    else:
        status = jsons.get('status', 'NEW')
        if status not in ['NEW', 'READY']:
            abort(403)
        price = jsons.get('price', 0)
        if status == 'READY' and price == 0:
            abort(403)

        task = Task(jsons.get('title'), jsons.get('detail'), status=status, price=price, team=current_user.teams[0])
        for category_name in jsons.get('categories', '').split(','):
            category = Category.query.filter(Category.name == category_name).first()
            if category:
                task.categories.append(category)
            else:
                task.categories.append(Category(category_name))
        db.session.add(task)
        db.session.commit()
        return jsonify(object=task.toJSON()), 201


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

    tasks = Task.query.filter(
        or_(*team_conditions)).order_by(Task.created_time.desc()).paginate(int(page), per_page=15, error_out=True)
    return render_template('tasks.html', pagination=tasks, user=current_user)


@app.route('/task/<task_id>', methods=['GET'])
@login_required
def load_task(task_id):
    return jsonify(object=Task.query.get_or_404(task_id).toJSON())


@app.route('/tasks/<status>', methods=['GET'])
@login_required
def load_tasks(status):
    team_conditions = [Task.team is None]
    team_id = int(request.args.get('team_id', '0'))
    if team_id > 0:
        team_conditions.append(Task.team == Team.query.get_or_404(team_id))
    else:
        for team in current_user.teams:
            team_conditions.append(Task.team == team)
    if status == 'DONE':
        return jsonify(objects=[t.toJSON() for t in Task.query.filter(Task.start_time > utils.get_current_monday(), Task.status == status, or_(*team_conditions))])
        # return render_template('task_card.html',
        # tasks=Task.query.filter(Task.start_time > utils.get_current_monday(),
        # Task.status == status, or_(*team_conditions)), user=current_user)
    return jsonify(objects=[t.toJSON() for t in Task.query.filter(Task.status == status, or_(*team_conditions))])


@app.route('/estimate/<tid>/<estimate>', methods=['PUT'])
@login_required
def estimate(tid, estimate):
    if estimate <= 0:
        abort(403)
    task = Task.query.get_or_404(tid)
    task.estimating(estimate)
    return jsonify(object=task.toJSON())


@app.route('/pricing/<tid>/<price>', methods=['PUT'])
@login_required
def pricing(tid, price):
    if price <= 0:
        abort(403)
    task = Task.query.get_or_404(tid)
    task.pricing(price)
    return jsonify(id=task.id)


@app.route('/jointask/<tid>', methods=['PUT'])
@login_required
def join_task(tid):
    task = current_user.join(tid)
    return jsonify(object=task.toJSON())


@app.route('/leavetask/<tid>', methods=['PUT'])
@login_required
def leave_task(tid):
    task = current_user.leave(tid)
    return jsonify(object=task.toJSON())


@app.route('/tasks/<status>/<tid>', methods=['PUT'])
@login_required
def to_status(status, tid):
    task = Task.query.get_or_404(tid)
    try:
        task.changeTo(status)
        return jsonify(object=task.toJSON())
    except NotPricing:
        return jsonify(id=task.id), 400
    except NotEstimate:
        return jsonify(id=task.id), 400


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
    return review_team(current_user.teams[0].id)


@app.route('/review/<team_id>', methods=['GET'])
@login_required
def review_team(team_id):
    team = Team.query.get(team_id)
    return render_template('review.html', review_data=team.review_data(utils.get_last_monday()), user=current_user)


@app.route('/review/<team_id>/member/<member_id>', methods=['GET'])
@login_required
def review_member(team_id, member_id):
    member = User.query.get(member_id)

    return render_template('review_personal.html', review_data=member.review_data(utils.get_last_monday(), team_id), personal_card=member.personal_card())


@app.route('/burning', methods=['GET'])
@login_required
def burning():
    return burning_team(current_user.teams[0].id)


@app.route('/burning/<team_id>', methods=['GET'])
@login_required
def burning_team(team_id):
    return render_template('burning.html', team=Team.query.get(team_id), user=current_user)


@app.route('/burning/team/<team_id>', methods=['GET'])
@login_required
def burning_team_ajax(team_id):
    team = Team.query.get_or_404(team_id)
    burning_data = json.loads(team.burning_data())
    return jsonify(remaining=[[idx + 1, value] for idx, value in enumerate(burning_data[0])], burning=[[idx + 1, value] for idx, value in enumerate(burning_data[1])])

@app.route('/burning/tasks', methods=['GET'])
@login_required
def burning_tasks():
    team_id = int(request.args.get('team_id', '0'))
    return jsonify(objects=[t.toJSON() for t in Team.query.get_or_404(team_id).daily_meeting_tasks()])

