import pandas as pd
import json
import os
from datetime import datetime
import requests
from flask import Flask, render_template, jsonify
import folium
from folium.plugins import HeatMap, MarkerCluster
import branca.colormap as cm

app = Flask(__name__)

# Configuration
MAPBOX_ACCESS_TOKEN = None
GEOCODED_DATA_FILE = 'geocoded_pantry_data.json'
PROCESSED_DATA_FILE = 'processed_pantry_data.json'

def get_mapbox_token():
    """Get Mapbox token from user input if not set in environment"""
    global MAPBOX_ACCESS_TOKEN
    MAPBOX_ACCESS_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN')
    
    if not MAPBOX_ACCESS_TOKEN:
        print("\nNo Mapbox token found in environment variables.")
        print("You can get a token from: https://account.mapbox.com/")
        MAPBOX_ACCESS_TOKEN = input("Please enter your Mapbox access token: ").strip()
        
        if not MAPBOX_ACCESS_TOKEN:
            raise ValueError("Mapbox token is required to run this application")
        
        os.environ['MAPBOX_ACCESS_TOKEN'] = MAPBOX_ACCESS_TOKEN
        print("Token saved for this session.")
    
    print("Mapbox token loaded successfully")
    return MAPBOX_ACCESS_TOKEN

def geocode_address(address_components):
    """Geocode an address using Mapbox API"""
    if not MAPBOX_ACCESS_TOKEN:
        get_mapbox_token()
    
    # Convert all components to strings and handle NaN/None values
    def clean_component(component):
        if pd.isna(component) or component is None:
            return ''
        return str(component).strip()
    
    # Construct full address
    address = ' '.join(filter(None, [
        clean_component(address_components['Street Address']),
        clean_component(address_components['Unit Number']),
        clean_component(address_components['City']),
        clean_component(address_components['Province']),
        clean_component(address_components['Country']),
        clean_component(address_components['Postal Code'])
    ]))
    
    print(f"Geocoding address: {address}")
    
    # Check if we already have this address geocoded
    if os.path.exists(GEOCODED_DATA_FILE):
        with open(GEOCODED_DATA_FILE, 'r') as f:
            geocoded_data = json.load(f)
            if address in geocoded_data:
                print(f"Found cached coordinates for: {address}")
                return geocoded_data[address]
    
    # Geocode using Mapbox
    url = f'https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json'
    params = {
        'access_token': MAPBOX_ACCESS_TOKEN,
        'types': 'address'
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['features']:
                result = {
                    'lat': data['features'][0]['center'][1],
                    'lng': data['features'][0]['center'][0]
                }
                
                # Save to geocoded data file
                if os.path.exists(GEOCODED_DATA_FILE):
                    with open(GEOCODED_DATA_FILE, 'r') as f:
                        geocoded_data = json.load(f)
                else:
                    geocoded_data = {}
                
                geocoded_data[address] = result
                with open(GEOCODED_DATA_FILE, 'w') as f:
                    json.dump(geocoded_data, f)
                
                print(f"Successfully geocoded: {address}")
                return result
            else:
                print(f"No results found for: {address}")
        else:
            print(f"Error geocoding {address}: {response.status_code}")
    except Exception as e:
        print(f"Exception while geocoding {address}: {str(e)}")
    
    return None

def process_and_geocode_data():
    """Process and geocode all data before starting the server"""
    print("\nStarting data processing and geocoding...")
    
    try:
        # Load and process CSV
        print("Loading CSV file...")
        if not os.path.exists('PantryMap.csv'):
            raise FileNotFoundError("PantryMap.csv not found in current directory")
            
        df = pd.read_csv('PantryMap.csv')
        print(f"Loaded {len(df)} rows from CSV")
        
        # Convert date column to datetime
        print("\nConverting dates...")
        df['Association Creation Date'] = pd.to_datetime(df['Association Creation Date'])
        min_date = df['Association Creation Date'].min()
        max_date = df['Association Creation Date'].max()
        print(f"Date range: {min_date} to {max_date}")
        
        # Create full name
        df['Full Name'] = df['Name Last'] + ', ' + df['Name First']
        
        # Create full address
        print("\nCreating full addresses...")
        df['Full Address'] = df.apply(lambda row: ' '.join(filter(None, [
            str(row['Street Address']),
            str(row['Unit Number']),
            str(row['City']),
            str(row['Province']),
            str(row['Country']),
            str(row['Postal Code'])
        ])), axis=1)
        
        # Remove duplicates
        print("\nRemoving duplicates...")
        df = df.drop_duplicates(subset=['Full Name', 'Address Type'])
        print(f"After removing duplicates: {len(df)} rows")
        
        # Geocode addresses
        print("\nStarting geocoding...")
        df['coordinates'] = df.apply(lambda row: geocode_address({
            'Street Address': row['Street Address'],
            'Unit Number': row['Unit Number'],
            'City': row['City'],
            'Province': row['Province'],
            'Country': row['Country'],
            'Postal Code': row['Postal Code']
        }), axis=1)
        
        # Convert to format needed for the map
        processed_data = []
        for _, row in df.iterrows():
            if row['coordinates']:
                # Format person ID: remove 'P' prefix and leading zeros
                person_id = str(row['Person ID']).lstrip('P0')
                processed_data.append({
                    'lat': float(row['coordinates']['lat']),
                    'lng': float(row['coordinates']['lng']),
                    'name': str(row['Full Name']),
                    'address_type': str(row['Address Type']),
                    'date': row['Association Creation Date'].strftime('%Y-%m-%d'),
                    'person_id': person_id
                })
        
        if not processed_data:
            raise ValueError("No data points were successfully processed and geocoded")
            
        # Save processed data
        with open(PROCESSED_DATA_FILE, 'w') as f:
            json.dump(processed_data, f)
        
        print(f"\nProcessing complete. {len(processed_data)} addresses geocoded and saved.")
        print(f"Date range in processed data: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
        
        if len(processed_data) > 0:
            print("\nSample processed data point:")
            print(json.dumps(processed_data[0], indent=2))
        
        return processed_data
        
    except Exception as e:
        print(f"Error in process_and_geocode_data: {str(e)}")
        raise

def update_processed_data():
    """Update existing processed data with new formatting without re-geocoding"""
    try:
        if os.path.exists(PROCESSED_DATA_FILE):
            print("\nUpdating existing processed data...")
            with open(PROCESSED_DATA_FILE, 'r') as f:
                data = json.load(f)
            
            # Update person IDs in existing data
            for item in data:
                if 'person_id' in item:
                    item['person_id'] = str(item['person_id']).lstrip('P0')
            
            # Save updated data
            with open(PROCESSED_DATA_FILE, 'w') as f:
                json.dump(data, f)
            print("Processed data updated successfully")
            return data
    except Exception as e:
        print(f"Error updating processed data: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('pantry_map.html')

@app.route('/data')
def get_data():
    try:
        # Load the pre-processed data
        if not os.path.exists(PROCESSED_DATA_FILE):
            raise FileNotFoundError(f"{PROCESSED_DATA_FILE} not found")
            
        with open(PROCESSED_DATA_FILE, 'r') as f:
            data = json.load(f)
            
        if not data:
            raise ValueError("No data found in processed data file")
            
        print(f"Sending {len(data)} data points to client")
        return jsonify(data)
    except Exception as e:
        print(f"Error in get_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Get Mapbox token
    get_mapbox_token()
    
    # Try to update existing data first
    data = update_processed_data()
    
    # If no existing data or update failed, process and geocode all data
    if not data:
        data = process_and_geocode_data()
    
    # Start the server
    print("\nStarting Flask server...")
    app.run(host='0.0.0.0', port=5001, debug=True) 
    
