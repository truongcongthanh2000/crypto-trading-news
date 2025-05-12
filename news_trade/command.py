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
import json
import traceback
import html

EPS = 1e-2
class Command:
    def __init__(self, config: Config, logger: Logger, binance_api: BinanceAPI):
        self.config = config
        self.logger = logger
        self.binance_api = binance_api

    def start_bot(self):
        if self.config.COMMAND_ENABLED == False:
            return
        application = Application.builder().token(self.config.TELEGRAM_BOT_TOKEN).read_timeout(7).get_updates_read_timeout(42).build()
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("info", self.info))
        application.add_handler(CommandHandler("forder", self.forder))
        application.add_handler(CommandHandler("fclose", self.fclose))
        application.add_error_handler(self.error)
        application.run_polling(drop_pending_updates=True)

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
            await update.message.reply_text(text=msg, parse_mode=ParseMode.MARKDOWN_V2, link_preview_options=LinkPreviewOptions(is_disabled=True))
        except Exception as err:
            self.logger.error(Message(
                title=f"Error Command.faccount - {update}",
                body=f"Error: {err=}", 
                format=apprise.NotifyFormat.TEXT
            ), True)
    
    # forder buy/sell coin leverage margin sl(optional) tp(optional)
    async def forder(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        side = context.args[0]
        coin = context.args[1].upper()
        leverage = int(context.args[2])
        margin = float(context.args[3])
        try:
            symbol = coin + "USDT"
            # change leverage for symbol first
            self.binance_api.f_change_leverage(symbol, leverage)
            batch_orders = self.f_get_orders(side, symbol, leverage, margin, context)
            responses = self.binance_api.f_batch_order(batch_orders)
            ok = True
            for idx in range(len(responses)):
                if "code" in responses[idx] and int(responses[idx]["code"]) < 0:
                    # Error
                    self.logger.error(Message(
                        title=f"Error Command.forder - {batch_orders[idx]['side']} - {batch_orders[idx]['type']} - {symbol}",
                        body=f"Error: {responses[idx]['msg']}",
                        format=apprise.NotifyFormat.TEXT
                    ), True)
                    ok = False
            if ok:
                await update.message.reply_text(text=f"👋 Your order for {symbol} is successful\n {json.dumps(batch_orders, indent=2)}")
        except Exception as err:
            self.logger.error(Message(
                title=f"Error Command.forder - {side} - {symbol} - {leverage} - {margin}",
                body=f"Error: {err=}", 
                format=apprise.NotifyFormat.TEXT
            ), True)
    
    async def fclose(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        coin = context.args[0].upper()
        try:
            symbol = coin + "USDT"
            batch_orders = self.f_get_close_positions(symbol)
            responses = self.binance_api.f_batch_order(batch_orders)
            ok = True
            for idx in range(len(responses)):
                if "code" in responses[idx] and int(responses[idx]["code"]) < 0:
                    # Error
                    self.logger.error(Message(
                        title=f"Error Command.forder - {batch_orders[idx]['side']} - {batch_orders[idx]['type']} - {symbol}",
                        body=f"Error: {responses[idx]['msg']}",
                        format=apprise.NotifyFormat.TEXT
                    ), True)
                    ok = False
            if ok:
                msg = f"👋 Your close positions for {symbol} is successful\n {json.dumps(batch_orders, indent=2)}\n-------------\n"
                cancel_open_orders_response = self.binance_api.f_cancel_all_open_orders(symbol)
                msg += f"👋 Cancel all open orders for {symbol}\n {json.dumps(cancel_open_orders_response, indent=2)}"
                await update.message.reply_text(text=msg)
        except Exception as err:
            self.logger.error(Message(
                title=f"Error Command.fclose - {symbol}",
                body=f"Error: {err=}", 
                format=apprise.NotifyFormat.TEXT
            ), True)
    
    async def error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log the error and send a telegram message to notify the developer."""
        # traceback.format_exception returns the usual python message about an exception, but as a
        # list of strings rather than a single string, so we have to join them together.
        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = "".join(tb_list)
        self.logger.error(Message(f"Exception while handling an update:, exc_info={tb_string}"))

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
        info += f"**Total ROI**: {round(float(account_info['totalUnrealizedProfit']) / float(account_info['totalWalletBalance']) * 100, 2)}%\n"
        info += f"**After Total Balance**: ${float(account_info['totalMarginBalance']):.2f}"
        return info
    
    def f_get_orders(self, side: str, symbol: str, leverage: int, margin: float, context: ContextTypes.DEFAULT_TYPE):
        price = self.binance_api.f_price(symbol)
        pair_info = self.binance_api.f_get_symbol_info(symbol)
        quantity_precision = int(pair_info['quantityPrecision']) if pair_info else 3
        quantity = round(margin * leverage / price, quantity_precision)
        if 'b' in side:
            side_upper = "BUY"
        else:
            side_upper = "SELL"
        order = {
            "type": "MARKET",
            "side": side_upper,
            "symbol": symbol,
            "quantity": str(quantity)
        }
        batch_orders = [order]
        if len(context.args) > 4:
            sl_order = {
                "type": "STOP_MARKET",
                "side": "BUY" if side_upper == "SELL" else "SELL",
                "symbol": symbol,
                "stopPrice": context.args[4],
                "closePosition": "true"
            }
            batch_orders.append(sl_order)
        if len(context.args) > 5:
            tp_order = {
                "type": "TAKE_PROFIT_MARKET",
                "side": "BUY" if side_upper == "SELL" else "SELL",
                "symbol": symbol,
                "stopPrice": context.args[5],
                "closePosition": "true"
            }
            batch_orders.append(tp_order)
        return batch_orders

    def f_get_close_positions(self, symbol: str):
        positions = self.binance_api.get_current_position(symbol=symbol)
        batch_orders = []
        for position in positions:
            amount = float(position["positionAmt"])
            if amount > 0:
                side_upper = "BUY"
            else:
                side_upper = "SELL"
            close_order = {
                "type": "MARKET",
                "side": "BUY" if side_upper == "SELL" else "SELL",
                "symbol": symbol,
                "quantity": position["positionAmt"],
            }
            batch_orders.append(close_order)
        return batch_orders