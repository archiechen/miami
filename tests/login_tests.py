#-*- coding:utf-8 -*-

import unittest
import os
os.environ['MIAMI_ENV'] = 'test'
import miami
from miami.models import User


def create_entity(entity):
    miami.db.session.add(entity)
    miami.db.session.commit()


class LoginTest(unittest.TestCase):

    def setUp(self):
        self.app = miami.app.test_client()
        miami.init_db()
        create_entity(User('Mike'))

    def tearDown(self):
        pass

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('Mike', '')
        assert 'Dashborad' in rv.data
        rv = self.logout()
        assert '<form action="/login" method="POST" class="form-horizontal">' in rv.data

    def test_login_nouser(self):
        rv = self.login('NoUser', '')
        assert '<form action="/login" method="POST" class="form-horizontal">' in rv.data