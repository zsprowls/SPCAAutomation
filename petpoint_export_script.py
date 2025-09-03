import re
import os
from pathlib import Path
from playwright.sync_api import Playwright, sync_playwright, expect

# Configuration - using the working credentials from your recording
PETPOINT_USER = 'zaks'
PETPOINT_PASS = 'Gillian666!'
PETPOINT_SHELTER_ID = 'USNY9'
DOWNLOAD_DIR = Path(__file__).parent / "__Load Files Go Here__"
DOWNLOAD_DIR.mkdir(exist_ok=True)

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False, slow_mo=1000)  # Add 1 second delay between actions
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://sms.petpoint.com/sms3/forms/signinout.aspx")
    page.wait_for_load_state('networkidle')  # Wait for page to fully load
    page.locator("#loginFrame").content_frame.locator("#LoginShelterId").click()
    page.locator("#loginFrame").content_frame.locator("#LoginShelterId").fill(PETPOINT_SHELTER_ID)
    page.locator("#loginFrame").content_frame.get_by_role("link", name="Next").click()
    page.locator("#loginFrame").content_frame.locator("#LoginUsername").fill(PETPOINT_USER)
    page.locator("#loginFrame").content_frame.locator("#LoginPassword").click()
    page.locator("#loginFrame").content_frame.locator("#LoginPassword").fill(PETPOINT_PASS)
    page.locator("#loginFrame").content_frame.get_by_role("link", name="Login").click()
    page.wait_for_load_state('networkidle')  # Wait for login to complete
    
    print("Login completed, looking for Reports dropdown...")
    # Wait for the Reports dropdown to be available
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
    page1.wait_for_load_state('networkidle')  # Wait for reports page to load
    print("Report Website opened successfully")
    
    print("Looking for 'Animal' link...")
    page1.wait_for_selector("text=Animal", timeout=10000)
    page1.get_by_role("link", name="Animal", exact=True).click()
    print("Clicked Animal link")
    
    print("Looking for 'Animal: Animal Inventory'...")
    page1.wait_for_selector("text=Animal: Animal Inventory", timeout=10000)
    page1.get_by_text("Animal: Animal Inventory").click()
    print("Clicked Animal Inventory")
    
    print("Looking for Summary dropdown...")
    page1.locator("[id=\"1\"]").get_by_text("Summary", exact=True).click()
    page1.get_by_role("option", name="Detail").click()
    print("Selected Detail option")
    print("Clicking Submit button...")
    with page1.expect_popup() as page2_info:
        page1.get_by_role("button", name="Submit").click()
    page2 = page2_info.value
    page2.wait_for_load_state('networkidle')  # Wait for report to load
    print("Report generated, looking for export options...")
    
    print("Looking for export button...")
    page2.wait_for_selector("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg", timeout=10000)
    page2.locator("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg").click()
    print("Clicked export button")
    
    print("Looking for CSV export option...")
    page2.wait_for_selector("a[title='CSV (comma delimited)']", timeout=5000)
    with page2.expect_download() as download_info:
        page2.locator("a[title='CSV (comma delimited)']").click()
    download = download_info.value
    # Save Animal Inventory
    download.save_as(DOWNLOAD_DIR / "AnimalInventory.csv")
    print("✅ Saved AnimalInventory.csv")
    page2.close()
    
    # Navigate back to reports page for next report
    page1.goto("https://repstd.petpoint.com/Index#")
    page1.wait_for_load_state('networkidle')
    
    print("Looking for 'Animal' link for Stage Review...")
    page1.get_by_role("link", name="Animal", exact=True).click()
    page1.get_by_text("Stage: Review").click()
    page1.locator("[id=\"1\"]").get_by_text("Summary", exact=True).click()
    page1.get_by_role("option", name="Detail").click()
    with page1.expect_popup() as page4_info:
        page1.get_by_role("button", name="Submit").click()
    page4 = page4_info.value
    print("Looking for export button for Stage Review...")
    page4.wait_for_selector("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg", timeout=10000)
    page4.locator("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg").click()
    print("Clicked export button")
    
    print("Looking for CSV export option...")
    page4.wait_for_selector("a[title='CSV (comma delimited)']", timeout=5000)
    with page4.expect_download() as download1_info:
        page4.locator("a[title='CSV (comma delimited)']").click()
    download1 = download1_info.value
    # Save Stage Review
    download1.save_as(DOWNLOAD_DIR / "StageReview.csv")
    print("✅ Saved StageReview.csv")
    page4.close()
    
    # Navigate back to reports page for next report
    page1.goto("https://repstd.petpoint.com/Index#")
    page1.wait_for_load_state('networkidle')
    
    print("Looking for 'Care' link for Foster Current...")
    page1.get_by_role("link", name="Care").click()
    page1.get_by_text("Foster: Current").click()
    page1.get_by_text("select").nth(4).click()
    page1.get_by_role("option", name="Detail").click()
    with page1.expect_popup() as page6_info:
        page1.get_by_role("button", name="Submit").click()
    page6 = page6_info.value
    page6.get_by_role("link", name="J K").click()
    print("Looking for export button for Foster Current...")
    page6.wait_for_selector("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg", timeout=10000)
    page6.locator("#ReportViewer1_ctl09_ctl04_ctl00_ButtonImg").click()
    print("Clicked export button")
    
    print("Looking for CSV export option...")
    page6.wait_for_selector("a[title='CSV (comma delimited)']", timeout=5000)
    with page6.expect_download() as download2_info:
        page6.locator("a[title='CSV (comma delimited)']").click()
    download2 = download2_info.value
    # Save Foster Current
    download2.save_as(DOWNLOAD_DIR / "FosterCurrent.csv")
    print("✅ Saved FosterCurrent.csv")
    page6.close()
    page1.close()
    
    # Now go back to main page and use Report Builder
    print("Going back to main page for Report Builder...")
    page.wait_for_selector("#ReportsNavbarDropdown", timeout=10000)
    
    # Hover over the Reports dropdown again
    page.locator("#ReportsNavbarDropdown").hover()
    print("Hovered over Reports dropdown for Report Builder")
    
    # Wait for the dropdown menu to appear
    page.wait_for_selector("a:has-text('Report Builder')", timeout=5000)
    print("Report Builder option appeared in dropdown")
    
    # Click on Report Builder
    with page.expect_popup() as page8_info:
        page.get_by_role("link", name="Report Builder").click()
    page8 = page8_info.value
    page8.wait_for_load_state('networkidle')
    print("Report Builder opened successfully")
    
    print("Looking for search box...")
    page8.wait_for_selector("input[placeholder*='Search'], input[name*='Search']", timeout=10000)
    page8.get_by_role("textbox", name="Search Report Names...").click()
    page8.get_by_role("textbox", name="Search Report Names...").fill("hold")
    print("Searched for 'hold'")
    
    print("Looking for 'Hold - Foster Stage Date'...")
    page8.wait_for_selector("text=Hold - Foster Stage Date", timeout=10000)
    page8.get_by_text("Hold - Foster Stage Date").click()
    print("Clicked Hold - Foster Stage Date")
    
    print("Looking for run button...")
    page8.locator("#WebReportsCtrl_MainSplitter_ReportsCtrl_ReportsTree_TreeContent").get_by_role("button").first.click()
    print("Clicked run button")
    
    print("Looking for Export button...")
    page8.get_by_role("button", name="Export").click()
    print("Clicked Export button")
    
    print("Looking for Express View Export button...")
    page8.locator("#wrCtrl4e30_ExpressViewExportButton").click()
    print("Clicked Express View Export button")
    
    print("Looking for CSV export option...")
    with page8.expect_download() as download3_info:
        page8.locator("#wrExpressViewExportTypeMenu_947096786").get_by_text("Export CSV").click()
    download3 = download3_info.value
    # Save Hold - Foster Stage Date
    download3.save_as(DOWNLOAD_DIR / "Hold - Foster Stage Date.csv")
    print("✅ Saved Hold - Foster Stage Date.csv")

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
