"""
Scheduler
"""
from apscheduler.datastores.memory import MemoryDataStore
from apscheduler.eventbrokers.local import LocalEventBroker
from apscheduler import AsyncScheduler
from apscheduler.triggers.cron import CronTrigger
from starlette.middleware import Middleware
import httpx
import logging

import auth
import mailer
import repo

CRON = repo.get_schedule("HEAD")

def run_report(db, file, type, format, to):
    """
    Report runner
    """
    # workaround since jinja template cant be rendered outside of routes
    try:
        client_kwargs = {"headers": {"User-Agent": "Gitbi Scheduler"}}
        if auth.USERS:
            client_kwargs["auth"] = auth.USERS[0]
        url = f"http://localhost:8000/report/{db}/{file}/HEAD/{format}"
        with httpx.Client(**client_kwargs) as client:
            response = client.get(url)
        no_rows = int(response.headers.get("Gitbi-Row-Count") or 0)
        print(no_rows)
        print(response.text)
        if (no_rows == 0) and (type == "alert"):
            pass
        else:
            _res = mailer.send(response.text, format, to, file)
        logging.info(f"{type} for {db}/{file} executed")
    except Exception as e:
        logging.error(f"Scheduler error: {str(e)}")
    return True

class SchedulerMiddleware:
    def __init__(self, app, scheduler):
        self.app = app
        self.scheduler = scheduler
    async def __call__(self, scope, receive, send):
        if scope["type"] == "lifespan":
            async with self.scheduler:
                for kwargs in CRON:
                    cron = kwargs.pop("cron")
                    job_id = "/".join(f"{k}={v}" for k, v in kwargs.items())
                    await self.scheduler.add_schedule(
                        run_report,
                        CronTrigger.from_crontab(cron),
                        id=job_id,
                        kwargs=kwargs
                    )
                await self.scheduler.start_in_background()
                await self.app(scope, receive, send)
        else:
            await self.app(scope, receive, send)

if CRON:
    SCHEDULER = Middleware(
        SchedulerMiddleware,
        scheduler=AsyncScheduler(data_store=MemoryDataStore(), event_broker=LocalEventBroker())
    )
else:
    SCHEDULER = None

#TODO problem: this starts scheduler in every uvicorn process