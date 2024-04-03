from crewai import Task, Agent, Crew
from linkedin_search import LinkedinAccountDetailsTool, LinkedinAccountSearch
from selenium import webdriver
from selenium_tools import login_linkedin
import os
# agent setup 

# activate web driver
driver = webdriver.Chrome()

username =  os.environ["LINKEDIN_USERNAME"]
password =  os.environ["LINKEDIN_PASSWORD"]

# local ollama testing to reduce testing costs
os.environ["OPENAI_API_BASE"] = 'http://localhost:11434/v1'
os.environ["OPENAI_MODEL_NAME"] = 'mistral:instruct'

# login to linkdin 
login_linkedin(username=username, password=password, driver=driver, bypassCookie=False)

account_search = LinkedinAccountSearch(selenium_webdriver=driver)
account_details_scraper = LinkedinAccountDetailsTool(selenium_webdriver=driver)


LinkedinSearch_agent = Agent(
        role="Linkdin researcher",
        goal="Identify Linkein profiles based on search critera and extract relevant information",
        backstory="""
        You are an expert linkedin researcher with experience identifying profiles and extracting relevant information.
        you are great at searching through a list of profiles to find the most relevent ones based on the search criteria.
        Your tools allow you to easily search LinkedIn for a list of accounts and that search through specific accounts to get the full details
        you do not make assumptions only rely on data from your tools. 
        """,
        tools=[account_search, account_details_scraper],
        verbose=True,
        allow_delegation=False
    )

# test tasks setup
find_all_john_smiths = Task(
    description="Search for 'John Smith' on Linkedin and get top 5 profiles",
    expected_output="A json containing top 5 Linkedin profiles for 'John Smith'",
    output_file="./test_output/john_smiths_list.json",
    agent=LinkedinSearch_agent
)

search_for_daniel_task = Task(
    description="Search for Daniel Steigman web3 software engineer on Linkedin and get his account details",
    expected_output="A json containing Daniel Steigman's Linkedin profile details",
    output_file="./test_output/daniel_details.json",
    agent=LinkedinSearch_agent
)

# run test tasks

test_crew = Crew(
    agents=[LinkedinSearch_agent],
    tasks=[ search_for_daniel_task],
    verbose=2
)

test_crew.kickoff()