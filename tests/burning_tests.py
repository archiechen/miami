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
        when(miami.models).now().thenReturn(datetime(2012, 11, 5, 9, 0, 0))
        self.create_entity(Team('Log'))
        burning = Burning(Team.query.get(1), miami.models.get_current_monday())
        burning.burning = 1
        burning.remaining = 10
        self.create_entity(burning)

        burning = Burning(Team.query.get(1), miami.models.get_current_monday() + timedelta(days=1))
        burning.burning = 2
        burning.remaining = 8
        self.create_entity(burning)
        
    def test_burning(self):

        rv = self.app.get('/burning/1')

        self.assertEquals(200, rv.status_code)
        print rv.data

        assert 'var line1=[[10, 8], [1, 2]];' in rv.data
