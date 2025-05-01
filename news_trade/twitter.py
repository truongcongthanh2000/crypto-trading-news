from twikit import Client, TooManyRequests
from .logger import Logger
from .config import Config
import asyncio

class Twitter:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.client = Client(language='en-US')
        self.client.set_cookies(config.TWITTER_COOKIES_DICT)

    def get_tweets(self, query: str):
        self.logger.info(f"get tweets with query: {query}")
        loop = asyncio.get_event_loop()
        tweets = loop.run_until_complete(self.client.search_tweet(query, product='Latest'))
        return tweets
    

