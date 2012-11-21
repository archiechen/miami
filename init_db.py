import os
os.environ['MIAMI_ENV'] = 'test'
import miami
from miami.models import User, Team
from miami import db

miami.init_db()
user = User('gen.li')
team = Team('Log')
user.teams.append(team)
db.session.add(user)
db.session.commit()