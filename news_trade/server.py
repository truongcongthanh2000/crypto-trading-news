import time
from .logger import Logger
from .scheduler import SafeScheduler
from .twitter import Twitter
from .config import Config
from .threads import Threads
import json
from .notification import Message

def main():
    logger = Logger("news_trade_server")
    logger.info(Message("Starting"), True)

    config = Config()

    threads = Threads(config, logger)
    threads.scrape_user_posts()
    schedule = SafeScheduler(logger)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    finally:
        return
  