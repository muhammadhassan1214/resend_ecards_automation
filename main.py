import time
import datetime
from utils.elements_locators import ECardsLocators as El
from utils.helper import check_element_exists, click_element
from utils.resend_using_requests import get_cookie_header, resend_ecard
from utils.helper import (
    logger, select_by_text,
    get_undetected_driver,
    save_error_screenshot,
    SessionPopupHandler,
    ReportLogger
)

from utils.automation import (
    search_sent_cards,
    wait_while_loading_display,
    login_to_ecards
)


def run_at_intervals(hours):
    """Runs immediately, then repeats every X hours."""
    print(f"Starting scheduled execution. The function will run now and every {hours} hours.")
    main()  # Initial run

    while True:
        try:
            # Sleep for the specified number of hours (converted to seconds)
            time.sleep(hours * 3600)
            main()
        except KeyboardInterrupt:
            print("\nScheduler stopped by user.")
            break


def run_at_specific_time(target_time_str):
    """Waits until a specific time of day, runs, and repeats every 24 hours."""
    print(f"Scheduler set to run daily at {target_time_str}.")

    while True:
        try:
            now = datetime.datetime.now()
            # Parse the user's target time
            target_time = datetime.datetime.strptime(target_time_str, "%H:%M").time()
            target_datetime = datetime.datetime.combine(now.date(), target_time)

            # If the target time has already passed today, schedule for tomorrow
            if target_datetime <= now:
                target_datetime += datetime.timedelta(days=1)

            # Calculate how many seconds to wait
            sleep_seconds = (target_datetime - now).total_seconds()
            print(f"Waiting for {int(sleep_seconds)} seconds (until {target_datetime})...")

            time.sleep(sleep_seconds)
            main()

        except ValueError:
            print("Invalid time format. Please use HH:MM (e.g., 14:30).")
            break
        except KeyboardInterrupt:
            print("\nScheduler stopped by user.")
            break


def start_scheduler():
    """Displays the menu and triggers the appropriate scheduling mode."""
    print("Select a time mode to run the script:")
    print("1. Every 12 hours")
    print("2. Every 24 hours")
    print("3. At a specific time (e.g., 05:30, 18:00)")
    print("4. Run now (no repetitions)")
    print("Press Ctrl+C at any time to stop the scheduler.")

    choice = input("\nEnter your choice (1/2/3/4): ").strip()

    if choice == '1':
        run_at_intervals(12)
    elif choice == '2':
        run_at_intervals(24)
    elif choice == '3':
        time_input = input("Enter the time in 24-hour HH:MM format (e.g., 18:30): ").strip()
        run_at_specific_time(time_input)
    elif choice == '4':
        print("Running immediately...")
        main()
    else:
        print("Invalid choice. Please enter 1, 2, 3, or 4.")


def main():
    page_counter = 1
    driver = get_undetected_driver()
    popup_handler = SessionPopupHandler(driver)
    report = ReportLogger()
    try:
        popup_handler.start()
        if login_to_ecards(driver, popup_handler=popup_handler):
            logger.info("Login successful!")
            # Capture authenticated cookies for this run; never reuse a copied
            # browser cookie header from a previous session.
            cookie_header = get_cookie_header(driver)
            logger.info("Fetched authenticated cookies for this run (%d characters).",
                        len(cookie_header))
            # Inject override right after login lands on the eCards page
            popup_handler.inject_override()
            select_by_text(driver, El.TRAINING_CENTER_SELECT, "Shell CPR, LLC.")
            wait_while_loading_display(driver)
            popup_handler.inject_override()
            ecard_data = []

            training_sites = driver.find_elements(*El.TRAINING_SITE_OPTIONS)
            for i, site in enumerate(training_sites):
                if i == 0:
                    continue

                search_sent_cards(driver, site)
                popup_handler.inject_override()
                training_site = site.text

                while True:
                    search_results = driver.find_elements(*El.EMAIL_BUTTONS)
                    if search_results:
                        for result in search_results:
                            ecard_data.append({
                                "ECardUId": result.get_attribute("data-eid"),
                                "StudentId": result.get_attribute("data-stuid"),
                                "EmailAddress": result.get_attribute("data-email"),
                                "TrainingSite": training_site
                            })
                    else:
                        logger.info(f"No sent cards found for {training_site}.")
                        break

                    page_counter += 1
                    next_page = check_element_exists(driver, El.NEXT_PAGE_SELECTOR(page_counter))
                    if not next_page:
                        page_counter = 1
                        break

                    click_element(driver, El.NEXT_PAGE_SELECTOR(page_counter))
                    wait_while_loading_display(driver)
                    popup_handler.inject_override()

            if ecard_data:
                logger.info(f"Found {len(ecard_data)} sent eCards to resend.")
                for ecard in ecard_data:
                    response = resend_ecard(driver, ecard, cookie=cookie_header)
                    if response.status_code == 200:
                        logger.info(f"Successfully resent eCard to {ecard['EmailAddress']} "
                                    f"for training site {ecard['TrainingSite']}.")
                    else:
                        logger.error(f"Failed to resend eCard to {ecard['EmailAddress']} "
                                     f"for training site {ecard['TrainingSite']}. "
                                     f"Status code: {response.status_code}, Response: {response.text}")
        else:
            logger.warning("Login failed.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        save_error_screenshot(driver)
        driver.quit()

    finally:
        report.save_report()
        popup_handler.stop()
        driver.quit()


if __name__ == "__main__":
    start_scheduler()
