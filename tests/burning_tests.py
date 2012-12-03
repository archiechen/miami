#-*- coding:utf-8 -*-

import unittest
import os
os.environ['MIAMI_ENV'] = 'test'
import miami
import simplejson as json
from datetime import datetime, timedelta
from miami.models import Team, User, Burning
from tests import BaseTestCase
from mockito import when


class TeamTest(BaseTestCase):

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
        
    def test_burning(self):

        rv = self.app.get('/burning')

        self.assertEquals(200, rv.status_code)

        assert 'var line1=[[10, 8], [1, 2]];' in rv.data

    def test_burning_team(self):

        rv = self.app.get('/burning/1')

        self.assertEquals(200, rv.status_code)

        assert 'var line1=[[10, 8], [1, 2]];' in rv.data
