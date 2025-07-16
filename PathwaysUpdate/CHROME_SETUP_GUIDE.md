# Chrome Setup Guide for SPCA Automation

## Problem Description

The SPCA Automation application uses Chrome WebDriver for image scraping functionality. In cloud environments (like Linux servers), Chrome and ChromeDriver require additional system dependencies that aren't installed by default. This causes the error:

```
Failed to setup Chrome driver: Message: Service /home/appuser/.wdm/drivers/chromedriver/linux64/114.0.5735.90/chromedriver unexpectedly exited. Status code was: 127
```

Status code 127 typically means "command not found" - the ChromeDriver binary is downloaded but can't execute because required libraries are missing.

## Solutions

### Option 1: Install Chrome Dependencies (Recommended for Cloud Environments)

Run the provided installation script:

```bash
cd PathwaysUpdate
chmod +x install_chrome_deps.sh
sudo ./install_chrome_deps.sh
```

This script will:
- Install Google Chrome and all required system libraries
- Configure the Chrome repository
- Install dependencies like fonts, audio libraries, and display libraries

### Option 2: Use Docker (Recommended for Containerized Deployments)

Build and run the application using Docker:

```bash
cd PathwaysUpdate
docker build -t spca-automation .
docker run -p 8501:8501 spca-automation
```

The Dockerfile includes all necessary Chrome dependencies and is optimized for cloud environments.

### Option 3: Manual Installation

If the script doesn't work, manually install the dependencies:

```bash
# Update package list
sudo apt-get update

# Install basic dependencies
sudo apt-get install -y wget gnupg unzip curl xvfb

# Add Google Chrome repository
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list

# Update and install Chrome
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Install required libraries
sudo apt-get install -y \
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
```

## Verification

After installation, test if Chrome works:

```bash
cd PathwaysUpdate
python -c "from image_cache_manager import get_cache_manager; manager = get_cache_manager(); driver = manager.setup_driver(); print('Chrome setup successful!' if driver else 'Chrome setup failed'); driver.quit() if driver else None"
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Make sure you have sudo privileges
2. **Repository Errors**: Some cloud providers block external repositories
3. **Memory Issues**: Chrome requires significant memory in headless mode

### Alternative: Disable Image Scraping

If Chrome setup continues to fail, the application will still work without image scraping. The cache will be empty, but all other functionality will remain available.

### Logs

Check the application logs for detailed error messages:

```bash
tail -f /path/to/your/app.log
```

## Performance Notes

- Chrome in headless mode uses significant memory (~200-500MB per instance)
- The application processes animals in batches to manage memory usage
- Consider increasing available memory if running in a cloud environment

## Security Considerations

- Chrome runs in headless mode with security flags enabled
- No user data is stored locally
- All connections use HTTPS
- The application includes anti-detection measures for web scraping 