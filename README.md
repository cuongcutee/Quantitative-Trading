# Quantitative Trading Platform

A modular Python codebase for collecting market data from Binance, running algorithmic trading strategies, and executing trades automatically.

## Features

- Binance REST API client with signed requests
- Market data ingestion into a SQL database (SQLite by default)
- CSV export utilities for analytics and research
- Moving average crossover strategy with backtesting support
- Trading engine supporting paper trading and live Binance execution
- Command line interface for orchestrating workflows

## Getting Started

### 1. Clone and install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

Copy the sample environment file and populate it with your Binance API credentials:

```bash
cp config/example.env .env
```

Update the following keys:

- `BINANCE_API_KEY`
- `BINANCE_API_SECRET`

Additional optional settings:

- `BINANCE_USE_TESTNET` (set to `true` to use the Binance testnet)
- `DATABASE_URL` (SQLAlchemy connection string)
- `TRADING_SYMBOLS` (comma-separated list of trading pairs)
- `CANDLES_INTERVAL` (e.g. `1m`, `1h`, `1d`)

### 3. Run commands

Collect candles:

```bash
python -m quant_trader.main collect --limit 200
```

Export to CSV:

```bash
python -m quant_trader.main export --limit 1000 --output data
```

Run trading engine in paper mode:

```bash
python -m quant_trader.main trade --paper
```

For live trading, omit `--paper` and set `--trade-size` to your desired quantity (ensure compliance with Binance lot sizes).

## Backtesting

The `Backtester` class allows simple evaluation of strategies against historical candles stored in the database. Extend the strategies package to add new algorithmic approaches.

## Development

Run tests with:

```bash
pytest
```

## Disclaimer

Use this software responsibly. Algorithmic trading carries significant risk. Always validate strategies on testnet or with paper trading before deploying real capital.
