import asyncio
from contextlib import asynccontextmanager
import uvicorn
import os
from dotenv import load_dotenv
from fastapi import FastAPI
import app.api.v1.doctors as apiV1
from app.init_logic import update_subs_service, telegram_client
from random import randint

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(run_periodic_updates())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)
app.include_router(apiV1.router)


async def run_periodic_updates():
    """Фоновая задача с интервалом 1 минута"""
    while True:
        try:
            await update_subs_service.update_subscribers()
            sleep_time = randint(3, 5)
            await asyncio.sleep(60 * sleep_time)
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Update error: {e}")
            await asyncio.sleep(30)


# # todo это для создания сессии телеграм на серваке
# async def main():
#     tg_cl = telegram_client
#     await tg_cl.start()
#     print("Вы успешно авторизованы!")
#
#
# if __name__ == '__main__':
#     asyncio.run(main())

## todo это для создания сессии инстаграмма на серваке
# async def main():
#     inst_cl = instagram_client
#     print("Вы успешно авторизованы!")
#
#
# if __name__ == '__main__':
#     asyncio.run(main())

if __name__ == '__main__':
    load_dotenv()

    port = 8000
    debug = os.getenv('DEBUG') == 'True'
    if debug:
        port = 8001

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=debug
    )
