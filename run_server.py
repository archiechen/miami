
import os
os.environ['MIAMI_ENV'] = 'dev'
import miami
from apscheduler.scheduler import Scheduler


def main():
    # Start the scheduler
    sched = Scheduler()
    sched.start()
    sched.add_cron_job(miami.zeroing, hour='23')
    miami.app.run(host='0.0.0.0',port=5001)

if __name__ == "__main__":
    main()
