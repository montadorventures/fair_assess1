import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

# Construct the Google Sheets CSV export URL
CSV_URL = f"https://docs.google.com/spreadsheets/d/e/2PACX-1vRa5d5Esfr7xKB1oR8mr7WyD61TZbCz1YIpQFffF9C8ghGEjII3qjPiXHiNNrjb6VVYZXDjTrI8wEed/pub?gid=1273093190&single=true&output=csv"

# Load the Google Sheet data
def load_data():
    df = pd.read_csv(CSV_URL)
    return df

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Google Sheets Data in Dash"),
    html.Button("Refresh Data", id="refresh-btn", n_clicks=0),
    dash_table.DataTable(
        id="data-table",
        columns=[],
        data=[],
        page_size=10,
        style_table={'overflowX': 'auto'}
    )
])

# Callback to refresh data
@app.callback(
    Output("data-table", "columns"),
    Output("data-table", "data"),
    Input("refresh-btn", "n_clicks")
)
def update_table(n_clicks):
    df = load_data()
    columns = [{"name": col, "id": col} for col in df.columns]
    data = df.to_dict("records")
    return columns, data

# Run app
server = app.server  # This line is crucial
if __name__ == "__main__":
    app.run_server(debug=True)
