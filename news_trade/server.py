import time
from .logger import Logger
from .scheduler import SafeScheduler
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

def main():
    config = Config()
    notification = NotificationHandler(config)
    logger = Logger(config, notification, "news_trade_server")
    logger.info(Message(title = f"Start News Trade - Time: {datetime.fromtimestamp(int(time.time()), tz=pytz.timezone('Asia/Ho_Chi_Minh'))}", body=f"{json.dumps(config.beautify(), indent=2)}", chat_id=config.TELEGRAM_LOG_PEER_ID), True)

    twitter = Twitter(config, logger)
    threads = Threads(config, logger)
    telegram = Telegram(config, logger)
    discord = Discord(config, logger)
    schedule = SafeScheduler(logger)
    schedule.every(config.THREADS_SCRAPE_SLEEP_TIME).seconds.do(threads.scrape_user_posts).tag("threads_scrape_news")
    schedule.every(config.TWITTER_SCRAPE_SLEEP_TIME).seconds.do(twitter.scrape_user_tweets).tag("twitter_scrape_news")
    schedule.every(config.TELEGRAM_SCRAPE_SLEEP_TIME).seconds.do(telegram.scrape_channel_messages).tag("telegram_scrape_channel_messages")
    schedule.every(config.DISCORD_SCRAPE_SLEEP_TIME).seconds.do(discord.scrape_channel_messages).tag("discord_scrape_channel_messages")
    schedule.every(config.NOTIFICATION_SLEEP_TIME).seconds.do(notification.process_queue).tag("notification_process_queue")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    finally:
        return
