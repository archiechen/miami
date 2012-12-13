
import unittest
import os
os.environ['MIAMI_ENV'] = 'test'
import simplejson as json
from miami.models import Team

class ModelsTest(unittest.TestCase):
    def test_team_toJSON(self):
        team = Team('Log')

        self.assertEquals({'name':'Log','color':'2a33d8'},team.toJSON())
