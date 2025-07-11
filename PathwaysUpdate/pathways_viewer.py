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
    # Load Pathways for Care data
    pathways_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'Pathways for Care.csv')
    df = pd.read_csv(pathways_path)
    
    # Load Animal Inventory data for current location
    inventory_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'AnimalInventory.csv')
    
    try:
        # The AnimalInventory.csv has a complex structure with multiple header rows
        # We need to skip the first 2 rows to get to the actual data
        inventory_df = pd.read_csv(inventory_path, skiprows=2)
        print(f"Loaded Animal Inventory with {len(inventory_df)} records")
        
        # Find the AID column in inventory (try different possible names)
        aid_columns = ['AnimalNumber', 'AID', 'Animal ID', 'AnimalID', 'ID', 'id']
        inventory_aid_col = None
        for col in aid_columns:
            if col in inventory_df.columns:
                inventory_aid_col = col
                break
        
        if inventory_aid_col:
            print(f"Found AID column in inventory: {inventory_aid_col}")
            
            # Find the location and sublocation columns in inventory
            location_columns = ['Location', 'Current Location', 'Location ', 'CurrentLocation']
            sublocation_columns = ['SubLocation', 'Sub Location', 'SubLocation ', 'Sub-Location']
            
            inventory_location_col = None
            inventory_sublocation_col = None
            
            for col in location_columns:
                if col in inventory_df.columns:
                    inventory_location_col = col
                    break
            
            for col in sublocation_columns:
                if col in inventory_df.columns:
                    inventory_sublocation_col = col
                    break
            
            print(f"Found location column: {inventory_location_col}")
            print(f"Found sublocation column: {inventory_sublocation_col}")
            
            if inventory_location_col:
                # Create a mapping from AID to current location (with sublocation if available)
                location_mapping = {}
                for idx, row in inventory_df.iterrows():
                    full_aid = str(row[inventory_aid_col]).strip()
                    
                    # Extract numeric part from full AID (e.g., "A0058757250" -> "58757250")
                    if full_aid.startswith('A00'):
                        aid = full_aid[3:]  # Remove "A00" prefix
                    else:
                        aid = full_aid  # Keep as is if not in expected format
                    
                    location = str(row[inventory_location_col]).strip() if pd.notna(row[inventory_location_col]) else ''
                    
                    # Add sublocation if available
                    if inventory_sublocation_col and pd.notna(row[inventory_sublocation_col]):
                        sublocation = str(row[inventory_sublocation_col]).strip()
                        if sublocation and location:
                            location = f"{location} {sublocation}"
                        elif sublocation:
                            location = sublocation
                    
                    location_mapping[aid] = location
                
                # Update the Pathways data with current locations
                df['Location '] = df['AID'].astype(str).str.strip().map(location_mapping).fillna(df['Location '])
                print(f"Updated locations for {len(location_mapping)} animals from Animal Inventory")
            else:
                print("Warning: No location column found in Animal Inventory")
        else:
            print("Warning: No AID column found in Animal Inventory")
            
    except Exception as e:
        print(f"Warning: Could not load Animal Inventory data: {e}")
        print("Using location data from Pathways for Care only")
    
    # Clean up the data
    df = df.fillna('')  # Replace NaN with empty string
    
    # Clean up welfare notes - split into individual lines and ensure consistent spacing
    def clean_welfare_notes(notes):
        if not notes or pd.isna(notes):
            return ""
        
        notes_str = str(notes).strip()
        if not notes_str:
            return ""
        
        # Common separators that indicate different entries
        separators = [
            '\n\n',  # Double line breaks
            ' | ',   # Pipe separator
            ' - ',   # Dash separator
            ' • ',   # Bullet separator
            ' * ',   # Asterisk separator
            ' ~ ',   # Tilde separator
            ' / ',   # Forward slash separator
            ' || ',  # Double pipe
            ' -- ',  # Double dash
        ]
        
        # Try to split by common separators
        for separator in separators:
            if separator in notes_str:
                parts = notes_str.split(separator)
                # Clean up each part and join with double line breaks for consistent spacing
                cleaned_parts = [part.strip() for part in parts if part.strip()]
                return '\n\n'.join(cleaned_parts)
        
        # If no separators found, check for date patterns that might indicate new entries
        import re
        # Look for date patterns like MM/DD, MM-DD, etc.
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # MM/DD/YYYY or MM/DD/YY
            r'\d{1,2}-\d{1,2}-\d{2,4}',  # MM-DD-YYYY
            r'\d{1,2}\.\d{1,2}\.\d{2,4}', # MM.DD.YYYY
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, notes_str):
                # Split by date patterns
                parts = re.split(pattern, notes_str)
                if len(parts) > 1:
                    # Reconstruct with dates and double line breaks for consistent spacing
                    result = []
                    for i, part in enumerate(parts):
                        if part.strip():
                            if i > 0:  # Add date back to the part
                                # Find the date that was split
                                date_match = re.search(pattern, notes_str)
                                if date_match:
                                    result.append(f"{date_match.group()}{part.strip()}")
                            else:
                                result.append(part.strip())
                    return '\n\n'.join(result)
        
        # If no clear separators found, normalize line breaks to ensure consistent spacing
        # Replace single line breaks with double line breaks for consistency
        notes_str = re.sub(r'\n(?!\n)', '\n\n', notes_str)
        # Remove any triple or more line breaks and replace with double
        notes_str = re.sub(r'\n{3,}', '\n\n', notes_str)
        
        return notes_str
    
    # Apply welfare notes cleaning
    df['Welfare Notes'] = df['Welfare Notes'].apply(clean_welfare_notes)
    
    # Calculate Days in System from Intake Date
    try:
        # Convert Intake Date to datetime
        df['Intake Date'] = pd.to_datetime(df['Intake Date'], errors='coerce')
        
        # Format Intake Date as mm/dd/yyyy (without time component)
        df['Intake Date'] = df['Intake Date'].dt.strftime('%m/%d/%Y')
        
        # Convert back to datetime for calculation (but keep original for display)
        intake_dates_for_calc = pd.to_datetime(df['Intake Date'], errors='coerce')
        
        # Calculate days from intake date to today
        today = pd.Timestamp.now().normalize()
        df['Days in System'] = (today - intake_dates_for_calc).dt.days
        
        # Fill any invalid values with 0
        df['Days in System'] = df['Days in System'].fillna(0).astype(int)
        
        print(f"Calculated Days in System for {len(df)} animals from intake dates")
    except Exception as e:
        print(f"Warning: Could not calculate Days in System: {e}")
        # Fall back to original calculation
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
                            'maxWidth': '400px',
                            'cursor': 'pointer'
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
    ], style={'display': 'block'}),
    
    # Record Browser View
    html.Div(id="browser-view", children=[
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        # Search dropdown
                        dbc.Row([
                            dbc.Col([
                                html.Label("Search Animal:", className="form-label fw-bold"),
                                dcc.Dropdown(
                                    id='animal-search-dropdown',
                                    options=[],  # Will be populated with AID - Name combinations
                                    placeholder="Type AID or Name to search...",
                                    style={'width': '100%'},
                                    clearable=True,
                                    searchable=True
                                )
                            ], width=12)
                        ], className="mb-3"),
                        
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
                        
                        # Edit Section
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader("Edit Information", className="bg-success text-white"),
                                    dbc.CardBody([
                                        dbc.Row([
                                            dbc.Col([
                                                html.Label("Foster Attempted:", className="form-label fw-bold"),
                                                dcc.Dropdown(
                                                    id='edit-foster-dropdown',
                                                    options=[
                                                        {'label': 'Yes', 'value': 'Yes'},
                                                        {'label': 'No', 'value': 'No'},
                                                        {'label': 'N/A', 'value': 'N/A'}
                                                    ],
                                                    placeholder="Select...",
                                                    style={'width': '100%'}
                                                )
                                            ], width=4),
                                            dbc.Col([
                                                html.Label("Transfer Attempted:", className="form-label fw-bold"),
                                                dcc.Dropdown(
                                                    id='edit-transfer-dropdown',
                                                    options=[
                                                        {'label': 'Yes', 'value': 'Yes'},
                                                        {'label': 'No', 'value': 'No'},
                                                        {'label': 'N/A', 'value': 'N/A'}
                                                    ],
                                                    placeholder="Select...",
                                                    style={'width': '100%'}
                                                )
                                            ], width=4),
                                            dbc.Col([
                                                html.Label("Communications Team Attempted:", className="form-label fw-bold"),
                                                dcc.Dropdown(
                                                    id='edit-communications-dropdown',
                                                    options=[
                                                        {'label': 'Yes', 'value': 'Yes'},
                                                        {'label': 'No', 'value': 'No'},
                                                        {'label': 'N/A', 'value': 'N/A'}
                                                    ],
                                                    placeholder="Select...",
                                                    style={'width': '100%'}
                                                )
                                            ], width=4)
                                        ], className="mb-3"),
                                        dbc.Row([
                                            dbc.Col([
                                                html.Label("Add New Welfare Note:", className="form-label fw-bold"),
                                                dcc.Textarea(
                                                    id='new-welfare-note',
                                                    placeholder="Type your new welfare note here...",
                                                    style={'width': '100%', 'height': '100px'},
                                                    value=""
                                                )
                                            ], width=12)
                                        ], className="mb-3"),
                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Button("Save Changes", id="btn-save-changes", color="success", size="lg", className="me-2"),
                                                html.Span(id="save-status", className="text-success fw-bold")
                                            ], width=12, className="text-center")
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
                                        html.Div(id="browser-notes", style={
                                            'fontSize': '14px', 
                                            'lineHeight': '1.6',
                                            'whiteSpace': 'pre-line'  # Preserve line breaks
                                        })
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

# View switching callback
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

# Populate search dropdown options
@app.callback(
    Output("animal-search-dropdown", "options"),
    [Input("btn-browser", "n_clicks")]
)
def populate_search_dropdown(btn_browser):
    """Populate the search dropdown with AID - Name combinations"""
    options = []
    for idx, row in df.iterrows():
        aid = str(row['AID']).strip()
        name = str(row['Name']).strip() if pd.notna(row['Name']) else "No Name"
        label = f"{aid} - {name}"
        options.append({"label": label, "value": idx})
    return options

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
     Output("image-container", "children"),
     Output("edit-foster-dropdown", "value"),
     Output("edit-transfer-dropdown", "value"),
     Output("edit-communications-dropdown", "value")],
    [Input("btn-browser", "n_clicks"),
     Input("btn-prev", "n_clicks"),
     Input("btn-next", "n_clicks"),
     Input("animal-search-dropdown", "value")],
    [State("page-indicator", "children")]
)
def update_browser_view(btn_browser, btn_prev, btn_next, search_value, current_page):
    print(f"DEBUG: Record browser callback triggered")
    
    ctx = callback_context
    if not ctx.triggered:
        # Initialize with first record
        current_index = 0
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == "animal-search-dropdown" and search_value is not None:
            # User selected an animal from the dropdown
            current_index = search_value
        elif button_id == "btn-browser":
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
        image_components,
        record['Foster Attempted'] or None,  # dropdown value
        record['Transfer Attempted'] or None,  # dropdown value
        record['Communications Team Attempted'] or None  # dropdown value
    ]
    
    print(f"DEBUG: Returning result with {len(result)} outputs")
    return result

# Save changes callback
@app.callback(
    Output("save-status", "children"),
    [Input("btn-save-changes", "n_clicks")],
    [State("page-indicator", "children"),
     State("edit-foster-dropdown", "value"),
     State("edit-transfer-dropdown", "value"),
     State("edit-communications-dropdown", "value"),
     State("new-welfare-note", "value")]
)
def save_changes(btn_save, current_page, foster_value, transfer_value, communications_value, new_note):
    if not btn_save:
        return ""
    
    try:
        # Get current record index
        if current_page:
            current_index = int(current_page.split('/')[0]) - 1
        else:
            current_index = 0
        
        # Update the dataframe
        if foster_value is not None:
            df.at[current_index, 'Foster Attempted'] = foster_value
        
        if transfer_value is not None:
            df.at[current_index, 'Transfer Attempted'] = transfer_value
        
        if communications_value is not None:
            df.at[current_index, 'Communications Team Attempted'] = communications_value
        
        # Add new welfare note if provided
        if new_note and new_note.strip():
            # Get current welfare notes
            current_notes = df.at[current_index, 'Welfare Notes']
            if pd.isna(current_notes) or not current_notes:
                current_notes = ""
            
            # Add new note with proper formatting
            if current_notes:
                new_welfare_notes = f"{current_notes}\n\n{new_note.strip()}"
            else:
                new_welfare_notes = new_note.strip()
            
            df.at[current_index, 'Welfare Notes'] = new_welfare_notes
        
        # Save to CSV file
        csv_path = os.path.join(os.path.dirname(__file__), '..', '__Load Files Go Here__', 'Pathways for Care.csv')
        df.to_csv(csv_path, index=False)
        
        print(f"Saved changes for animal {df.at[current_index, 'AID']} ({df.at[current_index, 'Name']})")
        
        return "✓ Changes saved successfully!"
        
    except Exception as e:
        print(f"Error saving changes: {e}")
        return f"✗ Error saving changes: {str(e)}"

# Clear new welfare note after saving
@app.callback(
    Output("new-welfare-note", "value"),
    [Input("btn-save-changes", "n_clicks")],
    [State("new-welfare-note", "value")]
)
def clear_new_note(btn_save, current_note):
    if btn_save and current_note and current_note.strip():
        return ""  # Clear the text area after saving
    return dash.no_update  # Don't update if no save action



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