from twikit import Client, TooManyRequests
from .logger import Logger
from .config import Config
import time

class Twitter:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.client = Client(language='en-US')
        # client.login(auth_info_1=self.config.TWITTER_USERNAME, auth_info_2=self.config.TWITTER_PASSWORD, password=self.config.TWITTER_EMAIL)
        # client.save_cookies('cookies.json')
        self.client.load_cookies('cookies.json')

    def get_tweets(self, query: str):
        self.logger.info(f"get tweets with query: {query}")
        tweets = self.client.search_tweet(query, product='Top')
        self.logger.info(tweets)
