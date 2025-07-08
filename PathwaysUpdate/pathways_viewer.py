import dash
from dash import dcc, html, dash_table, callback, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
import time
from functools import lru_cache
import os

# Import our image cache manager
from image_cache_manager import get_animal_images_cached, initialize_cache, cleanup_cache, get_cache_stats

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Pathways for Care Viewer"

# Load the CSV data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'Pathways for Care.csv')
    df = pd.read_csv(csv_path)
    
    # Clean up the data
    df = df.fillna('')  # Replace NaN with empty string
    
    # Convert Days in System to numeric, handling any non-numeric values
    df['Days in System'] = pd.to_numeric(df['Days in System'], errors='coerce').fillna(0)
    
    return df

# Load data
df = load_data()

# Initialize image cache during startup
print("Initializing image cache...")
cache_success = initialize_cache()
if cache_success:
    stats = get_cache_stats()
    print(f"Cache stats: {stats['animals_with_images']} animals with images, {stats['total_images']} total images")
else:
    print("Cache initialization failed, images may not be available")

# App layout
app.layout = dbc.Container([
    # Hidden div to store current animal ID and image display state
    dcc.Store(id='current-animal-id', data=''),
    dcc.Store(id='show-all-images', data=False),
    dcc.Location(id='url', refresh=False),
    
    dbc.Row([
        dbc.Col([
            html.H1("Pathways for Care Viewer", className="text-center mb-4"),
            html.Hr()
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.ButtonGroup([
                dbc.Button("Spreadsheet View", id="btn-spreadsheet", color="primary", outline=True),
                dbc.Button("Record Browser", id="btn-browser", color="primary", outline=True)
            ], className="mb-3")
        ], className="text-center")
    ]),
    
    # Spreadsheet View
    html.Div(id="spreadsheet-view", children=[
        dbc.Row([
            dbc.Col([
                dash_table.DataTable(
                    id='data-table',
                    columns=[
                        {"name": "Name", "id": "Name", "type": "text"},
                        {"name": "AID", "id": "AID", "type": "text"},
                        {"name": "Species", "id": "Species", "type": "text"},
                        {"name": "Location", "id": "Location ", "type": "text"},
                        {"name": "Intake Date", "id": "Intake Date", "type": "text"},
                        {"name": "Days in System", "id": "Days in System", "type": "numeric"},
                        {"name": "Foster Attempted", "id": "Foster Attempted", "type": "text"},
                        {"name": "Transfer Attempted", "id": "Transfer Attempted", "type": "text"},
                        {"name": "Communications Team Attempted", "id": "Communications Team Attempted", "type": "text"},
                        {"name": "Welfare Notes", "id": "Welfare Notes", "type": "text"}
                    ],
                    data=df.to_dict('records'),
                    style_table={'height': '70vh', 'overflowY': 'auto'},
                    style_cell={
                        'textAlign': 'center',
                        'verticalAlign': 'middle',
                        'minHeight': '80px',
                        'maxHeight': '120px',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        'whiteSpace': 'normal',
                        'fontSize': '12px',
                        'padding': '8px'
                    },
                    style_cell_conditional=[
                        {
                            'if': {'column_id': 'Welfare Notes'},
                            'textAlign': 'left',
                            'minWidth': '300px',
                            'maxWidth': '400px'
                        },
                        {
                            'if': {'column_id': 'AID'},
                            'textAlign': 'center',
                            'minWidth': '100px',
                            'maxWidth': '120px',
                            'color': '#007bff',
                            'textDecoration': 'underline',
                            'cursor': 'pointer'
                        }
                    ],
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#f8f9fa'
                        },
                        {
                            'if': {'state': 'selected'},
                            'backgroundColor': '#007bff',
                            'color': 'white'
                        }
                    ],
                    style_header={
                        'backgroundColor': '#343a40',
                        'color': 'white',
                        'fontWeight': 'bold',
                        'textAlign': 'center',
                        'verticalAlign': 'middle'
                    },
                    page_size=20,
                    sort_action='native',
                    filter_action='native',
                    sort_mode='multi',
                    row_selectable=False,
                    selected_rows=[],
                    tooltip_header={
                        'Welfare Notes': 'Detailed notes about animal welfare and care',
                        'AID': 'Click to open animal page in PetPoint'
                    },
                    tooltip_delay=0,
                    tooltip_duration=None
                )
            ])
        ])
    ], style={'display': 'none'}),
    
    # Record Browser View
    html.Div(id="browser-view", children=[
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        # Navigation controls
                        dbc.Row([
                            dbc.Col([
                                dbc.Button("← Previous", id="btn-prev", color="secondary", outline=True, size="sm")
                            ], width=2),
                            dbc.Col([
                                html.H5(id="page-indicator", className="text-center mb-0")
                            ], width=8),
                            dbc.Col([
                                dbc.Button("Next →", id="btn-next", color="secondary", outline=True, size="sm")
                            ], width=2, className="text-end")
                        ], className="mb-3"),
                        
                        # Image section
                        dbc.Row([
                            dbc.Col([
                                html.Div(id="image-container", className="text-center mb-3")
                            ])
                        ]),
                        
                        # Animal information
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Animal Information", className="bg-primary text-white"),
                                    dbc.CardBody([
                                        dbc.Row([
                                            dbc.Col([
                                                html.Strong("Name: "), html.Span(id="browser-name"),
                                                html.Br(),
                                                html.Strong("AID: "), html.Span(id="browser-aid"),
                                                html.Br(),
                                                html.Strong("Species: "), html.Span(id="browser-species")
                                            ], width=4),
                                            dbc.Col([
                                                html.Strong("Location: "), html.Span(id="browser-location"),
                                                html.Br(),
                                                html.Strong("Intake Date: "), html.Span(id="browser-intake"),
                                                html.Br(),
                                                html.Strong("Days in System: "), html.Span(id="browser-days")
                                            ], width=4),
                                            dbc.Col([
                                                html.Strong("Foster Attempted: "), html.Span(id="browser-foster"),
                                                html.Br(),
                                                html.Strong("Transfer Attempted: "), html.Span(id="browser-transfer"),
                                                html.Br(),
                                                html.Strong("Communications Team: "), html.Span(id="browser-communications")
                                            ], width=4)
                                        ])
                                    ])
                                ])
                            ])
                        ], className="mb-3"),
                        
                        # Welfare Notes section
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Welfare Notes", className="bg-warning text-dark"),
                                    dbc.CardBody([
                                        html.Div(id="browser-notes", style={'fontSize': '14px', 'lineHeight': '1.6'})
                                    ])
                                ])
                            ])
                        ])
                    ])
                ])
            ])
        ])
    ], style={'display': 'none'})
], fluid=True)

# Callbacks
@app.callback(
    [Output("spreadsheet-view", "style"),
     Output("browser-view", "style"),
     Output("btn-spreadsheet", "outline"),
     Output("btn-browser", "outline")],
    [Input("btn-spreadsheet", "n_clicks"),
     Input("btn-browser", "n_clicks")]
)
def switch_view(btn_spreadsheet, btn_browser):
    ctx = callback_context
    if not ctx.triggered:
        # Default to spreadsheet view
        return {'display': 'block'}, {'display': 'none'}, False, True
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "btn-spreadsheet":
        return {'display': 'block'}, {'display': 'none'}, False, True
    else:
        return {'display': 'none'}, {'display': 'block'}, True, False

# Record browser callback - handles both initialization and navigation
@app.callback(
    [Output("page-indicator", "children"),
     Output("browser-name", "children"),
     Output("browser-aid", "children"),
     Output("browser-species", "children"),
     Output("browser-location", "children"),
     Output("browser-intake", "children"),
     Output("browser-days", "children"),
     Output("browser-foster", "children"),
     Output("browser-transfer", "children"),
     Output("browser-communications", "children"),
     Output("browser-notes", "children"),
     Output("image-container", "children")],
    [Input("btn-browser", "n_clicks"),
     Input("btn-prev", "n_clicks"),
     Input("btn-next", "n_clicks")],
    [State("page-indicator", "children")]
)
def update_browser_view(btn_browser, btn_prev, btn_next, current_page):
    print(f"DEBUG: Record browser callback triggered")
    
    ctx = callback_context
    if not ctx.triggered:
        # Initialize with first record
        current_index = 0
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == "btn-browser":
            # Initialize browser view - start with first record
            current_index = 0
        else:
            # Parse current page indicator for navigation
            if current_page:
                current_index = int(current_page.split('/')[0]) - 1
            else:
                current_index = 0
            
            if button_id == "btn-prev":
                current_index = max(0, current_index - 1)
            elif button_id == "btn-next":
                current_index = min(len(df) - 1, current_index + 1)
    
    if current_index >= len(df):
        current_index = 0
    
    record = df.iloc[current_index]
    print(f"DEBUG: Processing record {current_index}: {record['Name']} (AID: {record['AID']})")
    
    # Get images for the animal from cache
    animal_id = str(record['AID']).strip()
    print(f"DEBUG: Getting images for animal {animal_id} (name: {record['Name']})")
    image_urls = get_animal_images_cached(animal_id)
    print(f"DEBUG: Found {len(image_urls)} images for animal {animal_id}")
    
    # Create clickable AID link
    aid_link = html.A(
        animal_id,
        href=f"https://sms.petpoint.com/sms3/enhanced/animal/{animal_id}",
        target="_blank",
        style={'color': '#007bff', 'textDecoration': 'underline', 'cursor': 'pointer'}
    )
    
    # Create image components (show all images)
    image_components = []
    if image_urls:
        for i, url in enumerate(image_urls):  # Show all images
            image_components.append(
                html.Img(
                    src=url,
                    style={
                        'maxWidth': '200px',
                        'maxHeight': '200px',
                        'margin': '5px',
                        'borderRadius': '8px',
                        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                    },
                    alt=f"Animal {animal_id} image {i+1}"
                )
            )
    else:
        image_components.append(
            html.Div([
                html.I(className="fas fa-image fa-3x text-muted"),
                html.Br(),
                html.Span("No images available", className="text-muted")
            ], style={'padding': '20px'})
        )
    
    result = [
        f"{current_index + 1}/{len(df)}",  # page indicator
        record['Name'] or "N/A",
        aid_link,  # clickable AID
        record['Species'] or "N/A",
        record['Location '] or "N/A",
        record['Intake Date'] or "N/A",
        f"{record['Days in System']:.0f}" if pd.notna(record['Days in System']) else "N/A",
        record['Foster Attempted'] or "N/A",
        record['Transfer Attempted'] or "N/A",
        record['Communications Team Attempted'] or "N/A",
        record['Welfare Notes'] or "No notes available",
        image_components
    ]
    
    print(f"DEBUG: Returning result with {len(result)} outputs")
    return result

# Add JavaScript to handle AID clicks in spreadsheet
app.clientside_callback(
    """
    function(active_cell, data) {
        if (active_cell && active_cell.column_id === 'AID' && active_cell.row !== null) {
            const animal_id = data[active_cell.row].AID;
            if (animal_id) {
                window.open(`https://sms.petpoint.com/sms3/enhanced/animal/${animal_id}`, '_blank');
            }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('url', 'pathname'),
    Input('data-table', 'active_cell'),
    State('data-table', 'data')
)

# Note: AID column is styled to look clickable but click functionality will be added later

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=8050)
    finally:
        # Clean up cache resources when the app shuts down
        cleanup_cache() 