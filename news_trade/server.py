import time
from .logger import Logger
from .scheduler import SafeScheduler
from .twitter import Twitter
from .config import Config
from .threads import Threads
from .telegram import Telegram
from .notification import Message
from datetime import datetime
import pytz
import json
import apprise
import asyncio

def main():
    config = Config()
    logger = Logger(config, "news_trade_server")
    logger.info(Message(title = f"Start News Trade - Time: {datetime.fromtimestamp(int(time.time()), tz=pytz.timezone('Asia/Ho_Chi_Minh'))}", body=f"{json.dumps(config.beautify(), indent=2)}", format=apprise.NotifyFormat.TEXT), False)

    twitter = Twitter(config, logger)
    threads = Threads(config, logger)
    telegram = Telegram(config, logger)
    schedule = SafeScheduler(logger)
    schedule.every(config.THREADS_SCRAPE_SLEEP_TIME).seconds.do(threads.scrape_user_posts).tag("threads_scrape_news")
    schedule.every(config.TWITTER_SCRAPE_SLEEP_TIME).seconds.do(twitter.scrape_user_tweets).tag("twitter_scrape_news")
    schedule.every(config.TELEGRAM_SCRAPE_SLEEP_TIME).seconds.do(telegram.scrape_channel_messages).tag("scrape_channel_messages")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    finally:
        return
