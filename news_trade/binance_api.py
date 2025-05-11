from .config import Config
from .logger import Logger
import threading
from contextlib import contextmanager
from typing import Dict, Set, Tuple
from .notification import Message
from binance.client import Client

class BinanceCache:  # pylint: disable=too-few-public-methods
    _balances: Dict[str, float] = {}
    _balances_mutex: threading.Lock = threading.Lock()

    @contextmanager
    def open_balances(self):
        with self._balances_mutex:
            yield self._balances
class BinanceAPI:
    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.binance_client = Client(
            api_key=config.COMMAND_API_KEY,
            api_secret=config.COMMAND_API_SECRET,
            tld=config.COMMAND_TLD
        )

    # spot api
    def get_account(self):
        """
        Get account information
        """
        return self.binance_client.get_account(omitZeroBalances="true")
    
    def get_ticker_price(self, symbol: str):
        price = self.binance_client.get_symbol_ticker(symbol=symbol)
        if price is None or "price" not in price:
            return 0.0
        return float(price["price"])

    # future api
    def get_futures_account(self):
        return self.binance_client.futures_account()
    
    def get_current_position(self):
        return self.binance_client.futures_position_information()