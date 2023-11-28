"""
Scheduler
"""
from apscheduler.datastores.memory import MemoryDataStore
from apscheduler.eventbrokers.local import LocalEventBroker
from apscheduler import AsyncScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from starlette.middleware import Middleware
from starlette.requests import Request

import mailer
from routes_execute import report_route
import repo

CRON = repo.get_crontab("HEAD")

async def run_report(db, file, type, format, to):
    """
    Report runner
    """
    # workaround with calling route functions, since jinja template needs to be rendered
    # TODO
    assert type in ("report", "alert", ), "Bad type"
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
    response = await report_route(req)
    if (no_rows == 0) and (type == "alert"):
        pass
    else:
        try:
            response = await _mailer_response(report, format, to, file_name)
            _res = mailer.send(report, format, to, file_name)
        except Exception as e:
            response = PlainTextResponse(content=str(e), status_code=500)
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