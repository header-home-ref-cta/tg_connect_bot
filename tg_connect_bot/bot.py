import asyncio
import contextlib
import logging
import sys

from aiogram import Dispatcher
from database import creation
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from configuration import settings, scheduler
from configuration.notify import notify
import decouple



class SharedData:
    def __init__(self):
        self.data = None
shared_data = SharedData()


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    data = await reader.read(2048)
    shared_data.data = data.decode()
    try:
        await notify(data)
    except Exception as e:
        logging.exception(f"[bot] HANDLE CLIENT ERROR\n {e}")
    addr, port  =writer.get_extra_info("peername")
    responce = "ok 200".encode()
    writer.write(responce)
    await writer.drain()
    writer.close()



async def run_server():
    HOST = "127.0.0.1"
    PORT = 5099
    server = await asyncio.start_server(handle_client, HOST, PORT )
    async with server:
        print("Server Started")
        await server.serve_forever()


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format=u'[%(asctime)s] - %(message)s',
        handlers=[
            logging.FileHandler(decouple.config("PATH_TO_LOGS")+'bot.log', mode='a', encoding='utf-8'),
            logging.StreamHandler()
        ] if decouple.config("PATH_TO_LOGS") else [logging.StreamHandler()]
    )

    dp = Dispatcher()
    bot_scheduler = AsyncIOScheduler()
    await settings.register_handlers(dp)
    await settings.register_middlewares(dp)
    await settings.bot_commands()
    bot_scheduler.add_job(scheduler.check_users_payments, 'interval', days=1)
    bot_scheduler.start()

    try:
        await dp.start_polling(settings.bot, allowed_updates=dp.resolve_used_update_types(),
                               on_startup=creation.create_tables())
    except Exception as ex:
        logging.error(f'[Exception] - {ex}', exc_info=True)
    finally:
        await settings.bot.session.close()


async def third():
    await asyncio.gather(main(), run_server())

if __name__ == '__main__':
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(third())
        # asyncio.run(main())
        # asyncio.run(run_server())

