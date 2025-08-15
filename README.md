# 📈 Stock Price Tracker

A simple and elegant web app to track stock prices in real-time using **Python**, **Dash**, and **Yahoo Finance (yfinance)**.

![Stock Tracker Screenshot](screenshot.png)

Enter any stock ticker (e.g., `TSLA`, `NVDA`, `AAPL`) and instantly view:
- ✅ Interactive price chart
- ✅ Current price and trading volume
- ✅ Clean, responsive UI
- ✅ Works with any publicly traded stock

Deployed live on Render:  
👉 [https://stock-tracker.onrender.com](https://stock-tracker.onrender.com) *(example link – replace with yours)*

---

## 🚀 Features

- Real-time stock price charts
- Supports **any ticker** (US and most international stocks)
- Mobile-friendly design
- Built with **Dash** (Plotly + Flask)
- Powered by **yfinance** (free Yahoo Finance API)
- Easy to deploy and customize

---

## 🖥️ Run Locally

### 1. Clone the repository

git clone https://github.com/your-username/stock-tracker.git
cd stock-tracker

### 2. Create a virtual environment

python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

### 3. Install dependencies
pip install -r requirements.txt

### 4. Run the app
python app.py

### 5. Open in browser
Go to: http://127.0.0.1:8050
