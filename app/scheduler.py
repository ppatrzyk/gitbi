"""
Scheduler
"""
# https://github.com/agronholm/apscheduler/blob/48007ff4ec0b632d990b1b751c7fe9a61bb50433/examples/web/asgi_starlette.py

from apscheduler.datastores.memory import MemoryDataStore
from apscheduler.eventbrokers.local import LocalEventBroker
from apscheduler.schedulers.async_ import AsyncScheduler
from apscheduler.triggers.cron import CronTrigger
from starlette.middleware import Middleware

import query
import repo

CRON = repo.get_crontab("HEAD")

def _gen_report_func(path):
    """
    Get function for running given report
    """
    db, file = path.split("/")
    return lambda f: _run_report("HEAD", db, file)

def _run_report(state, db, file):
    """
    Report runner
    """
    table, vega_viz = query.execute_from_file(state, db, file)
    print(f"report run successfully {db} {file} TODO email or something")

def tick():
    print("Running scheduler")

class SchedulerMiddleware:
    def __init__(self, app, scheduler):
        self.app = app
        self.scheduler = scheduler
    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            async with self.scheduler:
                for (cron, path) in CRON:
                    # TODO fix - this fails, due to lambda passed
                    # https://github.com/agronholm/apscheduler/blob/master/src/apscheduler/marshalling.py#L96
                    await self.scheduler.add_schedule(
                        _gen_report_func(path),
                        CronTrigger.from_crontab(cron),
                        id=path
                    )
                await self.scheduler.start_in_background()
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)

scheduler = AsyncScheduler(data_store=MemoryDataStore(), event_broker=LocalEventBroker())
scheduler_middleware = Middleware(SchedulerMiddleware, scheduler=scheduler)
