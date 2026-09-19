import os
import time
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from utils.elements_locators import ECardsLocators as El
from utils.helper import (
    logger, click_element,
    input_element, select_by_text,
    wait_while_element_is_displaying,
    safe_navigate_to_url, check_element_exists
)


load_dotenv(verbose=True)

def login_to_ecards(driver, popup_handler=None) -> bool:
    BASE_URL = "https://ecards.heart.org"
    """Login to eCards with comprehensive error handling and retry logic."""
    try:
        safe_navigate_to_url(driver, f"{BASE_URL}/Inventory", popup_handler=popup_handler)
        # Check if already logged in
        if f"{BASE_URL}/Inventory" == driver.current_url:
            safe_navigate_to_url(driver, f"{BASE_URL}/SearchAllECards", popup_handler=popup_handler)
            return True
        # Check for sign-in button
        sign_in_button = check_element_exists(driver, El.SIGN_IN_BUTTON, timeout=3)
        email_field = check_element_exists(driver, El.EMAIL_FIELD, timeout=5)
        if sign_in_button:
            if not click_element(driver, El.SIGN_IN_BUTTON):
                return False
            time.sleep(3)
            # Check if redirected to inventory
            if "Inventory" in driver.current_url:
                return True
        # Proceed with login if email field exists
        if email_field:
            if not input_element(driver, El.EMAIL_FIELD, os.getenv("ATLAS_USERNAME")):
                return False
            time.sleep(1)
            if not input_element(driver, El.PASSWORD_FIELD, os.getenv("ATLAS_PASSWORD")):
                return False
            time.sleep(1)
            # Try to click remember me checkbox (optional)
            if check_element_exists(driver, El.REMEMBER_ME, timeout=3):
                click_element(driver, El.REMEMBER_ME)
            time.sleep(1)
            # Click sign-in button
            if not click_element(driver, El.SUBMIT_BUTTON):
                return False
            time.sleep(5)
            # Verify login success
            if f"{BASE_URL}/Inventory" == driver.current_url:
                safe_navigate_to_url(driver, f"{BASE_URL}/SearchAllECards", popup_handler=popup_handler)
                return True
            else:
                return False
        else:
            return True

    except Exception as e:
        logger.error("Failed to login to Atlas\nError: %s", e)
        return False


def search_sent_cards(driver, training_site):
    """Search for sent cards based on the provided training site."""
    try:
        text = training_site.text
        logger.info(f"Working on Training Site: {text}")
        select_by_text(driver, El.TRAINING_SITE_SELECT, text)
        wait_while_loading_display(driver)
        select_by_text(driver, El.ECARD_STATUS_SELECT, "Sent")
        click_element(driver, El.SEARCH_CARD_BUTTON)
        wait_while_loading_display(driver)
    except Exception as e:
        logger.error(f"An error occurred while searching for sent cards: {e}")


def resend_ecard(driver, i):
    """Resend an eCard and handle potential errors."""
    try:
        click_element(driver, (By.XPATH, f"(//a[text()= 'Email'])[{i}]"))
        click_element(driver, El.RESEND_ECARD_BUTTON)
        wait_while_loading_display(driver)
        wait_until_scrolled_to_top(driver)
    except Exception as e:
        logger.error(f"An error occurred while resending the eCard: {e}")


def wait_while_loading_display(driver):
    wait_while_element_is_displaying(driver, El.WAIT_MESSAGE)


def wait_until_scrolled_to_top(driver, timeout=10):
    def is_at_top(driver):
        scroll_position = driver.execute_script("return window.pageYOffset;")
        return scroll_position == 0

    try:
        WebDriverWait(driver, timeout).until(is_at_top)
        return True
    except TimeoutException:
        return False
