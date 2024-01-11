#!/usr/bin/env python
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import Select
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.edge.service import Service
from datetime import datetime
import re

caching_Data = []

def reg_log(string):
    try:
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        with open("log.txt", 'a') as file:
            file.write(formatted_datetime + "::" + string + '\n')
    except Exception as e:
        print(f"Error: {e}")

def log_in(driver, username, password):
    try:
        url = 'https://frontier.flica.net/ui/public/login/index.html'
        driver.get(url)
        
        wait = WebDriverWait(driver, 3)
        
        username_field = wait.until(EC.presence_of_element_located((By.NAME, 'UserId')))
        username_field.send_keys(username)
        
        password_field = driver.find_element(By.NAME, 'Password')
        password_field.send_keys(password)
        
        remember_me = driver.find_element(By.NAME, 'RememberMe')
        driver.execute_script("arguments[0].click()", remember_me)
        
        submit = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]')))
        submit.click()
        reg_log("log_in Success!\n")
    except Exception as e:
        reg_log("log_in Error!\n")

def log_out(driver):
    driver.switch_to.default_content()
    wait = WebDriverWait(driver, 3)
    
    try:
        sign_out = wait.until(EC.element_to_be_clickable((By.XPATH, '(//a[@id="logoutBtn"])[1]')))
        driver.execute_script("arguments[0].click()", sign_out)
    except TimeoutException:
        reg_log("Timed out waiting for logout button. Exiting...")
    except NoSuchElementException:
        reg_log("Logout button not found. Exiting...")

def pilot_daily_opentime_live_ca(driver, is_enabled):
    if not is_enabled:
        return
    
    # pilot_daily_opentime_live_ca_url = 'https://frontier.flica.net/full/otframe.cgi?BCID=018.000'
    pilot_daily_opentime_live_ca_url = 'https://frontier.flica.net/full/otframe.cgi?BCID=005.224'
    
    driver.get(pilot_daily_opentime_live_ca_url)
    
    wait = WebDriverWait(driver, 3)
    iframe_switch = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'MainFrame')))
    
    previous_element = None

    iframe_items = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'tabFrame')))

    while True:
        items_added = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//table[@id="reqTable"]//tbody//tr')))

        for item in items_added:
            td_items = item.find_elements(By.TAG_NAME, 'td')
            reg_log(td_items[1].text)

        break
    reg_log("\n")
    driver.switch_to.default_content()
    iframe_switch = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'MainFrame')))

    click_opentime = wait.until(EC.element_to_be_clickable((By.ID, 'tabOpentime')))
    driver.execute_script("arguments[0].click()", click_opentime)

    iframe_items = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'tabFrame')))

    while True:
        try:
            select = Select(wait.until(EC.element_to_be_clickable((By.ID, "ccList"))))
            select.select_by_value("B3C")
            select = Select(wait.until(EC.element_to_be_clickable((By.ID, "ccList"))))
            select.select_by_value("M3C")
            while True:
                try:
                    items_to_add = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//table[@class="otpottable"]//tr[@bgcolor="WHITE"]')))

                    if len(items_to_add) != 0:
                        reg_log("Exist Open time!")        
                        for item in items_to_add:
                            td_items = item.find_elements(By.TAG_NAME, 'td')
                            _pairing = td_items[0].text
                            _date = re.sub(r"\s+", "", td_items[1].text)
                            _credit = td_items[7].text
                            _time = td_items[8].text
                            reg_log(f"date: {_date}, credit: {_credit}, time: {_time}")
                            reg_log(f"Add booked option to cache - {_pairing}:{_date}")

                        # driver.switch_to.default_content()

                        # iframe_switch = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'MainFrame')))

                        # click_add = wait.until(EC.element_to_be_clickable((By.ID, 'btnAdd')))
                        # driver.execute_script("arguments[0].click()", click_add)

                        # _adds = wait.until(EC.element_to_be_clickable((By.ID, 'btnAdd')))
                        # driver.execute_script("arguments[0].click()", _adds)

                        # submit_request = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Submit Request"]')))
                        # driver.execute_script("arguments[0].click()", submit_request)

                        break  # Exit the loop after interacting with a new element

                except StaleElementReferenceException:
                    # Handling StaleElementReferenceException to avoid script crash
                    reg_log("Stale Element Reference Exception. Retrying...\n")
                    break  # Break out of the loop and retry the entire process

                except Exception as e:
                    reg_log(f"Error: No Opentime")
                    reg_log("Retrying...\n")
                    break  # Break out of the loop and retry the entire process

        except Exception as e:
            reg_log(f"Error: {str(e)}")
            reg_log("Restarting the script...\n")
            continue  # Restart the script in case of an exception


# def pilot_daily_opentime_live_ca(driver, is_enabled):
#     reg_log("Login successful")
#     if not is_enabled:
#         return

#     # params
#     params = {
#         "date":"21DEC",
#         "credit": "0500",
#         "time": None
#     }
#     pilot_daily_opentime_live_ca_url = 'https://frontier.flica.net/full/otframe.cgi?BCID=018.000'
#     # pilot_daily_opentime_live_ca_url = 'https://frontier.flica.net/full/otframe.cgi?BCID=005.224'
#     driver.get(pilot_daily_opentime_live_ca_url)

#     while True:
#         try:
#             # Remove the following line to navigate explicitly to the Open Time page

#             wait = WebDriverWait(driver, 3)
#             driver.switch_to.default_content()
#             iframe_switch = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'MainFrame')))

#             click_opentime = wait.until(EC.element_to_be_clickable((By.ID, 'tabOpentime')))
#             driver.execute_script("arguments[0].click()", click_opentime)

#             iframe_items = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'tabFrame')))
#             time.sleep(0.5)

#             items_to_add = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//table[@class="otpottable"]//tr[@bgcolor="WHITE"]')))

#             pairs = []
#             for item in items_to_add:
#                 td_items = item.find_elements(By.TAG_NAME, 'td')
#                 _date = td_items[1].text
#                 _credit = td_items[7].text
#                 _time = td_items[8].text

#                 print("date:", _date)
#                 print("credit:", _credit)
#                 print("time:", params["time"].find(_time))

#                 if params["date"] != None and _date.strip().find(params["date"].strip()) == -1: continue
#                 if params["credit"] != None and _credit.strip().find(params["credit"].strip()) == -1: continue
#                 if params["time"] != None and _time.strip().find(params["time"].strip()) == -1: continue

#                 _pairing = td_items[0].find_element(By.TAG_NAME, 'u').text

#                 pairs.append(_pairing)

#             driver.switch_to.default_content()
#             iframe_switch = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'MainFrame')))
#             click_add = wait.until(EC.element_to_be_clickable((By.ID, 'btnAdd')))
#             driver.execute_script("arguments[0].click()", click_add)

#             driver.switch_to.default_content()
#             wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'MainFrame')))

#             previous_element = None
#             for pair in pairs:

#                 print(f'pairing: {pair}')
#                 if item != previous_element:
#                     time.sleep(1)

#                 while True:
#                     try:
#                         _add = wait.until(EC.element_to_be_clickable((By.XPATH, f'//table//a[@id="PC_{pair}"]//ancestor::tr[@bgcolor="WHITE"]//input[@id="btnAdd"]')))
#                         driver.execute_script("arguments[0].click()", _add)
#                         time.sleep(0.5)
#                         print(f"clicked add {pair}")
#                         break

#                     except Exception as e:
#                         print(f"Error: {str(e)}")
#                         print("Retrying....")

#                         select = Select(wait.until(EC.element_to_be_clickable((By.ID, "ccList"))))
#                         select.select_by_value("A3C")
#                         time.sleep(1)
#                         select = Select(wait.until(EC.element_to_be_clickable((By.ID, "ccList"))))
#                         select.select_by_value("M3C")
#                         time.sleep(1)

#                         continue

#                 time.sleep(3)

#                 submit_request = wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@value="Submit Request"]')))
#                 driver.execute_script("arguments[0].click()", submit_request)
#                 print("Submited")
#                 break  # Exit the loop after interacting with a new element

#         except StaleElementReferenceException:
#             # Handling StaleElementReferenceException to avoid script crash
#             print("Stale Element Reference Exception. Retrying...")
#             continue  # Continue to the next iteration of the outer loop
        
#         except TimeoutException:
#             print("Stale Element Reference Exception. Retrying...")
#             continue  # Continue to the next iteration of the outer loop

#         except Exception as e:
#             print(f"Error: {str(e)}")
#             print("Retrying...")
#             continue  # Continue to the next iteration of the outer loop


def main():
    username = 'fft425207'
    password = 'Crj200fo!!'
    is_enabled = True
    
    # Add Chrome options
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-animations")

    reg_log("\n Scripting Start!\n")
    
    while True:
        chrome_service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=chrome_service, options=options)
        
        try:
            log_in(driver, username, password)
            time.sleep(1)
            pilot_daily_opentime_live_ca(driver, is_enabled)
            time.sleep(2)
        
        except Exception as e:
            reg_log(f"Error: {str(e)}")
            reg_log("Restarting the script...")
        
        finally:
            # Ensure to log out and quit the driver
            log_out(driver)
            driver.quit()

if __name__ == "__main__":
    main()