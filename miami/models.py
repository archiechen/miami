from miami import db
from datetime import datetime
from flask.ext.login import UserMixin, AnonymousUser

import math


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