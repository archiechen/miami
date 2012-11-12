#-*- coding:utf-8 -*-

import unittest
import os
import tempfile
import miami
import simplejson as json
from datetime import datetime
from mockito import when

when(miami).now().thenReturn(datetime(2012, 11, 11, 0, 1, 0))


def create_task(task):
    miami.db.session.add(task)
    miami.db.session.commit()


class Test(unittest.TestCase):

    def setUp(self):
        self.db_fd, miami.app.config['DATABASE'] = tempfile.mkstemp()
        miami.app.config['TESTING'] = True
        self.app = miami.app.test_client()
        miami.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(miami.app.config['DATABASE'])

    def test_create_task(self):
        rv = self.app.post('/api/task', data='{"title":"title1","detail":"detail1"}')

        self.assertEquals(201, rv.status_code)
        self.assertEquals({"id": 1}, json.loads(rv.data))

        task = miami.Task.query.get(1)
        self.assertEquals('NEW', task.status)

    def test_new_to_progress_without_estimate(self):
        create_task(miami.Task('title1', 'detail1'))

        rv = self.app.put('/tasks/PROGRESS/1')

        self.assertEquals(400, rv.status_code)

        assert '<h3 id="myModalLabel">Estimate</h3>' in rv.data
        assert '<h4>title1</h4>' in rv.data
        assert '<p>detail1</p>' in rv.data
        assert '<input id="estimate" type="text" class="input-small" placeholder="estimate" value="0"/>' in rv.data

    def test_new_to_progress_with_estimate(self):
        create_task(miami.Task('title2', 'detail2', estimate=10))

        rv = self.app.put('/tasks/PROGRESS/1')

        self.assertEquals(200, rv.status_code)
        task = miami.Task.query.get(1)
        self.assertEquals('PROGRESS', task.status)

    def test_estimate(self):
        create_task(miami.Task('title1', 'detail1'))

        rv = self.app.put('/api/task/1', data='{"status":"PROGRESS","estimate":10}')

        self.assertEquals('200 OK', rv.status)
        updated = json.loads(rv.data)
        self.assertEquals('PROGRESS', updated['status'])
        self.assertEquals(10, updated['estimate'])

    def test_progress_to_ready(self):
        create_task(miami.Task('title2', 'detail2', estimate=10, price=10,status='PROGRESS', start_time=datetime(2012, 11, 11)))
        rv = self.app.put('/tasks/READY/1')

        self.assertEquals(200, rv.status_code)
        task = miami.Task.query.get(1)
        self.assertEquals('READY', task.status)
        self.assertEquals(60, task.consuming)
