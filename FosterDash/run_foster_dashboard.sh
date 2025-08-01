#!/bin/bash

echo "Starting SPCA Foster Dashboard..."
echo ""
echo "Make sure the CSV files are in the \"__Load Files Go Here__\" folder (parent directory):"
echo "- AnimalInventory.csv"
echo "- FosterCurrent.csv"
echo ""
read -p "Press Enter to continue..."

streamlit run foster_dashboard.py 