from playwright.sync_api import sync_playwright, expect
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print("Navigating to app...")
            page.goto("http://localhost:8501", timeout=60000)

            # Wait for main title in the body
            print("Waiting for main header...")
            page.wait_for_selector("h1", timeout=60000)

            # Check for specific text in H1
            header = page.locator("h1")
            print(f"Header found: {header.inner_text()}")
            expect(header).to_contain_text("Crypto P's")

            # Take screenshot
            print("Taking screenshot...")
            page.screenshot(path="verification_screenshot.png")
            print("Done.")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification_error_2.png")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
