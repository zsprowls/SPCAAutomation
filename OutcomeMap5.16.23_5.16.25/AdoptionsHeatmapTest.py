import pandas as pd
import folium
from folium.plugins import HeatMap
import re
import requests
import time
import logging
import json
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def geocode_address(row, mapbox_token):
    """Geocode an address using Mapbox."""
    try:
        # Construct the address string
        address = f"{row['Street Address']}, {row['City']}, {row['Province Abbr']}, {row['Postal Code']}"
        
        # URL encode the address
        encoded_address = requests.utils.quote(address)
        
        # Make the request to Mapbox
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{encoded_address}.json?access_token={mapbox_token}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data['features']:
                # Get the first result's coordinates
                lon, lat = data['features'][0]['center']
                return lat, lon
        return None, None
    except Exception as e:
        logger.error(f"Error geocoding address: {address}. Error: {str(e)}")
        return None, None

def extract_numeric(animal_number):
    """Extract numeric part from AnimalNumber."""
    return re.sub(r'\D', '', str(animal_number))

def create_tooltip(row):
    """Create HTML tooltip content."""
    return f"""
    <div style='font-family: Arial; padding: 5px;'>
        <b>{row['AnimalName']}</b><br>
        {row['Name First']} {row['Name Last']}<br>
        <a href='https://sms.petpoint.com/sms3/enhanced/animal/{extract_numeric(row['AnimalNumber'])}' 
           target='_blank'>View Details</a>
    </div>
    """

def create_html_with_filters(df_merged, coordinates):
    """Create an HTML page with filters and the heat map."""
    # Get unique values for filters
    species_list = sorted(df_merged['Species'].unique())
    breed_list = sorted(df_merged['PrimaryBreed'].unique())
    
    # Calculate the center of the map based on the coordinates
    if coordinates:
        center_lat = sum(c[0] for c in coordinates) / len(coordinates)
        center_lon = sum(c[1] for c in coordinates) / len(coordinates)
        logger.info(f"Map center: {center_lat}, {center_lon}")
    else:
        center_lat, center_lon = 56.1304, -106.3468  # Default to Canada center
        logger.info("No coordinates found, using default center")
    
    # Prepare data for JavaScript
    js_coordinates = json.dumps(coordinates)
    js_data = df_merged.to_json(orient='records')
    
    logger.info(f"Number of coordinates for heatmap: {len(coordinates)}")
    logger.info(f"Number of data points: {len(df_merged)}")
    
    # Create the HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Adoptions Heat Map</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js"></script>
        <style>
            body {{ margin: 0; padding: 0; }}
            #map {{ height: 100vh; width: 100%; }}
            .filter-panel {{
                position: absolute;
                top: 10px;
                right: 10px;
                z-index: 1000;
                background: white;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0,0,0,0.2);
            }}
            .filter-group {{
                margin-bottom: 10px;
            }}
            select {{
                width: 200px;
                padding: 5px;
            }}
            .info {{
                padding: 6px 8px;
                font: 14px/16px Arial, Helvetica, sans-serif;
                background: white;
                background: rgba(255,255,255,0.8);
                box-shadow: 0 0 15px rgba(0,0,0,0.2);
                border-radius: 5px;
            }}
            .info h4 {{
                margin: 0 0 5px;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <div class="filter-panel">
            <div class="filter-group">
                <label for="species">Species:</label><br>
                <select id="species" multiple>
                    <option value="">All Species</option>
                    {''.join(f'<option value="{s}">{s}</option>' for s in species_list)}
                </select>
            </div>
            <div class="filter-group">
                <label for="breed">Primary Breed:</label><br>
                <select id="breed" multiple>
                    <option value="">All Breeds</option>
                    {''.join(f'<option value="{b}">{b}</option>' for b in breed_list)}
                </select>
            </div>
            <button onclick="applyFilters()">Apply Filters</button>
        </div>
        <div id="map"></div>
        
        <script>
            // Data
            const coordinates = {js_coordinates};
            const data = {js_data};
            
            console.log('Number of coordinates:', coordinates.length);
            console.log('First few coordinates:', coordinates.slice(0, 5));
            console.log('Number of data points:', data.length);
            
            // Initialize map
            const map = L.map('map').setView([{center_lat}, {center_lon}], 8);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                attribution: '© OpenStreetMap contributors'
            }}).addTo(map);
            
            // Create layer groups
            let heatmapLayer = L.heatLayer(coordinates, {{
                radius: 25,
                blur: 15,
                maxZoom: 10,
                max: 1.0,
                gradient: {{0.4: 'blue', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'}}
            }});
            
            const markersLayer = L.layerGroup();
            data.forEach(item => {{
                if (item.lat && item.lon) {{
                    const marker = L.marker([item.lat, item.lon])
                        .bindPopup(item.tooltip);
                    markersLayer.addLayer(marker);
                }}
            }});
            
            // Add layers to map
            heatmapLayer.addTo(map);
            
            // Add layer control
            const overlayMaps = {{
                "Heat Map": heatmapLayer,
                "Markers": markersLayer
            }};
            L.control.layers(null, overlayMaps).addTo(map);
            
            // Add legend
            const legend = L.control({{position: 'bottomright'}});
            legend.onAdd = function(map) {{
                const div = L.DomUtil.create('div', 'info legend');
                div.innerHTML = '<h4>Adoption Density</h4>' +
                    '<div style="background: linear-gradient(to right, blue, lime, yellow, red); height: 20px; width: 200px;"></div>' +
                    '<div style="display: flex; justify-content: space-between;"><span>Low</span><span>High</span></div>';
                return div;
            }};
            legend.addTo(map);
            
            // Filter function
            function applyFilters() {{
                const selectedSpecies = Array.from(document.getElementById('species').selectedOptions).map(opt => opt.value);
                const selectedBreeds = Array.from(document.getElementById('breed').selectedOptions).map(opt => opt.value);
                
                const filteredData = data.filter(item => {{
                    const speciesMatch = selectedSpecies.length === 0 || selectedSpecies.includes(item.Species);
                    const breedMatch = selectedBreeds.length === 0 || selectedBreeds.includes(item.PrimaryBreed);
                    return speciesMatch && breedMatch;
                }});
                
                const filteredCoordinates = filteredData.map(item => {{
                    const coords = coordinates.find(c => c[0] === item.lat && c[1] === item.lon);
                    return coords || [0, 0, 0];
                }}).filter(c => c[0] !== 0);
                
                // Update heatmap
                map.removeLayer(heatmapLayer);
                heatmapLayer = L.heatLayer(filteredCoordinates, {{
                    radius: 25,
                    blur: 15,
                    maxZoom: 10,
                    max: 1.0,
                    gradient: {{0.4: 'blue', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'}}
                }}).addTo(map);
                
                // Update markers
                markersLayer.clearLayers();
                filteredData.forEach(item => {{
                    if (item.lat && item.lon) {{
                        const marker = L.marker([item.lat, item.lon])
                            .bindPopup(item.tooltip);
                        markersLayer.addLayer(marker);
                    }}
                }});
            }}
        </script>
    </body>
    </html>
    """
    
    return html_content

def main():
    try:
        # Check if geocoded data exists
        geocoded_file = 'geocoded_data.json'
        if os.path.exists(geocoded_file):
            logger.info("Loading existing geocoded data...")
            with open(geocoded_file, 'r') as f:
                df_merged = pd.read_json(f)
            coordinates = [[row['lat'], row['lon'], 1] for _, row in df_merged.iterrows() if pd.notna(row['lat']) and pd.notna(row['lon'])]
            logger.info(f"Loaded {len(coordinates)} coordinates from saved data")
            logger.info(f"First few coordinates: {coordinates[:5]}")
        else:
            # Get Mapbox token from environment variable or user input
            mapbox_token = input("Please enter your Mapbox access token: ")
            
            # Read the CSV file, skipping the first 3 rows to get to the header
            logger.info("Reading AnimalOutcome.csv...")
            df_outcomes = pd.read_csv('AnimalOutcome.csv', skiprows=3)
            logger.info(f"Read {len(df_outcomes)} rows from AnimalOutcome.csv")
            
            # Filter for adoptions
            df_adoptions = df_outcomes[df_outcomes['OperationType'] == 'Adoption']
            logger.info(f"Found {len(df_adoptions)} adoptions")
            
            # Select required columns
            df_adoptions = df_adoptions[['AnimalNumber', 'Species', 'PrimaryBreed', 
                                       'OperationType', 'OperationSubType', 'AnimalName']]
            
            # Read the Excel file, skipping the first row to get to the header
            logger.info("Reading AnimalAddress.xlsx...")
            df_addresses = pd.read_excel('AnimalAddress.xlsx', skiprows=1)
            logger.info(f"Read {len(df_addresses)} rows from AnimalAddress.xlsx")
            
            # Merge the dataframes on AnimalNumber
            df_merged = pd.merge(df_adoptions, df_addresses, on='AnimalNumber', how='inner')
            logger.info(f"Merged data has {len(df_merged)} rows")
            
            # Create tooltips
            df_merged['tooltip'] = df_merged.apply(create_tooltip, axis=1)
            
            # Geocode addresses
            logger.info("Geocoding addresses...")
            coordinates = []
            total_addresses = len(df_merged)
            
            for idx, row in df_merged.iterrows():
                lat, lon = geocode_address(row, mapbox_token)
                if lat is not None and lon is not None:
                    coordinates.append([lat, lon, 1])
                    df_merged.at[idx, 'lat'] = lat
                    df_merged.at[idx, 'lon'] = lon
                
                # Print progress
                if (idx + 1) % 10 == 0:
                    logger.info(f"Processed {idx + 1}/{total_addresses} addresses")
                
                # Small delay to respect rate limits
                time.sleep(0.1)
            
            logger.info(f"Successfully geocoded {len(coordinates)} addresses")
            logger.info(f"First few coordinates: {coordinates[:5]}")
            
            # Save geocoded data
            logger.info("Saving geocoded data...")
            df_merged.to_json(geocoded_file)
        
        # Create HTML with filters
        logger.info("Creating HTML with filters...")
        html_content = create_html_with_filters(df_merged, coordinates)
        
        # Save the HTML file
        with open('adoptions_heatmap.html', 'w') as f:
            f.write(html_content)
        
        logger.info("Interactive heat map has been created and saved as 'adoptions_heatmap.html'")
        
        # Print some statistics
        print(f"\nTotal adoptions processed: {len(df_merged)}")
        print(f"Successfully geocoded addresses: {len(coordinates)}")
        print("\nSpecies distribution:")
        print(df_merged['Species'].value_counts())
        print("\nPrimary breed distribution (top 10):")
        print(df_merged['PrimaryBreed'].value_counts().head(10))
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main() 