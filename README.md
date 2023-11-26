# Hilan New Payslip Watch

Isn't it annoying not to know when a new payslip arrives? Well, it annoys me. So I fixed it.

By defining a cron job that will run this script, you will be able to watch Hilan for new payslips


# Features!
  - Notifications on Mac for new payslips in Hilan

### Requirements

* [Python 3+](https://www.python.org/download/releases/3.0/?) - Pyhton 3.6+ verion
* [Selenium](https://github.com/SeleniumHQ/selenium) - Selenium for web automation

### Installation
Step 1: Create virtual environment and install requirements
```sh
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r pip_requirements.txt
```

Step 2: Add your credentials
```sh
$ nano creds.json
```

Your credentials need to be in that file in the following format:
```json
{
    "username": "<hilan_username>",
    "password": "<hilan_password"
}
```

Step 3: Selenium requires a driver to interface with the chosen browser.
> For [Click for Chrome](https://sites.google.com/a/chromium.org/chromedriver/downloads)
> For [Click for FireFox](https://github.com/mozilla/geckodriver/releases)
> For [Click for safari](https://webkit.org/blog/6900/webdriver-support-in-safari-10)

Step 4: Extract the downloaded driver onto a folder

Step 5: Set path variable to the environment. Paste this command to the terminal
```sh
$ export PATH=$PATH:/home/path/to/the/driver/folder/
```

Step 6: Add the cron job
```sh
crontab -e
```

In the editor enter the following line (replace the path to the repo with your own):
```
*/15 * * * * cd <path_to_repo> ; /usr/bin/env venv/bin/python hilan.py
```
