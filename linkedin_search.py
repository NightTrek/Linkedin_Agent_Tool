from crewai_tools import BaseTool
from selenium.webdriver import Chrome, Firefox, ChromiumEdge, Safari, Edge
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Type, List
from pydantic.v1 import BaseModel, Field, AnyHttpUrl
from selenium_tools import DEFAULT_WAIT_TIME, search_url, get_search_results, LinkedinAccountDetails
import json
import sys

class LinkedinAccountSearchSchema(BaseModel):
	"""Input for Account search tool."""
	fullName: str = Field(..., description="Mandatory query with the first name and last name separated by a space")


class LinkedinAccountSearch(BaseTool):
    name: str = "Linkedin Account Search Tool"
    description: str = "Searches for Linkedin accounts by first name and last name"
    # args_schema: LinkedinAccountSearchSchema = LinkedinAccountSearchSchema()
    args_schema: Type[BaseModel] = LinkedinAccountSearchSchema

    default_page_count: str = 1
    selenium_webdriver: Chrome | Firefox | ChromiumEdge | Safari | Edge
    
    class Config:
            arbitrary_types_allowed = True

    def _run(self, fullName: str) -> str:
        # Implementation goes here
        # use tsarsier to search for the customer name here
        # https://www.linkedin.com/search/results/people/?keywords=joseph%20remio&origin=SWITCH_SEARCH_VERTICAL&sid=%3Alt
        fullName = fullName.split(" ")
        if len(fullName) == 2:
            firstName = fullName[0]
            lastName = fullName[1]
            url = search_url(firstName, lastName)
            search_results = get_search_results(url,self.selenium_webdriver,  self.default_page_count)
            str_output = ""
            for page in search_results:
                 for row in page:
                      str_output += row.to_str()
            return str_output
        
        elif len(fullName) == 3 & len(fullName[1]) <= 2:
            firstName = fullName[0]
            lastName = fullName[2]
            url = search_url(firstName, lastName)
            search_results = get_search_results(url,self.selenium_webdriver,  self.default_page_count)
            str_output = ""
            for page in search_results:
                 for row in page:
                      str_output += row.to_json()
            return str_output
        else:
            return "Invalid input Argument should be in the format of \"first_name last_name\" seperated by a space no aditional arguments"




class LinkedinAccountDetailsTool(BaseModel):
    """Input for LinkedinAccountDetails Tool"""
    profile_url: str = Field(..., description="Mandatory query with the first name and last name separated by a space")


class LinkedinAccountDetailsTool(BaseTool):
    name: str = "Linkedin Account Details Tool"
    description: str = "Scrapes details from a Linkedin profile_url an returns them"
    args_schema: Type[BaseModel] = LinkedinAccountDetailsTool
    selenium_webdriver: Chrome | Firefox | ChromiumEdge | Safari | Edge
    
    class Config:
            arbitrary_types_allowed = True

    def _run(self, profile_url: str) -> str:
        # Initialize the webdriver 
        driver = self.selenium_webdriver

        # Navigate to the LinkedIn profile page
        driver.get(profile_url)

        # Wait for the profile page to load
        wait = WebDriverWait(driver, DEFAULT_WAIT_TIME())
        try:
            profile_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "scaffold-layout__main")))

            # Extract the account details using the LinkedinAccountDetails class
            account_details = LinkedinAccountDetails.from_dom(profile_container)
            print(account_details.to_json_str())
            return account_details.to_json_str()
        except Exception as e:
            print(f"Error extract Linkedin Account details: {e}")
            sys.exit("Intentionally exiting the program")
        