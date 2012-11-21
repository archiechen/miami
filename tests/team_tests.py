#-*- coding:utf-8 -*-

import unittest
import os
os.environ['MIAMI_ENV'] = 'test'
import miami
import simplejson as json
from miami.models import Team,User
from tests import BaseTestCase


class TeamTest(BaseTestCase):


    def test_join_team(self):
        self.create_entity(Team('Log'))

        rv = self.app.put('/teams/join/1')

        self.assertEquals(200,rv.status_code)

        mike = User.query.get(1)
        self.assertEquals(1,mike.teams.count())
        self.assertEquals(Team.query.get(1),mike.teams[0])

    def test_leave_team(self):
        team =Team('Log')
        team.members.append(User.query.get(1))
        self.create_entity(team)

        rv = self.app.put('/teams/leave/1')

        self.assertEquals(200,rv.status_code)

        mike = User.query.get(1)
        self.assertEquals(0,mike.teams.count())

