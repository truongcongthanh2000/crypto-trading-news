import time
from .logger import Logger
from .scheduler import SafeScheduler
from .twitter import Twitter
from .config import Config
from .threads import Threads
from .notification import Message
from datetime import datetime
import pytz

def main():
    config = Config()
    logger = Logger(config, "news_trade_server")
    logger.info(Message(title = f"News Trade - Time: {datetime.fromtimestamp(int(time.time()), tz=pytz.timezone('Asia/Ho_Chi_Minh'))}", body='Starting'), True)

    twitter = Twitter(config, logger)
    tweets = twitter.get_tweets('python')
    for tweet in tweets:
        print(
            tweet.user.name,
            tweet.text,
            tweet.created_at
        )
    threads = Threads(config, logger)
    schedule = SafeScheduler(logger)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    finally:
        return
