from flask import render_template, abort, flash, request, redirect, url_for
from miami import app, db
from miami.models import User, Task, TimeSlot, NotPricing, NotEstimate
from flask.ext.login import login_user, logout_user, login_required, current_user
from datetime import datetime


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


@app.route('/tasks/<status>', methods=['GET'])
@login_required
def load_tasks(status):
    tasks = Task.query.filter_by(status=status)

    return render_template('task_card.html', tasks=tasks, user=current_user)


@app.route('/estimate/<tid>/<estimate>', methods=['PUT'])
@login_required
def estimate(tid, estimate):
    task = Task.query.get_or_404(tid)
    if task.status == 'READY' or task.status == 'DONE':
        task.estimate = estimate
        task.status = 'PROGRESS'
        task.start_time = now()
        task.owner = current_user
        db.session.commit()
        return render_template('task_card.html', tasks=[task], user=current_user)

    abort(400)


@app.route('/pricing/<tid>/<price>', methods=['PUT'])
@login_required
def pricing(tid, price):
    task = Task.query.get_or_404(tid)
    if task.status == 'NEW':
        task.price = price
        task.status = 'READY'
        db.session.commit()
        return render_template('task_card.html', tasks=[task], user=current_user)

    abort(400)


@app.route('/jointask/<tid>', methods=['PUT'])
@login_required
def join_task(tid):
    current_user.check_progress()
    task = Task.query.get_or_404(tid)
    task.partner = current_user
    current_time = now()
    task.time_slots.append(TimeSlot(task.start_time, (current_time - task.start_time).total_seconds(), task.owner))
    task.start_time = current_time
    db.session.commit()
    return render_template('task_card.html', tasks=[task], user=current_user)


@app.route('/leavetask/<tid>', methods=['PUT'])
@login_required
def leave_task(tid):
    task = Task.query.get_or_404(tid)
    task.partner = None
    current_time = now()
    task.time_slots.append(TimeSlot(task.start_time, (current_time - task.start_time).total_seconds(), task.owner, partner=current_user))
    task.start_time = current_time
    db.session.commit()
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
