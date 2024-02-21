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

# Conditional Options
cond_opt = {
    "Start_Dates":"20FEB",
    "End_Dates":"05MAR", # JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OPT, NOV, DEC
    "Days": 5,
    "Start_Report": "00:00",
    "End_Report": "23:59",
    "Start_Arrive": "00:00",
    "End_Arrive": "23:59",
    "Credit": 2000
}



def reg_log(string):
    try:
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        with open("log.txt", 'a') as file:
            file.write(formatted_datetime + "::" + string + '\n')
    except Exception as e:
        print(f"Error: {e}")

def from_str_to_date(date_str):
    date_format = "%d%b"
    date_obj = datetime.strptime(date_str, date_format)
    return date_obj

def from_str_to_time(time_str):
    time_format = "%H:%M"
    time_obj = datetime.strptime(time_str, time_format).time()
    return time_obj

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
    
    pilot_daily_opentime_live_ca_url = 'https://frontier.flica.net/full/otframe.cgi?BCID=004.225'
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

                    if items_to_add is not None:
                        for item in items_to_add:
                            td_items = item.find_elements(By.TAG_NAME, 'td')

                            _pairing = td_items[1].text
                            _dates = td_items[2].text
                            _days = td_items[3].text
                            _report = td_items[4].text
                            _depart = td_items[5].text
                            _arrive = td_items[6].text
                            _credit = td_items[8].text
                            _date = re.sub(r"\s+", "", td_items[2].text)

                            cur_book_time = f"{_pairing}:{_date}"

                            if cur_book_time not in alreadyBookedOptions:
                                alreadyBookedOptions.append(cur_book_time)
                                if cond_opt["Start_Dates"] != "" and from_str_to_date(cond_opt["Start_Dates"]) > from_str_to_date(_date):
                                    break
                                elif cond_opt["End_Dates"] != "" and from_str_to_date(cond_opt["End_Dates"]) < from_str_to_date(_date):
                                    break
                                elif cond_opt["Start_Arrive"] != "" and from_str_to_time(cond_opt["Start_Arrive"]) > from_str_to_time(_arrive):
                                    break
                                elif cond_opt["End_Arrive"] != "" and from_str_to_time(cond_opt["End_Arrive"]) < from_str_to_time(_arrive):
                                    break
                                elif cond_opt["Start_Report"] != "" and from_str_to_time(cond_opt["Start_Report"]) > from_str_to_time(_report):
                                    break
                                elif cond_opt["End_Report"] != "" and from_str_to_time(cond_opt["End_Report"]) < from_str_to_time(_report):
                                    break
                                elif int(cond_opt["Days"]) < int(_days):
                                    break
                                elif int(cond_opt["Credit"]) < int(_credit):
                                    break
                                else:
                                    print(f'Pairing: {_pairing}, Dates: {_dates}, Days: {_days}, Report: {_report}, Depart: {_depart}, Arrive: {_arrive}, Credit: {_credit}')
                                    reg_log(f"Add booked option to cache - {_pairing}:{_date}")
                                    _adds = td_items[0].find_element(By.ID, 'btnAdd')
                                    _adds.click()
                                    # Assuming you want to submit the request after clicking the "Add" button
                                    # submit_request = driver.find_element(By.XPATH, '//input[@value="Submit Request"]')
                                    # submit_request.click()
                                    break
                            else:
                                break
                            
                        break  # Exit the loop after interacting with a new element
                    else:
                        print("No Opentimes else")
                        break

                except StaleElementReferenceException:
                    # Handling StaleElementReferenceException to avoid script crash
                    reg_log("Stale Element Reference Exception. Retrying...\n")
                    break  # Break out of the loop and retry the entire process

                except Exception as e:
                    reg_log(f"Error: {e}")
                    reg_log("Retrying...\n")
                    break  # Break out of the loop and retry the entire process

        except Exception as e:
            reg_log(f"Error: {str(e)}")
            reg_log("pilot_daily_opentime_live_ca Error! \n Restarting the script...\n")
            break  # Restart the script in case of an exception

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
    
    retry_limit = 5
    retry_count = 0

    while retry_count < retry_limit:
        try:
            chrome_service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=chrome_service, options=options)
            log_in(driver, username, password)
            time.sleep(1)
            pilot_daily_opentime_live_ca(driver, is_enabled)
            time.sleep(1)
        
        except NoSuchElementException as e:
            reg_log(f"Element not found: {str(e)}")
            reg_log("No Such Element Exception. Restarting the script...")
            retry_count += 1
            continue
        
        except Exception as e:
            reg_log(f"Error: {str(e)}")
            reg_log("Error: {e} \n Restarting the script...")
            retry_count += 1
            continue
        
        finally:
            log_out(driver)
            driver.quit()

    if retry_count == retry_limit:
        reg_log("Maximum retry limit reached. Exiting the script.")

if __name__ == "__main__":
    main()