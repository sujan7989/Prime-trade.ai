# Prime Trade AI - Binance Futures Trading Bot

A simplified trading bot for Binance Futures Testnet (USDT-M) built with Python.

## Features

- **Market Orders**: Place market orders instantly
- **Limit Orders**: Place limit orders with specific prices
- **Stop Market Orders**: Place stop orders (bonus feature)
- **Account Management**: View account information and balances
- **Order Management**: View, cancel, and check order status
- **Real-time Pricing**: Get current prices for any symbol
- **Comprehensive Logging**: All operations are logged with timestamps
- **Input Validation**: Robust validation for all user inputs
- **Error Handling**: Proper exception handling for API errors
- **CLI Interface**: User-friendly command-line interface with colored output

## Setup Instructions

### 1. Prerequisites

- Python 3.7 or higher
- Binance Futures Testnet account

### 2. Get Binance Testnet Credentials

1. Register and activate a Binance Futures Testnet account
2. Generate API credentials (API Key & Secret)
3. Ensure you have testnet funds in your account

### 3. Installation

1. Clone or download this project
2. Navigate to the project directory
3. Install dependencies:

```bash
pip install -r requirements.txt
```

### 4. Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit the `.env` file and add your Binance Testnet API credentials:
```
BINANCE_API_KEY=your_actual_api_key
BINANCE_API_SECRET=your_actual_api_secret
```

## Running the Application

### Non-interactive (argparse) — recommended

```bash
# Market order
python main.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Limit order
python main.py order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 80000

# Stop Market order (bonus)
python main.py order --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --stop-price 75000
```

### Interactive menu

```bash
python main.py interactive
# or simply:
python main.py
```

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py           # Package initialization
│   ├── client.py             # Binance client wrapper
│   ├── orders.py             # Order placement logic
│   ├── validators.py         # Input validation
│   ├── logging_config.py     # Logging configuration
│   └── cli.py                # CLI entry point
├── logs/                     # Log files (created automatically)
├── main.py                   # Main application entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## API Endpoints Used

- **Testnet Base URL**: `https://testnet.binancefuture.com`
- **Account Info**: `/fapi/v1/account`
- **Market Data**: `/fapi/v1/ticker/price`
- **Order Management**: `/fapi/v1/order`
- **Open Orders**: `/fapi/v1/openOrders`

## Logging

All operations are logged to files in the `logs/` directory:
- Log files are named with timestamps: `trading_bot_YYYYMMDD_HHMMSS.log`
- Logs include API requests, responses, and errors
- Console output is also logged for real-time monitoring

## Error Handling

The bot includes comprehensive error handling for:
- Invalid user inputs
- API errors (invalid credentials, insufficient funds, etc.)
- Network failures
- Invalid order parameters

## Assumptions & Limitations

- This bot works only with Binance Futures Testnet (not mainnet)
- Orders are placed in USDT-margined futures
- Minimum order quantities and price precisions follow Binance rules
- The bot assumes proper API permissions for trading

## Security Notes

- Never share your API credentials
- Use testnet credentials only
- The `.env` file should not be committed to version control
- Consider using IP restrictions for your API keys

## Dependencies

- `python-binance`: Official Binance Python API
- `requests`: HTTP library for API calls
- `python-dotenv`: Environment variable management
- `colorama`: Cross-platform colored terminal output

## Testing

The bot has been tested with:
- Market orders (BTCUSDT, ETHUSDT)
- Limit orders with various price points
- Account information retrieval
- Order cancellation and status checking

## Bonus Features Implemented

- **Stop Market Orders**: Advanced order type for risk management
- **Enhanced CLI UX**: Colored output, input validation, clear error messages
- **Comprehensive Logging**: Detailed logs for all operations

## Troubleshooting

### Common Issues

1. **"API credentials not found"**
   - Ensure `.env` file exists with correct credentials
   - Check file permissions

2. **"Invalid API key"**
   - Verify testnet credentials (not mainnet)
   - Check API key permissions

3. **"Insufficient balance"**
   - Ensure you have testnet funds
   - Check wallet balance via option 2

4. **"Invalid symbol"**
   - Use correct symbol format (e.g., BTCUSDT)
   - Verify symbol exists on testnet

### Getting Help

- Check the log files in `logs/` directory for detailed error messages
- Ensure all dependencies are installed correctly
- Verify Binance Testnet account is active and funded

## License

This project is for educational purposes as part of the Python Developer Intern Assignment.
