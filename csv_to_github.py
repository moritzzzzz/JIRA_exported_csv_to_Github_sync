import requests
import csv
import random

randint = random.randrange(0, 1000000)  # random number as post param to mitigate caching

# open session to write to github

user = "<USR>"
pswd = "<PWD>"
repo = "jira_sync_test"

ses = requests.Session()
ses.auth = (user, pswd)
issue_url = "https://api.github.com/repos/<organization>/<project>/issues"  # + user + "/" + repo + "/issues"

# init empty arrays for issue data from CSV
rows_array = []
uIDs_array = []
issue_already_written = []

# Read issues CSV file
with open('issues.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, dialect='excel')  # delimiter=',', quotechar='|')

    row_counter = 0

    for row in spamreader:  # row is array of columns for this line

        if row_counter >= 1:
            rows_array.append(row)
            issue_already_written.append(0)

        row_counter += 1

# sample row ['Crash of application', 'T12121', '421133318', 'Bug', 'Open', 'T11', 'team', 'software', 'Test111', '', '', 'Critical', '', 'test', 'test', 'test', '27/Aug/20 11:44 AM', '02/Oct/20 2:09 PM', '05/Oct/20 11:50 AM', '', 'TAS600Program', '', '0', 'Mapbox', '*ActionsÂ\xa0:*\r\n* Given the user zoomed out the map to show France\r\n* And the user placed a pin in france(D 1, Marson)\r\n* And user started the navigation\r\n* When the user presses the button to view the route on the map screen\r\n\r\n*Expected ResultsÂ\xa0:*\r\nThen the user can see the complete route that he has to drive to the destination\r\n\r\n*Actual BehaviourÂ\xa0:*\r\nAfter a fresh update of the system, the first time this scenario ran it caused a crash of the navigation. The user was taken back to the main menu, and could not start the navigation again from the main menu.\r\n\r\n*Repeatability:* \r\nOnce\r\n', 'â€¢ TYPE OF TEST: E2E\r\nâ€¢ HEAD-UNIT HARDWARE : ED3\r\nâ€¢ MAPBOX RELEASE : DROP 6\r\nâ€¢ HARMANN RELEASE: 9.2\r\nâ€¢ TESTBENCH / VEHICULE : RAV4\r\nâ€¢ VARIABLES : \r\nâ€¢\tDRIVING : NO\r\nâ€¢\tITINERARY\r\nâ€¢\tDESTINATION PINNED OR SEARCHED : D 1, Marson, France\r\nâ€¢\tADRESS OR POI : CURRENT LOCAITON : BOURGETLAAN, 1140 BRUSSELS', 'PLI6087', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'To Be Assigned Later', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Both', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '9223372036854775807', '', '', '', 'N', '', '', 'TME', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '2|i03jlm:', '', '9223372036854775807', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']

# Getting all issues from github repo

response_all_issues = ses.get(issue_url)
json_data_issues = response_all_issues.json()

while 'next' in response_all_issues.links.keys():  # getting other pages of github response
    response_all_issues = ses.get(response_all_issues.links['next']['url'])
    json_data_issues.extend(response_all_issues.json())

issue_array_iterator = 0

for issue_csv in rows_array:

    for issue in json_data_issues:

        # extract first 6 letters of body --> issue ID from JIRA
        title = issue["title"]
        unique_id = issue["body"][:6]

        if unique_id == issue_csv[2]:
            issue_already_written[issue_array_iterator] = 1

    issue_array_iterator += 1

issue_already_written_iterator = 0
for is_written_to_git2 in issue_already_written:
    if is_written_to_git2 == 0:
        print(rows_array[issue_already_written_iterator][0])
    issue_already_written_iterator += 1

input("Press Enter to continue writing above issues to the target repository...")

issue_already_written_iterator = 0
for is_written_to_git in issue_already_written:
    if is_written_to_git == 0:
        # Writing issue to github, if not exists

        issue = {
            "title": rows_array[issue_already_written_iterator][0],
            "labels": ['TME Issue', rows_array[issue_already_written_iterator][11]],
            "body": rows_array[issue_already_written_iterator][2] + " \n # Summary \n " + " \n # Jira link \n "
                    + "https://cde.toyota-europe.com/jira/browse/" + rows_array[issue_already_written_iterator][1] +
                    " \n " + rows_array[issue_already_written_iterator][24] + " \n " + " # Environment \n " +
                    rows_array[issue_already_written_iterator][25]
        }

        # sending request to write issue
        r = ses.post(issue_url, json=issue)

        print(r)
        print(str(r.content))

    issue_already_written_iterator += 1

# kill session
ses.close()
