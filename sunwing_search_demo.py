import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime, timedelta

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()

        print("[Step 1] Go to Sunwing homepage...")
        try:
            await page.goto("https://www.sunwing.ca/en/", wait_until="domcontentloaded", timeout=90000)
            await page.wait_for_load_state('domcontentloaded')
            await page.screenshot(path="step1_homepage.png")
            print("[Step 1] Screenshot saved: step1_homepage.png")
        except Exception as e:
            print(f"[Step 1] ERROR: {e}")
            await page.screenshot(path="step1_homepage_error.png")
            print("[Step 1] Error screenshot saved: step1_homepage_error.png")
            await browser.close()
            return

        # Handle cookie consent if present
        print("[Step 1.1] Check for cookie consent banner...")
        try:
            accept_button = await page.query_selector('button:has-text("Accept")')
            if accept_button:
                print("[Step 1.1] Clicking 'Accept' on cookie banner...")
                await accept_button.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path="step1_after_accept.png")
                print("[Step 1.1] Screenshot saved: step1_after_accept.png")
            else:
                print("[Step 1.1] No cookie banner found.")
        except Exception as e:
            print(f"[Step 1.1] Error handling cookie banner: {e}")

        # Handle 'JOIN THE CLUB' modal popup if present, wait up to 10s
        print("[Step 1.2] Check for 'JOIN THE CLUB' modal...")
        modal_closed = False
        try:
            # Wait for modal or timeout
            for i in range(10):
                close_modal_btn = await page.query_selector('button[aria-label="Close"]')
                if not close_modal_btn:
                    # Try alternative selectors
                    close_modal_btn = await page.query_selector('button:has-text("×")')
                if close_modal_btn:
                    print("[Step 1.2] Closing 'JOIN THE CLUB' modal...")
                    await close_modal_btn.click()
                    await page.wait_for_timeout(1000)
                    modal_closed = True
                    break
                await page.wait_for_timeout(1000)
            if not modal_closed:
                print("[Step 1.2] No modal found after waiting.")
            else:
                await page.screenshot(path="step1_after_modal_closed.png")
                print("[Step 1.2] Screenshot saved: step1_after_modal_closed.png")
        except Exception as e:
            print(f"[Step 1.2] Error handling modal: {e}")
        # Take a screenshot after modal handling regardless
        await page.screenshot(path="step1_after_modal_handling.png")
        print("[Step 1.2] Screenshot saved: step1_after_modal_handling.png")

        # Fill 'From' (departure city)
        print("[Step 2] Fill 'From' field...")
        from_selector = 'input[name="origin"]'  # Updated selector
        try:
            await page.wait_for_selector(from_selector, timeout=10000)
            await page.click(from_selector)
            await page.fill(from_selector, "Vancouver")
            await page.wait_for_timeout(1000)
            await page.keyboard.press('Enter')
            await page.screenshot(path="step2_from_filled.png")
            print("[Step 2] Screenshot saved: step2_from_filled.png")
        except PlaywrightTimeoutError:
            print(f"[Step 2] ERROR: Could not find 'From' field after waiting.")
            await page.screenshot(path="step2_from_error.png")
            print("[Step 2] Error screenshot saved: step2_from_error.png")
            await browser.close()
            return

        # Fill 'To' (destination or hotel)
        print("[Step 3] Fill 'To' field...")
        to_selector = 'input[name="destination"]'  # Updated selector
        await page.click(to_selector)
        await page.fill(to_selector, "Cuba")
        await page.wait_for_timeout(1000)
        await page.keyboard.press('Enter')
        await page.screenshot(path="step3_to_filled.png")
        print("[Step 3] Screenshot saved: step3_to_filled.png")

        # Set Dates (next week)
        print("[Step 4] Open date picker...")
        date_selector = 'input[name="departDate"]'  # Updated selector
        await page.click(date_selector)
        await page.wait_for_timeout(1000)
        await page.screenshot(path="step4_date_picker.png")
        print("[Step 4] Screenshot saved: step4_date_picker.png")
        # The date picker may require more advanced interaction; for demo, just close it
        await page.keyboard.press('Escape')

        # Set Rooms & Guests (default is 1 Room, 2 Adults)
        # If you want to change, you can interact with the corresponding button
        # rooms_selector = 'input[aria-label="Rooms & Guests"]'
        # await page.click(rooms_selector)
        # await page.wait_for_timeout(1000)
        # await page.keyboard.press('Escape')

        # Click Search
        print("[Step 5] Click Search button...")
        search_selector = 'button:has-text("Search")'
        await page.click(search_selector)
        await page.screenshot(path="step5_after_search.png")
        print("[Step 5] Screenshot saved: step5_after_search.png")

        # Wait for results page to load
        print("[Step 6] Waiting for results page to load...")
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(5000)
        await page.screenshot(path="step6_results.png")
        print("[Step 6] Screenshot saved: step6_results.png")
        print("Search completed and results page loaded.")

        await browser.close()

# --- Minimal Playwright demo: Select 'Vancouver' in 'From' field ---
def playwright_select_vancouver():
    from playwright.sync_api import sync_playwright
    import time
    from datetime import datetime, timedelta
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.sunwing.ca/en")
        page.wait_for_load_state('networkidle')
        page.wait_for_selector('input#packages-from-input', state='visible', timeout=15000)
        page.wait_for_selector('input#packages-from-input:enabled', timeout=15000)
        page.wait_for_timeout(2000)
        try:
            if page.is_visible('button[aria-label="Close"]'):
                page.click('button[aria-label="Close"]')
                page.wait_for_timeout(1000)
            elif page.is_visible('button:has-text("×")'):
                page.click('button:has-text("×")')
                page.wait_for_timeout(1000)
        except Exception:
            pass
        page.click('input#packages-from-input')
        page.fill('input#packages-from-input', 'Vancouver')
        try:
            page.wait_for_selector('div[role="listbox"] [role="option"]:has-text("Vancouver")', timeout=4000)
            page.click('div[role="listbox"] [role="option"]:has-text("Vancouver")')
            page.wait_for_timeout(1000)
        except Exception:
            print("[DEBUG] Could not find or click the Vancouver dropdown item.")
        try:
            page.click('input#packages-to-input')
            page.wait_for_timeout(1000)
        except Exception:
            print("[DEBUG] Could not click the 'To' field to blur 'From'.")
        page.fill('input#packages-to-input', 'Mexico')
        try:
            page.wait_for_selector('div[role="listbox"] [role="option"]:has-text("Mexico")', timeout=4000)
            page.click('div[role="listbox"] [role="option"]:has-text("Mexico")')
            page.wait_for_timeout(1000)
        except Exception:
            print("[DEBUG] Could not find or click the Mexico dropdown item.")
        # --- Set Dates: Find and click the correct day buttons in June 2025 ---
        try:
            page.click('input[readonly][value*="Jun"]')
            page.wait_for_timeout(1500)
            june_buttons = page.query_selector_all('div.rdrMonthName:has-text("June 2025") ~ div.rdrDays button.rdrDay')
            found_start = False
            found_end = False
            for btn in june_buttons:
                day_num = btn.query_selector('span.rdrDayNumber > span')
                if day_num:
                    text = day_num.inner_text().strip()
                    if text == "1":
                        btn.click()
                        found_start = True
                        print("[DEBUG] Clicked start date: June 1, 2025")
                        page.wait_for_timeout(500)
                    if text == "8":
                        btn.click()
                        found_end = True
                        print("[DEBUG] Clicked end date: June 8, 2025")
                        page.wait_for_timeout(500)
            if not found_start:
                print("[DEBUG] Start date button not found!")
            if not found_end:
                print("[DEBUG] End date button not found!")
            # Immediately try clicking Search after setting the date, with force=True
            print("[DEBUG] Attempting to click Search button with force=True after setting dates...")
            page.click('button[type="submit"]', force=True)
            print("[DEBUG] Clicked Search button (force=True).")
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"[DEBUG] Could not set dates or click Search: {e}")
        page.screenshot(path="debug_after_to_and_dates.png")
        page.wait_for_timeout(3000)
        browser.close()

if __name__ == "__main__":
    # asyncio.run(main())
    playwright_select_vancouver() 