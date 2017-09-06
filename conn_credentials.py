# This script shows how to connect to a JIRA instance with a
# username and password over HTTP BASIC authentication.
from collections import Counter
from jira import JIRA

# By default, the client will connect to a JIRA instance started from the Atlassian Plugin SDK.
# See https://developer.atlassian.com/display/DOCS/Installing+the+Atlassian+Plugin+SDK
# for details.

options = {
'server': 'http://issues.mercap.net:8080'}

jira = JIRA(options, basic_auth=('emartinez', 'itT85278952'))# a username/password tuple

# Get the mutable application properties for this server (requires
# jira-system-administrators permission)
#props = jira.application_properties()
# Find all issues reported by the admin

#Check how many files are required:
issues = jira.search_issues("project='BSTI'",startAt=0, maxResults=0)
issues = jira.search_issues("project='BSTI'",startAt=0, maxResults=issues.total)

completedSPs = 0
totalSPs = 0
totalIssues = 0
print ("Total amount issues available: " + str(issues.total))

#TODO Revisar el custom field de "Story Point", como hacerlo dinamico en vez de hardcodearlo.
#TODO Tirar todo en un csv file.
#TODO verificar por que nos da diferentes los totales de SPs con lo que sale de la aplicacion WEB.

for i in issues:

    totalIssues = totalIssues + 1
    try:
        if(i.fields.customfield_11602!=None):
            print("Issue: " + str(i.key) + " Summary: " + i.fields.summary + " Status: " + str(i.fields.status) + " SPs: " + str(int(str(i.fields.customfield_11602)[::-2])))
            totalSPs = totalSPs + int(str(i.fields.customfield_11602)[::-2])
            if ((str(i.fields.status)=='Approved') or (str(i.fields.status)=='Closed') or (str(i.fields.status)=="Ready to Merge")  or (str(i.fields.status)=="Ready to Test")):
                completedSPs = completedSPs + int(str(i.fields.customfield_11602)[::-2])
    except:
        pass

print("Total issues: " + str(totalIssues))
print("Completed SPs: " + str(completedSPs))
print("Total SPs: " + str(totalSPs))

def getCustomFieldID(name):
    '''Getting all the custom fields ID's'''
    # Fetch all fields
    allfields=jira.fields()
    # Make a map from field name -> field id
    nameMap = {field['name']:field['id'] for field in allfields}

    #Well known codes:
        #customfield_11602 <- Story Points code for the custom field.
    return nameMap[name]

# Find the top three projects containing issues reported by admin
'''top_three = Counter(
[issue.fields.project.key for issue in issues]).most_common(3)

print(top_three)

boardBST = jira.boards(name='BST - Scrum')

print(boardBST)'''
