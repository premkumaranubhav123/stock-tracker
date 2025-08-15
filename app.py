import yfinance as yf
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import datetime
import pandas as pd
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Initialize the app
app = Dash(__name__)
server = app.server

# App layout
app.layout = html.Div([
    html.H1("Stock Price Viewer", style={'textAlign': 'center', 'marginBottom': 30}),
    html.Div([
        html.Label("Enter Stock Ticker (e.g., TSLA, AAPL, NVDA):"),
        dcc.Input(
            id='ticker-input',
            value='TSLA',
            type='text',
            style={'fontSize': 18, 'marginLeft': 10}
        ),
    ], style={'textAlign': 'center', 'marginBottom': 20}),
    dcc.Loading(
        id="loading-graph",
        type="circle",
        children=dcc.Graph(
            id='price-graph',
            figure=px.line(title="Enter a ticker symbol").update_layout(
                template='plotly_dark',
                paper_bgcolor='black',
                plot_bgcolor='black'
            )
        )
    ),
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
        # Fetch data with 1 year history
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        
        # If empty, try alternative method
        if hist.empty:
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=365)
            hist = stock.history(start=start_date, end=end_date)
            if hist.empty:
                raise ValueError(f"No data found for {ticker}")

        # Ensure we have valid data points
        if len(hist) < 2:
            raise ValueError("Insufficient data points")

        # Reset index and clean data
        hist = hist.reset_index()
        hist = hist.dropna(subset=['Date', 'Close'])
        
        # Create the figure with proper configuration
        fig = px.line(
            hist,
            x='Date',
            y='Close',
            title=f"{ticker.upper()} Stock Price (Last Year)",
            labels={'Close': 'Price (USD)'}
        )
        
        # Update layout for better visibility
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='black',
            plot_bgcolor='black',
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            hovermode='x unified',
            showlegend=False
        )
        
        # Style the line
        fig.update_traces(
            line=dict(width=2.5, color='#00cc96'),
            hovertemplate='Date: %{x|%b %d, %Y}<br>Price: $%{y:.2f}<extra></extra>'
        )

        # Get latest price and volume
        current_price = hist.iloc[-1]['Close']
        volume = hist.iloc[-1]['Volume']

        info_text = [
            html.Span(f"Current Price: ${current_price:,.2f} | "),
            html.Span(f"Volume: {volume:,.0f}")
        ]

        return fig, info_text

    except Exception as e:
        # Create error visualization
        error_fig = px.line(title=f"Error: {str(e)}")
        error_fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='black',
            plot_bgcolor='black',
            xaxis={'visible': False},
            yaxis={'visible': False}
        )
        return error_fig, html.Span(f"❌ {str(e)}", style={'color': 'red'})

application = DispatcherMiddleware(server)