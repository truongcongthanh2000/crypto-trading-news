from .logger import Logger
from .config import Config
from .notification import Message
from telegram import Update, LinkPreviewOptions
import telegramify_markdown
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, Updater
import apprise
import socket
import requests
from .binance_api import BinanceAPI

EPS = 1e-2
class Command:
    def __init__(self, config: Config, logger: Logger, binance_api: BinanceAPI):
        self.config = config
        self.logger = logger
        self.application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        self.binance_api = binance_api

    def start_bot(self):
        if self.config.COMMAND_ENABLED == False:
            return
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("info", self.info))
        self.application.add_error_handler(self.error)
        self.application.run_polling()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handles command /start from the admin"""
        try:
            hostname = socket.gethostname()
            IPAddr = socket.gethostbyname(hostname)
            public_ip = requests.get('https://api.ipify.org').text
            await update.message.reply_text(text=f"👋 Hello, your server public IP is {public_ip}, local IP is {IPAddr}")
        except Exception as err:
            self.logger.error(Message(
                title=f"Error Command.start - {update}",
                body=f"Error: {err=}", 
                format=apprise.NotifyFormat.TEXT
            ), True)
    
    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE): # info current spot/future account, ex: balance, pnl, orders, ...
        try:
            msg = self.info_spot() + '\n--------------------\n' + self.info_future()
            msg = telegramify_markdown.markdownify(msg)
            print(msg)
            await update.message.reply_text(text=msg, parse_mode=ParseMode.MARKDOWN_V2, link_preview_options=LinkPreviewOptions(is_disabled=True))
        except Exception as err:
            self.logger.error(Message(
                title=f"Error Command.faccount - {update}",
                body=f"Error: {err=}", 
                format=apprise.NotifyFormat.TEXT
            ), True)

    async def error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.error(Message(
            title=f"Error Command.Update {update}",
            body=f"Error Msg: {context.error}",
            format=apprise.NotifyFormat.TEXT
        ), True)

    def info_spot(self):
        account_info = self.binance_api.get_account()
        total_balance = 0.0
        info = "**SPOT Account**\n"
        for balance in account_info["balances"]:
            coin = balance["asset"]
            free_price = float(balance["free"])
            locked_price = float(balance["locked"])
            if free_price + locked_price <= EPS:
                continue
            total_balance += free_price + locked_price
            message = ""
            if coin == "USDT":
                message = "USDT: $%.2f" % round(free_price + locked_price, 2)
            else:
                message = f"[{coin}](https://www.binance.com/en/trade/{coin}_USDT?type=spot): ${free_price + locked_price:.2f}"
            message += "\n"
            info += message
        info += "\n"
        info += f"**Total balance**: {total_balance:.2f}"
        return info
    
    def info_future(self):
        info = "**Future Account**\n"
        account_info = self.binance_api.get_futures_account()
        positions = self.binance_api.get_current_position()
        for position in positions:
            symbol = position["symbol"]
            url = f"https://www.binance.com/en/futures/{symbol}"
            amount = float(position["positionAmt"])
            if abs(amount) <= EPS: # Open orders
                continue
            if amount > 0:
                position_type = "**BUY**"
            else:
                position_type = "**SHORT**"
            info_position = f"[{symbol}]({url}): {position_type} **{abs(round(float(position['notional']) / float(position['initialMargin'])))}x**, size: **${position['notional']}**, margin: **${position['initialMargin']}**\n"
            info_position += f"- entryPrice: **${position['entryPrice']}**, marketPrice: **{position['markPrice']}**\n"
            info_position += f"- PNL: **${float(position['unRealizedProfit']):.2f}**, ROI: **{round(float(position['unRealizedProfit']) / float(position['initialMargin']) * 100.0, 2)}%**\n\n"
            info += info_position

        info += "\n"
        info += f"**Before Total Balance**: ${float(account_info['totalWalletBalance']):.2f}\n"
        info += f"**Total Initial Margin**: ${float(account_info['totalInitialMargin']):.2f} (Position: ${float(account_info['totalPositionInitialMargin']):.2f}, Open: ${float(account_info['totalOpenOrderInitialMargin']):.2f})\n"
        info += f"**Available Balance**: ${float(account_info['availableBalance']):.2f}\n\n"
        info += f"**Total Unrealized Profit**: ${float(account_info['totalUnrealizedProfit']):.2f}\n"
        info += f"**After Total Balance**: ${float(account_info['totalMarginBalance']):.2f}"
        return info