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
if (len(sys.argv)<2):
    print ("Not enough parameters.")
    sys.exit()
else:
    __PROJECT__=sys.argv[1]
    __USERID__=sys.argv[2]
    __PASS__=sys.argv[3]

#Common functions

def getCustomFieldID(name):
    '''Getting all the current custom fields ID's and dump it to a CSV file for revision.'''
    # Fetch all fields
    allfields=jira.fields()
    # Make a map from field name -> field id
    nameMap = {field['name']:field['id'] for field in allfields}

    stringBuffer = StringIO()
    stringBuffer.write("Field Name;Code\n")

    for field in allfields:
        stringBuffer.write(field['name'] + ";" + field['id'] + "\n")

    getSendToCSVFile(stringBuffer.getvalue())
       
    if (name!=None):
        try:
            result=nameMap[name]
        except:
            return None
        #Well known codes:
            #customfield_11602 <- Story Points code for the custom field.
            #customfield_11606 <- Epic Link.
            #customfield_11607 <- Epic Name

        return result
    else:
        return None

def getSendToCSVFile(fileStr):
    '''Sends the String to a file'''
    f = open(".\\xls-export\\" + time.strftime("%Y%m%d") + "-" + time.strftime("%H%M%S") + "-jira-export.csv","wb")
    f.write(fileStr)
    f.close()

def getSendToOutputFile(fileStr):
    '''Sends the String to a file'''
    f = open(".\\xls-export\\" + time.strftime("%Y%m%d") + "-" + time.strftime("%H%M%S") + "-process-output.csv","wb")
    f.write(fileStr)
    f.close()

# By default, the client will connect to a JIRA instance started from the Atlassian Plugin SDK.
# See https://developer.atlassian.com/display/DOCS/Installing+the+Atlassian+Plugin+SDK
# for details.

options = {'server': 'http://issues.mercap.net:8080'}
jira = JIRA(options, basic_auth=(__USERID__, __PASS__))# a username/password tuple

# Get the mutable application properties for this server (requires
# jira-system-administrators permission)
#props = jira.application_properties()
# Find all issues reported by the admin


#Check how many files are required:
query= 'project=' + __PROJECT__  + ' order by "Epic Name"'

#The next line goest to know the total amount of records to be returned.
issues = jira.search_issues(query, startAt=0, maxResults=0)
issues = jira.search_issues(query,startAt=0, maxResults=issues.total)

#Variable definition and declaretion
completedDevelopmentSPs = 0
completedAnalysisSPs = 0
inprogressDevelopmentSPs=0
inprogressAnalysisSPs=0
totalDevelopmentSPs = 0 
totalAnalysisSPs = 0
totalSPs = 0
totalHHSpentDev = 0
totalHHSpentAnalysis = 0
totalHHSpent = 0
totalIssues = 0
errorCount = 0
maxSprints = 0
csvString=""
storyPoints = ""

#getCustomFieldID(None)
#time.sleep(1)

print ("Total amount issues available: " + str(issues.total))

#Searching for the issues and preparing the excel file for processing.
stringBuffer = StringIO()
stringBuffer.write("Issue;Type;Summary; Status; SPs; Epic Code; HH spent; Sprints; Count Sprints; Created\n")

for i in issues:

    totalIssues += 1
    #TODO: this needs a STRONG refactoring (specially extract method!)

    try:
        
        #Getting the related EPIC Name.
        try:
            epicName = str(i.fields.customfield_11606)
        except Exception as e:
            epicName = ""

        #calculate consumption in hours for the issue.
        timespent = i.fields.timespent
        if timespent is None:
            timespent=0
        else:
            timespent/=3600 

        #Just for tasks with SPs (calculating totals for report)
        if ((str(i.fields.issuetype) == "Testing") or (str(i.fields.issuetype) == "Analysis") or (str(i.fields.issuetype) == "Development")):
            
            storyPoints = str(i.fields.customfield_11602)

            if (str(i.fields.customfield_11602) != "None"):
                                             
                totalSPs = totalSPs + float(storyPoints)

                if (str(i.fields.status)!='Canceled'):
                    #Summing the analysis and development story points by each side. #TODO:Needed refactoring.
                    if ((str(i.fields.issuetype) == "Testing") or (str(i.fields.issuetype) == "Analysis")):
                        totalAnalysisSPs += float(storyPoints)
                        totalHHSpentAnalysis += timespent

                    elif ((str(i.fields.issuetype) == "Development")):
                        totalDevelopmentSPs += float(storyPoints)
                        totalHHSpentDev += timespent
                    
                    if ((str(i.fields.status)=='Approved') or (str(i.fields.status)=='Closed') or (str(i.fields.status)=="Ready To Merge")  or (str(i.fields.status)=="Ready To Test")):
                        
                        if (str(i.fields.issuetype) == "Development"):
                            completedDevelopmentSPs = completedDevelopmentSPs + float(storyPoints)
                        else:
                            completedAnalysisSPs = completedAnalysisSPs + float(storyPoints)
                    elif (str(i.fields.status)!='Open'):
                        if (str(i.fields.issuetype) == "Development"):
                            inprogressDevelopmentSPs += float(storyPoints)
                        else:
                            inprogressAnalysisSPs += float(storyPoints)

        totalHHSpent+=timespent
        numSprints = len(i.fields.customfield_11605) if i.fields.customfield_11605 != None else 0
        maxSprints = numSprints if numSprints > maxSprints else maxSprints

        #Getting the string output (It's a CSV file that will be consumed by excel)
        stringBuffer.write(str(i.key).strip() + ";" + str(i.fields.issuetype) +  ";" + i.fields.summary.strip() + ";" + str(i.fields.status).strip() + ";" + storyPoints + ";" + epicName + ";" + str(timespent) + ";" + str(i.fields.customfield_11605) + ";" + str(numSprints)+ ";" + str(i.fields.created) + "\n")
                    
    except Exception as e:

        print("Error in Issue: " + str(i.key) + " -> " + i.fields.summary + " Error: " + str(e))

        stringBuffer.write(str(i.key) + ";" + str(i.fields.issuetype) +  ";" +  i.fields.summary.strip() +";" + str(i.fields.status) + ";0" + "\n")

        errorCount = errorCount + 1
        pass

getSendToCSVFile(stringBuffer.getvalue())

print("\n"*3)
print("-"*80)
print("\n")
print("Total issues: " + str(totalIssues))
print("Completed Development SPs: " + str(completedDevelopmentSPs) + "/" + str(totalDevelopmentSPs))
print("Completed Analysis SPs: " + str(completedAnalysisSPs) + "/" + str(totalAnalysisSPs))
print("In Progress Development SPs: " + str(inprogressDevelopmentSPs) + "/" + str(totalDevelopmentSPs))
print("In Progress Analysis SPs: " + str(inprogressAnalysisSPs) + "/" + str(totalAnalysisSPs))
print("Total SPs: " + str(totalSPs))
print("Total HH spent Development: " +str(totalHHSpentDev))
print("Total HH spent Analysis: " +str(totalHHSpentAnalysis))
print("Total HH spent: " +str(totalHHSpent))
print("Total Closed Sprints: " +str(maxSprints)) #TODO: OJO! esta metrica esta dando ERRONEA!!!
print("Error records: " + str(errorCount))

stringBuffer = StringIO()
stringBuffer.write("Total issues; " + str(totalIssues) + "\n")
stringBuffer.write("Completed Development SPs; " + str(completedDevelopmentSPs) + "/" + str(totalDevelopmentSPs) + ";" + str(completedDevelopmentSPs/totalDevelopmentSPs) + "\n")
stringBuffer.write("Completed Analysis SPs; " + str(completedAnalysisSPs) + "/" + str(totalAnalysisSPs) + ";" + str(completedAnalysisSPs/totalAnalysisSPs) + "\n")
stringBuffer.write("In Progress SPs; " + str(inprogressDevelopmentSPs) + "/" + str(totalDevelopmentSPs)  + ";" + str(inprogressDevelopmentSPs/totalDevelopmentSPs)  + "\n")
stringBuffer.write("In Progress SPs; " + str(inprogressAnalysisSPs) + "/" + str(totalAnalysisSPs) + ";" + str(inprogressAnalysisSPs/totalAnalysisSPs) + "\n")
stringBuffer.write("Total SPs; " + str(totalSPs) + "\n")
stringBuffer.write("Total HH spent Development: " +str(totalHHSpentDev) + "\n")
stringBuffer.write("Total HH spent Analysis: " +str(totalHHSpentAnalysis) + "\n")
stringBuffer.write("Total HH spent; " +str(totalHHSpent) + "\n")
stringBuffer.write("Total Closed Sprints: " +str(maxSprints) + "\n")
stringBuffer.write("Error records; " + str(errorCount) + "\n")

getSendToOutputFile(stringBuffer.getvalue())

stringBuffer.close()

# Find the top three projects containing issues reported by admin
'''top_three = Counter(
[issue.fields.project.key for issue in issues]).most_common(3)

print(top_three)

boardBST = jira.boards(name='BST - Scrum')

print(boardBST)'''
