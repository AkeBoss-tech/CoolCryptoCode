import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import io

# Initialize session state for portfolio and settings
if "portfolio" not in st.session_state:
    st.session_state.portfolio = {"cash": 10000, "shares": 0}
if "current_price" not in st.session_state:
    st.session_state.current_price = None
if "current_index" not in st.session_state:
    st.session_state.current_index = 0  # Tracks current point in simulation

# Function to fetch stock data
def fetch_stock_data(ticker, start="2020-01-01", end=None):
    data = yf.download(ticker, start=start, end=end)
    return data

# Function to plot data using Matplotlib
def plot_stock_data(data, title, ylabel):
    fig, ax = plt.subplots()
    ax.plot(data.index, data["Close"], label="Close Price", color="blue")
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid(True)
    
    # Convert plot to a streamlit-compatible format
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close(fig)
    return buf

# Sidebar for settings
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Enter Stock Ticker", value="AAPL")
start_date = st.sidebar.date_input("Start Date", value="2020-01-01")
before_date = st.sidebar.date_input("Before Date (optional)")
currency = st.sidebar.selectbox("Currency", options=["USD", "EUR", "JPY", "GBP"], index=0)
timesteps = st.sidebar.slider("Advance Timesteps", min_value=1, max_value=30, value=1)

# Currency exchange rates (mocked for demonstration)
exchange_rates = {"USD": 1.0, "EUR": 0.85, "JPY": 110.0, "GBP": 0.75}

# Fetch and display stock data
st.title(f"Trading Simulator - {ticker}")
end_date = before_date.strftime("%Y-%m-%d") if before_date else None
data = fetch_stock_data(ticker, start=start_date.strftime("%Y-%m-%d"), end=end_date)

if not data.empty:
    # Initialize session state for data
    if "data" not in st.session_state:
        st.session_state.data = data

    # Limit the data to the current point in the simulation
    simulation_data = st.session_state.data.iloc[: st.session_state.current_index + 1]

    # Update current price based on the latest point in simulation
    if not simulation_data.empty:
        st.session_state.current_price = float(simulation_data["Close"].iloc[-1]) * exchange_rates[currency]

    # Plot the data with Matplotlib
    st.subheader("Stock Price Chart")
    buf = plot_stock_data(
        simulation_data, 
        title=f"{ticker} Stock Prices (Up to Current Simulation Point)", 
        ylabel=f"Price ({currency})"
    )
    st.image(buf, use_container_width=True)

    # Trading actions
    st.subheader("Portfolio Management")
    st.write(f"Cash: {st.session_state.portfolio['cash'] * exchange_rates[currency]:.2f} {currency}")
    st.write(f"Shares: {st.session_state.portfolio['shares']}")
    st.write(f"Current Price: {st.session_state.current_price:.2f} {currency}")

    col1, col2, col3 = st.columns(3)
    with col1:
        buy_shares = st.number_input("Buy Shares", min_value=0, step=1, value=0)
        if st.button("Buy"):
            cost = buy_shares * st.session_state.current_price
            if cost <= st.session_state.portfolio["cash"] * exchange_rates[currency]:
                st.session_state.portfolio["cash"] -= cost / exchange_rates[currency]
                st.session_state.portfolio["shares"] += buy_shares
            else:
                st.error("Not enough cash!")

    with col2:
        sell_shares = st.number_input("Sell Shares", min_value=0, step=1, value=0)
        if st.button("Sell"):
            if sell_shares <= st.session_state.portfolio["shares"]:
                st.session_state.portfolio["shares"] -= sell_shares
                st.session_state.portfolio["cash"] += sell_shares * st.session_state.current_price / exchange_rates[currency]
            else:
                st.error("Not enough shares!")

    with col3:
        if st.button("Hold"):
            st.write("No action taken.")

    # Advance timesteps
    if st.button(f"Advance {timesteps} timesteps"):
        if st.session_state.current_index + timesteps < len(st.session_state.data):
            st.session_state.current_index += timesteps
            st.success(f"Advanced {timesteps} timesteps.")
        else:
            st.error("Not enough data to advance the specified number of timesteps.")

    # Display portfolio value
    portfolio_value = (
        st.session_state.portfolio["cash"] * exchange_rates[currency]
        + st.session_state.portfolio["shares"] * st.session_state.current_price
    )
    st.write(f"Portfolio Value: {portfolio_value:.2f} {currency}")
else:
    st.error("No data available. Please check the ticker symbol or start date.")
