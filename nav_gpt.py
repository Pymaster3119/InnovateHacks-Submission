import openai
import base64
import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service;
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.support import expected_conditions as EC
import re
import time
import json
import gpt_interactor

def fill_field(xp, value):
    el = driver.find_element(By.XPATH, xp)
    if el is None:
        raise RuntimeError("Bad XPATH")
    ActionChains(driver) \
        .move_to_element(to_element=el) \
        .click() \
        .send_keys(value) \
        .perform()

def clickElement(xp):
    el = driver.find_element(By.XPATH, xp)
    if el is None:
        raise RuntimeError("Bad XPATH")
    ActionChains(driver) \
        .move_to_element(to_element=el) \
        .click() \
        .perform()

options = webdriver.FirefoxOptions()
options.add_argument("--headless")

driver = webdriver.Firefox(options=options)

def get_website(URL):
    driver.get(URL)

system_text = """You are an automation helper to navigate web pages to fulfill task.
Output json array of navigation commands, each command following keys: "xpath", "action", and "value".
Xpath must uniquely identify a specific form field, button or link. Xpath must be accurate.
The action must be one of: "enter" or "click". The value could contain the string that needs to be populated into the element.
If the requested information is on the page, output a string "done" instead of the navigation commands.
Do not generate anything else. No markdown, headers or explanations."""

def navigate_around_current_website(user_prompt):
    pageno = 1
    while(True):
        time.sleep(5)
        driver.save_full_page_screenshot(f"page_{pageno}.png")
        with open(f'page_{pageno}.html', 'wt', encoding='utf-8') as pgsrc:
            page_html = driver.page_source
            pgsrc.write(page_html)

        user_input = user_prompt + page_html
        resp = gpt_interactor.run_query(system_text= system_text, user_prompt=user_input, image_fname=f"page_{pageno}.png")
        with open(f'page_{pageno}.json', 'wt', encoding='utf-8') as f:
            f.write(resp)
        if "done" in resp:
            driver.save_full_page_screenshot(f"result.png")
            return
        cmds = json.loads(resp)
        for cmd in cmds:
            if cmd['action'] == 'enter':
                fill_field(cmd['xpath'], cmd['value'])
            elif cmd['action'] == 'click':
                clickElement(cmd['xpath'])

        pageno += 1

def take_full_page_png(name):
    total_height = driver.execute_script("return document.body.scrollHeight")
    total_width = driver.execute_script("return document.body.scrollWidth")

    driver.set_window_size(total_width, total_height)
    time.sleep(5)
    driver.save_screenshot("result/" + name)

def find_list_of_elements():
    total_height = driver.execute_script("return document.body.scrollHeight")
    total_width = driver.execute_script("return document.body.scrollWidth")

    driver.set_window_size(total_width, total_height)
    time.sleep(5)
    elements = driver.find_elements(By.XPATH, ".//*")
    visible_elements = [el for el in elements if el.is_displayed()]
    output = ""
    index = 0
    ids = {}
    classnames = {}
    for i in visible_elements:
        if i.get_attribute('id') != "":
            if not i.get_attribute('id') in ids.keys():
                ids[i.get_attribute('id')] = 0
            else:
                ids[i.get_attribute('id')] += 1
        elif i.get_attribute('class') != None and i.get_attribute('class') != "":
            if not i.get_attribute('class') in classnames.keys():
                classnames[i.get_attribute('class')] = 0
            else:
                classnames[i.get_attribute('class')] += 1

    elementholders = {}
    for i in ids.keys():
        if ids[i] == 0:
            try:
                elementholders["id = " + i] = driver.find_element(By.ID, i)
            except:
                pass
    for i in classnames.keys():
        if classnames[i] == 0:
            try:
                elementholders["classname = " + i] = driver.find_element(By.CLASS_NAME, i)
            except:
                pass
    for i in elementholders.keys():
        index += 1
        output += str(index) + ". " + i
        output += "\n"
    return output
    

if __name__ == "__main__":
    driver.get("https://www.itch.io")
    print(find_list_of_elements())
    take_full_page_png("test.png")