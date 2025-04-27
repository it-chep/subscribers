import asyncio
import logging
from app.main import update_subs_service, celeryApp

# logger = logging.getLogger(__name__)


# @celeryApp.task(bind=True, max_retries=3)
# async def update_subscribers_task(self):
#     try:
#         await update_subs_service.update_subscribers()
#     except Exception as e:
#         logger.exception(e)
#

