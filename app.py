import yfinance as yf
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import datetime
import requests

# Initialize the app
app = Dash(__name__)
server = app.server

# Set custom user agent for yfinance
user_agent = 'Mozilla/5.0'
yf.pdr_override()  # Reset any existing overrides

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
        # Create session with custom headers
        session = requests.Session()
        session.headers['User-agent'] = user_agent
        
        # Get stock data with custom session
        stock = yf.Ticker(ticker, session=session)
        
        # Use date range instead of period
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=90)
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            return px.line(title=f"No data found for {ticker}"), f"❌ No data found for {ticker}"

        hist_reset = hist.reset_index()
        
        fig = px.line(
            hist_reset,
            x='Date',
            y='Close',
            title=f"{ticker.upper()} Stock Price (Last 3 Months)",
            labels={'Close': 'Price (USD)'},
            template='plotly_dark'
        )
        fig.update_traces(line=dict(width=2.5))
        fig.update_layout(paper_bgcolor='black', plot_bgcolor='black')

        current_price = hist['Close'][-1]
        volume = hist['Volume'][-1]

        info_text = [
            html.Span(f"Current Price: ${current_price:,.2f} | "),
            html.Span(f"Volume: {volume:,.0f}")
        ]

        return fig, info_text

    except Exception as e:
        error_msg = f"❌ Error fetching {ticker}: {str(e)}"
        fig = px.line(title=error_msg)
        fig.update_layout(template='plotly_dark')
        return fig, html.Span(error_msg, style={'color': 'red'})

# WSGI application
application = server