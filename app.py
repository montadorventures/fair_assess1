import re
import pandas as pd
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px

# Load the data
def load_data(file_path):
    df = pd.read_csv(file_path, encoding='ISO-8859-1',
                     dtype={'Year_Built': 'Int64', 'Appraised_Value': 'float', 'Living_Area': 'float'})

    df = df[['Owner_Name', 'Situs_Address', 'GIS_Link','City', 'MAPSCO', 'TAD_Map', 'Year_Built', 'Appraised_Value','Land_Value',
             'Land_SqFt', 'Living_Area', 'Account_Num','LegalDescription','Property_Class','State_Use_Code','Exemption_Code']].dropna()
    df = df[df['Living_Area'] > 0]
#    df['Subdivision'] = df['LegalDescription'].str.extract(r'^(\S+\s\S+)(?=\s|ADDITION|BLOCK|-|$)', flags=re.IGNORECASE)
    df['Subdivision'] = df['LegalDescription'].str.extract(r'^(.*?)\sBLOCK', flags=re.IGNORECASE)
    df['GIS_short'] = df['GIS_Link'].str.extract(r'^([^-]+)', flags=re.IGNORECASE)
    df['Block_Number'] = df['LegalDescription'].str.extract(r'Block (\d+)')
    # df['Value_PSF'] = df['Value_PSF'].apply(lambda x: f"${round(x):,}")
    # df['Appraised_Value'] = df['Appraised_Value'].apply(lambda x: f"${round(x):,}")

    df['Value_PSF'] = df['Appraised_Value'] / df['Living_Area']
    df['TAD_Link'] = df['Account_Num'].apply(
        lambda x: f'<a href="https://www.tad.org/property?account={x}" target="_blank">View Property</a>')
    return df


# Initialize Dash app
app = dash.Dash(__name__,
                external_stylesheets=["https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"])
server = app.server  # Required for deployment
# Replace this with your Google Sheets URL in CSV format
google_sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRa5d5Esfr7xKB1oR8mr7WyD61TZbCz1YIpQFffF9C8ghGEjII3qjPiXHiNNrjb6VVYZXDjTrI8wEed/pub?gid=1273093190&single=true&output=csv"

# Load the data directly into a DataFrame
df = pd.read_csv(google_sheet_url)

#df = load_data("reduced_data.csv")
app.layout = html.Div(style={
    'width': 'auto',  # 8.5 inches (~800px)
    'height': '1056px',  # 11 inches (~1056px)
    'margin': 'auto',  # Center the content
    'padding': '10px',  # Add padding
    'border': '1px solid #ddd',  # Optional border for print preview
    'backgroundColor': '#ffffff'  # Ensure white background for printing
}, children=[

    html.Div(className="text-center mb-3", children=[
        html.H2("Is My Property Fairly Assessed?", className="fw-bold"),
        html.P("Find out if you're overpaying on property taxes and how much you could save.", className="lead"),
        html.P(
            "This tool is provided for informational purposes only and is derived from sources deemed reliable but is not guaranteed for accuracy or completeness. Use of this tool does not constitute tax, legal, or investment advice.",
            className="mt-3 fst-italic fs-6")
    ]),

    html.Div(className="mb-2", children=[
        html.Label("Search by Address:", className="form-label fw-bold"),
        dcc.Input(id='search_input', type='text', className="form-control", placeholder='Enter Address',
                  debounce=True)
    ]),

    html.Div(className="mb-2", style={'height': '150', 'overflowY': 'auto'}, children=[
        dash_table.DataTable(
            id='address_selection_table',
            columns=[
                {'name': 'Legal Description', 'id': 'LegalDescription'},
                {'name': 'Address', 'id': 'Situs_Address'},
            ],
            row_selectable='single',
            page_size=5,  # Reduce page size to fit the layout
            style_cell={'textAlign': 'left', 'padding': '5px', 'fontSize': '12px'},
            style_header={'fontWeight': 'bold', 'backgroundColor': '#f8f9fa'}
        )
    ]),

    html.Div(id='assessment_text', className="alert alert-info mt-2", style={'fontSize': '16px'}),

    dcc.Graph(id='value_psf_chart', className="mt-3", style={'height': '300px'}),  # Reduce chart height

    ### Comparable Properties Table
    html.H4("Comparable Properties:", className="mt-3 fw-bold fs-12"),
    dash_table.DataTable(
        id='results_table',
        columns=[
            {'name': 'Address', 'id': 'Situs_Address'},
            {'name': 'Appraised Value', 'id': 'Appraised_Value', 'type': 'numeric', 'format': {'specifier': '$,.0f'}},
           # {'name': 'Adjusted Value', 'id': 'Adjusted_Value', 'type': 'numeric', 'format': {'specifier': '$,.0f'}},
            {'name': 'Value PSF', 'id': 'Value_PSF', 'type': 'numeric', 'format': {'specifier': '$,.0f'}},
            {'name': 'Square Feet', 'id': 'Living_Area', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
            {'name': 'Year Built', 'id': 'Year_Built'},
            {'name': 'Land SqFt', 'id': 'Land_SqFt', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
        ],
        page_size=10,  # Reduce rows per page
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px', 'fontSize': '12px'},
        style_header={'fontWeight': 'bold', 'backgroundColor': '#f8f9fa'}
    ),

    ## Properties Supporting a Lower Valuation
    html.H4("Properties Supporting a Lower Assessed Value:", className="mt-3 fw-bold fs-12"),
    dash_table.DataTable(
        id='lower_valuation_table',
        columns=[
            {'name': 'Address', 'id': 'Situs_Address'},
            {'name': 'Appraised Value', 'id': 'Appraised_Value', 'type': 'numeric', 'format': {'specifier': '$,.0f'}},
           # {'name': 'Adjusted Value', 'id': 'Adjusted_Value', 'type': 'numeric', 'format': {'specifier': '$,.0f'}},
            {'name': 'Value PSF', 'id': 'Value_PSF', 'type': 'numeric', 'format': {'specifier': '$,.0f'}},
            {'name': 'Square Feet', 'id': 'Living_Area', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
            {'name': 'Year Built', 'id': 'Year_Built'},
            {'name': 'Land SqFt', 'id': 'Land_SqFt', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
        ],
        page_size=10,  # Reduce rows per page
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px', 'fontSize': '12px'},
        style_header={'fontWeight': 'bold', 'backgroundColor': '#f8f9fa'}
    )
])

# Define max width and height constraints

html.P("This information is provided for informational purposes only. It is derived from sources deemed reliable but is not guaranteed for accuracy or completeness. This does not constitute tax, legal, or investment advice.", className="alert alert-info mt-2", style={'fontSize': '8px'})
####
## Address Selection
@app.callback(
    Output('address_selection_table', 'data'),
    Input('search_input', 'value')
)

def update_search_results(search_value):
    if not search_value:
        return df[['Situs_Address']].to_dict('records')

    filtered_df = df[df['Situs_Address'].str.contains(search_value, case=False, na=False)]
    return filtered_df[['Situs_Address']].to_dict('records')

## Results Table
@app.callback(
    [Output('results_table', 'data'),
     Output('value_psf_chart', 'figure'),
     Output('assessment_text', 'children'),
     Output('lower_valuation_table', 'data')],
    [Input('address_selection_table', 'selected_rows'),
     Input('address_selection_table', 'data')]
)
def update_report(selected_rows, table_data):
    if not selected_rows or not table_data:
        return [], px.bar(), "", []

    selected_address = table_data[selected_rows[0]]['Situs_Address']
    matched_row = df[df['Situs_Address'] == selected_address].iloc[0]

    result_df = df[
        (
                (df['TAD_Map'] == matched_row['TAD_Map']) |
                (df['MAPSCO'] == matched_row['MAPSCO'])
        ) &
        (
                (df['GIS_short'] == matched_row['GIS_short']) |
                (df['Subdivision'] == matched_row['Subdivision'])
        )
        ]
    result_df = result_df[result_df['Property_Class'] == matched_row['Property_Class']]
    result_df = result_df[result_df['State_Use_Code'] == matched_row['State_Use_Code']]
    result_df = result_df[
        result_df['Year_Built'].between(matched_row['Year_Built'] - 20, matched_row['Year_Built'] + 20) &
        result_df['Living_Area'].between(matched_row['Living_Area'] * 0.85, matched_row['Living_Area'] * 1.15) &
        result_df['Land_SqFt'].between(matched_row['Land_SqFt'] * 0.85, matched_row['Land_SqFt'] * 1.15) &
        result_df['Value_PSF'].between(matched_row['Value_PSF'] * 0.50, matched_row['Value_PSF'] * 1.5)
        # &result_df['Situs_Address'] != matched_row['Situs_Address']
        ].sort_values(by='Value_PSF', ascending=True)

    value_psf_value = matched_row['Value_PSF']
    median_value_psf = result_df['Value_PSF'].median()

    over_under = (value_psf_value / median_value_psf - 1)  if median_value_psf else None
    discount = (median_value_psf / value_psf_value - 1)
    savings = matched_row['Appraised_Value'] * 0.025 * -discount  if discount else None
    total_addresses = result_df['Situs_Address'].count()
    result_df['abs_from_median'] = abs(over_under)
    result_df['index_value'] =abs(( matched_row['Living_Area'] / result_df['Living_Area']-1) * (
                                              matched_row['Year_Built'] / result_df['Year_Built']-1) * 4)
    appraised_value = matched_row['Appraised_Value']
    above_below = f"above" if over_under > 0 else f"below"
    result_df['Adjusted_Value'] = result_df['Appraised_Value']+(matched_row['Living_Area']-result_df['Living_Area'])*70+(matched_row['Land_Value']-result_df['Land_Value'])+(matched_row['Year_Built']-result_df['Year_Built'])*result_df['Appraised_Value']*.005
    median_adjusted_value = result_df['Adjusted_Value'].median()
    savings_based_on_adjusted = (median_adjusted_value / matched_row['Appraised_Value'] - 1) * 0.025 * matched_row['Appraised_Value']
    cutoff = 0.7 if total_addresses < 10  else 0.90
    lower_valuation_df = result_df[
        (result_df['Value_PSF'] < ((median_value_psf + value_psf_value) / 2)) &
        (result_df['Value_PSF'] < value_psf_value) &
        (result_df['Value_PSF'] > (median_value_psf * cutoff))
        ].sort_values(by='Adjusted_Value', ascending=True)
    lower_addresses = lower_valuation_df['Situs_Address'].count()
    lower_median_value_psf = lower_valuation_df['Value_PSF'].median()
    assessment_text = f"There are not enough comparable properties in the neighborhood to provide an educated assessment." \
        if total_addresses < 6 else (f"{selected_address} is fairly assessed based on {total_addresses} comparable properties.  \n{lower_addresses} are assessed lower with a median value of ${lower_median_value_psf:,.0f}") \
        if value_psf_value < median_value_psf and savings < 250 else (f"{selected_address} is assessed at ${value_psf_value:,.0f} vs ${median_value_psf:,.0f} for similar properties and"
                                                                      f"{((value_psf_value / median_value_psf) - 1) * 100:,.1f}% "
                                                                      f" {above_below} {total_addresses} relevant comps in the neighborhood. \n{lower_addresses} properties are assessed lower with a median value of ${lower_median_value_psf:,.0f}. \n"
                                                                      f"\nAn equitable assessment could result in ${savings:,.0f} in annual savings."
                                                                      f"\nAdjusted Value: ${median_adjusted_value:,.0f} Appraised Value: ${appraised_value:,.0f}.")
    result_df['distance_from_median'] = abs(result_df['Value_PSF'] / median_value_psf -1)
    result_df['Adjustment'] = result_df['Appraised_Value'] + (
                matched_row['Living_Area'] - result_df['Living_Area']) * 70 + (
                                              matched_row['Land_Value'] - result_df['Land_Value']) + (
                                              matched_row['Year_Built'] - result_df['Year_Built']) * result_df[
                                      'Appraised_Value'] * .005 - result_df['Appraised_Value']
    result_df['Adjusted_vs_Appraised'] = result_df['Appraised_Value'] / result_df['Adjusted_Value'] - 1



    # Assessment message
    ## assessment_text = f"Based on {total_addresses} relevant comps in the neighborhood, {selected_address} is over-assessed by {over_under} at ${value_psf_value:,.0f} PSF vs ${median_value_psf:,.0f} PSF for comparable properties" if value_psf_value > median_value_psf else f"Based on {total_addresses} relevant comps in the neighborhood, {selected_address} is fairly assessed."
    sublabelposition = f"right" if value_psf_value > median_value_psf else f"left"
    complabelposition = f"left" if value_psf_value > median_value_psf else f"right"

    # Generate Chart
    fig = px.histogram(result_df, x='Value_PSF', nbins=10, title=f"{selected_address} vs Neighborhood Comps")
    fig.update_layout(bargap=0.1)  # Adjust this value to control the space between the bars

    fig.add_vline(x=value_psf_value, line_dash='dash', line_color='red',
                  annotation_text=f'{selected_address}: ${value_psf_value:,.0f}',
                  annotation_position=f"top {sublabelposition}")
    fig.add_vline(x=median_value_psf, line_dash='dash', line_color='green',
                  annotation_text=f'Comp Median: ${median_value_psf:,.0f}',
                  annotation_position=f"top {complabelposition}")

    # Adjust Chart Layout
    fig.update_layout(
        width='auto',  # Set chart width
        margin=dict(l=50, r=50, t=50, b=50),  # Adjust margins
        title_x=0.5  # Center title
    )

    # Display Chart in Centered Container
    html.Div(
        dcc.Graph(figure=fig),
        style={'display': 'flex', 'justify-content': 'center'}  # Center the chart
    )

    # Highlight rows where Value_PSF is lower than the selected property
    style_data_conditional = [
        {'if': {'filter_query': f'{{Value_PSF}} < {value_psf_value}'}, 'backgroundColor': '#FFDDDD'}
    ]

    return result_df.to_dict('records'), fig, assessment_text, lower_valuation_df.to_dict('records')


if __name__ == "__main__":
    app.run_server(debug=True)
