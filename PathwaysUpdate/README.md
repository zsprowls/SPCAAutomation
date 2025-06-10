# SPCA Pathways Dashboard

A Dash application for tracking and managing long-term animal care at SPCA.

## Features

- Interactive dashboard for viewing animals in long-term care
- Filtering by Animal Type, Breed, Location, and SubLocation
- Real-time data updates
- Basic authentication for security
- Responsive design for all devices

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Access the dashboard at `http://localhost:8050`

## Default Login

- Username: admin
- Password: spca2024

## Data Sources

The application uses two main data sources:
1. `Pathways for Care.csv` - Contains information about animals in long-term care
2. `AnimalInventory.csv` - Contains detailed animal information

## Deployment

The application can be deployed to platforms like Render or Heroku. Make sure to:
1. Update the authentication credentials
2. Set up environment variables for sensitive information
3. Configure the server to handle multiple users

## Development

To modify the application:
1. Edit `app.py` for main functionality
2. Update `requirements.txt` for new dependencies
3. Test locally before deploying changes 