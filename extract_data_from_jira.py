
import csv
from jira import JIRA 
import os
from dotenv import load_dotenv

load_dotenv() 

JIRA_EMAIL=os.getenv('JIRA_EMAIL') 
API_token=os.getenv('API_token')
JIRA_PROJECT=os.getenv('JIRA_PROJECT')

jiraOptions = {'server': JIRA_PROJECT} 

# JIRA client instance
jira = JIRA(options=jiraOptions, basic_auth=( 
	JIRA_EMAIL, API_token)) 


def write_issue_to_csv(csv_writer, issue, existing_issue_keys):
    issue_key = issue.key
    if issue_key in existing_issue_keys:
        return
            
    # Get the issue summary
    issue_summary = issue.fields.summary
            
    # Get the priority name
    priority_name = issue.fields.priority.name

    # Get the priority ID
    priority_id = issue.fields.priority.id

    # Get the issue description (content)
    issue_description = issue.fields.description.replace('\n', ' ')
            
    # Write data to the CSV file
    csv_writer.writerow([issue_key, issue_summary,priority_name, priority_id, issue_description])

    # Add the issue key to the set of existing issue keys
    existing_issue_keys.add(issue_key)


# name of csv file
filename = "issues.csv"

# Set to store unique issue keys
existing_issue_keys = set()

if (not os.path.exists(filename) or os.stat(filename).st_size == 0):  # if file do not exist or is empty
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    # creating a csv writer object
        csv_writer = csv.writer(csvfile)
    # writing the header row 
        csv_writer.writerow(['Issue Key', 'Summary','Priority Name', 'Priority ID', 'Description'])
    # Search all issues within the project 
        for issue in jira.search_issues(jql_str='project = "PFE" ORDER BY created ASC',maxResults=100):
            write_issue_to_csv(csv_writer, issue, existing_issue_keys)

else:  #if file exists and already has items
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        # Skip header row
        next(reader)
        # Add existing issue keys to the set
        for row in reader:
            if row:  # Check if the row is not empty
                existing_issue_keys.add(row[0])
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        for issue in jira.search_issues(jql_str='project = "PFE" ORDER BY created ASC',maxResults=100):
            write_issue_to_csv(csv_writer, issue, existing_issue_keys)



