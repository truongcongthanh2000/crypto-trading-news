from .config import Config
from .logger import Logger
from .notification import Message
from binance.client import Client
class BinanceAPI:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.binance_client = Client(
            api_key=config.COMMAND_API_KEY,
            api_secret=config.COMMAND_API_SECRET,
            tld=config.COMMAND_TLD
        )

    def get_account(self):
        """
        Get account information
        """
        return self.binance_client.futures_account_balance()