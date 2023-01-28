"""
Scheduler
"""
# https://github.com/agronholm/apscheduler/blob/48007ff4ec0b632d990b1b751c7fe9a61bb50433/examples/web/asgi_starlette.py

from apscheduler.datastores.memory import MemoryDataStore
from apscheduler.eventbrokers.local import LocalEventBroker
from apscheduler.schedulers.async_ import AsyncScheduler
from apscheduler.triggers.cron import CronTrigger
from starlette.middleware import Middleware

def tick():
    print("Running scheduler")

class SchedulerMiddleware:
    def __init__(self, app, scheduler):
        self.app = app
        self.scheduler = scheduler
    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            async with self.scheduler:
                # TODO read and parse cron file, add in a loop
                await self.scheduler.add_schedule(tick, CronTrigger.from_crontab('* * * * *'), id="tick")
                await self.scheduler.start_in_background()
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)

scheduler = AsyncScheduler(data_store=MemoryDataStore(), event_broker=LocalEventBroker())
scheduler_middleware = Middleware(SchedulerMiddleware, scheduler=scheduler)
