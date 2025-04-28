import time
from .logger import Logger
from .scheduler import SafeScheduler
from .twitter import Twitter
from .config import Config
from .threads import Threads
from .notification import Message
from datetime import datetime

def main():
    config = Config()
    logger = Logger(config, "news_trade_server")
    logger.info(Message(title = f'News Trade - Time: {datetime.now()}', body='Starting'), True)


    threads = Threads(config, logger)
    schedule = SafeScheduler(logger)
    schedule.every(config.THREADS_SCRAPE_SLEEP_TIME).seconds.do(threads.scrape_user_posts).tag("threads_scrape_news")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    finally:
        return
  