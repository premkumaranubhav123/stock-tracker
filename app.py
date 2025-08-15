import yfinance as yf
from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Stock Price Viewer", style={'textAlign': 'center', 'marginBottom': 30}),

    # Input box
    html.Div([
        html.Label("Enter Stock Ticker (e.g., TSLA, AAPL, NVDA):"),
        dcc.Input(id='ticker-input', value='TSLA', type='text', style={'fontSize': 18, 'marginLeft': 10}),
    ], style={'textAlign': 'center', 'marginBottom': 20}),

    # Graph
    dcc.Graph(id='price-graph'),

    # Current price & volume
    html.Div(id='price-info', style={'textAlign': 'center', 'fontSize': 20, 'marginTop': 20})
])

# Callback to update graph and info
@callback(
    [Output('price-graph', 'figure'),
     Output('price-info', 'children')],
    [Input('ticker-input', 'value')]
)
def update_stock_data(ticker):
    if not ticker:
        return px.line(title="Enter a valid ticker"), "Enter a ticker symbol"

    try:
        # Fetch data
        stock = yf.Ticker(ticker)
        hist = stock.history(period="3mo")  # Last 3 months

        if hist.empty:
            raise ValueError("No data found")

        # Reset index to use Date as a column
        hist_reset = hist.reset_index()

        # Create chart
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

        # Get current price and volume
        current_price = hist['Close'][-1]
        volume = hist['Volume'][-1]

        info_text = [
            html.Span(f"Current Price: ${current_price:,.2f} | "),
            html.Span(f"Volume: {volume:,.0f}")
        ]

        return fig, info_text

    except Exception as e:
        fig = px.line(title=f"Error: '{ticker}' not found or no internet")
        fig.update_layout(template='plotly_dark')
        return fig, html.Span("❌ Check ticker or connection", style={'color': 'red'})

# Run the app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8050, debug=True)