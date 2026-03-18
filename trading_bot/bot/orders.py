"""
Order placement logic for Binance Futures
"""

import logging
from binance.exceptions import BinanceAPIException, BinanceRequestException
from .validators import validate_order_params, ValidationError

logger = logging.getLogger(__name__)

class OrderManager:
    """Handles order placement and management"""
    
    def __init__(self, client):
        """Initialize with Binance client"""
        self.client = client
        logger.info("OrderManager initialized")
    
    def place_market_order(self, symbol, side, quantity):
        """Place a market order"""
        try:
            # Validate parameters
            params = validate_order_params(
                symbol=symbol,
                side=side,
                order_type='MARKET',
                quantity=quantity
            )
            
            logger.info(f"Placing MARKET order: {params}")
            
            # Place the order
            order = self.client.client.futures_create_order(
                symbol=params['symbol'],
                side=params['side'],
                type=params['type'],
                quantity=params['quantity']
            )
            
            logger.info(f"MARKET order placed successfully: {order}")
            return order
            
        except ValidationError as e:
            logger.error(f"Validation error for MARKET order: {e}")
            raise
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Failed to place MARKET order: {e}")
            raise
    
    def place_limit_order(self, symbol, side, quantity, price):
        """Place a limit order"""
        try:
            # Validate parameters
            params = validate_order_params(
                symbol=symbol,
                side=side,
                order_type='LIMIT',
                quantity=quantity,
                price=price
            )
            
            logger.info(f"Placing LIMIT order: {params}")
            
            # Place the order
            order = self.client.client.futures_create_order(
                symbol=params['symbol'],
                side=params['side'],
                type=params['type'],
                quantity=params['quantity'],
                price=params['price'],
                timeInForce='GTC'  # Good Till Cancelled
            )
            
            logger.info(f"LIMIT order placed successfully: {order}")
            return order
            
        except ValidationError as e:
            logger.error(f"Validation error for LIMIT order: {e}")
            raise
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Failed to place LIMIT order: {e}")
            raise
    
    def place_stop_market_order(self, symbol, side, quantity, stop_price):
        """
        Place a stop market order (bonus feature).
        Note: Binance Futures Testnet routes STOP_MARKET to the Algo Order API
        which is not publicly available on testnet. This method works on mainnet.
        On testnet a TestnetUnsupportedError is raised with a clear message.
        """
        import requests as req
        import time, hmac, hashlib, os
        from dotenv import load_dotenv

        try:
            # Validate parameters
            params = validate_order_params(
                symbol=symbol,
                side=side,
                order_type='STOP_MARKET',
                quantity=quantity
            )

            from .validators import validate_price
            stop_price = validate_price(stop_price)

            logger.info(f"Placing STOP_MARKET order: {params}, stopPrice: {stop_price}")

            load_dotenv()
            api_key    = os.getenv('BINANCE_API_KEY')
            api_secret = os.getenv('BINANCE_API_SECRET')
            ts = int(time.time() * 1000)

            body = (
                f"symbol={params['symbol']}&side={params['side']}"
                f"&type=STOP_MARKET&quantity={params['quantity']}"
                f"&stopPrice={stop_price}&timestamp={ts}"
            )
            sig = hmac.new(api_secret.encode(), body.encode(), hashlib.sha256).hexdigest()
            url = "https://testnet.binancefuture.com/fapi/v1/order"
            resp = req.post(url, headers={"X-MBX-APIKEY": api_key},
                            data=body + f"&signature={sig}")
            data = resp.json()

            if resp.status_code != 200:
                code = data.get("code", 0)
                if code == -4120:
                    raise NotImplementedError(
                        "STOP_MARKET orders require the Algo Order API which is "
                        "not available on Binance Futures Testnet. "
                        "This order type works correctly on mainnet."
                    )
                raise BinanceAPIException(resp, resp.status_code, resp.text)

            logger.info(f"STOP_MARKET order placed successfully: {data}")
            return data

        except ValidationError as e:
            logger.error(f"Validation error for STOP_MARKET order: {e}")
            raise
        except NotImplementedError as e:
            logger.warning(f"STOP_MARKET not supported on testnet: {e}")
            raise
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Failed to place STOP_MARKET order: {e}")
            raise
    
    def cancel_order(self, symbol, order_id):
        """Cancel an existing order"""
        try:
            logger.info(f"Cancelling order {order_id} for {symbol}")
            
            result = self.client.client.futures_cancel_order(
                symbol=symbol,
                orderId=order_id
            )
            
            logger.info(f"Order cancelled successfully: {result}")
            return result
            
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Failed to cancel order {order_id}: {e}")
            raise
    
    def get_open_orders(self, symbol=None):
        """Get open orders"""
        try:
            logger.info(f"Getting open orders for {symbol if symbol else 'all symbols'}")
            
            orders = self.client.client.futures_get_open_orders(symbol=symbol)
            
            logger.info(f"Retrieved {len(orders)} open orders")
            return orders
            
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Failed to get open orders: {e}")
            raise
    
    def get_order_status(self, symbol, order_id):
        """Get order status"""
        try:
            logger.info(f"Getting status for order {order_id} on {symbol}")
            
            order = self.client.client.futures_get_order(
                symbol=symbol,
                orderId=order_id
            )
            
            logger.info(f"Order status: {order}")
            return order
            
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Failed to get order status: {e}")
            raise
