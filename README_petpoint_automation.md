# PetPoint Report Automation

This project automates the process of logging into PetPoint, navigating to Reports, running specific reports, and saving CSV files to a fixed path without browser auto-rename issues.

## Features

- **Secure Login**: Uses environment variables for credentials
- **Download Management**: Intercepts downloads and saves with custom filenames
- **Atomic Overwrites**: Prevents file corruption during saves
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Headless Operation**: Runs in background without visible browser
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.7+
- Playwright with Chromium browser
- PetPoint account credentials

## Quick Start

### 1. Setup Environment

**On macOS/Linux:**
```bash
chmod +x setup_petpoint.sh
./setup_petpoint.sh
```

**On Windows:**
```cmd
setup_petpoint.bat
```

### 2. Configure Credentials

Edit the `.env` file with your PetPoint credentials:
```env
PETPOINT_USER=your_username
PETPOINT_PASS=your_password
PETPOINT_BASE_URL=https://your-petpoint-instance.com
```

### 3. Update Selectors

The script contains TODO comments for selectors that need to be updated based on your PetPoint instance:

- **Login Form**: Username field, password field, login button
- **Reports Navigation**: Link to Reports section
- **Report Configuration**: Report type dropdown, date range inputs
- **Report Execution**: Run report button

### 4. Run the Script

```bash
# Activate virtual environment
source petpoint_env/bin/activate  # macOS/Linux
# or
petpoint_env\Scripts\activate.bat  # Windows

# Run the automation
python pull_petpoint_reports.py
```

## File Structure

```
├── pull_petpoint_reports.py      # Main automation script
├── requirements_petpoint.txt     # Python dependencies
├── setup_petpoint.sh            # macOS/Linux setup script
├── setup_petpoint.bat           # Windows setup script
├── README_petpoint_automation.md # This file
└── __Load Files Go Here__/      # Output directory for reports
```

## How It Works

### 1. Login Process
- Navigates to PetPoint URL
- Fills in username/password
- Submits login form
- Verifies successful login

### 2. Report Generation
- Navigates to Reports section
- Selects report type and parameters
- Sets date range
- Triggers report generation

### 3. Download Handling
- Uses `page.expect_download()` to intercept downloads
- Saves to temporary location first
- Performs atomic overwrite to final destination
- Prevents browser auto-rename issues

### 4. File Management
- Outputs to `__Load Files Go Here__/` directory
- Creates directory if it doesn't exist
- Deletes existing files before saving
- Uses atomic operations for data integrity

## Selector Strategy

The script uses a layered approach to selectors:

1. **Preferred**: `get_by_role()` and `get_by_label()` for accessibility
2. **Fallback**: CSS selectors with semantic meaning
3. **Last Resort**: Text-based selectors

Example selector updates:
```python
# Instead of brittle XPath:
# page.locator("//div[@id='login']//input[@name='username']")

# Use semantic selectors:
username_field = page.get_by_label("Username")
# or
username_field = page.locator("input[name='username']")
```

## Customization

### Changing Report Type
Modify the `run_report()` function:
```python
# Change default filename
report_path = run_report(page, "CustomReport.csv")

# Update report type selection
report_type_select.select_option(value="your_report_type")
```

### Adding New Reports
Create additional functions for different report types:
```python
def run_animal_intake_report(page: Page) -> Optional[Path]:
    # Custom logic for animal intake report
    pass

def run_foster_report(page: Page) -> Optional[Path]:
    # Custom logic for foster report
    pass
```

### Date Range Configuration
Update the date inputs in `run_report()`:
```python
# Set custom date range
start_date.fill("01/01/2025")
end_date.fill("01/31/2025")

# Or make it dynamic
from datetime import datetime, timedelta
today = datetime.now()
start_date.fill((today - timedelta(days=30)).strftime("%m/%d/%Y"))
end_date.fill(today.strftime("%m/%d/%Y"))
```

## Troubleshooting

### Common Issues

1. **Login Fails**
   - Check credentials in `.env` file
   - Verify PetPoint URL is correct
   - Update selectors if login form changed

2. **Report Not Found**
   - Update report type selector
   - Check if report name/value is correct
   - Verify user has access to reports

3. **Download Issues**
   - Ensure `accept_downloads=True` is set
   - Check browser context configuration
   - Verify output directory permissions

4. **Selector Errors**
   - Use browser dev tools to inspect elements
   - Update selectors based on actual HTML structure
   - Test selectors interactively first

### Debug Mode

Enable debug logging by modifying the script:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Manual Testing

Test selectors manually in a browser:
```python
# Comment out headless mode temporarily
browser: Browser = p.chromium.launch(headless=False)
```

## Security Notes

- Never commit `.env` files to version control
- Use strong, unique passwords for PetPoint
- Consider using API keys if available
- Regularly rotate credentials

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Playwright documentation
3. Verify PetPoint instance compatibility
4. Test selectors manually in browser

## License

This project is for internal SPCA use only.
