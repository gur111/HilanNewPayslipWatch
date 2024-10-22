# This file is meant to be called by a cron job
# It will check if the current month's payslip is available on Hilan
# If it is, it will send a notification to the user
# The cronjob should be something like (every 15 minutes):
# */15 * * * * cd <path_to_repo> ; /usr/bin/env venv/bin/python hilan.py

from subprocess import check_output
import os
import json
from datetime import datetime
import logging
from curl_cffi import requests

# Config the log to include the time, level, and message
logging.basicConfig(filename='last_run_logs.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
file_indicator = 'hilan.txt'
current_month = datetime.now().month


def login():
    password = get_password()
    url = "https://apple.net.hilan.co.il/HilanCenter/Public/api/LoginApi/LoginRequest"

    payload = f'orgId=1047&username=632382&password={password}&isEn=true'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    session = requests.Session()
    response = session.post(url, headers=headers, data=payload, max_redirects=3, timeout=5).json()
    if response['IsFail']:
        logging.error(f'Login error: {response}')
        return None

    return session


def get_data(session):
    url = "https://apple.net.hilan.co.il/Hilannetv2/Services/Public/WS/HSalaryApiapi.asmx/GetData"

    payload = {
        "IsLastPayslipMonth": True
    }
    response = session.post(url, data=payload)
    return response.json()


def is_current_month_available():
    session = login()

    if not session:
        logging.error('Failed to login to HilaNet')
        return False

    data = get_data(session)
    ans = False
    if data['Month'] == current_month:
        ans = True

    logging.info(f'Is new payslip is available for month {current_month}? {"Yes" if ans else "No"} (last = {data["Month"]})')
    return ans


def was_curr_month_last_reported_month():
    # Check if we already sent a notification for this month
    if os.path.exists(file_indicator):
        with open(file_indicator, 'r') as f:
            if f.read() == f'{current_month}':
                logging.debug(f'Already sent notification for month {current_month}')
                return True

    return False


def persist_current_month_as_reported():
    # Save an indication that we found this month's payslip already
    with open(file_indicator, 'w') as f:
        f.write(f'{current_month}')


def report_current_month():
    os.system(
        f"""osascript -e 'display notification "✅💵💰 Hilan has this month: {current_month}'"'"'s payslip" with title "Hilan Payslip Watch" sound name "Submarine"'""")
    # os.system(f'''osascript -e 'tell application "Shortcuts Events" to run the shortcut named "Send Payslip Notification Message"' ''')

    persist_current_month_as_reported()


def get_password():
    # Load credentials from creds.json
    try:
        with open('creds.json', 'r') as f:
            creds = json.load(f)
    except Exception as e:
        logging.error(f'Failed to load creds.json: {e}')
        raise e

    if 'password' in creds:
        password = creds['password']
    else:
        onepass_output = check_output(f"op item get {creds['1pass_item_id']} --fields label=username,label=password", shell=True).decode()
        password = onepass_output[onepass_output.find(',') + 1:].strip()

    return password


def is_new_payslip_available():
    if was_curr_month_last_reported_month():
        return False

    if is_current_month_available():
        return True

    return False


def main():
    if is_new_payslip_available():
        report_current_month()


if __name__ == '__main__':
    main()
