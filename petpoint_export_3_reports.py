import re
import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from playwright.sync_api import Playwright, sync_playwright, expect

# Configuration - using the working credentials from your recording
PETPOINT_USER = 'zaks'
PETPOINT_PASS = 'Gillian666!'
PETPOINT_SHELTER_ID = 'USNY9'
DOWNLOAD_DIR = Path(__file__).parent / "__Load Files Go Here__"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Setup logging
LOG_DIR = DOWNLOAD_DIR / "AutomationLog"
LOG_DIR.mkdir(exist_ok=True)

def setup_logging():
    """Setup logging to file with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"petpoint_automation_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also print to console
        ]
    )
    return log_file

def git_pull_and_push():
    """Pull latest changes and push the __Load Files Go Here__ folder."""
    try:
        logging.info("🔄 Updating Git repository...")
        
        # First, stash any unstaged changes to clean up the working directory
        logging.info("Stashing any unstaged changes...")
        result = subprocess.run(['git', 'stash'], capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode != 0 and "No local changes to save" not in result.stderr:
            logging.warning(f"Git stash had issues: {result.stderr}")
        
        # Pull latest changes
        logging.info("Pulling latest changes...")
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode != 0:
            logging.error(f"Git pull failed: {result.stderr}")
            return False
        logging.info("✅ Git pull completed")
        
        # Add our new files (including logs)
        logging.info("Adding __Load Files Go Here__ folder to Git...")
        result = subprocess.run(['git', 'add', '__Load Files Go Here__/'], capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode != 0:
            logging.error(f"Git add failed: {result.stderr}")
            return False
        
        # Check if there are any changes to commit
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode == 0:
            logging.info("📝 No changes to commit")
            return True
        
        # Commit our changes
        logging.info("Committing our changes...")
        result = subprocess.run(['git', 'commit', '-m', 'Auto-update: PetPoint reports exported'], capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode != 0:
            logging.error(f"Git commit failed: {result.stderr}")
            return False
        
        # Push the changes
        logging.info("Pushing to remote repository...")
        result = subprocess.run(['git', 'push'], capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode != 0:
            logging.error(f"Git push failed: {result.stderr}")
            return False
        
        logging.info("✅ Git push completed successfully!")
        return True
        
    except Exception as e:
        logging.error(f"Git operation failed: {e}")
        return False

def run(playwright: Playwright) -> None:
    # Setup logging first
    log_file = setup_logging()
    logging.info(f"Starting PetPoint automation - Log file: {log_file}")
    
    browser = playwright.chromium.launch(headless=True, slow_mo=500)  # Run headless for automation
    context = browser.new_context()
    page = context.new_page()
    
    try:
        logging.info("Navigating to PetPoint login...")
        page.goto("https://sms.petpoint.com/sms3/forms/signinout.aspx")
        page.wait_for_load_state('networkidle')
        
        logging.info("Logging in...")
        page.locator("#loginFrame").content_frame.locator("#LoginShelterId").click()
        page.locator("#loginFrame").content_frame.locator("#LoginShelterId").fill(PETPOINT_SHELTER_ID)
        page.locator("#loginFrame").content_frame.get_by_role("link", name="Next").click()
        page.locator("#loginFrame").content_frame.locator("#LoginUsername").fill(PETPOINT_USER)
        page.locator("#loginFrame").content_frame.locator("#LoginPassword").click()
        page.locator("#loginFrame").content_frame.locator("#LoginPassword").fill(PETPOINT_PASS)
        page.locator("#loginFrame").content_frame.get_by_role("link", name="Login").click()
        page.wait_for_load_state('networkidle')
        
        logging.info("Login completed, looking for Reports dropdown...")
        page.wait_for_selector("#ReportsNavbarDropdown", timeout=15000)
        logging.info("Found Reports dropdown")
        
        # Hover over the Reports dropdown to show the menu
        page.locator("#ReportsNavbarDropdown").hover()
        logging.info("Hovered over Reports dropdown")
        
        # Wait for the dropdown menu to appear
        page.wait_for_selector("a:has-text('Report Website')", timeout=5000)
        logging.info("Report Website option appeared in dropdown")
        
        # Click on Report Website
        with page.expect_popup() as page1_info:
            page.get_by_role("link", name="Report Website").click()
        page1 = page1_info.value
        page1.wait_for_load_state('networkidle')
        logging.info("Report Website opened successfully")
        
        # Report 1: Animal Inventory
        logging.info("=== EXPORTING ANIMAL INVENTORY ===")
        page1.wait_for_selector("text=Animal", timeout=10000)
        page1.get_by_role("link", name="Animal", exact=True).click()
        logging.info("Clicked Animal link")
        
        page1.wait_for_selector("text=Animal: Animal Inventory", timeout=10000)
        page1.get_by_text("Animal: Animal Inventory").click()
        logging.info("Clicked Animal Inventory")
        
        page1.locator("[id=\"1\"]").get_by_text("Summary", exact=True).click()
        page1.get_by_role("option", name="Detail").click()
        logging.info("Selected Detail option")
        
        with page1.expect_popup() as page2_info:
            page1.get_by_role("button", name="Submit").click()
        page2 = page2_info.value
        page2.wait_for_load_state('networkidle')
        logging.info("Report generated, looking for export options...")
        
        page2.wait_for_selector("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg", timeout=10000)
        page2.locator("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg").click()
        logging.info("Clicked export button")
        
        page2.wait_for_selector("a[title='CSV (comma delimited)']", timeout=5000)
        with page2.expect_download() as download_info:
            page2.locator("a[title='CSV (comma delimited)']").click()
        download = download_info.value
        download.save_as(DOWNLOAD_DIR / "AnimalInventory.csv")
        logging.info("✅ Saved AnimalInventory.csv")
        page2.close()
        
        # Report 2: Stage Review
        logging.info("=== EXPORTING STAGE REVIEW ===")
        logging.info("⚠️  Stage Review can take 2+ minutes due to photos...")
        page1.goto("https://repstd.petpoint.com/Index#")
        page1.wait_for_load_state('networkidle')
        
        page1.get_by_role("link", name="Animal", exact=True).click()
        page1.get_by_text("Stage: Review").click()
        page1.locator("[id=\"1\"]").get_by_text("Summary", exact=True).click()
        page1.get_by_role("option", name="Detail").click()
        
        with page1.expect_popup() as page3_info:
            page1.get_by_role("button", name="Submit").click()
        page3 = page3_info.value
        
        logging.info("⏳ Waiting for Stage Review to generate (this can take 2+ minutes)...")
        # Wait for the loading indicator to disappear first
        try:
            page3.wait_for_selector("#ReportViewer1_AsyncWait_Wait", state="hidden", timeout=180000)  # 3 minutes
            logging.info("✅ Loading completed, looking for export button...")
        except:
            logging.warning("⚠️  Loading indicator didn't disappear, proceeding anyway...")
        
        # Wait much longer for the export button
        page3.wait_for_selector("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg", timeout=60000)  # 1 minute
        page3.locator("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg").click()
        logging.info("Clicked export button")
        
        page3.wait_for_selector("a[title='CSV (comma delimited)']", timeout=10000)
        with page3.expect_download() as download1_info:
            page3.locator("a[title='CSV (comma delimited)']").click()
        download1 = download1_info.value
        download1.save_as(DOWNLOAD_DIR / "StageReview.csv")
        logging.info("✅ Saved StageReview.csv")
        page3.close()
        
        # Report 3: Foster Current
        logging.info("=== EXPORTING FOSTER CURRENT ===")
        page1.goto("https://repstd.petpoint.com/Index#")
        page1.wait_for_load_state('networkidle')
        
        page1.get_by_role("link", name="Care").click()
        page1.get_by_text("Foster: Current").click()
        page1.get_by_text("select").nth(4).click()
        page1.get_by_role("option", name="Detail").click()
        
        with page1.expect_popup() as page4_info:
            page1.get_by_role("button", name="Submit").click()
        page4 = page4_info.value
        page4.get_by_role("link", name="J K").click()
        
        page4.wait_for_selector("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg", timeout=10000)
        page4.locator("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg").click()
        logging.info("Clicked export button")
        
        page4.wait_for_selector("a[title='CSV (comma delimited)']", timeout=5000)
        with page4.expect_download() as download2_info:
            page4.locator("a[title='CSV (comma delimited)']").click()
        download2 = download2_info.value
        download2.save_as(DOWNLOAD_DIR / "FosterCurrent.csv")
        logging.info("✅ Saved FosterCurrent.csv")
        page4.close()
        page1.close()
        
        logging.info("🎉 All 3 reports exported successfully!")
        logging.info("Files saved to: __Load Files Go Here__")
        
        # Push to Git repository
        git_success = git_pull_and_push()
        if git_success:
            logging.info("✅ All done! Reports exported and pushed to Git.")
        else:
            logging.warning("⚠️  Reports exported but Git push failed.")
        
    except Exception as e:
        logging.error(f"❌ Error: {e}")
        logging.error("Automation failed - check logs for details")
    
    finally:
        context.close()
        browser.close()
        logging.info("Automation completed")

with sync_playwright() as playwright:
    run(playwright)
