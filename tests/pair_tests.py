#-*- coding:utf-8 -*-

import unittest
import os
os.environ['MIAMI_ENV'] = 'test'
import miami
import simplejson as json
from datetime import datetime
from mockito import when, unstub
from miami.models import Task, TimeSlot, User, Team


def create_entity(entity):
    miami.db.session.add(entity)
    miami.db.session.commit()


class PairTest(unittest.TestCase):

    def setUp(self):
        self.app = miami.app.test_client()
        miami.init_db()
        team = Team('Log')
        team.members.append(User('Mike'))
        team.members.append(User('Bob'))

        create_entity(team)
        when(miami.utils).now().thenReturn(datetime(2012, 11, 11, 0, 1, 0))
        self.login('Mike', '')

    def tearDown(self):
        unstub()

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_join_partner(self):
        task = Task('title2', 'detail2', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11), team=Team.query.get(1))
        task.owner = User.query.get(2)
        create_entity(task)

        rv = self.app.put('/jointask/1')

        self.assertEquals(200, rv.status_code)
        self.assertEquals({
                          "object": {
                              "status": "PROGRESS",
                              "owner": {
                                  "gravater": "91f376c4b36912e5075b6170d312eab5",
                                  "name": "Bob"
                              },
                              "title": "title2",
                              "estimate": 10,
                              "partner": {
                                  "gravater": "91f376c4b36912e5075b6170d312eab5",
                                  "name": "Mike"
                              },
                              "price": 10,
                              "team": {
                                  "color": "2a33d8",
                                  "name": "Log"
                              },
                              "id": 1,
                              "detail": "detail2"
                          }
                          }, json.loads(rv.data))
        task = Task.query.get(1)
        self.assertEquals(1, task.time_slots.count())
        self.assertEquals('PROGRESS', task.status)
        self.assertEquals(60, task.time_slots[0].consuming)
        self.assertEquals('Bob', task.time_slots[0].user.name)
        self.assertIsNone(task.time_slots[0].partner)
        self.assertEquals(task.start_time, miami.utils.now())

    def test_paired_to_done(self):
        task = Task('title2', 'detail2', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11), team=Team.query.get(1))
        task.owner = User.query.get(1)
        task.partner = User.query.get(2)
        task.start_time = datetime(2012, 11, 11, 0, 1, 0)
        task.time_slots.append(TimeSlot(task.start_time, 60, task.owner))
        create_entity(task)

        when(miami.utils).now().thenReturn(datetime(2012, 11, 11, 0, 2, 0))
        rv = self.app.put('/tasks/DONE/1')

        self.assertEquals(200, rv.status_code)
        self.assertEquals({'object': {'detail': 'detail2',
                                      'estimate': 10,
                                      'id': 1,
                                      'owner': {},
                                      'partner': {},
                                      'price': 10,
                                      'status': 'DONE',
                                      'team': {'color': '2a33d8', 'name': 'Log'},
                                      'title': 'title2'}}, json.loads(rv.data))

        task = Task.query.get(1)
        self.assertIsNone(task.partner)
        self.assertIsNone(task.owner)
        self.assertEquals('DONE', task.status)
        self.assertEquals(2, task.time_slots.count())
        self.assertEquals(60, task.time_slots[0].consuming)
        self.assertEquals('Mike', task.time_slots[0].user.name)
        self.assertIsNone(task.time_slots[0].partner)
        self.assertEquals(60, task.time_slots[1].consuming)
        self.assertEquals('Mike', task.time_slots[1].user.name)
        self.assertEquals('Bob', task.time_slots[1].partner.name)

    def test_leave_paired(self):
        task = Task('title2', 'detail2', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11), team=Team.query.get(1))
        task.owner = User.query.get(2)
        task.partner = User.query.get(1)
        create_entity(task)

        rv = self.app.put('/leavetask/1')

        self.assertEquals(200, rv.status_code)
        self.assertEquals({
              "object": {
                  "status": "PROGRESS",
                  "owner": {
              "gravater": "91f376c4b36912e5075b6170d312eab5",
              "name": "Bob"
                  },
                  "title": "title2",
                  "estimate": 10,
                  "partner": {
                  },
                  "price": 10,
                  "team": {
              "color": "2a33d8",
              "name": "Log"
                  },
                  "id": 1,
                  "detail": "detail2"
              }
        }, json.loads(rv.data))

        task = Task.query.get(1)
        self.assertIsNone(task.partner)
        self.assertEquals('PROGRESS', task.status)
        self.assertEquals(1, task.time_slots.count())
        self.assertEquals(datetime(2012, 11, 11, 0, 1, 0), task.start_time)
        self.assertEquals(60, task.time_slots[0].consuming)
        self.assertEquals('Bob', task.time_slots[0].user.name)
        self.assertEquals('Mike', task.time_slots[0].partner.name)

    def test_not_allow_join(self):
        create_entity(User('Bob'))
        task = Task('title1', 'detail1', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11))
        task.owner = User.query.get(2)
        create_entity(task)
        task = Task('title2', 'detail2', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11))
        task.owner = User.query.get(1)
        create_entity(task)

        rv = self.app.put('/jointask/1')

        self.assertEquals(403, rv.status_code)

    def test_not_allow_multi_paired(self):
        create_entity(User('Bob'))
        create_entity(User('Martin'))
        task = Task('title1', 'detail1', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11))
        task.partner = User.query.get(1)
        task.owner = User.query.get(2)
        create_entity(task)
        task = Task('title2', 'detail2', estimate=10, price=10, status='READY', start_time=datetime(2012, 11, 11))
        task.owner = User.query.get(3)
        create_entity(task)

        rv = self.app.put('/jointask/2')

        self.assertEquals(403, rv.status_code)

    def test_not_allow_to_progress(self):
        create_entity(User('Bob'))
        task = Task('title1', 'detail1', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11))
        task.partner = User.query.get(1)
        task.owner = User.query.get(2)
        create_entity(task)
        create_entity(Task('title2', 'detail2', estimate=10, price=10, status='READY', start_time=datetime(2012, 11, 11)))

        rv = self.app.put('/tasks/PROGRESS/2')

        self.assertEquals(403, rv.status_code)