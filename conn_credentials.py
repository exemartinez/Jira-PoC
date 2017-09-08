# This script shows how to connect to a JIRA instance with a
# username and password over HTTP BASIC authentication.
from collections import Counter
from jira import JIRA
from cStringIO import StringIO
import time
import sys 

#Codification system.
'''WATCH OUT THIS LINES ~ THESE COULD BROKE THE ENTIRE CODE; FIND SOME OTHER WAY TO ENCONDE THE STRINGS.'''
reload(sys)
sys.setdefaultencoding('utf-8')

#Constants
__PROJECT__='BSTI'

#Common functions
def getCustomFieldID(name):
    '''Getting all the custom fields ID's'''
    # Fetch all fields
    allfields=jira.fields()
    # Make a map from field name -> field id
    nameMap = {field['name']:field['id'] for field in allfields}

    try:
        result=nameMap[name]
    except:
        return None
    #Well known codes:
        #customfield_11602 <- Story Points code for the custom field.

    return result

def getSendToCSVFile(fileStr):
    '''Sends the String to a file'''
    f = open(time.strftime("%Y%m%d") + "-" + time.strftime("%H%M%S") + "-jira-export.csv","wb")
    f.write(fileStr)
    f.close()

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
issues = jira.search_issues("project=" + __PROJECT__,startAt=0, maxResults=0)
issues = jira.search_issues("project=" + __PROJECT__,startAt=0, maxResults=issues.total)

completedSPs = 0
totalSPs = 0
totalIssues = 0
errorCount = 0
csvString=""

print ("Total amount issues available: " + str(issues.total))

#TODO: verificar por que nos da diferentes los totales de SPs con lo que sale de la aplicacion WEB.

#Prepare to efficiently concatenate strings.
stringBuffer = StringIO()
stringBuffer.write("Issue;Summary; Status; SPs\n")

for i in issues:

    totalIssues = totalIssues + 1

    #print(getCustomFieldID("Story Point"))
    #print(getCustomFieldID("Story Points"))

    try:
        if(i.fields.customfield_11602!=None):

            print("Issue: " + i.key.decode() + " Summary: " + i.fields.summary.strip() + " Status: \'" + str(i.fields.status) + "\' SPs: " + str(int(str(i.fields.customfield_11602)[::-2])))
            stringBuffer.write(str(i.key).strip() + ";" + i.fields.summary.strip() + ";" + str(i.fields.status).strip() + ";" + str(int(str(i.fields.customfield_11602)[::-2].strip())) +"\n")

            totalSPs = totalSPs + int(str(i.fields.customfield_11602)[::-2])
            
            if ((str(i.fields.status)=='Approved') or (str(i.fields.status)=='Closed') or (str(i.fields.status)=="Ready To Merge")  or (str(i.fields.status)=="Ready To Test")):
                completedSPs = completedSPs + int(str(i.fields.customfield_11602)[::-2])
    except Exception as e:

        print("Error in Issue: " + str(i.key) + " -> " + i.fields.summary + " Error: " + str(e))


        stringBuffer.write(str(i.key) + ";" + i.fields.summary.strip() +";" + str(i.fields.status) + ";0" + "\n")

        errorCount = errorCount + 1
        pass

print("Total issues: " + str(totalIssues))
print("Completed SPs: " + str(completedSPs))
print("Total SPs: " + str(totalSPs))
print("Error records: " + str(errorCount))

getSendToCSVFile(stringBuffer.getvalue())
stringBuffer.close()

# Find the top three projects containing issues reported by admin
'''top_three = Counter(
[issue.fields.project.key for issue in issues]).most_common(3)

print(top_three)

boardBST = jira.boards(name='BST - Scrum')

print(boardBST)'''
