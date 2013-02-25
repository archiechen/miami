
import unittest
import os
os.environ['MIAMI_ENV'] = 'test'
import simplejson as json
from miami.models import Team, User, Task


class ModelsTest(unittest.TestCase):
    def test_team_toJSON(self):
        team = Team('Log')

        self.assertEquals({'name': 'Log', 'color': '2a33d8'}, team.toJSON())

        def test_team_toJSON(self):
            user = User('Mike')

            self.assertEquals({'name': 'Mike', 'gravater': '91f376c4b36912e5075b6170d312eab5'}, user.toJSON())

            def test_task_toJSON(self):
                task = Task('title1', 'detail', status='DONE', price=1, estimate=4, team=Team('Log'))
                task.id = 1
                task.owner = User('Mike')

                self.assertEquals({'id': 1, 'title': 'title1', 'detail': 'detail', 'status': 'DONE', 'price': 1, 'estimate': 4, 'last_updated': 'just now', 'team': {
                                  'name': 'Log', 'color': '2a33d8'}, 'owner': {'name': 'Mike', 'gravater': '91f376c4b36912e5075b6170d312eab5'}, 'partner': {}}, task.toJSON())
