#!/bin/bash

# Script to install Chrome and dependencies for SPCA Automation
# This is needed for the image scraping functionality to work in cloud environments

echo "Installing Chrome and dependencies for SPCA Automation..."

# Update package list
sudo apt-get update

# Install basic dependencies
sudo apt-get install -y wget gnupg unzip curl xvfb

# Add Google Chrome repository
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list

# Update package list again
sudo apt-get update

# Install Google Chrome and required libraries
sudo apt-get install -y google-chrome-stable \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xdg-utils

# Clean up
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*

echo "Chrome and dependencies installation complete!"
echo "You can now run the SPCA Automation application." 