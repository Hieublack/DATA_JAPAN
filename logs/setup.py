import logging
from datetime import datetime

# logging.getLogger("selenium.webdriver.common.selenium_manager").setLevel(logging.INFO)


def logMessage(save_log, message):
    if save_log:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"{timestamp} - {message}")
