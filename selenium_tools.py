from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Type, List
from pydantic.v1 import BaseModel, Field, AnyHttpUrl
import os
import json

def DEFAULT_WAIT_TIME():
    return 100000

def login_linkedin(username, password, driver, bypassCookie=False):
    # sometimes we have cookie issues and you can bypass
    if bypassCookie == False:
        # Check if the cookies file exists
        if os.path.isfile('cookies.json'):
            # Load the saved cookies
            driver.get("https://www.linkedin.com/login")
            with open('cookies.json', 'r') as f:
                cookie_json = json.load(f)
                for line in cookie_json['cookies']:
                    driver.add_cookie(line)

            # Refresh the page to apply the cookies
            driver.get("https://www.linkedin.com/feed/")

            # Wait for the home link to detect a successful login
            wait = WebDriverWait(driver, DEFAULT_WAIT_TIME())
            try:
                home_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.app-aware-link.global-nav__primary-link--active.global-nav__primary-link[href='https://www.linkedin.com/feed/?doFeedRefresh=true&nis=true&']")))
                print("Login successful using saved cookies.")
                return
            except:
                print("Login failed using saved cookies. Proceeding with login process.")

    # Navigate to the login page
    driver.get("https://www.linkedin.com/login")

    # Find the username/email input element
    username_input = driver.find_element(By.ID, "username")

    # Find the password input element
    password_input = driver.find_element(By.ID, "password")

    # Find the login button element
    login_button = driver.find_element(By.CSS_SELECTOR, "button.btn__primary--large.from__button--floating")

    # Enter the username and password
    username_input.send_keys(username)
    password_input.send_keys(password)

    # Click the login button
    login_button.click()

    # Wait for the home link to detect a successful login
    wait = WebDriverWait(driver, DEFAULT_WAIT_TIME())
    home_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.app-aware-link.global-nav__primary-link--active.global-nav__primary-link[href='https://www.linkedin.com/feed/?doFeedRefresh=true&nis=true&']")))

    # Save the cookies to a file
    cookies = driver.get_cookies()
    with open('cookies.json', 'w') as f:
        print("Saving cookies to file...")
        print(cookies)
        cookie_json = {
            "cookies": []
        }
        for cookie in cookies:
            cookie_data = {
                'domain': cookie['domain'],
                'httpOnly': cookie['httpOnly'],
                'name': cookie['name'],
                'path': '/',
                'secure': cookie['secure'],
                'value': cookie['value']
            }
            if 'expiry' in cookie:
                cookie_data['expiry'] = cookie['expiry']
            if 'sameSite' in cookie:
                cookie_data['sameSite'] = cookie['sameSite']
            cookie_json['cookies'].append(cookie_data)
        f.write(json.dumps(cookie_json)) 

    print("Login successful.")



class SearchResult(BaseModel):
    first_name: str
    last_name: str
    description: str
    location: str
    profile_link: str

    def to_str(self):
        return f"""
        First Name: {self.first_name} Last Name: {self.last_name}
        Description: {self.description}
        Location: {self.location}
        profile_link: {self.profile_link}
        """

def search_url (firstName: str, lastName: str) -> str:
    return f"https://www.linkedin.com/search/results/people/?keywords={firstName}%20{lastName}&origin=SWITCH_SEARCH_VERTICAL&sid=%3Alt"
    # https://www.linkedin.com/search/results/people/?keywords=joseph%20remo&origin=SPELL_CHECK_NO_RESULTS&spellCorrectionEnabled=false

def extract_results_from_page(search_result_containers):
    search_results_page = []
    for search_result in search_result_containers:
        try:
            first_name = search_result.find_element(By.CSS_SELECTOR, "span.entity-result__title-text > a > span:nth-child(1)").text.split(' ')[0]
            last_name = search_result.find_element(By.CSS_SELECTOR, "span.entity-result__title-text > a > span:nth-child(1)").text.split(' ')[1]
            description = search_result.find_element(By.CSS_SELECTOR, "div.entity-result__primary-subtitle").text
            location = search_result.find_element(By.CSS_SELECTOR, "div.entity-result__secondary-subtitle").text
            profile_link = search_result.find_element(By.CSS_SELECTOR, "a.app-aware-link").get_attribute("href")
            search_results_page.append(SearchResult(
            first_name=first_name,
            last_name=last_name,
            description=description,
            location=location,
            profile_link=profile_link))
        except Exception as e:
            print(f"Error extracting data from search result container: {e}")
            pass

    return search_results_page

def get_search_results(url: str, driver, num_pages=1) -> list[list[SearchResult]]:
    # Navigate to the LinkedIn search results page
    driver.get(url)
    # Wait for the search results to load
    wait = WebDriverWait(driver, DEFAULT_WAIT_TIME())
    search_results_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search-results-container")))
    results_pages = []
    # Extract the data for each search result
    search_result_containers = search_results_container.find_elements(By.CSS_SELECTOR, "li.reusable-search__result-container") # page 1
    results_pages.append(extract_results_from_page(search_result_containers))

    print(f"first page extracted, {len(results_pages)} pages, {len(results_pages[0])} results")

    # Navigate to the next N number of pages
    # current_page = 1
    

    # print('do we go to the next page? ' + current_page + '/' + num_pages)
    # while current_page < num_pages:
    #     # Check if there is a next page
    #     print('going to next page', current_page)
    #     try:
    #         next_page_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.artdeco-pagination__button--next")))

    #         if next_page_button.is_enabled():
    #             next_page_button.click()
    #             current_page += 1
    #             search_result_containers = search_results_container.find_elements(By.CSS_SELECTOR, "li.reusable-search__result-container")
    #             print('extracting page: ' + current_page)
    #             results_pages.append(extract_results_from_page(search_result_containers))
    #             print("pages extracted: " + len(results_pages))
    #             next_page_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.artdeco-pagination__button--next")))

    #         else:
    #             break
    #     except Exception as e:
    #         print(f"Error extracting from or switching pages: {e}")
    #         pass
    # return results pages
    return results_pages


    