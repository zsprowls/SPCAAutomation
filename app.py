from petpoint_image_scraper import setup_driver, login_to_petpoint, get_animal_images, download_images
from dash import html, dcc, Input, Output, State, callback, dash_table, ctx, no_update
import base64 
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import os
from datetime import datetime
from contextlib import contextmanager

def load_data():
    # Load the Pathways for Care data
    pathways_df = pd.read_csv('__Load Files Go Here__/Pathways for Care.csv')
    pathways_df['AID'] = pathways_df['AID'].astype(str)
    
    # Load the Animal Inventory data
    inventory_df = pd.read_csv('__Load Files Go Here__/AnimalInventory.csv', skiprows=2)
    
    # Extract the last 8 characters from AnimalNumber to match with AID
    inventory_df['AID'] = inventory_df['AnimalNumber'].str[-8:].astype(str)
    
    # Merge the dataframes on AID
    merged_df = pd.merge(pathways_df, inventory_df, on='AID', how='left')
    
    # Calculate Length of Stay
    merged_df['IntakeDateTime'] = pd.to_datetime(merged_df['IntakeDateTime'])
    merged_df['Length of Stay'] = (datetime.now() - merged_df['IntakeDateTime']).dt.days
    
    # Select and rename columns for display
    display_columns = {
        'AID': 'AID',  # Make sure AID is included
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
    
    # Add Images column
    merged_df['Images'] = ''  # This will be populated with image URLs
    
    return merged_df[display_columns.keys()].rename(columns=display_columns)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.css.append_css({
    'external_url': 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css'
})

# Load the data
df = load_data()

# Add this before the driver initialization
ANIMAL_IMAGES = {}  # Initialize the dictionary to store image URLs

# Initialize the driver and login once when the app starts
driver = setup_driver()
if login_to_petpoint(driver, "USNY9", "zaks", "Gillian666!"):
    print("Successfully logged in to PetPoint")
    
    # Get all unique AIDs from the dataframe
    all_aids = df['AID'].unique()
    print(f"Found {len(all_aids)} unique animal IDs")
    
    # Fetch images for all animals
    for aid in all_aids:
        print(f"\nProcessing animal {aid}...")
        image_urls = get_animal_images(driver, aid)
        if image_urls:
            print(f"Found {len(image_urls)} images")
            ANIMAL_IMAGES[aid] = image_urls
        else:
            print("No images found")
else:
    print("Failed to log in")

# Store images in memory when app starts
ANIMAL_IMAGES = {} 

# Store current image index for each animal
current_image_indices = {}

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
                                options=[{'label': x, 'value': x} for x in sorted(df['Animal Type'].dropna().unique())],
                                multi=True,
                                placeholder="Select Animal Type(s)"
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Primary Breed"),
                            dcc.Dropdown(
                                id='breed-filter',
                                options=[{'label': x, 'value': x} for x in sorted(df['Primary Breed'].dropna().unique())],
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
                                options=[{'label': x, 'value': x} for x in sorted(df['Location'].dropna().unique())],
                                multi=True,
                                placeholder="Select Location(s)"
                            )
                        ], width=6),
                        dbc.Col([
                            html.Label("Sub Location"),
                            dcc.Dropdown(
                                id='sub-location-filter',
                                options=[{'label': x, 'value': x} for x in sorted(df['Sub Location'].dropna().unique())],
                                multi=True,
                                placeholder="Select Sub Location(s)"
                            )
                        ], width=6)
                    ])
                ])
            ]),
            dash_table.DataTable(
                id='data-table',
                columns=[
                    {"name": "Images", "id": "Images", "type": "text", "presentation": "markdown"},
                    *[{"name": i, "id": i} for i in df.columns if i != 'Images']
                ],
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
                sort_mode='multi',
                markdown_options={"html": True},
                hidden_columns=['AID']
            )
        ], width=12)  # Changed from width=8 to width=12 since we removed the right column
    ])
], fluid=True)

@app.callback(
    Output('sub-location-filter', 'options'),
    Input('location-filter', 'value')
)
def update_sub_location_options(selected_locations):
    if not selected_locations:
        return [{'label': x, 'value': x} for x in sorted(df['Sub Location'].dropna().unique())]
    
    filtered_df = df[df['Location'].isin(selected_locations)]
    return [{'label': x, 'value': x} for x in sorted(filtered_df['Sub Location'].dropna().unique())]

@app.callback(
    Output('data-table', 'data'),
    [Input('animal-type-filter', 'value'),
     Input('breed-filter', 'value'),
     Input('location-filter', 'value'),
     Input('sub-location-filter', 'value'),
     Input('data-table', 'active_cell'),
     Input('data-table', 'data')],
    [State('data-table', 'data')]
)
def update_table(animal_types, breeds, locations, sub_locations, active_cell, current_data, table_data):
    # Get the trigger that caused the callback
    trigger = ctx.triggered_id if not isinstance(ctx.triggered_id, dict) else ctx.triggered_id.get('type')
    
    # First, filter the data based on dropdown selections
    filtered_df = df.copy()
    
    if animal_types:
        filtered_df = filtered_df[filtered_df['Animal Type'].isin(animal_types)]
    if breeds:
        filtered_df = filtered_df[filtered_df['Primary Breed'].isin(breeds)]
    if locations:
        filtered_df = filtered_df[filtered_df['Location'].isin(locations)]
    if sub_locations:
        filtered_df = filtered_df[filtered_df['Sub Location'].isin(sub_locations)]
    
    # Convert to records for the table
    records = filtered_df.to_dict('records')
    
    # Handle image navigation if a cell is selected
    if active_cell and active_cell['column_id'] == 'Images':
        row_idx = active_cell['row']
        animal_id = records[row_idx]['AID']
        
        print(f"Processing images for animal {animal_id}")  # Debug log
        
        # Initialize image index if needed
        if animal_id not in current_image_indices:
            current_image_indices[animal_id] = 0
        
        # Handle navigation
        if trigger == 'prev-image':
            current_image_indices[animal_id] = max(0, current_image_indices[animal_id] - 1)
        elif trigger == 'next-image':
            if animal_id in ANIMAL_IMAGES:
                current_image_indices[animal_id] = min(
                    len(ANIMAL_IMAGES[animal_id]) - 1,
                    current_image_indices[animal_id] + 1
                )
        
        # Fetch images if needed
        if animal_id not in ANIMAL_IMAGES:
            print(f"Fetching images for {animal_id}")  # Debug log
            image_urls = get_animal_images(driver, animal_id)
            if image_urls:
                print(f"Successfully fetched {len(image_urls)} images for {animal_id}")
                print(f"First image URL: {image_urls[0]}")
                ANIMAL_IMAGES[animal_id] = image_urls
            else:
                print(f"No images found for {animal_id}")
        
        # Update the image in the table with navigation buttons
        if animal_id in ANIMAL_IMAGES and ANIMAL_IMAGES[animal_id]:
            current_idx = current_image_indices[animal_id]
            total_images = len(ANIMAL_IMAGES[animal_id])
            image_url = ANIMAL_IMAGES[animal_id][current_idx]
            
            print(f"Displaying image {current_idx + 1} of {total_images} for {animal_id}")  # Debug log
            print(f"Image URL: {image_url}")  # Debug log
            
            # Create HTML for image with navigation buttons
            image_html = f"""
            <div style="text-align: center;">
                <img src="{image_url}" style="max-width: 200px; max-height: 200px; margin-bottom: 10px;" onerror="this.onerror=null; this.src='https://via.placeholder.com/200x200?text=Image+Not+Found';">
                <div>
                    <button id="prev-{animal_id}" class="btn btn-sm btn-primary me-2">Previous</button>
                    <span>Image {current_idx + 1} of {total_images}</span>
                    <button id="next-{animal_id}" class="btn btn-sm btn-primary ms-2">Next</button>
                </div>
            </div>
            """
            records[row_idx]['Images'] = image_html
        else:
            print(f"No images available for {animal_id}")  # Debug log
            records[row_idx]['Images'] = "No images available"
    
    return records

# Add a single clientside callback for both navigation buttons
app.clientside_callback(
    """
    function(n_clicks) {
        if (!n_clicks) return window.dash_clientside.no_update;
        
        const buttonId = window.dash_clientside.callback_context.triggered[0].prop_id.split('.')[0];
        const isPrev = buttonId.startsWith('prev-');
        const animal_id = buttonId.replace('prev-', '').replace('next-', '');
        
        return {
            'type': isPrev ? 'prev-image' : 'next-image',
            'animal_id': animal_id
        };
    }
    """,
    Output('data-table', 'active_cell'),
    [Input({'type': 'prev-image', 'index': dash.ALL}, 'n_clicks'),
     Input({'type': 'next-image', 'index': dash.ALL}, 'n_clicks')],
    prevent_initial_call=True
)

# Initialize scraper
scraper = None

def initialize_scraper():
    global scraper
    if scraper is None:
        scraper = PetPointImageScraper()
        scraper.login()

@app.callback(
    Output('image-gallery', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    initialize_scraper()
    if pathname == '/':
        return []
    return []

if __name__ == '__main__':
    app.run(debug=True) 