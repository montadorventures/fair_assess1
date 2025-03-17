import dash
from flask import Flask, render_template

# Create Flask server
server = Flask(__name__)

# Serve index.html on root route
@server.route("/")
def serve_index():
    return render_template("index.html")

# Initialize Dash and attach it to Flask
app = dash.Dash(__name__, server=server, routes_pathname_prefix="/dashboard/")

if __name__ == "__main__":
    app.run_server(debug=False, host='0.0.0.0', port=8050)
