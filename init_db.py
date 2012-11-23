import os
os.environ['MIAMI_ENV'] = 'dev'
import miami
from miami.models import User, Team, Task, TimeSlot
from miami import db

miami.init_db()
team = Team('Log')
team.members.append(User('yachuan.chen', email='yachuan.chen@chinacache.com'))
team.members.append(User('yue.zhang', email='yue.zhang@chinacache.com'))
team.members.append(User('peng.yuan', email='peng.yuan@chinacache.com'))
task = Task('title1', 'detail', status='DONE', price=2, estimate=4, team=team)
ts = TimeSlot(miami.views.get_last_monday().replace(hour=10), 3600, User.query.get(1))
task.time_slots.append(ts)
db.session.add(task)
db.session.commit()

task2 = Task('title2', 'detai2', status='NEW', price=2, estimate=4, team=Team.query.get(1))
ts2 = TimeSlot(miami.views.get_last_monday().replace(hour=12), 3600, User.query.get(1), partner=User.query.get(2))
task2.time_slots.append(ts2)
db.session.add(task2)
db.session.commit()