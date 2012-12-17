#-*- coding:utf-8 -*-
import os
os.environ['MIAMI_ENV'] = 'dev'
import miami
from miami.models import User, Team, Task, TimeSlot, Burning,Category
from miami import db
from datetime import timedelta

miami.init_db()
team = Team('Log')
team.members.append(User('yachuan.chen', email='yachuan.chen@chinacache.com'))
team.members.append(User('yue.zhang', email='yue.zhang@chinacache.com'))
team.members.append(User('peng.yuan', email='peng.yuan@chinacache.com'))
db.session.add(team)
db.session.add(Category(u'功能'))
db.session.add(Category('Bug'))
db.session.add(Category('Test'))
db.session.commit()

task = Task('title1', 'detail', status='DONE', price=1, estimate=4, team=Team.query.get(1), start_time=miami.utils.get_last_monday().replace(hour=10), ready_time=miami.utils.get_last_monday().replace(hour=10))
ts = TimeSlot(miami.utils.get_last_monday().replace(hour=10), 7200, User.query.get(1))
task.time_slots.append(ts)
task.categories.append(Category.query.get(1))
task.time_slots.append(TimeSlot(miami.utils.get_last_monday().replace(hour=14), 7200, User.query.get(1), partner=User.query.get(2)))
db.session.add(task)
db.session.commit()

task = Task('title2', 'detail2', status='DONE', price=2, estimate=4, team=Team.query.get(1), start_time=miami.utils.get_last_monday().replace(hour=12), ready_time=miami.utils.get_last_monday().replace(hour=12))
ts = TimeSlot(miami.utils.get_last_monday().replace(hour=12), 3600, User.query.get(1), partner=User.query.get(2))
task.time_slots.append(ts)
task.categories.append(Category.query.get(1))
db.session.add(task)
db.session.commit()

task = Task('title2', 'detail2', status='DONE', price=2, estimate=4, team=Team.query.get(1), start_time=miami.utils.get_last_monday().replace(hour=12), ready_time=miami.utils.get_last_monday().replace(hour=12))
ts = TimeSlot(miami.utils.get_last_monday().replace(hour=12), 3600, User.query.get(1), partner=User.query.get(2))
task.time_slots.append(ts)
db.session.add(task)
db.session.commit()

task = Task('title3', 'detail3', status='DONE', price=2, estimate=4, team=Team.query.get(1), start_time=miami.utils.get_last_monday().replace(hour=14), ready_time=miami.utils.get_last_monday().replace(hour=14))
ts = TimeSlot(miami.utils.get_last_monday().replace(hour=14), 3600, User.query.get(2), partner=User.query.get(1))
task.time_slots.append(ts)
task.categories.append(Category.query.get(2))
db.session.add(task)
db.session.commit()

task = Task('title4', 'detail4', status='READY', price=2, estimate=4, team=Team.query.get(1), start_time=miami.utils.get_last_monday().replace(hour=15), ready_time=miami.utils.get_last_monday().replace(hour=15))
ts = TimeSlot(miami.utils.get_last_monday().replace(hour=15), 3600, User.query.get(2), partner=User.query.get(1))
task.time_slots.append(ts)
task.categories.append(Category.query.get(2))
db.session.add(task)
db.session.commit()

task = Task('title6', 'detail4', status='READY', price=1, estimate=4, team=Team.query.get(1), start_time=miami.utils.get_last_monday().replace(hour=15), ready_time=miami.utils.get_last_monday().replace(hour=15))
db.session.add(task)
task.categories.append(Category.query.get(3))
db.session.commit()

task = Task('title5', 'detail5', status='DONE', price=2, estimate=4, team=Team.query.get(1), start_time=(miami.utils.get_last_monday() - timedelta(days=5)).replace(hour=14), ready_time=(miami.utils.get_last_monday() - timedelta(days=5)).replace(hour=14))
ts = TimeSlot((miami.utils.get_last_monday() - timedelta(days=5)).replace(hour=14), 3600, User.query.get(2))
task.time_slots.append(ts)
task.categories.append(Category.query.get(1))
db.session.add(task)
db.session.commit()

task = Task('title7', 'detail5', status='DONE', price=2, estimate=4, team=Team.query.get(1), start_time=miami.utils.yestoday().replace(hour=14), ready_time=miami.utils.yestoday().replace(hour=14))
ts = TimeSlot(task.start_time, 3600, User.query.get(2))
task.categories.append(Category.query.get(2))
task.time_slots.append(ts)
db.session.add(task)
db.session.commit()

task = Task('title8', 'detail4', status='NEW', team=Team.query.get(1))
task.categories.append(Category.query.get(2))
db.session.add(task)
db.session.commit()

task = Task('title9', 'detail4', status='NEW', team=Team.query.get(1))
task.categories.append(Category.query.get(2))
db.session.add(task)
db.session.commit()

burning = Burning(Team.query.get(1), miami.utils.get_current_monday())
burning.burning = 1
burning.remaining = 10
db.session.add(burning)
db.session.commit()

burning = Burning(Team.query.get(1), miami.utils.get_current_monday() + timedelta(days=1))
burning.burning = 2
burning.remaining = 8
db.session.add(burning)
db.session.commit()