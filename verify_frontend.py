from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("Navigating to app...")
            page.goto("http://localhost:8501", timeout=60000)

            print("Waiting for sidebar...")
            page.wait_for_selector('[data-testid="stSidebar"]', timeout=30000)
            time.sleep(5)

            print("Locating Forecast Settings...")
            # Verify new Model Ensemble multiselect is present
            page.locator('label:has-text("Select Models to Combine")').wait_for()

            # Verify Forecast Days slider (we updated it to 365, but visual check is harder in code, just checking presence)
            page.locator('label:has-text("Forecast Horizon (Days)")').wait_for()

            print("Taking screenshot...")
            page.screenshot(path="verification_screenshot.png", full_page=True)
            print("Screenshot saved to verification_screenshot.png")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification_error.png")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
