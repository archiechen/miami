import unittest
import os
os.environ['MIAMI_ENV'] = 'test'
import miami
from miami.models import Task, TimeSlot, User
from datetime import datetime
from mockito import when, unstub


def create_entity(entity):
    miami.db.session.add(entity)
    miami.db.session.commit()


class JobTest(unittest.TestCase):

    def setUp(self):
        miami.init_db()
        create_entity(User('Mike'))
        when(miami).now().thenReturn(datetime(2012, 11, 11, 23, 0, 0))

    def tearDown(self):
        unstub()

    def test_task_zeroing(self):
        task = Task('title2', 'detail2', estimate=10, price=10, status='PROGRESS', start_time=datetime(2012, 11, 11, 10, 0, 0))
        task.owner = User.query.get(1)
        create_entity(task)

        miami.zeroing()

        task = Task.query.get(1)
        self.assertEquals('READY', task.status)
        self.assertIsNone(task.partner)
        self.assertEquals(28800.0, task.consuming)
        self.assertEquals(1, task.time_slots.count())
