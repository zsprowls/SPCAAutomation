#!/bin/bash

# Production deployment script for Pathways for Care Viewer

echo "=================================================="
echo "Pathways for Care Viewer - Production Deployment"
echo "=================================================="

# Check if running in production mode
if [ "$1" = "production" ]; then
    echo "🚀 Starting production server with Gunicorn..."
    
    # Install production dependencies
    pip install gunicorn
    
    # Start with Gunicorn
    gunicorn --config gunicorn_config.py wsgi:app.server
    
else
    echo "🔧 Starting development server..."
    python run_app.py
fi 