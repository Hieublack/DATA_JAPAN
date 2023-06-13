import logging
from datetime import datetime
logging.getLogger("selenium.webdriver.common.selenium_manager").setLevel(logging.WARNING)
def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f'{timestamp} - {message}')