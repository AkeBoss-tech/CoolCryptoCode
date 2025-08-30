from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt, seaborn as sns

class TradingStrategy(ABC):
    """
    Base class for any trading strategy.
    """
    def __init__(self, buy_trail_pct=0.05, sell_trail_pct=0.02):
        self.buy_trail_pct = buy_trail_pct  # Trailing stop percentage
        self.sell_trail_pct = sell_trail_pct  # Trailing stop percentage

    @abstractmethod
    def decide_action(self, current_data, positions, cash_balance, crypto_balance, coin_orders):
        """
        Decides what action to take (buy, short, or nothing).
        
        Parameters:
        - current_data: The current market data row (such as price).
        - positions: The current open positions in the market.
        - cash_balance: Current cash balance.
        - crypto_balance: Current crypto balance.
        - coin_orders: Number of coins per order.

        Returns:
        - A string representing the action ('buy', 'short', 'nothing').
        """
        pass

    @abstractmethod
    def manage(self, current_data, positions, crypto_balance, coin_orders, cash_balance):
        """
        Manages the portfolio before the first trade
        """
        pass

    def manage_clear_position(self, current_data, positions, crypto_balance, coin_orders, cash_balance):
        """ 
        Close all positions.

        Sell all buy positions and buy back all short positions.
        """
        
        price = current_data['Open']
        for idx, position in positions[positions["Price Sold"].isna()].iterrows():
            if position["Type"] == "buy":
                coins_to_sell = min(coin_orders, crypto_balance)
                crypto_balance -= coins_to_sell
                cash_balance = coins_to_sell * price
                gross_profit = coins_to_sell * (price - position["Price Bought"])
                positions.loc[idx, "Price Sold"] = price
                positions.loc[idx, "Value Sold"] = price * coins_to_sell
                positions.loc[idx, "Gross Profit"] = gross_profit
                positions.loc[idx, "Time Sold"] = current_data.name
                positions.loc[idx, "Coins"] = coin_orders
                positions.loc[idx, "Time Held"] = current_data.name - position["Date Bought"]

            elif position["Type"] == "short":
                coins_to_cover = coin_orders
                cash_balance -= coins_to_cover * price
                gross_profit = coins_to_cover * (position["Price Bought"] - price)
                positions.loc[idx, "Price Sold"] = price
                positions.loc[idx, "Value Sold"] = price * coins_to_cover
                positions.loc[idx, "Gross Profit"] = gross_profit
                positions.loc[idx, "Time Sold"] = current_data.name
                positions.loc[idx, "Coins"] = coin_orders
                positions.loc[idx, "Time Held"] = current_data.name - position["Date Bought"]

        return positions, cash_balance, crypto

    def manage_trailing_stops(self, current_data, positions, crypto_balance, coin_orders, cash_balance):
        """
        Manages trailing stops for open positions.

        Parameters:
        - current_data: The current market data row (such as price).
        - positions: The current open positions in the market.
        - crypto_balance: Current crypto balance.
        - coin_orders: Number of coins per order.

        Returns:
        - Updated positions with trailing stops managed.
        """
        price = current_data['Open']
        for idx, position in positions[positions["Price Sold"].isna()].iterrows():
            if position["Type"] == "buy":
                # Adjust trailing stop if market moves up
                new_trailing_stop = max(position["Trailing Stop"] or 0, price * (1 - self.buy_trail_pct))
                positions.loc[idx, "Trailing Stop"] = new_trailing_stop

                # Sell position if price drops below the trailing stop
                if price <= new_trailing_stop:
                    coins_to_sell = min(coin_orders, crypto_balance)
                    crypto_balance -= coins_to_sell
                    cash_balance = coins_to_sell * price
                    gross_profit = coins_to_sell * (price - position["Price Bought"])
                    positions.loc[idx, "Price Sold"] = price
                    positions.loc[idx, "Value Sold"] = price * coins_to_sell
                    positions.loc[idx, "Gross Profit"] = gross_profit
                    positions.loc[idx, "Time Sold"] = current_data.name
                    positions.loc[idx, "Coins"] = coin_orders
                    positions.loc[idx, "Time Held"] = current_data.name - position["Date Bought"]

            elif position["Type"] == "short":
                # Adjust trailing stop if market moves down
                new_trailing_stop = min(position["Trailing Stop"] or float('inf'), price * (1 + self.sell_trail_pct))
                positions.loc[idx, "Trailing Stop"] = new_trailing_stop

                # Cover position if price rises above the trailing stop
                if price >= new_trailing_stop:
                    coins_to_cover = coin_orders
                    cash_balance -= coins_to_cover * price
                    gross_profit = coins_to_cover * (position["Price Bought"] - price)
                    positions.loc[idx, "Price Sold"] = price
                    positions.loc[idx, "Value Sold"] = price * coins_to_cover
                    positions.loc[idx, "Gross Profit"] = gross_profit
                    positions.loc[idx, "Time Sold"] = current_data.name
                    positions.loc[idx, "Coins"] = coin_orders
                    positions.loc[idx, "Time Held"] = current_data.name - position["Date Bought"]
        
        return positions, cash_balance, crypto_balance

class RandomStrategy(TradingStrategy):
    """
    A random trading strategy that chooses to buy, short, or do nothing with equal probability.
    """
    def decide_action(self, current_data, positions, cash_balance, crypto_balance, coin_orders, buy_trail_pct=0.05, sell_trail_pct=0.02):
        # Probabilities for buy, nothing, short
        probs = [0.4, 0.4, 0.2]
        action = np.random.choice(["buy", "nothing", "short"], p=probs)
        self.buy_trail_pct = buy_trail_pct
        self.sell_trail_pct = sell_trail_pct
        return action
    
    def manage(self, current_data, positions, crypto_balance, coin_orders, cash_balance):
        return super().manage_trailing_stops(current_data, positions, crypto_balance, coin_orders, cash_balance)


class StockTradingSimulation:
    def __init__(self, start_cash, coin_orders, strategy: TradingStrategy):
        self.START_CASH = start_cash
        self.coin_orders = coin_orders
        self.strategy = strategy  # The strategy is passed in here
        self.reset()

    def reset(self):
        # Reset all tracking variables
        self.cash_balance = self.START_CASH
        self.crypto_balance = 0
        self.positions = pd.DataFrame(columns=[
            "Date Bought", "Price Bought", "Price Sold", "Value Sold", 
            "Gross Profit", "Time Sold", "Time Held", "Coins", "Type", "Trailing Stop"
        ])
        self.portfolio_value = []
        self.profits_over_time = []
        self.cash_over_time = []
        self.crypto_over_time = []
        self.time = []

    def execute_trades(self, data):
        """
        Executes trades on the data, using the strategy to decide the actions.

        Parameters:
        - data: DataFrame of price data.
        """
        for i in range(0, len(data) - 1, 1):  # Iterate through price data
            row = data.iloc[i]
            price = row['Open']
            date = row.name

            # First, manage trailing stops for all open positions
            self.positions, self.cash_balance, self.crypto_balance = self.strategy.manage(
                row, self.positions, self.crypto_balance, self.coin_orders, self.cash_balance
            )

            # Use the strategy to decide action (buy, short, or nothing)
            action = self.strategy.decide_action(row, self.positions, self.cash_balance, self.crypto_balance, self.coin_orders)

            if action == "buy" and self.cash_balance > price * self.coin_orders:
                # Execute Buy
                self.crypto_balance += self.coin_orders
                self.cash_balance -= price * self.coin_orders
                self.positions = pd.concat([self.positions, pd.DataFrame({
                    "Date Bought": [date],
                    "Price Bought": [price],
                    "Price Sold": [None],
                    "Value Sold": [None],
                    "Gross Profit": [None],
                    "Time Sold": [None],
                    "Time Held": [None],
                    "Coins": [self.coin_orders],
                    "Type": ["buy"],
                    "Trailing Stop": [price * (1 - self.strategy.buy_trail_pct)]
                })], ignore_index=True)

            elif action == "short" and self.cash_balance > price * self.coin_orders:
                # Open Short Position
                self.cash_balance += price * self.coin_orders  # Borrow and sell immediately
                self.positions = pd.concat([self.positions, pd.DataFrame({
                    "Date Bought": [date],
                    "Price Bought": [price],
                    "Price Sold": [None],
                    "Value Sold": [None],
                    "Gross Profit": [None],
                    "Time Sold": [None],
                    "Time Held": [None],
                    "Coins": [self.coin_orders],
                    "Type": ["short"],
                    "Trailing Stop": [price * (1 + self.strategy.sell_trail_pct)]
                })], ignore_index=True)

            # Track portfolio and balances
            total_portfolio_value = self.cash_balance + (self.crypto_balance * price)
            # subtract the current price of the short position from portfolio value
            current_positions = self.positions[self.positions["Price Sold"].isna()]
            current_positions = current_positions[current_positions["Type"] == "short"]
            total_portfolio_value -= (current_positions["Price Bought"] * current_positions["Coins"]).sum()
            self.portfolio_value.append((date, total_portfolio_value))
            self.profits_over_time.append((date, self.positions["Gross Profit"].sum()))
            self.cash_over_time.append((date, self.cash_balance))
            self.crypto_over_time.append((date, self.crypto_balance))
            self.time.append(date)

        self.end_simulation(data)

    def end_simulation(self, data):
        # At the end, realize all positions
        row = data.iloc[-1]
        price = row['Open']
        date = row.name

        for idx, position in self.positions[self.positions["Price Sold"].isna()].iterrows():
            if position["Type"] == "buy":
                coins_to_sell = min(self.coin_orders, self.crypto_balance)
                self.crypto_balance -= coins_to_sell
                self.cash_balance += coins_to_sell * price
                gross_profit = coins_to_sell * (price - position["Price Bought"])
                self.positions.loc[idx, "Price Sold"] = price
                self.positions.loc[idx, "Value Sold"] = price * coins_to_sell
                self.positions.loc[idx, "Gross Profit"] = gross_profit
                self.positions.loc[idx, "Time Sold"] = date
                self.positions.loc[idx, "Coins"] = self.coin_orders
                self.positions.loc[idx, "Time Held"] = date - position["Date Bought"]

            elif position["Type"] == "short":
                coins_to_cover = self.coin_orders
                self.cash_balance -= coins_to_cover * price
                gross_profit = coins_to_cover * (position["Price Bought"] - price)
                self.positions.loc[idx, "Price Sold"] = price
                self.positions.loc[idx, "Value Sold"] = price * coins_to_cover
                self.positions.loc[idx, "Gross Profit"] = gross_profit
                self.positions.loc[idx, "Time Sold"] = date
                self.positions.loc[idx, "Coins"] = self.coin_orders
                self.positions.loc[idx, "Time Held"] = date - position["Date Bought"]

        # Track final portfolio and balances
        total_portfolio_value = self.cash_balance + (self.crypto_balance * price)
        self.portfolio_value.append((date, total_portfolio_value))
        self.profits_over_time.append((date, self.positions["Gross Profit"].sum()))
        self.cash_over_time.append((date, self.cash_balance))
        self.crypto_over_time.append((date, self.crypto_balance))
        self.time.append(date)

    def plot(self):
        # Plot Portfolio, Cash, and Crypto Balances Over Time
        plt.figure(figsize=(12, 6))

        plt.plot(self.time, self.crypto_value, label="Crypto Value", color="red")
        plt.plot(self.cash_df["Date"], self.cash_df["Cash Balance"], label="Cash Balance", color="orange")
        plt.plot(self.crypto_df["Date"], self.crypto_df["Crypto Balance"], label="Crypto Balance", color="green")
        plt.plot(self.portfolio_df["Date"], self.portfolio_df["Portfolio Value"], label="Portfolio Value", color="blue")

        plt.title("Portfolio, Cash, and Crypto Balances Over Time")
        plt.xlabel("Date")
        plt.ylabel("Value")
        plt.legend()
        plt.show()

    def plot_positions(self):
        sns.set_style('whitegrid')

        plt.figure(figsize=(12, 6))


        plt.plot(self.time, self.btc_price, label='Open', color='blue')

        # graph the buy positions
        """ plt.plot(positions[positions['Type'] == 'buy']['Date Bought'], 
                positions[positions['Type'] == 'buy']['Price Bought'], 
                'o', markersize=5, color='green', label='Buy') """

        # starting from price bought draw a line to price sold
        for idx, position in self.positions[self.positions['Type'] == 'short'].iterrows():
            if pd.notna(position['Price Sold']):
                color = 'green' if position['Gross Profit'] > 0 else 'red'
                plt.plot([position['Date Bought'], position['Time Sold']], 
                        [position['Price Bought'], position['Price Sold']], 
                        color=color)

        # starting from price bought draw a line to price sold
        for idx, position in self.positions[self.positions['Type'] == 'buy'].iterrows():
            if pd.notna(position['Price Sold']):
                color = 'green' if position['Gross Profit'] > 0 else 'red'
                plt.plot([position['Date Bought'], position['Time Sold']], 
                        [position['Price Bought'], position['Price Sold']], 
                        color=color)
                

        # plot average value of positions at specific time
        average_value = pd.DataFrame(columns=['Date', 'Value'])
        # set date to index
        average_value['Date'] = self.time
        for date in self.time:
            buy = self.positions[(self.positions['Date Bought'] <= date) & (self.positions['Type'] == 'buy')]
            short = self.positions[(self.positions['Date Bought'] <= date) & (self.positions['Type'] == 'short')]
            value = (buy['Price Bought'] * buy['Coins']).sum() - (short['Price Bought'] * short['Coins']).sum()
            average_value.loc[average_value['Date'] == date, 'Value'] = value / (buy['Coins'].sum() - short['Coins'].sum())

        plt.plot(average_value['Date'], average_value['Value'], label='Average Value', color='black')
                
        """ 
        # graph the short positions
        plt.plot(positions[positions['Type'] == 'short']['Date Bought'], 
                positions[positions['Type'] == 'short']['Price Bought'], 
                'o', markersize=5, color='red', label='Short') """

        plt.legend()

        plt.title('Positions')
        plt.xlabel('Date')
        plt.ylabel('Price')

        DAYS = 30

        """ plt.xlim(btc.index[-1] - pd.DateOffset(days=DAYS), btc.index[-1]) """

    def stats(self, data):
        # Convert tracking lists to DataFrames
        self.portfolio_df = pd.DataFrame(self.portfolio_value, columns=["Date", "Portfolio Value"])
        self.profits_df = pd.DataFrame(self.profits_over_time, columns=["Date", "Cumulative Profit"])
        self.cash_df = pd.DataFrame(self.cash_over_time, columns=["Date", "Cash Balance"])
        self.crypto_df = pd.DataFrame(self.crypto_over_time, columns=["Date", "Crypto Balance"])

        self.btc_price = [data['Open'].loc[date] for date in self.time]
        self.crypto_value = self.crypto_df["Crypto Balance"] * self.btc_price