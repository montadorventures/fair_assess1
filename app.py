import dash
from flask import Flask
from dash import html  # Updated import

# Create Flask server
server = Flask(__name__)

# Serve index.html on root route
@server.route("/")
def serve_index():
    return server.send_static_file('index.html')  # Serve index.html from 'static' folder

# Initialize Dash and attach it to Flask
app = dash.Dash(__name__, server=server, routes_pathname_prefix="/main/")

# Define a simple layout for the Dash app
app.layout = html.Div("Hello, Dash!")  # Replace this with your actual layout

if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0', port=8050)
