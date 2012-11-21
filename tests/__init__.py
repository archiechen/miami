#-*- coding:utf-8 -*-

import unittest
import os
os.environ['MIAMI_ENV'] = 'test'
import miami
from mockito import unstub
from miami.models import Team, User


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.app = miami.app.test_client()
        miami.init_db()
        self.create_entity(User('Mike'))
        self.login('Mike', '')

    def tearDown(self):
        unstub()

    def create_entity(self, entity):
        miami.db.session.add(entity)
        miami.db.session.commit()

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)