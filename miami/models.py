#-*- coding:utf-8 -*-

from miami import db
from datetime import datetime, timedelta
from flask.ext.login import UserMixin, AnonymousUser, current_user
from flask import abort, render_template
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden
from sqlalchemy import or_

import math
import hashlib
import simplejson as json

price_colors={1:'badge-success',2:'badge-info',5:'badge-warning',10:'badge-important'}

def now():
    return datetime.now()

class NewState(object):
    def to(self, task, status):
        if task.status == 'NEW' and status == 'READY':
            if task.price == 0:
                raise NotPricing()
            task.start_time=now()
        else:
            raise BadRequest


class ReadyState(object):
    def to(self, task, status):
        if task.status == 'READY' and (status == 'PROGRESS' or status == 'NEW'):
            if status == 'PROGRESS':
                current_user.check_progress()
                if task.estimate == 0:
                    raise NotEstimate()

                task.start_time = datetime.now()
                task.owner = current_user
        else:
            raise BadRequest


class ProgressState(object):
    def to(self, task, status):
        if task.status == 'PROGRESS' and (status == 'READY' or status == 'DONE'):
            task.time_slots.append(TimeSlot(task.start_time, (now() - task.start_time).total_seconds(), current_user, partner=task.partner))
            task.partner = None
            task.owner = None
        else:
            raise BadRequest


class DoneState(object):
    def to(self, task, status):
        if task.status == 'DONE' and (status == 'READY' or status == 'PROGRESS'):
            if status == 'PROGRESS':
                task.owner = current_user
        else:
            raise BadRequest

task_state = {'NEW': NewState(), 'READY': ReadyState(), 'PROGRESS': ProgressState(), 'DONE': DoneState()}

members = db.Table('members',
                   db.Column('team_id', db.Integer, db.ForeignKey('team.id')),
                   db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                   )


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    members = db.relationship('User', secondary=members,
                              backref=db.backref('teams', lazy='dynamic'))

    def __init__(self, name):
        self.name = name

    def __getattr__(self, name):
        if name == 'color':
            return hashlib.sha224(self.name).hexdigest()[0:6]

        return db.Model.__getattr__(name)

    def has_member(self, user):
        for member in self.members:
            if member.id == user.id:
                return True
        return False

    def remove_member(self, user):
        for member in self.members:
            if member.id == user.id:
                self.members.remove(member)

    def review_data(self, last_monday):
        time_slots = TimeSlot.query.join(TimeSlot.task).filter(TimeSlot.start_time > last_monday, TimeSlot.start_time < last_monday + timedelta(days=7), Task.team == self)
        review_data = ReviewData()
        for ts in time_slots:
            review_data.merge(ts)
        review_data.merge_ready(Task.query.filter(Task.start_time > last_monday, Task.start_time < last_monday + timedelta(days=7), Task.status == 'READY', Task.team == self))

        return review_data


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

    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))
    team = db.relationship("Team")

    def __init__(self, title, detail, estimate=0, price=0, status='NEW', start_time=datetime.now(), team=None):
        self.title = title
        self.detail = detail
        self.price = price
        self.estimate = estimate
        self.status = status
        self.start_time = start_time
        self.team = team

    def __getattr__(self, name):
        if name == 'consuming':
            return math.fsum([ts.consuming for ts in self.time_slots])

        return db.Model.__getattr__(name)

    def changeTo(self, status):
        if self.owner and self.owner.id != current_user.id:
            raise Unauthorized()
        global task_state
        task_state[self.status].to(self, status)
        self.status = status
        db.session.commit()

    def estimating(self, estimate):
        if self.status == 'READY':
            self.estimate = estimate
            self.status = 'PROGRESS'
            self.start_time = now()
            self.owner = current_user
            db.session.commit()
        else:
            raise BadRequest()

    def pricing(self, price):
        if self.status == 'NEW':
            self.price = price
            self.status = 'READY'
            self.start_time = now()
            db.session.commit()
        else:
            raise BadRequest()

    def price_color(self):
        global price_colors
        return price_colors[self.price]

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
    email = db.Column(db.String(100))
    active = db.Column(db.Boolean)

    def __init__(self, name, email='default@gmail.com', active=True):
        self.name = name
        self.email = email
        self.active = active

    def is_active(self):
        return self.active

    def check_progress(self):
        if Task.query.filter_by(owner=self, status='PROGRESS').count() > 0 or Task.query.filter_by(partner=self, status='PROGRESS').count() > 0:
                raise Forbidden()

    def join(self, tid):
        self.check_progress()
        task = Task.query.get_or_404(tid)
        task.partner = self
        current_time = now()
        task.time_slots.append(TimeSlot(task.start_time, (current_time - task.start_time).total_seconds(), task.owner))
        task.start_time = current_time
        db.session.commit()
        return task

    def leave(self, tid):
        task = Task.query.get_or_404(tid)
        task.partner = None
        current_time = now()
        task.time_slots.append(TimeSlot(task.start_time, (current_time - task.start_time).total_seconds(), task.owner, partner=self))
        task.start_time = current_time
        db.session.commit()
        return task

    def personal_card(self):
        card = PersonCard(self)
        ts = TimeSlot.query.filter(or_(TimeSlot.user == self, TimeSlot.partner == self))
        for m_ts in ts:
            card.merge(m_ts)
        return card

    def review_data(self, last_monday, team_id):
        time_slots = TimeSlot.query.join(TimeSlot.task).filter(TimeSlot.start_time > last_monday, TimeSlot.start_time < last_monday + timedelta(days=7), Task.team == Team.query.get(team_id), or_(TimeSlot.user == self, TimeSlot.partner == self))
        review_data = ReviewData()
        for ts in time_slots:
            review_data.merge_personal(self, ts)
        return review_data

    def team_id(self):
        if self.teams.count():
            return self.teams[0].id
        return 0


class PersonCard(object):
    def __init__(self, user):
        self.user = user
        self.fortune = 0
        self.working_hours = 0
        self.valuable_hours = 0
        self.estimate = 0
        self.paired_hours = 0
        self.tasks = {}

    def merge(self, ts):
        if ts.task.id not in self.tasks:
            self.tasks[ts.task.id] = ts.task
            if ts.task.status == 'DONE':
                self.fortune += ts.task.price
                self.valuable_hours += ts.consuming / 3600.0
                if ts.user == self.user:
                    self.estimate += ts.task.estimate
        self.working_hours += ts.consuming / 3600.0
        if ts.user == self.user and ts.partner:
            self.paired_hours += ts.consuming / 3600.0
        if ts.partner == self.user:
            self.paired_hours += ts.consuming / 3600.0

    def estimate_deviation(self):
        if self.estimate < self.valuable_hours:
            return'{0:0.2%}'.format(self.estimate / self.valuable_hours if self.valuable_hours > 0 else 0)
        return'{0:0.2%}'.format(self.valuable_hours / self.estimate if self.estimate > 0 else 0)

    def paired_ratio(self):
        return'{0:0.2%}'.format(self.paired_hours / self.working_hours if self.working_hours > 0 else 0)

    def total_hours(self):
        return'{0:0.2g}'.format(self.working_hours)


class ReviewData(object):
    def __init__(self):
        self.price = 0
        self.done_price = 0
        self.estimate = 0
        self.working_hours = 0
        self.valuable_hours = 0
        self.paired_time = 0
        self.tasks = {}

    def merge(self, ts):
        if ts.task.id not in self.tasks:
            self.price += ts.task.price
            if ts.task.status == 'DONE':
                self.estimate += ts.task.estimate
                self.done_price += ts.task.price
                self.valuable_hours += ts.consuming / 3600.0
            self.tasks[ts.task.id] = ts.task
        self.working_hours += ts.consuming / 3600.0
        if ts.partner:
            self.paired_time += ts.consuming / 3600.0

    def merge_ready(self, ready_tasks):
        for rt in ready_tasks:
            if rt.id not in self.tasks:
                self.price += rt.price

    def merge_personal(self, person, ts):
        if ts.task.id not in self.tasks:
            self.price += ts.task.price
            if ts.task.status == 'DONE':
                if ts.user == person:
                    self.estimate += ts.task.estimate
                self.done_price += ts.task.price
                self.valuable_hours += ts.consuming / 3600.0
            self.tasks[ts.task.id] = ts.task
        self.working_hours += ts.consuming / 3600.0
        if ts.partner:
            self.paired_time += ts.consuming / 3600.0

    def price_ratio(self):
        ratio = [['$1', 0], ['$2', 0], ['$5', 0], ['$10', 0]]
        for tid, task in self.tasks.iteritems():
            if task.status == 'DONE':
                if task.price == 1:
                    ratio[0][1] += 1
                if task.price == 2:
                    ratio[1][1] += 1
                if task.price == 5:
                    ratio[2][1] += 1
                if task.price == 10:
                    ratio[3][1] += 1
        return str(ratio)


class Anonymous(AnonymousUser):
    name = u"Anonymous"


class NotPricing(BadRequest):
    pass


class NotEstimate(BadRequest):
    pass
