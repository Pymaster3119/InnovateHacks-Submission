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
from selenium.webdriver.support.ui import Select
import shutil

def selectItem(driver, xp, value):
    el = driver.find_element(By.XPATH, xp)
    if el is None:
        raise RuntimeError("Bad XPATH")
    ActionChains(driver) \
        .move_to_element(to_element=el) \
        .click() \
        .perform()
    Select(el).select_by_value(value)

def execute_selenium_command(driver, commmand, target, target_type, value):
    print("Recieved Command")
    if target_type == "XPATH":
        el = driver.find_element(By.XPATH, target)
        if el is None:
            raise RuntimeError("Bad XPATH")
    elif target_type == "CSS":
        el = driver.find_element(By.CSS_SELECTOR, target)
        if el is None:
            raise RuntimeError("Bad CSS")
    print(f"Element selected: {el}")

    if commmand == 'type':
        ActionChains(driver) \
        .move_to_element(to_element=el) \
        .click() \
        .send_keys(value) \
        .perform()
        print("Typed")

    elif commmand == 'click':
        ActionChains(driver) \
        .move_to_element(to_element=el) \
        .click() \
        .perform()
        print("Clicked")

options = webdriver.FirefoxOptions()
options.add_argument("--headless")
options.set_preference("browser.link.open_newwindow", 1)
driver = webdriver.Firefox(options=options)

def get_website(URL):
    driver.get(URL)

system_prompt = """You are an automation helper to navigate web pages to fulfill tasks. You will be provided a prompt with a request for information and the html and image of a web page.
If the requested information is on the page, output a string "stop". If the user must navigate the page to access the information, output a json array of navigation commands. Each navigation command must include the following keys:
 - "command": either "click" or "type".
 - "elementidentification": use this space as a scratch pad to help you choose your target and target-type. In this space, identify what element you want to select in the HTML by providing the exact element you need, verbatim.
 - "fieldselection": use this space as a scratch pad to help you choose the field inside your target that you want to identify. Make sure that this is a field which identifies only one element.
 - "fieldvalue": use this space as a scratch pad to lay out the value of the field chosen in the "fieldselection" section. This will help you create your xpath.
 - "target": Assemble the "fieldselction" and "fieldvalue" values into a valid xpath or css identifier. Make sure xpath and css identifiers are precise. Never enter anything into a hidden field.
 - "target-type": either "CSS" or "XPATH"
 - "value": string containing value to be entered.
Do not generate markdown, headers or explanations. Do not generate anything other than json navigation command array, or "stop"."""

def navigate_around_current_website(user_prompt):
    messages = []
    print(f"Recieved website call: {user_prompt}")
    pageno=1
    while(True):
        time.sleep(1)
        driver.save_full_page_screenshot(str(f"page_{pageno}.png"))
        print(f"Took screenshot: page_{pageno}.png")
        take_full_page_png("result.png")
        with open(f'page_{pageno}.html', 'wt', encoding='utf-8') as pgsrc:
            page_html = driver.page_source
            pgsrc.write(page_html)

        user_input = user_prompt + page_html
        # user_input = "Locate tax account with account number A74963." + page_html
        print("User prompt assembled")
        response = gpt_interactor.run_query(gpt_model="gpt-4o-mini", system_text=system_prompt, user_prompt=user_input, image_fname=str(f"page_{pageno}.png"), messages=messages, returnmessages=True)
        resp = response[0]
        messages = response[1]
        with open(f'page_{pageno}.json', 'wt', encoding='utf-8') as f:
            f.write(resp)
        print(f"GPT Responded in page_{pageno}.json")
        if "stop" in resp:
            print(f"Success recieved. Pulling out")
            take_full_page_png("result.png")
            break
        python_code = False
        if resp.startswith("```json"):
            resp = resp[7:]
        if resp.startswith("```python"):
            resp = resp[9:]
            python_code = True
        if resp.endswith("```"):
            resp = resp[:-3]
        print(f"Removed header/footer. Response: {resp}")
        if python_code:
            exec(resp)
            exec("nav(driver)")
        else:
            cmds = json.loads(resp)
            if not isinstance(cmds, list):
                cmds = [cmds]
            for cmd in cmds:
                if "command" not in cmd:
                    return
                print(f"Executed Command: {str(cmd)}")
                execute_selenium_command(driver, cmd['command'], cmd['target'], cmd['target-type'], cmd['value'] if 'value' in cmd else "")

        pageno += 1

def take_full_page_png(name):
    total_height = driver.execute_script("return document.body.scrollHeight")
    total_width = driver.execute_script("return document.body.scrollWidth")

    driver.set_window_size(total_width, total_height)
    time.sleep(5)
    driver.save_screenshot(name)
    if name == "result.png":
        shutil.copy("result.png", "static/result.png")

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
    get_website("https://montvillenj.org/243/Pay-For-Property-Tax")
    navigate_around_current_website("Click on 'Tax Account Look Up' link")