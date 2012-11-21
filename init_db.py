import os
os.environ['MIAMI_ENV'] = 'dev'
import miami
from miami.models import User, Team
from miami import db

miami.init_db()
team = Team('Log')
team.members.append( User('yachuan.chen',email='yachuan.chen@chinacache.com'))
team.members.append( User('yue.zhang',email='yue.zhang@chinacache.com'))
db.session.add(team)
db.session.commit()