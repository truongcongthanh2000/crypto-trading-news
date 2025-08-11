import time
from .logger import Logger
from .twitter import Twitter
from .config import Config
from .threads import Threads
from .telegram import Telegram
from .discord import Discord
from .notification import Message
from datetime import datetime
from .notification import NotificationHandler
import pytz
import json
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def init_scheduler(logger: Logger, config: Config, threads: Threads, twitter: Twitter, telegram: Telegram, discord: Discord, notification: NotificationHandler):
    scheduler = AsyncIOScheduler(logger=logger)
    scheduler.add_job(threads.scrape_user_posts, 'interval', seconds=config.THREADS_SCRAPE_SLEEP_TIME)
    scheduler.add_job(twitter.scrape_user_tweets, 'interval', seconds=config.TWITTER_SCRAPE_SLEEP_TIME)
    scheduler.add_job(telegram.scrape_channel_messages, 'interval', seconds=config.TELEGRAM_SCRAPE_SLEEP_TIME)
    scheduler.add_job(discord.scrape_channel_messages, 'interval', seconds=config.DISCORD_SCRAPE_SLEEP_TIME)
    scheduler.add_job(notification.process_queue, 'interval', seconds=config.NOTIFICATION_SLEEP_TIME)
    scheduler.start()
    try:
        while True:
            await asyncio.sleep(1)  # Keep the main loop alive
    except KeyboardInterrupt:
        scheduler.shutdown()

def main():
    config = Config()
    notification = NotificationHandler(config)
    logger = Logger(config, notification, "news_trade_server")
    logger.info(Message(title = f"Start News Trade - Time: {datetime.fromtimestamp(int(time.time()), tz=pytz.timezone('Asia/Ho_Chi_Minh'))}", body=f"{json.dumps(config.beautify(), indent=2)}", chat_id=config.TELEGRAM_LOG_PEER_ID), notification=True)

    loop = asyncio.get_event_loop()
    twitter = Twitter(config, logger)
    threads = Threads(config, logger)
    telegram = Telegram(config, logger)
    discord = Discord(config, logger)

    loop.create_task(init_scheduler(logger=logger, config=config, threads=threads, twitter=twitter, telegram=telegram, discord=discord, notification=notification))
    loop.run_forever()
