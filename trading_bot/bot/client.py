"""
Binance Futures Testnet Client Wrapper
Handles API connections and basic operations
"""

import os
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class BinanceFuturesClient:
    """Wrapper for Binance Futures Testnet API client"""
    
    def __init__(self):
        """Initialize client with testnet credentials"""
        load_dotenv()
        
        # Get API credentials from environment variables
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')
        
        if not api_key or not api_secret:
            raise ValueError("API credentials not found. Please set BINANCE_API_KEY and BINANCE_API_SECRET environment variables.")
        
        # Initialize client and point futures calls at the futures testnet
        self.client = Client(
            api_key=api_key,
            api_secret=api_secret,
        )
        # Override the futures URL to the testnet endpoint
        self.client.FUTURES_URL = self.client.FUTURES_TESTNET_URL
        
        logger.info("Binance Futures Testnet client initialized")
    
    def test_connection(self):
        """Test connection to Binance Futures Testnet"""
        try:
            # Get server time to test connection
            server_time = self.client.futures_time()
            logger.info(f"Connection successful. Server time: {server_time}")
            return True
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def get_account_info(self):
        """Get futures account information"""
        try:
            account = self.client.futures_account()
            logger.info("Account information retrieved successfully")
            return account
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Failed to get account info: {e}")
            raise
    
    def get_symbol_info(self, symbol):
        """Get symbol trading information"""
        try:
            info = self.client.futures_exchange_info()
            for s in info['symbols']:
                if s['symbol'] == symbol:
                    logger.info(f"Symbol info retrieved for {symbol}")
                    return s
            logger.warning(f"Symbol {symbol} not found")
            return None
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Failed to get symbol info: {e}")
            raise
    
    def get_current_price(self, symbol):
        """Get current price for a symbol"""
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            logger.info(f"Current price for {symbol}: {price}")
            return price
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Failed to get current price for {symbol}: {e}")
            raise
