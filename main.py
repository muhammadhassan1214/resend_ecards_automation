import time
from datetime import datetime
from utils.elements_locators import ECardsLocators as El
from utils.helper import check_element_exists, click_element

from utils.helper import (
    logger, select_by_text,
    get_undetected_driver
)

from utils.automation import (
    search_sent_cards,
    wait_while_loading_display,
    resend_ecard, login_to_ecards
)


DAILY_INTERVAL_SECONDS = 24 * 60 * 60

def run_daily():
    print("Starting scheduled automation (runs every day)")
    run_count = 0
    while True:
        run_count += 1
        start = time.time()
        print(f"\n{'=' * 50}")
        print(f"DAILY RUN #{run_count}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 50}")
        try:
            main()
        except Exception as e:
            print(f"Unhandled error in scheduled run #{run_count}: {e}")
        # --- Timing Logic ---
        elapsed = time.time() - start
        remaining = DAILY_INTERVAL_SECONDS - elapsed
        if remaining > 0:
            next_run_timestamp = time.time() + remaining
            next_run_time = datetime.fromtimestamp(next_run_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            print(f"Run #{run_count} completed in {elapsed:.1f}s")
            print(f"Next run scheduled for: {next_run_time}")
            print(f"Waiting {remaining / 3600:.2f} hours...")
            time.sleep(remaining)
        else:
            print(f"Run #{run_count} took longer than a day! Starting next run immediately.")


def main():
    page_counter = 1
    driver = get_undetected_driver()
    try:
        if login_to_ecards(driver):
            logger.info("Login successful!")
            select_by_text(driver, El.TRAINING_CENTER_SELECT, "Shell CPR, LLC.")
            wait_while_loading_display(driver)
            training_sites = driver.find_elements(*El.TRAINING_SITE_OPTIONS)
            for i, site in enumerate(training_sites):
                if i == 0:
                    continue
                search_sent_cards(driver, site)
                while True:
                    search_results = driver.find_elements(*El.EMAIL_BUTTONS)
                    if search_results:
                        for j in range(1, len(search_results) + 1):
                            logger.info(f"Processing Entry {j} at Page {page_counter} for {site.text}.")
                            if page_counter > 1:
                                click_element(driver, El.NEXT_PAGE_SELECTOR(page_counter))
                            resend_ecard(driver, j)
                    else:
                        logger.info(f"No sent cards found for {site.text}.")
                        break
                    page_counter += 1
                    next_page = check_element_exists(driver, El.NEXT_PAGE_SELECTOR(page_counter))
                    if not next_page:
                        page_counter = 1
                        break
                    click_element(driver, El.NEXT_PAGE_SELECTOR(page_counter))
                    wait_while_loading_display(driver)
        else:
            logger.warning("Login failed.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        driver.quit()

    finally:
        driver.quit()


if __name__ == "__main__":
    run_daily()
