from crewai_tools import BaseTool
from selenium.webdriver import Chrome, Firefox, ChromiumEdge, Safari, Edge
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Type, List
from pydantic.v1 import BaseModel, Field, AnyHttpUrl
from selenium_tools import login_linkedin, DEFAULT_WAIT_TIME, search_url, get_search_results
import json


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

            return "\n".join([result.to_str() for result in search_results])
        
        elif len(fullName) == 3 & len(fullName[1]) <= 2:
            firstName = fullName[0]
            lastName = fullName[2]
            url = search_url(firstName, lastName)
            search_results = get_search_results(url,self.selenium_webdriver,  self.default_page_count)

            return "\n".join([result.to_str() for result in search_results])
        else:
            return "Invalid input Argument should be in the format of \"first_name last_name\" seperated by a space no aditional arguments"


# Account details tool

class LinkedinActivity(BaseModel):
    reposted_by: str
    reposted_at: str
    title: str
    description: str
    source: str
    read_time: str
    reactions_count: int
    comments_count: int
    profile_url: AnyHttpUrl

class LinkedinExperience(BaseModel):
    job_title: str
    company_name: str
    employment_type: str
    start_date: str
    end_date: str
    location: str
    achievements: str
    product_links: list[AnyHttpUrl]

class LinkedinEducation(BaseModel):
    school_name: str
    degree: str
    grade: str
    activities_and_societies: str
    achievements: str
    project_link: AnyHttpUrl | None

class LinkedinAccountDetails(BaseModel):
    fullName: str
    tagline: str
    aboutSectionTxt: str
    followers: str
    activity: List[LinkedinActivity]
    experience: List[LinkedinExperience]
    education: List[LinkedinEducation]

    @classmethod
    def from_dom(cls, dom_element: str) -> 'LinkedinAccountDetails':
        # Parse the DOM element and extract the relevant information
        fullName = dom_element.find('.text-heading-xlarge').text.strip()
        tagline = dom_element.find('.text-body-medium').text.strip()
        aboutSectionTxt = dom_element.find('.IguNbNhRGdpQVIAecwUdxtZFuavNRBlrNTU').text.strip()
        followers = dom_element.find('.link-without-visited-state').text.strip()

        activity = []
        for activity_element in dom_element.find_all('.profile-creator-shared-feed-update__mini-update'):
            reposted_by = activity_element.find('.feed-mini-update-contextual-description__text').text.strip()
            reposted_at = activity_element.find('.feed-mini-update-contextual-description__text').text.strip()
            title = activity_element.find('.feed-mini-update-content__single-line-text').text.strip()
            description = activity_element.find('.IguNbNhRGdpQVIAecwUdxtZFuavNRBlrNTU').text.strip()
            source = activity_element.find('.feed-mini-update-content__single-line-text').text.strip()
            read_time = activity_element.find('.feed-mini-update-content__single-line-text').text.strip()
            reactions_count = int(activity_element.find('.social-details-social-counts__reactions-count').text.strip())
            comments_count = int(activity_element.find('.social-details-social-counts__comments').text.strip())
            profile_url = activity_element.find('.app-aware-link').get('href')
            activity.append(LinkedinActivity(
                reposted_by=reposted_by,
                reposted_at=reposted_at,
                title=title,
                description=description,
                source=source,
                read_time=read_time,
                reactions_count=reactions_count,
                comments_count=comments_count,
                profile_url=profile_url
            ))

        experience = []
        for experience_element in dom_element.find_all('.mjEVNJWXfAkXKyoszmIwMBjrzgkKLuAW'):
            job_title = experience_element.find('.display-flex .t-bold').text.strip()
            company_name = experience_element.find('.t-14.t-normal').text.split('·')[0].strip()
            employment_type = experience_element.find('.t-14.t-normal').text.split('·')[1].strip()
            start_date = experience_element.find_all('.t-14.t-normal.t-black--light')[0].text.strip()
            end_date = experience_element.find_all('.t-14.t-normal.t-black--light')[1].text.strip()
            location = experience_element.find_all('.t-14.t-normal.t-black--light')[2].text.strip()
            achievements = experience_element.find('.IguNbNhRGdpQVIAecwUdxtZFuavNRBlrNTU').text.strip()
            product_links = [link.get('href') for link in experience_element.find_all('a', {'data-field': 'experience_media'})]
            experience.append(LinkedinExperience(
                job_title=job_title,
                company_name=company_name,
                employment_type=employment_type,
                start_date=start_date,
                end_date=end_date,
                location=location,
                achievements=achievements,
                product_links=product_links
            ))

        education = []
        for education_element in dom_element.find_all('.mjEVNJWXfAkXKyoszmIwMBjrzgkKLuAW'):
            school_name = education_element.find('.display-flex .t-bold').text.strip()
            degree = education_element.find('.t-14.t-normal').text.strip()
            grade = education_element.find('.pv-shared-text-with-see-more').text.strip()
            activities_and_societies = education_element.find_all('.pv-shared-text-with-see-more')[1].text.strip()
            achievements = '\n'.join([x.strip() for x in education_element.find_all('.pv-shared-text-with-see-more')[2].text.split('\n')])
            project_link = education_element.find('a', {'class': 'optional-action-target-wrapper'}).get('href') if education_element.find('a', {'class': 'optional-action-target-wrapper'}) else None
            education.append(LinkedinEducation(
                school_name=school_name,
                degree=degree,
                grade=grade,
                activities_and_societies=activities_and_societies,
                achievements=achievements,
                project_link=project_link
            ))

        return cls(
            fullName=fullName,
            tagline=tagline,
            aboutSectionTxt=aboutSectionTxt,
            followers=followers,
            activity=activity,
            experience=experience,
            education=education
        )

    def to_json_str(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)



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
        profile_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "scaffold-layout__main")))

        # Extract the account details using the LinkedinAccountDetails class
        account_details = LinkedinAccountDetails.from_dom(profile_container.get_attribute('outerHTML'))

        # Close the webdriver
        driver.quit()

        return account_details.to_json_str()