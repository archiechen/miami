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


class PairTest(unittest.TestCase):

    def setUp(self):
        self.db_fd, miami.app.config['DATABASE'] = tempfile.mkstemp()
        miami.app.config['TESTING'] = True
        self.app = miami.app.test_client()
        miami.init_db()
        create_entity(User('Mike'))
        self.login('Mike', '')

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(miami.app.config['DATABASE'])

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_join_partner(self):
        create_entity(User('Bob'))
        task = Task('title2', 'detail2', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11))
        task.owner = User.query.get(2)
        create_entity(task)

        rv = self.app.put('/jointask/1')

        self.assertEquals(200, rv.status_code)
        assert '<h5>title2</h5>' in rv.data
        assert '<small>PROGRESS</small>' in rv.data
        assert '<p class="text-warning">$10</p>' in rv.data
        assert '<p class="text-info">10H</p>' in rv.data
        assert '<p class="text-info">60.0S</p>' in rv.data
        assert '<p class="text-info">Mike</p>' in rv.data
        assert '<p class="text-info">Bob</p>' in rv.data

        task = Task.query.get(1)
        self.assertEquals(1, task.time_slots.count())
        self.assertEquals(60, task.time_slots[0].consuming)
        self.assertEquals('Bob', task.time_slots[0].user.name)
        self.assertIsNone(task.time_slots[0].partner)
        self.assertEquals(task.start_time, miami.now())

    def test_paired_to_done(self):
        create_entity(User('Bob'))
        task = Task('title2', 'detail2', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11))
        task.owner = User.query.get(1)
        task.partner = User.query.get(2)
        task.start_time = datetime(2012, 11, 11, 0, 1, 0)
        task.time_slots.append(TimeSlot(task.start_time, 60, task.owner))
        create_entity(task)

        when(miami).now().thenReturn(datetime(2012, 11, 11, 0, 2, 0))
        rv = self.app.put('/tasks/DONE/1')

        self.assertEquals(200, rv.status_code)
        assert '<h5>title2</h5>' in rv.data
        assert '<small>DONE</small>' in rv.data
        assert '<p class="text-warning">$10</p>' in rv.data
        assert '<p class="text-info">10H</p>' in rv.data
        assert '<p class="text-info">120.0S</p>' in rv.data
        assert '<p class="text-info">Mike</p>' in rv.data
        assert '<p class="text-info"></p>' in rv.data

        task = Task.query.get(1)
        self.assertIsNone(task.partner)
        self.assertEquals(2, task.time_slots.count())
        self.assertEquals(60, task.time_slots[0].consuming)
        self.assertEquals('Mike', task.time_slots[0].user.name)
        self.assertIsNone(task.time_slots[0].partner)
        self.assertEquals(60, task.time_slots[1].consuming)
        self.assertEquals('Mike', task.time_slots[1].user.name)
        self.assertEquals('Bob', task.time_slots[1].partner.name)
