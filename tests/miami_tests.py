#-*- coding:utf-8 -*-

import unittest
import os
import tempfile
import miami
import simplejson as json
from datetime import datetime
from mockito import when
from miami import Task, TimeSlot, User


def create_entity(entity):
    miami.db.session.add(entity)
    miami.db.session.commit()


when(miami).now().thenReturn(datetime(2012, 11, 11, 0, 1, 0))


class MiamiTest(unittest.TestCase):

    def setUp(self):
        self.db_fd, miami.app.config['DATABASE'] = tempfile.mkstemp()
        miami.app.config['TESTING'] = True
        self.app = miami.app.test_client()
        miami.init_db()
        create_entity(User('Mike'))

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(miami.app.config['DATABASE'])

    def test_create_task(self):
        rv = self.app.post('/api/task', data='{"title":"title1","detail":"detail1"}')

        self.assertEquals(201, rv.status_code)
        self.assertEquals({"id": 1}, json.loads(rv.data))

        task = miami.Task.query.get(1)
        self.assertEquals('NEW', task.status)

    def test_ready_to_progress_without_estimate(self):
        create_entity(Task('title1', 'detail1', status='READY'))

        rv = self.app.put('/tasks/PROGRESS/1')

        self.assertEquals(400, rv.status_code)

        assert '<h3 id="myModalLabel">Estimate</h3>' in rv.data
        assert '<h4>title1</h4>' in rv.data
        assert '<p>detail1</p>' in rv.data
        assert '<input id="estimate" type="text" class="input-small" placeholder="estimate" value="0"/>' in rv.data

    def test_ready_to_progress_with_estimate(self):
        create_entity(Task('title2', 'detail2', status='READY', estimate=10))

        rv = self.app.put('/tasks/PROGRESS/1')

        self.assertEquals(200, rv.status_code)
        task = Task.query.get(1)
        self.assertEquals('PROGRESS', task.status)

    def test_estimate(self):
        create_entity(Task('title1', 'detail1'))

        rv = self.app.put('/api/task/1', data='{"status":"PROGRESS","estimate":10}')

        self.assertEquals('200 OK', rv.status)
        updated = json.loads(rv.data)
        self.assertEquals('PROGRESS', updated['status'])
        self.assertEquals(10, updated['estimate'])

    def test_progress_to_ready(self):
        create_entity(Task('title2', 'detail2', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11)))
        user = User.query.get(1)
        when(miami).current_user().thenReturn(user)
        rv = self.app.put('/tasks/READY/1')

        self.assertEquals(200, rv.status_code)
        task = Task.query.get(1)
        self.assertEquals('READY', task.status)
        self.assertEquals(60, task.consuming)
        self.assertEquals(1, task.time_slots[0].user.id)

    def test_multi_timeslots(self):
        task = Task('title2', 'detail2', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11))
        task.time_slots.append(TimeSlot(task.start_time, 20, User.query.get(1)))
        create_entity(task)
        create_entity(User('Bob'))
        when(miami).current_user().thenReturn(User.query.get(2))

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

        assert '<h3 id="myModalLabel">Pricing</h3>' in rv.data
        assert '<h4>title</h4>' in rv.data
        assert '<p>detail</p>' in rv.data
        assert '<input id="price" type="text" class="input-small" placeholder="price" value="0"/>' in rv.data

    def test_new_to_ready_with_price(self):
        create_entity(Task('title', 'detail', price=20))

        rv = self.app.put('/tasks/READY/1')
        self.assertEquals(200, rv.status_code)

        task = Task.query.get(1)
        self.assertEquals('READY', task.status)
id