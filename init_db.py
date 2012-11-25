import os
os.environ['MIAMI_ENV'] = 'dev'
import miami
from miami.models import User, Team, Task, TimeSlot
from miami import db
from datetime import timedelta

miami.init_db()
team = Team('Log')
team.members.append(User('yachuan.chen', email='yachuan.chen@chinacache.com'))
team.members.append(User('yue.zhang', email='yue.zhang@chinacache.com'))
team.members.append(User('peng.yuan', email='peng.yuan@chinacache.com'))
db.session.add(team)
db.session.commit()

task = Task('title1', 'detail', status='DONE', price=1, estimate=4, team=Team.query.get(1), start_time=miami.views.get_last_monday().replace(hour=10))
ts = TimeSlot(miami.views.get_last_monday().replace(hour=10), 7200, User.query.get(1))
task.time_slots.append(ts)
db.session.add(task)
db.session.commit()

task = Task('title2', 'detail2', status='DONE', price=2, estimate=4, team=Team.query.get(1), start_time=miami.views.get_last_monday().replace(hour=12))
ts = TimeSlot(miami.views.get_last_monday().replace(hour=12), 3600, User.query.get(1), partner=User.query.get(2))
task.time_slots.append(ts)
db.session.add(task)
db.session.commit()

task = Task('title3', 'detail3', status='DONE', price=2, estimate=4, team=Team.query.get(1), start_time=miami.views.get_last_monday().replace(hour=14))
ts = TimeSlot(miami.views.get_last_monday().replace(hour=14), 3600, User.query.get(2), partner=User.query.get(1))
task.time_slots.append(ts)
db.session.add(task)
db.session.commit()

task = Task('title4', 'detail4', status='Ready', price=2, estimate=4, team=Team.query.get(1), start_time=miami.views.get_last_monday().replace(hour=15))
ts = TimeSlot(miami.views.get_last_monday().replace(hour=15), 3600, User.query.get(2), partner=User.query.get(1))
task.time_slots.append(ts)
db.session.add(task)
db.session.commit()

task = Task('title5', 'detail5', status='DONE', price=2, estimate=4, team=Team.query.get(1), start_time=(miami.views.get_last_monday() - timedelta(days=5)).replace(hour=14))
ts = TimeSlot((miami.views.get_last_monday() - timedelta(days=5)).replace(hour=14), 3600, User.query.get(2))
task.time_slots.append(ts)
db.session.add(task)
db.session.commit()