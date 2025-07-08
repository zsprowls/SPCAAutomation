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
app.title = "Pathways for Care Viewer - Editable"

# Load the CSV data
def load_data():
    csv_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'Pathways for Care.csv')
    df = pd.read_csv(csv_path)
    df = df.fillna('')
    df['Days in System'] = pd.to_numeric(df['Days in System'], errors='coerce').fillna(0)
    return df

# Save data back to CSV
def save_data(df):
    csv_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'Pathways for Care.csv')
    df.to_csv(csv_path, index=False)
    print(f"Data saved to {csv_path}")

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
    dcc.Store(id='data-store', data=df.to_dict('records')),
    dcc.Location(id='url', refresh=False),
    
    dbc.Row([
        dbc.Col([
            html.H1("Pathways for Care Viewer - Editable", className="text-center mb-4"),
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
    
    # Spreadsheet View with editable cells
    html.Div(id="spreadsheet-view", children=[
        dbc.Row([
            dbc.Col([
                dash_table.DataTable(
                    id='data-table',
                    columns=[
                        {"name": "Name", "id": "Name", "type": "text", "editable": True},
                        {"name": "AID", "id": "AID", "type": "text", "editable": True},
                        {"name": "Species", "id": "Species", "type": "text", "editable": True},
                        {"name": "Location", "id": "Location ", "type": "text", "editable": True},
                        {"name": "Intake Date", "id": "Intake Date", "type": "text", "editable": True},
                        {"name": "Days in System", "id": "Days in System", "type": "numeric", "editable": True},
                        {"name": "Foster Attempted", "id": "Foster Attempted", "type": "text", "editable": True},
                        {"name": "Transfer Attempted", "id": "Transfer Attempted", "type": "text", "editable": True},
                        {"name": "Communications Team Attempted", "id": "Communications Team Attempted", "type": "text", "editable": True},
                        {"name": "Welfare Notes", "id": "Welfare Notes", "type": "text", "editable": True}
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
                        'Welfare Notes': 'Click to edit welfare notes',
                        'AID': 'Click to open animal page in PetPoint'
                    },
                    tooltip_delay=0,
                    tooltip_duration=None
                )
            ])
        ])
    ], style={'display': 'none'}),
    
    # Record Browser View with editable fields
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
                        
                        # Save button
                        dbc.Row([
                            dbc.Col([
                                dbc.Button("💾 Save Changes", id="btn-save", color="success", size="sm", className="mb-3")
                            ], className="text-center")
                        ]),
                        
                        # Image section
                        dbc.Row([
                            dbc.Col([
                                html.Div(id="image-container", className="text-center mb-3")
                            ])
                        ]),
                        
                        # Animal information with editable fields
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Animal Information", className="bg-primary text-white"),
                                    dbc.CardBody([
                                        dbc.Row([
                                            dbc.Col([
                                                html.Strong("Name: "), 
                                                dcc.Input(id="edit-name", type="text", placeholder="Enter name", className="form-control mb-2"),
                                                html.Br(),
                                                html.Strong("AID: "), 
                                                dcc.Input(id="edit-aid", type="text", placeholder="Enter AID", className="form-control mb-2"),
                                                html.Br(),
                                                html.Strong("Species: "), 
                                                dcc.Input(id="edit-species", type="text", placeholder="Enter species", className="form-control mb-2")
                                            ], width=4),
                                            dbc.Col([
                                                html.Strong("Location: "), 
                                                dcc.Input(id="edit-location", type="text", placeholder="Enter location", className="form-control mb-2"),
                                                html.Br(),
                                                html.Strong("Intake Date: "), 
                                                dcc.Input(id="edit-intake", type="text", placeholder="Enter intake date", className="form-control mb-2"),
                                                html.Br(),
                                                html.Strong("Days in System: "), 
                                                dcc.Input(id="edit-days", type="number", placeholder="Enter days", className="form-control mb-2")
                                            ], width=4),
                                            dbc.Col([
                                                html.Strong("Foster Attempted: "), 
                                                dcc.Input(id="edit-foster", type="text", placeholder="Enter foster status", className="form-control mb-2"),
                                                html.Br(),
                                                html.Strong("Transfer Attempted: "), 
                                                dcc.Input(id="edit-transfer", type="text", placeholder="Enter transfer status", className="form-control mb-2"),
                                                html.Br(),
                                                html.Strong("Communications Team: "), 
                                                dcc.Input(id="edit-communications", type="text", placeholder="Enter communications status", className="form-control mb-2")
                                            ], width=4)
                                        ])
                                    ])
                                ])
                            ])
                        ], className="mb-3"),
                        
                        # Welfare Notes section with large text area
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Welfare Notes", className="bg-warning text-dark"),
                                    dbc.CardBody([
                                        dcc.Textarea(
                                            id="edit-notes",
                                            placeholder="Enter welfare notes here...",
                                            style={'width': '100%', 'height': '150px', 'fontSize': '14px', 'lineHeight': '1.6'},
                                            className="form-control"
                                        )
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
        return {'display': 'block'}, {'display': 'none'}, False, True
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "btn-spreadsheet":
        return {'display': 'block'}, {'display': 'none'}, False, True
    else:
        return {'display': 'none'}, {'display': 'block'}, True, False

# Record browser callback - handles both initialization and navigation
@app.callback(
    [Output("page-indicator", "children"),
     Output("edit-name", "value"),
     Output("edit-aid", "value"),
     Output("edit-species", "value"),
     Output("edit-location", "value"),
     Output("edit-intake", "value"),
     Output("edit-days", "value"),
     Output("edit-foster", "value"),
     Output("edit-transfer", "value"),
     Output("edit-communications", "value"),
     Output("edit-notes", "value"),
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
        current_index = 0
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == "btn-browser":
            current_index = 0
        else:
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
        record['Name'] or "",  # name input
        record['AID'] or "",  # aid input
        record['Species'] or "",  # species input
        record['Location '] or "",  # location input
        record['Intake Date'] or "",  # intake input
        record['Days in System'] if pd.notna(record['Days in System']) else "",  # days input
        record['Foster Attempted'] or "",  # foster input
        record['Transfer Attempted'] or "",  # transfer input
        record['Communications Team Attempted'] or "",  # communications input
        record['Welfare Notes'] or "",  # notes textarea
        image_components
    ]
    
    print(f"DEBUG: Returning result with {len(result)} outputs")
    return result

# Save changes callback
@app.callback(
    Output("btn-save", "children"),
    [Input("btn-save", "n_clicks")],
    [State("page-indicator", "children"),
     State("edit-name", "value"),
     State("edit-aid", "value"),
     State("edit-species", "value"),
     State("edit-location", "value"),
     State("edit-intake", "value"),
     State("edit-days", "value"),
     State("edit-foster", "value"),
     State("edit-transfer", "value"),
     State("edit-communications", "value"),
     State("edit-notes", "value")]
)
def save_changes(btn_save, current_page, name, aid, species, location, intake, days, foster, transfer, communications, notes):
    if not btn_save:
        return "💾 Save Changes"
    
    try:
        # Get current record index
        current_index = int(current_page.split('/')[0]) - 1
        
        # Update the dataframe
        df.iloc[current_index, df.columns.get_loc('Name')] = name or ""
        df.iloc[current_index, df.columns.get_loc('AID')] = aid or ""
        df.iloc[current_index, df.columns.get_loc('Species')] = species or ""
        df.iloc[current_index, df.columns.get_loc('Location ')] = location or ""
        df.iloc[current_index, df.columns.get_loc('Intake Date')] = intake or ""
        df.iloc[current_index, df.columns.get_loc('Days in System')] = float(days) if days else 0
        df.iloc[current_index, df.columns.get_loc('Foster Attempted')] = foster or ""
        df.iloc[current_index, df.columns.get_loc('Transfer Attempted')] = transfer or ""
        df.iloc[current_index, df.columns.get_loc('Communications Team Attempted')] = communications or ""
        df.iloc[current_index, df.columns.get_loc('Welfare Notes')] = notes or ""
        
        # Save to CSV
        save_data(df)
        
        print(f"Changes saved for record {current_index + 1}")
        return "✅ Saved!"
        
    except Exception as e:
        print(f"Error saving changes: {e}")
        return "❌ Error"

# Data table callback for spreadsheet editing
@app.callback(
    Output("data-store", "data"),
    [Input("data-table", "data_timestamp")],
    [State("data-table", "data")]
)
def update_data_table(timestamp, data):
    if timestamp and data:
        # Convert back to dataframe and save
        new_df = pd.DataFrame(data)
        save_data(new_df)
        print("Spreadsheet changes saved")
    return data

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=8050)
    finally:
        cleanup_cache() 