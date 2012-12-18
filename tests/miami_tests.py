#-*- coding:utf-8 -*-

import unittest
import os
os.environ['MIAMI_ENV'] = 'test'
import miami
import simplejson as json
from datetime import datetime, timedelta
from mockito import when, unstub
from miami.models import Task, TimeSlot, User, Team, Category


def create_entity(entity):
    miami.db.session.add(entity)
    miami.db.session.commit()


class MiamiTest(unittest.TestCase):

    def setUp(self):
        self.app = miami.app.test_client()
        miami.init_db()
        team = Team('Log')
        team.members.append(User('Mike'))
        create_entity(team)
        create_entity(Category('BUG'))
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

    def test_create_task(self):
        rv = self.app.post('/tasks', data='{"title":"title1","detail":"detail1"}')

        self.assertEquals(201, rv.status_code)
        self.assertEquals({'object': {'detail': 'detail1',
                                      'estimate': 0,
                                      'id': 1,
                                      'owner': {},
                                      'partner': {},
                                      'price': 0,
                                      'status': 'NEW',
                                      'team': {'color': '2a33d8', 'name': 'Log'},
                                      'title': 'title1'}}, json.loads(rv.data))

        task = miami.Task.query.get(1)
        self.assertEquals('NEW', task.status)
        self.assertEquals(Team.query.get(1), task.team)

    def test_create_task_categories(self):
        rv = self.app.post('/tasks', data='{"title":"title1","detail":"detail1","categories":"Feature,Athena"}')

        self.assertEquals(201, rv.status_code)
        self.assertEquals({'object': {'detail': 'detail1',
                                      'estimate': 0,
                                      'id': 1,
                                      'owner': {},
                                      'partner': {},
                                      'price': 0,
                                      'status': 'NEW',
                                      'team': {'color': '2a33d8', 'name': 'Log'},
                                      'title': 'title1'}}, json.loads(rv.data))

        task = miami.Task.query.get(1)
        self.assertEquals('NEW', task.status)
        self.assertEquals(Team.query.get(1), task.team)
        self.assertEquals(2, len(task.categories))

    def test_create_task_duplicate_categories(self):
        rv = self.app.post('/tasks', data='{"title":"title1","detail":"detail1","categories":"BUG,Athena"}')

        self.assertEquals(201, rv.status_code)
        self.assertEquals({'object': {'detail': 'detail1',
                                      'estimate': 0,
                                      'id': 1,
                                      'price': 0,
                                      'status': 'NEW',
                                      'owner': {},
                                      'partner': {},
                                      'team': {'color': '2a33d8', 'name': 'Log'},
                                      'title': 'title1'}}, json.loads(rv.data))

        task = miami.Task.query.get(1)
        self.assertEquals('NEW', task.status)
        self.assertEquals(Team.query.get(1), task.team)
        self.assertEquals(2, len(task.categories))
        self.assertEquals(2, Category.query.count())

    def test_create_task_noteam(self):
        create_entity(User('Bob'))
        self.logout()
        self.login('Bob', '')
        rv = self.app.post('/tasks', data='{"title":"title1","detail":"detail1"}')

        self.assertEquals(403, rv.status_code)

    def test_create_task_invalid_status(self):
        rv = self.app.post('/tasks', data='{"title":"title1","detail":"detail1","status":"PROGRESS"}')

        self.assertEquals(403, rv.status_code)

    def test_create_task_ready_noprice(self):
        rv = self.app.post('/tasks', data='{"title":"title1","detail":"detail1","status":"READY","price":0}')

        self.assertEquals(403, rv.status_code)

    def test_create_task_logout(self):
        self.logout()
        rv = self.app.post('/api/task', data='{"title":"title1","detail":"detail1"}')

        self.assertEquals(401, rv.status_code)

    def test_load_task(self):
        create_entity(Task('title2', 'detail2', status='READY', price=10, team=Team.query.get(1)))
        create_entity(Task('title1', 'detail1', status='READY', price=10, team=Team('Refresh')))
        rv = self.app.get('/tasks/READY')

        self.assertEquals(200, rv.status_code)

        self.assertEquals({
                          "objects": [
                              {
                                  "title": "title2",
                                  "price": 10,
                                  "detail": "detail2",
                                  "status":'READY',
                                  "owner": {},
                                  "partner": {},
                                  "team": {
                                      "color": "2a33d8",
                                      "name": "Log"
                                  },
                                  "estimate": 0,
                                  "id": 1
                              }
                          ]
                          }, json.loads(rv.data))

    def test_load_task_done(self):
        create_entity(Task('title2', 'detail2', status='DONE', price=10, team=Team.query.get(1)))
        create_entity(Task('title1', 'detail1', status='DONE', price=10, start_time=miami.utils.now() - timedelta(days=7), team=Team.query.get(1)))
        rv = self.app.get('/tasks/DONE')

        self.assertEquals(200, rv.status_code)

        self.assertEquals({
                          "objects": [
                              {
                                  "title": "title2",
                                  "price": 10,
                                  "detail": "detail2",
                                  "status":'DONE',
                                  "owner": {},
                                  "partner": {},
                                  "team": {
                                      "color": "2a33d8",
                                      "name": "Log"
                                  },
                                  "estimate": 0,
                                  "id": 1
                              }
                          ]
                          }, json.loads(rv.data))

    def test_ready_to_progress_without_estimate(self):
        create_entity(Task('title1', 'detail1', status='READY'))

        rv = self.app.put('/tasks/PROGRESS/1')

        self.assertEquals(400, rv.status_code)

        self.assertEquals({'id': 1}, json.loads(rv.data))

    def test_ready_to_progress_without_estimate_logout(self):
        self.logout()
        create_entity(Task('title1', 'detail1', status='READY'))

        rv = self.app.put('/tasks/PROGRESS/1')

        self.assertEquals(401, rv.status_code)
        assert '<form action="/login" method="POST" class="form-horizontal">' in rv.data

    def test_ready_to_progress_with_estimate(self):
        create_entity(Task('title2', 'detail2', status='READY', estimate=10, team=Team.query.get(1)))

        rv = self.app.put('/tasks/PROGRESS/1')

        self.assertEquals(200, rv.status_code)
        task = Task.query.get(1)
        self.assertEquals('PROGRESS', task.status)

    def test_estimate(self):
        create_entity(Task('title1', 'detail1', status='READY', team=Team.query.get(1)))

        rv = self.app.put('/estimate/1/10')

        self.assertEquals('200 OK', rv.status)
        self.assertEquals({'object': {'detail': 'detail1',
                                      'estimate': 10,
                                      'id': 1,
                                      'owner': {'gravater': '91f376c4b36912e5075b6170d312eab5',
                                                'name': 'Mike'},
                                      'partner': {},
                                      'price': 0,
                                      'status': 'PROGRESS',
                                      'team': {'color': '2a33d8', 'name': 'Log'},
                                      'title': 'title1'}}, json.loads(rv.data))

        task = Task.query.get(1)
        self.assertEquals('PROGRESS', task.status)
        self.assertEquals('Mike', task.owner.name)

    def test_pricing(self):
        create_entity(Task('title1', 'detail1', status='NEW'))

        rv = self.app.put('/pricing/1/10')

        self.assertEquals(200, rv.status_code)

        self.assertEquals({"id": 1}, json.loads(rv.data))
        task = Task.query.get(1)
        self.assertEquals('READY', task.status)

    def test_ready_to_progress_noauth(self):
        task = Task('title2', 'detail2', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11))
        mike = User.query.get(1)
        task.owner = mike
        task.time_slots.append(TimeSlot(task.start_time, 20, mike))
        create_entity(task)
        create_entity(User('Bob'))
        self.logout()
        self.login('Bob', '')

        rv = self.app.put('/tasks/PROGRESS/1')

        self.assertEquals(401, rv.status_code)

    def test_progress_to_ready(self):
        task = Task('title2', 'detail2', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11), team=Team.query.get(1))
        task.owner = User.query.get(1)
        create_entity(task)

        rv = self.app.put('/tasks/READY/1')

        self.assertEquals(200, rv.status_code)
        task = Task.query.get(1)
        self.assertEquals('READY', task.status)
        self.assertEquals(60, task.consuming)
        self.assertEquals(1, task.time_slots[0].user.id)

    def test_multi_timeslots(self):
        create_entity(User('Bob'))
        task = Task('title2', 'detail2', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11), team=Team.query.get(1))
        task.time_slots.append(TimeSlot(task.start_time, 20, User.query.get(1)))
        task.owner = User.query.get(2)
        create_entity(task)
        self.logout()
        self.login('Bob', '')

        rv = self.app.put('/tasks/READY/1')

        self.assertEquals(200, rv.status_code)
        task = Task.query.get(1)
        self.assertEquals('READY', task.status)
        self.assertEquals(80, task.consuming)
        self.assertEquals(1, task.time_slots[0].user.id)
        self.assertEquals(2, task.time_slots[1].user.id)

    def test_new_to_ready_without_price(self):
        create_entity(Task('title', 'detail'))

        rv = self.app.put('/tasks/READY/1')
        self.assertEquals(400, rv.status_code)

        self.assertEquals({'id': 1}, json.loads(rv.data))

    def test_new_to_ready_with_price(self):
        create_entity(Task('title', 'detail', price=20, team=Team.query.get(1)))

        rv = self.app.put('/tasks/READY/1')
        self.assertEquals(200, rv.status_code)

        task = Task.query.get(1)
        self.assertEquals('READY', task.status)
        self.assertEquals(miami.utils.now(), task.ready_time)

    def test_owner_one_task(self):
        task = Task('title2', 'detail2', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11))
        task.owner = User.query.get(1)
        create_entity(task)
        create_entity(Task('title3', 'detail3', estimate=10, price=10, status='READY', start_time=datetime(2012, 11, 11)))
        rv = self.app.put('/tasks/PROGRESS/2')

        self.assertEquals(403, rv.status_code)
