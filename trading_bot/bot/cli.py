"""
Command Line Interface for the Trading Bot
Supports both argparse (non-interactive) and interactive menu modes.

Usage examples:
  python main.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  python main.py order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 80000
  python main.py order --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 75000
  python main.py interactive
"""

import argparse
import sys
from colorama import init, Fore, Style
from .client import BinanceFuturesClient
from .orders import OrderManager
from .validators import ValidationError
from .logging_config import setup_logging

init()  # colorama cross-platform colors


def print_order_result(order):
    """Print a clean order result summary"""
    print(f"\n{Fore.GREEN}Order placed successfully!{Style.RESET_ALL}")
    print("-" * 40)
    print(f"  Order ID    : {order.get('orderId')}")
    print(f"  Symbol      : {order.get('symbol')}")
    print(f"  Side        : {order.get('side')}")
    print(f"  Type        : {order.get('type')}")
    print(f"  Quantity    : {order.get('origQty')}")
    print(f"  Status      : {order.get('status')}")
    if order.get('price') and float(order.get('price', 0)) > 0:
        print(f"  Price       : {order.get('price')}")
    if order.get('stopPrice') and float(order.get('stopPrice', 0)) > 0:
        print(f"  Stop Price  : {order.get('stopPrice')}")
    if order.get('avgPrice') and float(order.get('avgPrice', 0)) > 0:
        print(f"  Avg Price   : {order.get('avgPrice')}")
    if order.get('executedQty'):
        print(f"  Executed Qty: {order.get('executedQty')}")
    print("-" * 40)


def cmd_order(args, order_manager, logger):
    """Handle the 'order' subcommand"""
    order_type = args.type.upper()
    side = args.side.upper()
    symbol = args.symbol.upper()

    # Print request summary
    print(f"\n{Fore.YELLOW}Order Request Summary:{Style.RESET_ALL}")
    print(f"  Symbol : {symbol}")
    print(f"  Side   : {side}")
    print(f"  Type   : {order_type}")
    print(f"  Qty    : {args.quantity}")
    if args.price:
        print(f"  Price  : {args.price}")
    if args.stop_price:
        print(f"  Stop   : {args.stop_price}")

    try:
        if order_type == 'MARKET':
            order = order_manager.place_market_order(symbol, side, args.quantity)
        elif order_type == 'LIMIT':
            if not args.price:
                print(f"{Fore.RED}Error: --price is required for LIMIT orders{Style.RESET_ALL}")
                sys.exit(1)
            order = order_manager.place_limit_order(symbol, side, args.quantity, args.price)
        elif order_type == 'STOP_MARKET':
            if not args.stop_price:
                print(f"{Fore.RED}Error: --stop-price is required for STOP_MARKET orders{Style.RESET_ALL}")
                sys.exit(1)
            try:
                order = order_manager.place_stop_market_order(symbol, side, args.quantity, args.stop_price)
            except NotImplementedError as e:
                print(f"{Fore.YELLOW}Note: {e}{Style.RESET_ALL}")
                sys.exit(0)
        else:
            print(f"{Fore.RED}Error: Unsupported order type '{order_type}'. Use MARKET, LIMIT, or STOP_MARKET.{Style.RESET_ALL}")
            sys.exit(1)

        print_order_result(order)

    except ValidationError as e:
        print(f"{Fore.RED}Validation error: {e}{Style.RESET_ALL}")
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}Failed to place order: {e}{Style.RESET_ALL}")
        logger.error(f"Order failed: {e}")
        sys.exit(1)


# ── Interactive menu (kept as fallback / bonus UX) ──────────────────────────

class TradingBotCLI:
    def __init__(self):
        self.logger = setup_logging()
        self.client = None
        self.order_manager = None

    def initialize_client(self):
        try:
            self.client = BinanceFuturesClient()
            self.order_manager = OrderManager(self.client)
            self.logger.info("Client initialized successfully")
            return True
        except Exception as e:
            print(f"{Fore.RED}Error initializing client: {e}{Style.RESET_ALL}")
            self.logger.error(f"Client initialization failed: {e}")
            return False

    def display_menu(self):
        print(f"\n{Fore.CYAN}=== Binance Futures Trading Bot ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Test Connection")
        print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Get Account Info")
        print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Get Current Price")
        print(f"{Fore.YELLOW}4.{Style.RESET_ALL} Place Market Order")
        print(f"{Fore.YELLOW}5.{Style.RESET_ALL} Place Limit Order")
        print(f"{Fore.YELLOW}6.{Style.RESET_ALL} Place Stop Market Order (Bonus)")
        print(f"{Fore.YELLOW}7.{Style.RESET_ALL} View Open Orders")
        print(f"{Fore.YELLOW}8.{Style.RESET_ALL} Cancel Order")
        print(f"{Fore.RED}0.{Style.RESET_ALL} Exit")
        print("-" * 40)

    def get_input(self, prompt, cast=str):
        while True:
            try:
                val = input(f"{Fore.GREEN}{prompt}: {Style.RESET_ALL}")
                return cast(val.strip())
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please try again.{Style.RESET_ALL}")

    def run_interactive(self):
        print(f"{Fore.CYAN}Welcome to Binance Futures Trading Bot!{Style.RESET_ALL}")
        if not self.initialize_client():
            return

        actions = {
            1: self._test_connection,
            2: self._account_info,
            3: self._current_price,
            4: self._market_order,
            5: self._limit_order,
            6: self._stop_market_order,
            7: self._open_orders,
            8: self._cancel_order,
        }

        while True:
            self.display_menu()
            choice = self.get_input("Enter your choice", int)
            if choice == 0:
                print(f"{Fore.YELLOW}Goodbye!{Style.RESET_ALL}")
                break
            action = actions.get(choice)
            if action:
                action()
            else:
                print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
            input(f"\n{Fore.GREEN}Press Enter to continue...{Style.RESET_ALL}")

    def _test_connection(self):
        try:
            ok = self.client.test_connection()
            msg = "Connection successful!" if ok else "Connection failed!"
            color = Fore.GREEN if ok else Fore.RED
            print(f"{color}{msg}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

    def _account_info(self):
        try:
            acc = self.client.get_account_info()
            print(f"\n{Fore.CYAN}Account Info:{Style.RESET_ALL}")
            print(f"  Wallet Balance : {float(acc['totalWalletBalance'])} USDT")
            print(f"  Available      : {float(acc['availableBalance'])} USDT")
            print(f"  Unrealized PNL : {float(acc['totalUnrealizedPnl'])} USDT")
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

    def _current_price(self):
        symbol = self.get_input("Symbol (e.g. BTCUSDT)").upper()
        try:
            price = self.client.get_current_price(symbol)
            print(f"{Fore.GREEN}{symbol}: {price} USDT{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

    def _market_order(self):
        symbol = self.get_input("Symbol").upper()
        side = self.get_input("Side (BUY/SELL)").upper()
        qty = self.get_input("Quantity", float)
        try:
            order = self.order_manager.place_market_order(symbol, side, qty)
            print_order_result(order)
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

    def _limit_order(self):
        symbol = self.get_input("Symbol").upper()
        side = self.get_input("Side (BUY/SELL)").upper()
        qty = self.get_input("Quantity", float)
        price = self.get_input("Price", float)
        try:
            order = self.order_manager.place_limit_order(symbol, side, qty, price)
            print_order_result(order)
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

    def _stop_market_order(self):
        symbol = self.get_input("Symbol").upper()
        side = self.get_input("Side (BUY/SELL)").upper()
        qty = self.get_input("Quantity", float)
        stop_price = self.get_input("Stop Price", float)
        try:
            order = self.order_manager.place_stop_market_order(symbol, side, qty, stop_price)
            print_order_result(order)
        except NotImplementedError as e:
            print(f"{Fore.YELLOW}Note: {e}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

    def _open_orders(self):
        symbol = input(f"{Fore.GREEN}Symbol (Enter for all): {Style.RESET_ALL}").strip().upper() or None
        try:
            orders = self.order_manager.get_open_orders(symbol)
            if orders:
                for o in orders:
                    print(f"  {o['orderId']} | {o['symbol']} | {o['side']} | {o['type']} | "
                          f"Qty: {o['origQty']} | Price: {o.get('price','N/A')} | {o['status']}")
            else:
                print(f"{Fore.GREEN}No open orders.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")

    def _cancel_order(self):
        symbol = self.get_input("Symbol").upper()
        order_id = self.get_input("Order ID", int)
        try:
            result = self.order_manager.cancel_order(symbol, order_id)
            print(f"{Fore.GREEN}Cancelled order {result['orderId']} — Status: {result['status']}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")


# ── Entry point ──────────────────────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet Trading Bot"
    )
    subparsers = parser.add_subparsers(dest="command")

    # 'order' subcommand
    order_p = subparsers.add_parser("order", help="Place an order")
    order_p.add_argument("--symbol",     required=True,  help="Trading pair, e.g. BTCUSDT")
    order_p.add_argument("--side",       required=True,  choices=["BUY", "SELL", "buy", "sell"])
    order_p.add_argument("--type",       required=True,  choices=["MARKET", "LIMIT", "STOP_MARKET",
                                                                    "market", "limit", "stop_market"])
    order_p.add_argument("--quantity",   required=True,  type=float, help="Order quantity")
    order_p.add_argument("--price",      type=float,     help="Limit price (required for LIMIT)")
    order_p.add_argument("--stop-price", type=float,     dest="stop_price",
                         help="Stop price (required for STOP_MARKET)")

    # 'interactive' subcommand
    subparsers.add_parser("interactive", help="Launch interactive menu")

    return parser


def main():
    logger = setup_logging()
    parser = build_parser()
    args = parser.parse_args()

    # Default to interactive if no subcommand given
    if not args.command or args.command == "interactive":
        cli = TradingBotCLI()
        cli.logger = logger
        cli.run_interactive()
        return

    if args.command == "order":
        try:
            client = BinanceFuturesClient()
            order_manager = OrderManager(client)
        except Exception as e:
            print(f"{Fore.RED}Failed to initialize client: {e}{Style.RESET_ALL}")
            logger.error(f"Client init failed: {e}")
            sys.exit(1)

        cmd_order(args, order_manager, logger)


if __name__ == "__main__":
    main()
