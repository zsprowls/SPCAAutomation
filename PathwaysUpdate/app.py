import os
import pandas as pd
import dash
from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import plotly.express as px
from datetime import datetime
import dash_auth
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Basic authentication
VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'spca'
}
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

def load_data():
    # Load the Pathways for Care data
    pathways_df = pd.read_csv('../__Load Files Go Here__/Pathways for Care.csv')
    pathways_df['AID'] = pathways_df['AID'].astype(str)
    
    # Load the Animal Inventory data
    inventory_df = pd.read_csv('../__Load Files Go Here__/AnimalInventory.csv', skiprows=2)
    
    # Extract the last 8 characters from AnimalNumber to match with AID
    inventory_df['AID'] = inventory_df['AnimalNumber'].str[-8:].astype(str)
    
    # Merge the dataframes on AID
    merged_df = pd.merge(pathways_df, inventory_df, on='AID', how='left')
    
    # Calculate Length of Stay
    merged_df['IntakeDateTime'] = pd.to_datetime(merged_df['IntakeDateTime'])
    merged_df['Length of Stay'] = (datetime.now() - merged_df['IntakeDateTime']).dt.days
    
    # Select and rename columns for display
    display_columns = {
        'AnimalName': 'Animal Name',
        'AnimalType': 'Animal Type',
        'PrimaryBreed': 'Primary Breed',
        'Age': 'Age',
        'Stage': 'Stage',
        'Location': 'Location',
        'SubLocation': 'Sub Location',
        'IntakeDateTime': 'Intake Date',
        'Foster Attempted': 'Foster Attempted',
        'Transfer Attempted': 'Transfer Attempted',
        'Communications Team Attempted': 'Communications Team Attempted',
        'Welfare Notes': 'Welfare Notes'
    }
    
    return merged_df[display_columns.keys()].rename(columns=display_columns)

# Load the data
df = load_data()

# Create the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("SPCA Pathways for Care Dashboard", className="text-center mb-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            html.H4("Filters", className="mb-3"),
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Animal Type"),
                            dcc.Dropdown(
                                id='animal-type-filter',
                                options=[{'label': x, 'value': x} for x in sorted(df['Animal Type'].unique())],
                                multi=True,
                                placeholder="Select Animal Type(s)"
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Primary Breed"),
                            dcc.Dropdown(
                                id='breed-filter',
                                options=[{'label': x, 'value': x} for x in sorted(df['Primary Breed'].unique())],
                                multi=True,
                                placeholder="Select Breed(s)"
                            )
                        ], width=6)
                    ], className="mb-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Location"),
                            dcc.Dropdown(
                                id='location-filter',
                                options=[{'label': x, 'value': x} for x in sorted(df['Location'].unique())],
                                multi=True,
                                placeholder="Select Location(s)"
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Sub Location"),
                            dcc.Dropdown(
                                id='sub-location-filter',
                                options=[{'label': x, 'value': x} for x in sorted(df['Sub Location'].unique())],
                                multi=True,
                                placeholder="Select Sub Location(s)"
                            )
                        ], width=6)
                    ])
                ])
            ])
        ])
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='data-table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                page_size=20,
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'whiteSpace': 'normal',
                    'height': 'auto',
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                filter_action='native',
                sort_action='native',
                sort_mode='multi'
            )
        ])
    ])
], fluid=True)

# Callback to update sub-location options based on selected locations
@app.callback(
    Output('sub-location-filter', 'options'),
    Input('location-filter', 'value')
)
def update_sub_location_options(selected_locations):
    if not selected_locations:
        return [{'label': x, 'value': x} for x in sorted(df['Sub Location'].unique())]
    
    filtered_df = df[df['Location'].isin(selected_locations)]
    return [{'label': x, 'value': x} for x in sorted(filtered_df['Sub Location'].unique())]

# Callback to filter data based on selections
@app.callback(
    Output('data-table', 'data'),
    [Input('animal-type-filter', 'value'),
     Input('breed-filter', 'value'),
     Input('location-filter', 'value'),
     Input('sub-location-filter', 'value')]
)
def update_table(animal_types, breeds, locations, sub_locations):
    filtered_df = df.copy()
    
    if animal_types:
        filtered_df = filtered_df[filtered_df['Animal Type'].isin(animal_types)]
    if breeds:
        filtered_df = filtered_df[filtered_df['Primary Breed'].isin(breeds)]
    if locations:
        filtered_df = filtered_df[filtered_df['Location'].isin(locations)]
    if sub_locations:
        filtered_df = filtered_df[filtered_df['Sub Location'].isin(sub_locations)]
    
    return filtered_df.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True) 