from core.app import rt
from fasthtml import Header, HTTPException
from db.task_db import TaskDatabase
import logging
from core.config import settings

logger = logging.getLogger(__name__)
db = TaskDatabase()

async def verify_webhook_secret(x_github_token: str = Header(None)):
    if x_github_token != settings.GITHUB_WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

@rt("/admin/tasks/archive", methods=["POST"])
async def archive_tasks_endpoint(x_github_token: str = Header(None)):
    await verify_webhook_secret(x_github_token)
    logger.info("Archiving tasks via GitHub Action")
    success = db.archive_tasks()
    return {"success": success}

@rt("/admin/tasks/reset", methods=["POST"])
async def reset_tasks_endpoint(x_github_token: str = Header(None)):
    await verify_webhook_secret(x_github_token)
    logger.info("Resetting tasks via GitHub Action")
    success = db.reset_tasks()
    return {"success": success}