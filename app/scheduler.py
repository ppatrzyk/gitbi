"""
Scheduler
"""
from apscheduler.datastores.memory import MemoryDataStore
from apscheduler.eventbrokers.local import LocalEventBroker
from apscheduler import AsyncScheduler
from apscheduler.triggers.cron import CronTrigger
from starlette.middleware import Middleware
from starlette.requests import Request

import logging
import mailer
from routes_execute import report_route
import repo

CRON = repo.get_schedule("HEAD")

async def run_report(db, file, type, format, to):
    """
    Report runner
    """
    # workaround with calling route functions, since jinja template needs to be rendered
    scope = {
        "type": "http",
        "path_params": {
            "state": "HEAD",
            "db": db,
            "file": file,
            "format": format,
        }
    }
    req = Request(scope=scope)
    try:
        response = await report_route(req)
        no_rows = int(response.headers.get("Gitbi-Row-Count") or 0)
        if (no_rows == 0) and (type == "alert"):
            pass
        else:
            content = response.body.decode()
            _res = mailer.send(content, format, to, file)
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

scheduler = AsyncScheduler(data_store=MemoryDataStore(), event_broker=LocalEventBroker())
scheduler_middleware = Middleware(SchedulerMiddleware, scheduler=scheduler)