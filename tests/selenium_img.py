import requests
import selenium
from selenium import webdriver
from selenium.webdriver.firefox.service import Service;
import os
import time

options = webdriver.FirefoxOptions()
options.browser_version = 'stable'
options.page_load_strategy = 'normal'
driver = webdriver.Firefox()

driver.get("https://www.cit-e.net/montville-nj/cn/taxinquiry_edm/?tpid=18157")

time.sleep(5)

# driver.save_full_page_screenshot("testscreenshot.png")



driver.close()