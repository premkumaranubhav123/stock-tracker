from app import app  # assuming your Dash app is in app.py

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)