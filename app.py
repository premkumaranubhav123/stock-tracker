import yfinance as yf
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import datetime
import requests
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter
import pandas as pd

class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass

# Initialize the app
app = Dash(__name__)
server = app.server

# Configure caching and rate limiting
session = CachedLimiterSession(
    limiter=Limiter(RequestRate(2, Duration.SECOND*5)),  # max 2 requests per 5 seconds
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
)

# Set custom headers to prevent blocking
session.headers['User-agent'] = 'Mozilla/5.0'

# App layout
app.layout = html.Div([
    html.H1("Stock Price Viewer", style={'textAlign': 'center', 'marginBottom': 30}),
    html.Div([
        html.Label("Enter Stock Ticker (e.g., TSLA, AAPL, NVDA):"),
        dcc.Input(id='ticker-input', value='TSLA', type='text', style={'fontSize': 18, 'marginLeft': 10}),
    ], style={'textAlign': 'center', 'marginBottom': 20}),
    dcc.Graph(id='price-graph'),
    html.Div(id='price-info', style={'textAlign': 'center', 'fontSize': 20, 'marginTop': 20})
])

@callback(
    [Output('price-graph', 'figure'),
     Output('price-info', 'children')],
    [Input('ticker-input', 'value')]
)
def update_stock_data(ticker):
    if not ticker:
        return px.line(title="Enter a valid ticker"), "Enter a ticker symbol"

    try:
        # Get stock data with our custom session
        stock = yf.Ticker(ticker, session=session)
        
        # Use 1y period for more reliable data
        hist = stock.history(period="1y")
        
        if hist.empty:
            # Try alternative method if standard approach fails
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=365)
            hist = stock.history(start=start_date, end=end_date)
            if hist.empty:
                raise ValueError(f"No data returned for {ticker}")

        # Process data
        hist = hist[hist['Close'].notna()]
        if len(hist) == 0:
            raise ValueError("Data contains no valid values")

        hist_reset = hist.reset_index()
        
        fig = px.line(
            hist_reset,
            x='Date',
            y='Close',
            title=f"{ticker.upper()} Stock Price (Last Year)",
            labels={'Close': 'Price (USD)'},
            template='plotly_dark'
        )
        fig.update_traces(line=dict(width=2.5))
        fig.update_layout(
            paper_bgcolor='black',
            plot_bgcolor='black',
            xaxis_title='Date',
            yaxis_title='Price (USD)'
        )

        current_price = hist['Close'][-1]
        volume = hist['Volume'][-1]

        info_text = [
            html.Span(f"Current Price: ${current_price:,.2f} | "),
            html.Span(f"Volume: {volume:,.0f}")
        ]

        return fig, info_text

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        fig = px.line(title=error_msg)
        fig.update_layout(template='plotly_dark')
        return fig, html.Span(error_msg, style={'color': 'red'})

application = server