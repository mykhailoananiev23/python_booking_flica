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

alreadyBookedOptions = []

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
    
    pilot_daily_opentime_live_ca_url = 'https://frontier.flica.net/full/otframe.cgi?BCID=018.000'
    # pilot_daily_opentime_live_ca_url = 'https://frontier.flica.net/full/otframe.cgi?BCID=005.224'
    
    driver.get(pilot_daily_opentime_live_ca_url)
    
    wait = WebDriverWait(driver, 3)
    iframe_switch = wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'MainFrame')))

    click_add = wait.until(EC.element_to_be_clickable((By.ID, 'btnAdd')))
    driver.execute_script("arguments[0].click()", click_add)

    while True:
        try:
            select = Select(wait.until(EC.element_to_be_clickable((By.ID, "ccList"))))
            select.select_by_value("B3C")
            select = Select(wait.until(EC.element_to_be_clickable((By.ID, "ccList"))))
            select.select_by_value("M3C")
            while True:
                try:
                    items_to_add = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//table[@class="otpottable"]//tr[@bgcolor="WHITE"]')))

                    if items_to_add:
                        for item in items_to_add:
                            td_items = item.find_elements(By.TAG_NAME, 'td')

                            _pairing = td_items[1].text
                            _date = re.sub(r"\s+", "", td_items[2].text)

                            cur_book_time = f"{_pairing}:{_date}"

                            if cur_book_time not in alreadyBookedOptions:
                                alreadyBookedOptions.append(cur_book_time)
                                reg_log(f"Add booked option to cache - {_pairing}:{_date}")
                                _adds = td_items[0].find_element(By.ID, 'btnAdd')
                                _adds.click()
                                # Assuming you want to submit the request after clicking the "Add" button
                                # submit_request = driver.find_element(By.XPATH, '//input[@value="Submit Request"]')
                                # submit_request.click()
                                break
                            
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
            continue
        
        finally:
            # Ensure to log out and quit the driver
            log_out(driver)
            driver.quit()

if __name__ == "__main__":
    main()