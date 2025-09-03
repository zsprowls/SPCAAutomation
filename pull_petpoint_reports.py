#!/usr/bin/env python3
"""
PetPoint Report Automation Script

This script automates the process of logging into PetPoint, navigating to Reports,
running a specific report, and saving the CSV to a fixed path without browser auto-rename.

Requirements:
- Python 3.7+
- Playwright with Chromium
- python-dotenv for environment variables

Usage:
    python pull_petpoint_reports.py

Environment Variables (.env file):
    PETPOINT_USER=your_username
    PETPOINT_PASS=your_password
    PETPOINT_BASE_URL=https://your-petpoint-instance.com
"""

import os
import logging
import tempfile
from pathlib import Path
from typing import Optional

from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PETPOINT_USER = os.getenv('PETPOINT_USER')
PETPOINT_PASS = os.getenv('PETPOINT_PASS')
PETPOINT_BASE_URL = os.getenv('PETPOINT_BASE_URL')

# Output directory
OUTPUT_DIR = Path(__file__).parent / "__Load Files Go Here__"
OUTPUT_DIR.mkdir(exist_ok=True)


def safe_overwrite_save(download_path: Path, target_filename: str) -> Path:
    """
    Safely save a downloaded file with atomic overwrite logic.
    
    Args:
        download_path: Path to the temporary downloaded file
        target_filename: Desired filename for the final file
        
    Returns:
        Path to the final saved file
    """
    target_path = OUTPUT_DIR / target_filename
    
    # If target exists, delete it first
    if target_path.exists():
        logger.info(f"Deleting existing file: {target_path}")
        target_path.unlink()
    
    # Create temporary path in the same directory
    temp_path = OUTPUT_DIR / f".__tmp_{target_filename}"
    
    try:
        # Move downloaded file to temp location first
        if download_path.exists():
            download_path.rename(temp_path)
            
            # Atomic replace: temp -> target
            temp_path.replace(target_path)
            logger.info(f"Successfully saved report to: {target_path}")
            return target_path
        else:
            raise FileNotFoundError(f"Downloaded file not found at: {download_path}")
            
    except Exception as e:
        # Clean up temp file if it exists
        if temp_path.exists():
            temp_path.unlink()
        raise RuntimeError(f"Failed to save file: {e}")


def login(page: Page) -> bool:
    """
    Log into PetPoint using credentials from environment variables.
    
    Args:
        page: Playwright page object
        
    Returns:
        True if login successful, False otherwise
    """
    if not all([PETPOINT_USER, PETPOINT_PASS, PETPOINT_BASE_URL]):
        logger.error("Missing required environment variables. Check your .env file.")
        return False
    
    try:
        logger.info(f"Navigating to PetPoint: {PETPOINT_BASE_URL}")
        page.goto(PETPOINT_BASE_URL)
        
        # TODO: Replace these selectors with actual PetPoint login form selectors
        # Prefer get_by_role, get_by_label, or specific CSS selectors over XPaths
        
        # Example: username field (adjust selector as needed)
        username_field = page.locator("input[name='username'], input#username, input[type='text']")
        username_field.fill(PETPOINT_USER)
        
        # Example: password field (adjust selector as needed)
        password_field = page.locator("input[name='password'], input#password, input[type='password']")
        password_field.fill(PETPOINT_PASS)
        
        # Example: login button (adjust selector as needed)
        login_button = page.locator("button[type='submit'], input[type='submit'], button:has-text('Login')")
        login_button.click()
        
        # Wait for navigation to complete
        page.wait_for_load_state('networkidle')
        
        # TODO: Add verification that login was successful
        # Example: check for dashboard elements, user menu, etc.
        # if page.locator(".dashboard, .user-menu, .logout").is_visible():
        
        logger.info("Login successful")
        return True
        
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return False


def run_report(page: Page, report_filename: str = "AnimalInventory.csv") -> Optional[Path]:
    """
    Navigate to Reports section and run a specific report.
    
    Args:
        page: Playwright page object
        report_filename: Desired filename for the downloaded report
        
    Returns:
        Path to the saved report file, or None if failed
    """
    try:
        # TODO: Replace with actual Reports navigation selector
        # Prefer: page.get_by_role("link", name="Reports") or page.locator("a:has-text('Reports')")
        reports_link = page.locator("a:has-text('Reports'), a[href*='reports'], .reports-link")
        reports_link.click()
        
        page.wait_for_load_state('networkidle')
        logger.info("Navigated to Reports section")
        
        # TODO: Replace with actual Report Type selector
        # Example: page.locator("select#reportType, select[name='reportType']")
        report_type_select = page.locator("select#reportType, select[name='reportType'], .report-type-select")
        # Select the desired report type (adjust value as needed)
        report_type_select.select_option(value="animal_inventory")  # Adjust this value
        
        # TODO: Replace with actual Date Range selectors
        # Example: page.locator("input[name='startDate'], input#startDate")
        start_date = page.locator("input[name='startDate'], input#startDate, .start-date-input")
        end_date = page.locator("input[name='endDate'], input#endDate, .end-date-input")
        
        # Set date range (adjust as needed)
        start_date.fill("01/01/2024")  # Adjust date format and range
        end_date.fill("12/31/2024")
        
        # TODO: Replace with actual Run Report button selector
        # Example: page.get_by_role("button", name="Run Report") or page.locator("button:has-text('Run Report')")
        run_button = page.locator("button:has-text('Run Report'), button[type='submit'], .run-report-btn")
        
        # Set up download expectation BEFORE clicking
        with page.expect_download() as download_info:
            run_button.click()
        
        # Wait for download to complete
        download = download_info.value
        logger.info(f"Report generation started, waiting for download...")
        
        # Wait for download to finish
        download_path = download.path()
        logger.info(f"Download completed: {download_path}")
        
        # Save with our own filename using atomic overwrite
        final_path = safe_overwrite_save(Path(download_path), report_filename)
        return final_path
        
    except Exception as e:
        logger.error(f"Failed to run report: {e}")
        return None


def main():
    """Main execution function."""
    logger.info("Starting PetPoint report automation")
    
    with sync_playwright() as p:
        # Launch browser with downloads enabled
        browser: Browser = p.chromium.launch(headless=True)
        
        # Create context with downloads enabled
        context: BrowserContext = browser.new_context(
            accept_downloads=True,
            # Additional context options for stability
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page: Page = context.new_page()
        
        try:
            # Login to PetPoint
            if not login(page):
                logger.error("Login failed. Exiting.")
                return
            
            # Run the report
            report_path = run_report(page, "AnimalInventory.csv")
            
            if report_path:
                logger.info(f"Report successfully saved to: {report_path}")
            else:
                logger.error("Failed to run and save report")
                
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            
        finally:
            # Clean up
            context.close()
            browser.close()
            logger.info("Browser session closed")


if __name__ == "__main__":
    main()
