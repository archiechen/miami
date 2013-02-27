#-*- coding:utf-8 -*-

import unittest
import os
os.environ['MIAMI_ENV'] = 'test'
import miami
import simplejson as json
from datetime import datetime, timedelta
from miami.models import Team, User, Burning, Task
from tests import BaseTestCase
from mockito import when


class BurningTest(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        when(miami.utils).now().thenReturn(datetime(2012, 11, 5, 9, 0, 0))
        team = Team('Miami')
        team.members.append(User.query.get(1))
        self.create_entity(team)
        burning = Burning(Team.query.get(1), miami.utils.get_current_monday())
        burning.burning = 1
        burning.remaining = 10
        self.create_entity(burning)

        burning = Burning(Team.query.get(1), miami.utils.get_current_monday() + timedelta(days=1))
        burning.burning = 2
        burning.remaining = 8
        self.create_entity(burning)

        task = Task('title1', 'detail', status='DONE', price=1, estimate=4, team=Team.query.get(1))
        self.create_entity(task)
        task = Task('title1', 'detail', status='PROGRESS', price=1, estimate=4, team=Team.query.get(1))
        self.create_entity(task)
        task = Task('title1', 'detail', status='READY', price=1, estimate=4, team=Team.query.get(1))
        self.create_entity(task)
        task = Task('title1', 'detail', status='NEW', price=1, estimate=4, team=Team.query.get(1))
        self.create_entity(task)

    def test_burning(self):

        rv = self.app.get('/burning')

        self.assertEquals(200, rv.status_code)

        assert 'var line1=[[10, 8, 2], [1, 2, 1]];' in rv.data

    def test_burning_team(self):

        rv = self.app.get('/burning/1')

        self.assertEquals(200, rv.status_code)

        assert 'var line1=[[10, 8, 2], [1, 2, 1]];' in rv.data

    def test_burning_ajax(self):

        rv = self.app.get('/burning/team/1')

        self.assertEquals({'remaining': [[1, 10], [2, 8], [3, 2]], 'burning': [[1, 1], [2, 2], [3, 1]]}, json.loads(rv.data))
