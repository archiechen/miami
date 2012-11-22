
import os
os.environ['MIAMI_ENV'] = 'dev'
import miami
from apscheduler.scheduler import Scheduler


def main():
    # Start the scheduler
    sched = Scheduler()
    sched.start()
    sched.add_cron_job(miami.zeroing, hour='15', minute='19')
    miami.app.run()

if __name__ == "__main__":
    main()
