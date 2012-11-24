#-*- coding:utf-8 -*-

import unittest
import os
os.environ['MIAMI_ENV'] = 'test'
import miami
import simplejson as json
from datetime import datetime
from miami.models import Team, User, Task, TimeSlot
from miami import db
from tests import BaseTestCase
from mockito import when


class ReviewTest(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)
        when(miami.views).now().thenReturn(datetime(2012, 11, 5, 9, 0, 0))

    def test_review(self):
        team = Team('Miami')
        team.members.append(User('Bob'))
        task = Task('title1', 'detail', status='DONE', price=2, estimate=4, team=team)
        ts = TimeSlot(datetime(2012, 11, 1, 10, 0, 0), 3600, User.query.get(1))
        task.time_slots.append(ts)
        self.create_entity(task)
        task = Task('title2', 'detai2', status='NEW', price=2, estimate=4, team=team)
        ts = TimeSlot(datetime(2012, 11, 2, 10, 0, 0), 3600, User.query.get(1),partner=User.query.get(2))
        task.time_slots.append(ts)
        self.create_entity(task)

        rv = self.app.get('/review')

        print rv.data

        self.assertEquals(200, rv.status_code)