"""
Scheduler
"""
# https://github.com/agronholm/apscheduler/blob/48007ff4ec0b632d990b1b751c7fe9a61bb50433/examples/web/asgi_starlette.py

from apscheduler.datastores.memory import MemoryDataStore
from apscheduler.eventbrokers.local import LocalEventBroker
from apscheduler import AsyncScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from starlette.middleware import Middleware

import repo

CRON = repo.get_crontab("HEAD")

def run_report(db, file, type, format, to):
    """
    Report runner
    """
    state = "HEAD"
    print(f"report run {db} {file} {type} {format} {to}. TODO execution")

def tick():
    print("Running scheduler")

class SchedulerMiddleware:
    def __init__(self, app, scheduler):
        self.app = app
        self.scheduler = scheduler
    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            async with self.scheduler:
                for (cron, db, file, type, format, to) in CRON:
                    kwargs = {"db": db, "file": file, "type": type, "format": format, "to": to}
                    await self.scheduler.add_schedule(
                        run_report,
                        CronTrigger.from_crontab(cron),
                        id=f"{format}/{db}/{file}",
                        kwargs=kwargs
                    )
                # await self.scheduler.add_schedule(
                #     tick, IntervalTrigger(seconds=1), id="tick"
                # )
                await self.scheduler.start_in_background()
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)

scheduler = AsyncScheduler(data_store=MemoryDataStore(), event_broker=LocalEventBroker())
scheduler_middleware = Middleware(SchedulerMiddleware, scheduler=scheduler)