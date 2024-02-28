# This file is meant to be called by a cron job
# It will check if the current month's payslip is available on Hilan
# If it is, it will send a notification to the user
# The cronjob should be something like (every 15 minutes):
# */15 * * * * cd <path_to_repo> ; /usr/bin/env venv/bin/python hilan.py

import time
import os
import json
from datetime import datetime
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
# Add logging to file
import logging
# Config the log to include the time, level, and message
logging.basicConfig(filename='last_run_logs.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


file_indicator = 'hilan.txt'

# Get current month and year
current_month = datetime.now().month
year = datetime.now().year

# Check if we already sent a notification for this month
if os.path.exists(file_indicator):
    with open(file_indicator, 'r') as f:
        if f.read() == f'{current_month}':
            logging.info(f'Already sent notification for month {current_month}')
            exit(0)

options = Options()
options.add_argument('-headless')
options.headless = True

logging.info(f'Checking if payslip is available for month {current_month}')
driver = webdriver.Firefox(options=options)

# link to open a site
driver.get("https://apple.net.hilan.co.il/")

# 10 sec wait time to load, if good internet connection is not good then increase the time
# units in seconds
# note this time is being used below also
wait25 = WebDriverWait(driver, 25)
wait10 = WebDriverWait(driver, 10)
wait5 = WebDriverWait(driver, 5)
# Wait for text input #user_nm to load
try:
    username_input = wait5.until(EC.presence_of_element_located((
        By.XPATH, '//input[@id="user_nm"]'
    )))
except Exception as e:
    logging.error(f'Failed to find username input: {e}')
    raise e

# Wait for text input #password_nm to load
try:
    password_input = wait5.until(EC.presence_of_element_located((
        By.XPATH, '//input[@id="password_nm"]'
    )))
except Exception as e:
    logging.error(f'Failed to find password input: {e}')
    raise e

# Load credentials from creds.json
try:
    with open('creds.json', 'r') as f:
        creds = json.load(f)
except Exception as e:
    logging.error(f'Failed to load creds.json: {e}')
    raise e

# Enter credentials
username = creds['username']
password = creds['password']

try:
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)
except Exception as e:
    logging.error(f'Failed to enter credentials: {e}')
    raise e

#  Wait for div with inner text " תקציר שכר " to load
try:
    wait5.until(EC.presence_of_element_located((
        By.XPATH, '//div[contains(text(),"תקציר שכר")]'
    )))
except Exception as e:
    logging.error(f'Failed to find salary summary: {e}')
    raise e

# Find a sibling element with class .month-year-wrapper
try:
    month_year_wrapper = wait5.until(EC.presence_of_element_located((
        By.XPATH, '//div[contains(text(),"תקציר שכר")]/following-sibling::div[contains(@class,"month-year-wrapper")]'
    )))
except Exception as e:
    logging.error(f'Failed to find month-year-wrapper: {e}')
    raise e

# Find the first <option> that element
try:
    first_option = wait5.until(EC.presence_of_element_located((
        By.XPATH, './/option[1]')))
except Exception as e:
    logging.error(f'Failed to find first option: {e}')
    raise e

available_months = [x for x in month_year_wrapper.text.split('\n') if str(year) in x]
driver.quit()
del driver
if (len(available_months)) == current_month:
    logging.info(f'Found payslip for month {current_month}')
    # Check if we already sent a notification for this month
    if os.path.exists(file_indicator):
        with open(file_indicator, 'r') as f:
            if f.read() == f'{current_month}':
                exit(0)
    os.system(f"""osascript -e 'display notification "✅💵💰 Hilan has this month: {len(available_months)}'"'"'s payslip" with title "Hilan Payslip Watch" sound name "Submarine"'""")
    os.system(f'''osascript -e 'tell application "Shortcuts Events" to run the shortcut named "Send Payslip Notification Message"' ''')
    # Save an indication that we found this month's payslip already
    with open(file_indicator, 'w') as f:
        f.write(f'{current_month}')
else:
    logging.info(f'No payslip for month {current_month} yet')
    # os.system(f"""osascript -e 'display notification "❌ Hilan last payslip month is {len(available_months)}" with title "Hilan Payslip Watch"'""")

