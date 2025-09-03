import re
import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from playwright.sync_api import Playwright, sync_playwright, expect

# Configuration - REPLACE WITH YOUR ACTUAL CREDENTIALS
PETPOINT_USER = 'YOUR_USERNAME_HERE'
PETPOINT_PASS = 'YOUR_PASSWORD_HERE'
PETPOINT_SHELTER_ID = 'USNY9'
DOWNLOAD_DIR = Path(__file__).parent / "__Load Files Go Here__"
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Email configuration - import from config file
try:
    from email_config import EMAIL_TO, EMAIL_FROM, SMTP_SERVER, SMTP_PORT, EMAIL_PASSWORD
    EMAIL_ENABLED = True
except ImportError:
    print("⚠️  Email config not found. Email notifications disabled.")
    EMAIL_ENABLED = False

def send_email(subject, body, success=True):
    """Send email notification about the script run."""
    if not EMAIL_ENABLED:
        print("📧 Email notifications disabled - no config file found")
        return
        
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        # Add timestamp to body
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_body = f"{body}\n\nTimestamp: {timestamp}"
        
        msg.attach(MIMEText(full_body, 'plain'))
        
        # Connect to server and send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_FROM, EMAIL_TO, text)
        server.quit()
        
        print(f"✅ Email notification sent: {subject}")
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False, slow_mo=1000)  # Add 1 second delay between actions
    context = browser.new_context()
    page = context.new_page()
    
    try:
        print("Navigating to PetPoint login...")
        page.goto("https://sms.petpoint.com/sms3/forms/signinout.aspx")
        page.wait_for_load_state('networkidle')
        
        print("Logging in...")
        page.locator("#loginFrame").content_frame.locator("#LoginShelterId").click()
        page.locator("#loginFrame").content_frame.locator("#LoginShelterId").fill(PETPOINT_SHELTER_ID)
        page.locator("#loginFrame").content_frame.get_by_role("link", name="Next").click()
        page.locator("#loginFrame").content_frame.locator("#LoginUsername").fill(PETPOINT_USER)
        page.locator("#loginFrame").content_frame.locator("#LoginPassword").click()
        page.locator("#loginFrame").content_frame.locator("#LoginPassword").fill(PETPOINT_PASS)
        page.locator("#loginFrame").content_frame.get_by_role("link", name="Login").click()
        page.wait_for_load_state('networkidle')
        
        print("Login completed, looking for Reports dropdown...")
        page.wait_for_selector("#ReportsNavbarDropdown", timeout=15000)
        print("Found Reports dropdown")
        
        # Hover over the Reports dropdown to show the menu
        page.locator("#ReportsNavbarDropdown").hover()
        print("Hovered over Reports dropdown")
        
        # Wait for the dropdown menu to appear
        page.wait_for_selector("a:has-text('Report Website')", timeout=5000)
        print("Report Website option appeared in dropdown")
        
        # Click on Report Website
        with page.expect_popup() as page1_info:
            page.get_by_role("link", name="Report Website").click()
        page1 = page1_info.value
        page1.wait_for_load_state('networkidle')
        print("Report Website opened successfully")
        
        # Report 1: Animal Inventory
        print("\n=== EXPORTING ANIMAL INVENTORY ===")
        page1.wait_for_selector("text=Animal", timeout=10000)
        page1.get_by_role("link", name="Animal", exact=True).click()
        print("Clicked Animal link")
        
        page1.wait_for_selector("text=Animal: Animal Inventory", timeout=10000)
        page1.get_by_text("Animal: Animal Inventory").click()
        print("Clicked Animal Inventory")
        
        page1.locator("[id=\"1\"]").get_by_text("Summary", exact=True).click()
        page1.get_by_role("option", name="Detail").click()
        print("Selected Detail option")
        
        with page1.expect_popup() as page2_info:
            page1.get_by_role("button", name="Submit").click()
        page2 = page2_info.value
        page2.wait_for_load_state('networkidle')
        print("Report generated, looking for export options...")
        
        page2.wait_for_selector("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg", timeout=10000)
        page2.locator("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg").click()
        print("Clicked export button")
        
        page2.wait_for_selector("a[title='CSV (comma delimited)']", timeout=5000)
        with page2.expect_download() as download_info:
            page2.locator("a[title='CSV (comma delimited)']").click()
        download = download_info.value
        download.save_as(DOWNLOAD_DIR / "AnimalInventory.csv")
        print("✅ Saved AnimalInventory.csv")
        page2.close()
        
        # Report 2: Stage Review
        print("\n=== EXPORTING STAGE REVIEW ===")
        page1.goto("https://repstd.petpoint.com/Index#")
        page1.wait_for_load_state('networkidle')
        
        page1.get_by_role("link", name="Animal", exact=True).click()
        page1.get_by_text("Stage: Review").click()
        page1.locator("[id=\"1\"]").get_by_text("Summary", exact=True).click()
        page1.get_by_role("option", name="Detail").click()
        
        with page1.expect_popup() as page3_info:
            page1.get_by_role("button", name="Submit").click()
        page3 = page3_info.value
        
        page3.wait_for_selector("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg", timeout=10000)
        page3.locator("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg").click()
        print("Clicked export button")
        
        page3.wait_for_selector("a[title='CSV (comma delimited)']", timeout=5000)
        with page3.expect_download() as download1_info:
            page3.locator("a[title='CSV (comma delimited)']").click()
        download1 = download1_info.value
        download1.save_as(DOWNLOAD_DIR / "StageReview.csv")
        print("✅ Saved StageReview.csv")
        page3.close()
        
        # Report 3: Foster Current
        print("\n=== EXPORTING FOSTER CURRENT ===")
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
        print("Clicked export button")
        
        page4.wait_for_selector("a[title='CSV (comma delimited)']", timeout=5000)
        with page4.expect_download() as download2_info:
            page4.locator("a[title='CSV (comma delimited)']").click()
        download2 = download2_info.value
        download2.save_as(DOWNLOAD_DIR / "FosterCurrent.csv")
        print("✅ Saved FosterCurrent.csv")
        page4.close()
        page1.close()
        
        print("\n🎉 All 3 reports exported successfully!")
        print("Files saved to: __Load Files Go Here__")
        
        # Send success email
        success_body = """PetPoint Export Script - SUCCESS

All 3 reports have been exported successfully:
✅ AnimalInventory.csv
✅ StageReview.csv  
✅ FosterCurrent.csv

Files saved to: __Load Files Go Here__"""
        
        send_email("PetPoint Export - SUCCESS", success_body, success=True)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check the browser window to see what happened...")
        
        # Send error email
        error_body = f"""PetPoint Export Script - ERROR

The script encountered an error and could not complete the export.

Error details: {str(e)}

Please check the system and try running the script manually."""
        
        send_email("PetPoint Export - ERROR", error_body, success=False)
        
        input("Press Enter to close browser...")
    
    finally:
        context.close()
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
