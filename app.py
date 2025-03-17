import os
from flask import Flask, send_from_directory
import dash
from dash import html

# Create Flask server
server = Flask(__name__)

# Serve index.html from the 'main' folder
@server.route("/")
def serve_index():
    return send_from_directory(os.getcwd(), 'index.html')  # Serving index.html from the main folder

# Initialize Dash and attach it to Flask
app = dash.Dash(__name__, server=server, routes_pathname_prefix="/dashboard/")

# Define a simple layout for the Dash app
app.layout = html.Div("Hello, Dash!")  # Replace this with your actual layout

if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0', port=8050)
