# Linkedin Agent Tool

A simple CrewAI tool giving agents access to search for accounts on LinkedIn and scrape account data for those found accounts. It uses LinkedIn's somewhat standardized structure to search for people on the platform and extract common profile fields like name, title, company, location, etc. Additionally, it looks for their experience, activity, and education. It gives CrewAI agents the ability to search for this information and perform name lookups.

## installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/Linkedin_Agent_Tool.git
   ```

2. Navigate to the project directory:
   ```
   cd Linkedin_Agent_Tool
   ```

3. Create a virtual environment (optional but recommended):
   ```
   python -m venv linkedin_agent-env
   ```

4. Activate the virtual environment:
   - For Windows:
     ```
     linkedin_agent-env\Scripts\activate
     ```
   - For macOS and Linux:
     ```
     source linkedin_agent-env/bin/activate
     ```

5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```



## Usage

To use the Linkedin Agent Tool, follow these steps:

1. Set up your LinkedIn login credentials as environment variables:
   - `LINKEDIN_USERNAME`: Your LinkedIn username or email.
   - `LINKEDIN_PASSWORD`: Your LinkedIn password.

2. Create an instance of the `LinkedinAccountSearch` and `LinkedinAccountDetailsTool` classes, passing the Selenium WebDriver as a parameter:
   ```python
   # activate web driver
   driver = webdriver.Chrome()

   # automatic login and cookie handling 
   login_linkedin(
      username=os.environ["LINKEDIN_USERNAME"],
      password=os.environ["LINKEDIN_PASSWORD"],
      driver=driver,
      bypassCookie=False)

   # setup the agent tools using the authenticated driver
   account_search = LinkedinAccountSearch(selenium_webdriver=driver)
   account_details_scraper = LinkedinAccountDetailsTool(selenium_webdriver=driver)
   ```

3. Create an instance of the `Agent` class, specifying the role, goal, backstory, and tools:
   ```python
   LinkedinSearch_agent = Agent(
       role="LinkedIn researcher",
       goal="Identify LinkedIn profiles based on search criteria and extract relevant information",
       backstory="...",
       tools=[account_search, account_details_scraper],
       verbose=True,
       allow_delegation=False
   )
   ```

4. Define tasks for the agent using the `Task` class, specifying the description, expected output, output file, and the agent:
   ```python
   find_all_john_smiths = Task(
       description="Search for 'John Smith' on LinkedIn and get top 5 profiles",
       expected_output="A json containing top 5 LinkedIn profiles for 'John Smith'",
       output_file="./tools/test_output/john_smiths_list.json",
       agent=LinkedinSearch_agent
   )
   ```

5. Create an instance of the `Crew` class, specifying the agents and tasks:
   ```python
   test_crew = Crew(
       agents=[LinkedinSearch_agent],
       tasks=[find_all_john_smiths, search_for_daniel_task],
       verbose=2
   )
   ```

6. Kick off the crew to execute the tasks:
   ```python
   test_crew.kickoff()
   ```

For a complete example, refer to the `@Linkedin_Agent_Tool/search_crew_test.py` file.

## Logging In

The tool handles logging in using your provided login credentials and saves the cookie to avoid frequent re-authentication. It does require some level of monitoring as LinkedIn's anti-bot systems are quite robust and may block access if too many requests are made too quickly. When that happens, you will see a CAPTCHA challenge. If you fill it out, it will fix the problem, and the agent will continue.
