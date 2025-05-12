from twikit import Client, TooManyRequests, Tweet
from twikit.utils import Result
from ..logger import Logger
from ..config import Config
import asyncio
from ..notification import Message
import time
import pytz
from datetime import datetime
from random import randint
import apprise

class Twitter:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.client = Client(language='en-US')
        self.client.set_cookies(config.TWITTER_COOKIES_DICT, clear_cookies=True)
        self.map_timestamp_by_user = {} 

    def filter_tweets(self, tweets: Result[Tweet]) -> list[Message]:
        twitter_tweets = []
        time_now = int(time.time())
        update_max_timestamp = {}
        for tweet in tweets:
            tweet_timestamp = int(tweet.created_at_datetime.timestamp())
            user_id = tweet.user.id
            user_name = tweet.user.name
            user_screen_name = tweet.user.screen_name
            url = f"https://x.com/{user_screen_name}/status/{tweet.id}"
            if time_now - tweet_timestamp >= self.config.TWITTER_SLA:
                continue
            if user_id in self.map_timestamp_by_user and tweet_timestamp <= self.map_timestamp_by_user[user_id]:
                continue
            if user_id in update_max_timestamp:
                update_max_timestamp[user_id] = max(update_max_timestamp[user_id], tweet_timestamp)
            else:
                update_max_timestamp[user_id] = tweet_timestamp
            twitter_tweets.append(Message(
                title= f"Twitter - {user_name} - Time: {datetime.fromtimestamp(tweet_timestamp, tz=pytz.timezone('Asia/Ho_Chi_Minh'))}",
                body= f"{tweet.full_text}\n\n[Link: {url}]({url})"
            ))
        for user_id in update_max_timestamp:
            self.map_timestamp_by_user[user_id] = update_max_timestamp[user_id]
        return twitter_tweets
        

    def get_tweets(self, query: str) -> list[Message]:
        loop = asyncio.get_event_loop()
        try:
            tweets = loop.run_until_complete(self.client.search_tweet(query, product='Latest', count=self.config.TWITTER_TWEETS_COUNT))
        except Exception as err:
            self.logger.error(Message(
                title=f"Error Twitter.get_tweets - {query}",
                body=f"Error: {err=}", 
                format=apprise.NotifyFormat.TEXT
            ), True)
            tweets = []
            # loop.close()
        return self.filter_tweets(tweets)
    
    def scrape_user_tweets(self):
        if self.config.TWITTER_ENABLED == False:
            return
        list_query = self.config.TWITTER_LIST_QUERY
        self.logger.debug(Message(f"Twitter.scrape_user_tweets with list query: {', '.join(list_query)}"))
        tweets = []
        for query in list_query:
            tweets.extend(self.get_tweets(query))
            time.sleep(randint(5, 10))
        for tweet in tweets:
            self.logger.info(tweet, True)

