# CoolCryptoCode

A comprehensive cryptocurrency and stock trading analysis toolkit featuring trading simulators, strategy backtesting, and real-time data visualization.

## 🚀 Features

- **Interactive Trading Simulator** - Web-based Streamlit app for simulating stock trades with portfolio management
- **Trading Strategy Framework** - Extensible abstract base classes for implementing custom trading strategies
- **Backtesting Engine** - Simulate trading strategies on historical cryptocurrency and stock data
- **Trailing Stop Management** - Built-in support for trailing stops on both long and short positions
- **Real-time Data Fetching** - Integration with Yahoo Finance for up-to-date market data
- **Polymarket Integration** - Connect to Polymarket for prediction market trading
- **Data Analysis Notebooks** - Jupyter notebooks for cryptocurrency market analysis and visualization

## 📋 Requirements

This project uses Python 3.x and requires numerous dependencies listed in `requirements.txt`. Key dependencies include:

- `streamlit` - Web interface for the trading simulator
- `yfinance` - Yahoo Finance data fetching
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computations
- `matplotlib` - Data visualization
- `seaborn` - Statistical data visualization
- `scikit-learn` - Machine learning utilities
- `statsmodels` - Statistical modeling

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/AkeBoss-tech/CoolCryptoCode.git
cd CoolCryptoCode
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

### Trading Simulator App

Launch the interactive Streamlit trading simulator:

```bash
streamlit run app.py
```

Features:
- Select stock tickers (default: AAPL)
- Set date ranges for historical data
- Choose currency (USD, EUR, JPY, GBP)
- Buy/sell shares with real-time portfolio tracking
- Advance through time steps to simulate trading over time
- Visualize stock prices with Matplotlib charts

### Trading Strategy Backtesting

Use the `helper.py` module to create and backtest custom trading strategies:

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

Fetch and cache financial data using the utility functions:

```python
from util import get_data

# Fetch cryptocurrency data (cached locally)
btc_data = get_data('BTC-USD')
eth_data = get_data('ETH-USD')
doge_data = get_data('DOGE-USD')
```

The `get_data()` function automatically caches data as CSV files in the `data/` directory to avoid repeated API calls.

### Creating Custom Trading Strategies

Extend the `TradingStrategy` abstract base class to implement your own strategies:

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

## 📁 Project Structure

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

## 🎯 Key Components

### TradingStrategy (Abstract Base Class)

Provides the framework for implementing trading strategies with:
- Abstract `decide_action()` method for trading decisions
- Abstract `manage()` method for position management
- Built-in `manage_trailing_stops()` for automatic stop-loss management
- Configurable trailing stop percentages for buys and shorts

### StockTradingSimulation

The main simulation engine that:
- Tracks cash and cryptocurrency balances
- Manages open positions (both long and short)
- Executes trades based on strategy decisions
- Calculates portfolio value over time
- Generates performance statistics and visualizations

### RandomStrategy

A sample implementation that randomly chooses actions (buy/short/nothing) for demonstration and baseline comparison purposes.

## 📊 Data

The project includes historical data for:
- **Cryptocurrencies**: Bitcoin (BTC-USD), Ethereum (ETH-USD), Dogecoin (DOGE-USD), Ripple (XRP-USD)
- **Stock Indices**: S&P 500 (^GSPC), Dow Jones (^DJI)

Data is fetched via Yahoo Finance API and cached locally in 15-minute intervals.

## 🔗 Polymarket Integration

The `polymarket/` directory contains code for integrating with Polymarket prediction markets. See `polymarket/socket.py` for client initialization examples.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📝 License

This project is provided as-is for educational and research purposes.

## ⚠️ Disclaimer

This software is for educational and research purposes only. It is not financial advice. Trading cryptocurrencies and stocks involves substantial risk of loss. Always do your own research and consult with qualified financial advisors before making investment decisions.
