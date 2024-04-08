from selenium import webdriver

from selenium_tools import login_linkedin, get_account_details,  ExtractedExperience
from web_extractor import extract_data_from_html_str

import os
from dotenv import load_dotenv
import asyncio
# Load environment variables from .env file
load_dotenv()


# activate web driver
driver = webdriver.Chrome()

username =  os.environ["LINKEDIN_USERNAME"]
password =  os.environ["LINKEDIN_PASSWORD"]

login_linkedin(username=username, password=password, driver=driver, bypassCookie=False)


# profile_url = "https://www.linkedin.com/in/jack-chitty-77484212a/" # he has the activity section before about
profile_url = "https://www.linkedin.com/in/albertski/"


response =  get_account_details(profile_url=profile_url, driver=driver)
print(response.model_dump_json(indent=2))