# CoolCryptoCode

This is a toolkit for analyzing and simulating cryptocurrency and stock trading. It includes a web-based trading simulator, a framework for building and testing custom trading strategies, and tools for visualizing market data.

## Features

- Interactive Trading Simulator: A web-based Streamlit app for simulating stock trades with portfolio management
- Trading Strategy Framework: Extensible abstract base classes for implementing custom trading strategies
- Backtesting Engine: Simulate trading strategies on historical cryptocurrency and stock data
- Trailing Stop Management: Built-in support for trailing stops on both long and short positions
- Real-time Data Fetching: Integration with Yahoo Finance for up-to-date market data
- Polymarket Integration: Connect to Polymarket for prediction market trading
- Data Analysis Notebooks: Jupyter notebooks for cryptocurrency market analysis and visualization

## Requirements

This project is built with Python 3.x and has quite a few dependencies (see `requirements.txt` for the full list). The main ones you'll need are:

- `streamlit` - For the web interface
- `yfinance` - To fetch market data from Yahoo Finance
- `pandas` - Data manipulation and analysis
- `numpy` - Number crunching
- `matplotlib` - Creating charts and visualizations
- `seaborn` - Statistical plotting
- `scikit-learn` - Machine learning tools
- `statsmodels` - Statistical modeling

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd CoolCryptoCode
```

2. Set up a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Trading Simulator App

To run the interactive trading simulator, just fire up Streamlit:

```bash
streamlit run app.py
```

With this app, you can:
- Pick stock tickers to analyze (defaults to AAPL)
- Set custom date ranges for historical data
- Switch between different currencies (USD, EUR, JPY, GBP)
- Buy and sell shares while tracking your portfolio in real-time
- Step through time to simulate how your trades would have performed
- View stock price charts

### Trading Strategy Backtesting

You can build and test your own trading strategies using the modules in `helper.py`. Here's a quick example:

```python
from helper import StockTradingSimulation, RandomStrategy
from util import get_data

# Load historical data
data = get_data('BTC-USD')

# Create a strategy instance
strategy = RandomStrategy(buy_trail_pct=0.05, sell_trail_pct=0.02)

# Initialize simulation
sim = StockTradingSimulation(
    start_cash=10000,
    coin_orders=1,
    strategy=strategy
)

# Execute trades
sim.execute_trades(data)

# View statistics and plots
sim.stats(data)
sim.plot_positions()
```

### Data Fetching

Need market data? The `util.py` file has helper functions for that:

```python
from util import get_data

# Fetch cryptocurrency data (cached locally)
btc_data = get_data('BTC-USD')
eth_data = get_data('ETH-USD')
doge_data = get_data('DOGE-USD')
```

The `get_data()` function will automatically cache data to the `data/` directory so you don't have to keep fetching the same data over and over.

### Creating Custom Trading Strategies

Want to create your own trading strategy? Just extend the `TradingStrategy` base class:

```python
from helper import TradingStrategy

class MyStrategy(TradingStrategy):
    def decide_action(self, current_data, positions, cash_balance, 
                     crypto_balance, coin_orders, buy_trail_pct=0.05, 
                     sell_trail_pct=0.02):
        # Implement your trading logic here
        # Return: 'buy', 'short', or 'nothing'
        pass
    
    def manage(self, current_data, positions, crypto_balance, 
              coin_orders, cash_balance):
        # Implement position management logic
        return super().manage_trailing_stops(
            current_data, positions, crypto_balance, 
            coin_orders, cash_balance
        )
```

## Project Structure

```
CoolCryptoCode/
├── app.py                  # Streamlit trading simulator web app
├── helper.py               # Trading strategy classes and simulation engine
├── util.py                 # Utility functions for data fetching
├── requirements.txt        # Python dependencies
├── polymarket/            # Polymarket integration
│   └── socket.py          # Polymarket client examples
├── data/                  # Cached market data (CSV files)
│   ├── BTC-USD.csv
│   ├── ETH-USD.csv
│   ├── DOGE-USD.csv
│   ├── XRP-USD.csv
│   └── ...
├── crypto.ipynb           # Cryptocurrency analysis notebook
├── crypto-trail.ipynb     # Trailing stop analysis notebook
├── test.ipynb             # Testing and experimentation notebook
└── try.ipynb              # Additional experiments
```

## Key Components

### TradingStrategy (Abstract Base Class)

This is the foundation for building any trading strategy. It gives you:
- A `decide_action()` method where you implement your trading logic
- A `manage()` method for handling open positions
- Built-in `manage_trailing_stops()` to automatically manage stop-losses
- Configurable trailing stop percentages for both buys and shorts

### StockTradingSimulation

This is the main engine that runs your backtests. It handles:
- Keeping track of your cash and crypto balances
- Managing open positions (long and short)
- Executing trades based on what your strategy tells it to do
- Calculating your portfolio value over time
- Generating charts and statistics about your performance

### RandomStrategy

This is just a sample strategy that makes random trading decisions. It's useful for testing the system or as a baseline to compare your strategies against.

## Data

The repository includes historical data for several assets:
- Cryptocurrencies: Bitcoin (BTC-USD), Ethereum (ETH-USD), Dogecoin (DOGE-USD), Ripple (XRP-USD)
- Stock Indices: S&P 500 (^GSPC), Dow Jones (^DJI)

All data comes from Yahoo Finance with 15-minute intervals and gets cached locally as CSV files.

## Polymarket Integration

There's some code in the `polymarket/` folder for connecting to Polymarket prediction markets. Check out `polymarket/socket.py` if you want to see how to initialize a client.

## Contributing

Want to contribute? Great! You can:
- Report bugs you find
- Suggest new features
- Submit pull requests
- Help improve the documentation

## License

This project is provided as-is for educational and research purposes.

## Disclaimer

Just a heads up: this software is meant for educational and research purposes only. It's not financial advice, and you shouldn't treat it as such. Trading crypto and stocks is risky - you can lose money. Always do your own research and talk to a qualified financial advisor before making any investment decisions.
