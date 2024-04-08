from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import NoSuchElementException, TimeoutException
import re
from web_extractor import extract_data_from_html_str




from typing import Optional, List
from pydantic import BaseModel, AnyHttpUrl, AnyHttpUrl

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

# Extract the text from each child span
def extract_text_from_spans(element):
    text = ''
    for span in element:
        if span.text:
            text += span.text
    return text

def extract_text_and_attributes(element: WebElement) -> str:
    # Get the inner HTML of the element
    inner_html = element.get_attribute("innerHTML")

    # Remove all HTML tags except <a> tags using a regular expression
    text_content = re.sub(r'<(?!a\b)[^>]+>', '', inner_html)

    # Extract href and aria-label attributes from <a> tags
    text_content = re.sub(r'<a\b[^>]*\bhref="([^"]*)"[^>]*>([^<]*)</a>', r'\2 (\1)', text_content)
    text_content = re.sub(r'<a\b[^>]*\baria-label="([^"]*)"[^>]*>([^<]*)</a>', r'\2 (\1)', text_content)

    # Remove any remaining <a> tags without href or aria-label attributes
    text_content = re.sub(r'<a\b[^>]*>([^<]*)</a>', r'\1', text_content)

    # Remove leading/trailing whitespace and normalize whitespace
    text_content = ' '.join(text_content.split())

    return text_content

# ============================
# Account details tool

class LinkedinActivity(BaseModel):
    title: str
    description: str
    link: str
    reactions_count: str
    comments_count: str


def get_linkedin_activity_section(wait: WebDriverWait):
    """
    Extracts the activity section of the LinkedIn profile page
    :param WebDriverWait: The driver wait Object
    :return: The activity section of the LinkedIn profile page
    """
    activity = []
    try:
        activity_ID = wait.until(EC.presence_of_element_located((By.ID, 'content_collections')))
        activity_section_container = activity_ID.find_element(By.XPATH, '..')  # fetch the parent element
        followers = activity_section_container.find_elements(By.XPATH, './/span[@aria-hidden="true"]')[0].text.strip().split(' ')[0]
        activity_parts = activity_section_container.find_elements(By.CSS_SELECTOR, '.profile-creator-shared-feed-update__mini-container')

        for activity_part in activity_parts:
            title = ''
            description = ''
            link = ''
            reactions_count = ''
            comments_count = ''
            # first we need to check if this is a post or a comment or repost
            try:
                link_wrapper_element = activity_part.find_element(By.TAG_NAME, "a")
                link = link_wrapper_element.get_attribute("href")
                try:
                    title_element = activity_part.find_element(By.CSS_SELECTOR, '.feed-mini-update-content__single-line-text')

                    title = title_element.find_element(By.TAG_NAME, "strong").text.strip()
                except (NoSuchElementException, IndexError):
                    title = "N/A"
                try:

                    description_element = activity_part.find_element(By.CSS_SELECTOR, '.inline-show-more-text--is-collapsed')
                    description = extract_text_from_spans(description_element.find_elements(By.TAG_NAME, 'span'))
                except Exception as e:
                    print(f"desciption error: {e}")
                try:
                    reactions_element = activity_part.find_element(By.XPATH, './/span[@class="social-details-social-counts__reactions-count"]')
                    reactions_count = reactions_element.text.strip()
                except (NoSuchElementException, IndexError):
                    reactions_count = "N/A"

                try:
                    comments_element = activity_part.find_element(By.XPATH, './/button[@aria-label and contains(@class, "social-details-social-counts__comments")]')
                    comments_count = comments_element.text.strip().split(' ')[0]
                except (NoSuchElementException, IndexError):
                    comments_count = 'N/A'

                activity.append(LinkedinActivity(
                    title=title,
                    description=description,
                    link=link,
                    reactions_count=reactions_count,
                    comments_count=comments_count
                ))
            except:
                print("ERROR")
                pass
                # print(activity_part.get_attribute("innerHTML"))
        return {
            "followers": followers,
            "activity": activity
        }
    except TimeoutException:
        print("Selector ERROR: Timeout waiting for elements")
        return []



class LinkedinExperience(BaseModel):
    job_title: str
    company_name: str
    employment_type: str
    start_date: str
    end_date: str
    location: Optional[str]
    achievements: Optional[str]
    product_links: list[str]

class ExtractedExperience(BaseModel):
    results: list[LinkedinExperience]


def get_linkedin_experient_section(wait: WebDriverWait) -> List[LinkedinExperience]:
    """
    Extracts the experience section of the LinkedIn profile page
    :param WebDriverWait: The driver wait Object
    :return: The experience section of the LinkedIn profile page
    """
    try:
        experience_ID = wait.until(EC.presence_of_element_located((By.ID, 'experience')))
        experience_section = experience_ID.find_element(By.XPATH, '..') # section parent
        stringToExtract = extract_text_and_attributes(experience_section)
        extracted_output = extract_data_from_html_str(
            html=stringToExtract,
            pydantic_model=ExtractedExperience,
        )
        return extracted_output

    except Exception as e:
        print(f"Error extracting experience section: {e}")
        return []


class LinkedinEducation(BaseModel):
    school_name: str
    degree: str
    grade: Optional[str]
    activities_and_societies: Optional[str]
    achievements: Optional[str]
    project_link: Optional[str]

class ExtractedEducation(BaseModel):
    results: list[LinkedinEducation]


def get_linkedin_education_section(wait: WebDriverWait) -> List[LinkedinEducation]:
    """
    Extracts the education section of the LinkedIn profile page
    :param WebDriverWait: The driver wait Object
    :return: The education section of the LinkedIn profile page
    """
    try:
        education_ID = wait.until(EC.presence_of_element_located((By.ID, 'education')))
        education_section = education_ID.find_element(By.XPATH, '..') # section parent
        stringToExtract = extract_text_and_attributes(education_section)
        extracted_output = extract_data_from_html_str(
            html=stringToExtract,
            pydantic_model=ExtractedEducation,
        )
        return extracted_output
    except Exception as e:
        print(f"Error extracting education section: {e}")
        return []


class LinkedinAccountDetails(BaseModel):
    fullName: str
    tagline: str
    aboutSectionTxt: str
    followers: str
    activity: List[LinkedinActivity]
    experience: ExtractedExperience | None
    education: ExtractedEducation | None


    def to_json_str(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def get_linkedin_profile_title(wait: WebDriverWait) -> dict:
    """
    Extracts the title of the LinkedIn profile page
    :param profile_container: The profile container element
    :return: The title of the LinkedIn profile page
    """
    titleInfo = {}
    
    try:
        profile_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "scaffold-layout__main")))

        titleContainerElement = profile_container.find_elements(By.CSS_SELECTOR, '.ph5.pb5')[0]
        try:
            titleInfo["fullName"] = titleContainerElement.find_element(By.TAG_NAME, 'h1').text.strip()
        except (NoSuchElementException, IndexError):
            titleInfo["fullName"] = "Not Found"

        titleInfo["alt_text"] = titleContainerElement.find_element(By.CSS_SELECTOR, '.text-body-medium.break-words').text.strip()

        titleInfo['location'] = titleContainerElement.find_element(By.CSS_SELECTOR, '.text-body-small.inline.t-black--light.break-words').text.strip() if titleContainerElement.find_elements(By.CSS_SELECTOR, '.text-body-small.inline.t-black--light.break-words') else 'Not Found'
        return titleInfo
    except Exception as e:
        print(f"Error extracting LinkedIn profile title: {e}")


## TODO make sure this works for Linkedin profiles that do NOT have an about section
def get_linkedin_about_section(wait: WebDriverWait) -> str:
    """
    Extracts the about section of the LinkedIn profile page
    :param WebDriverWait: The driver wait Object
    :return: The about section of the LinkedIn profile page
    """
    try:
        about_ID = wait.until(EC.presence_of_element_located((By.ID, 'about')))
        about_section_container = about_ID.find_element(By.XPATH, '..') # fetch the parent element
        about_text_container = about_section_container.find_elements(By.XPATH, './/span[@aria-hidden="true"]')[1]

        about_text = about_text_container.text.strip()
    except TimeoutException:
        return "Selector ERROR: Timeout waiting for elements"
    except NoSuchElementException:
        return "Selector ERROR: No such element found"
    return about_text



def get_account_details(driver, profile_url: str) -> LinkedinAccountDetails:
        # Navigate to the LinkedIn profile page
        driver.get(profile_url)

        # Wait for the profile page to load
        wait = WebDriverWait(driver, DEFAULT_WAIT_TIME())
        try:
            # Extract the account details using the LinkedinAccountDetails class
            titleInfo = get_linkedin_profile_title(wait)
            aboutSectionTxt = get_linkedin_about_section(wait)
            activity = get_linkedin_activity_section(wait)
            
            experience = None
            education = None
            with ThreadPoolExecutor() as executor:
                future_experience = executor.submit(get_linkedin_experient_section, wait)
                future_education =  executor.submit(get_linkedin_education_section, wait)
                try:
                    experience = future_experience.result()
                except Exception as e:
                    print(f"Error extracting LinkedIn experience section: {e}")
                try:
                    education = future_education.result()
                except Exception as e:
                    print(f"Error extracting LinkedIn education section: {e}")
                    
            return LinkedinAccountDetails(
                fullName=titleInfo["fullName"],
                tagline=titleInfo["alt_text"],
                followers=activity["followers"],
                aboutSectionTxt=aboutSectionTxt,
                activity=activity["activity"],
                experience=experience,
                education=education
            )

        except Exception as e:
            print(f"Error extracting LinkedIn account details: {e}")
