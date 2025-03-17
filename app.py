import dash
import dash_html_components as html
import dash_core_components as dcc
from flask import Flask, render_template

# Create Flask server
server = Flask(__name__)

# Initialize Dash and attach it to Flask
app = dash.Dash(__name__, server=server, routes_pathname_prefix="/")

app.layout = html.Div([
    html.H1("My Dash App"),
    dcc.Graph(
        id="example-graph",
        figure={
            "data": [{"x": [1, 2, 3], "y": [4, 1, 2], "type": "bar"}],
            "layout": {"title": "Sample Graph"}
        },
    ),
])

# Serve index.html
@server.route("/")
def serve_index():
    return render_template("index.html")

if __name__ == "__main__":
    server.run(debug=True, host="0.0.0.0", port=5000)
