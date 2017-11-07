# This script shows how to connect to a JIRA instance with a
# username and password over HTTP BASIC authentication.

from jira import JIRA
from cStringIO import StringIO
import ConfigParser 
import time
import sys 

# Constants
__JIRA_SERVER__ = 'http://issues.mercap.net:8080'
__INI_FILE__='..\\..\\properties.ini'

#********************************
#  System Codification.
#********************************

'''TODO: WATCH OUT THIS LINES ~ THESE COULD BROKE THE ENTIRE CODE; FIND SOME OTHER WAY TO ENCONDE THE STRINGS.'''
reload(sys)
#sys.setdefaultencoding('utf-8')

class PropertiesHandler():
    '''It opens the properties.ini file and loads into memory for consumption.'''
    
    config = None
    user = None
    pwd = None
    server_url=None
    
    def __init__(self):
        self.load()
    
    def load(self):
        '''It loads or reloads the configuration variables.'''
        config = ConfigParser.ConfigParser()
        config.read(__INI_FILE__)
        
        self.user = config.get('credentials','user')
        self.pwd = config.get('credentials','pwd')
        self.server_url = config.get('server','url')
        

class FileManager():
    '''Just handles files for the current project and data availability'''
    def getSendToCSVFile(self, fileStr):
        '''Sends the String to a file'''
        f = open("..\\..\\xls-export\\" + time.strftime("%Y%m%d") + "-" + time.strftime("%H%M%S") + "-jira-export.csv", "wb")
        f.write(fileStr)
        f.close()
    
    def getSendToOutputFile(self, fileStr):
        '''Sends the String to a file'''
        f = open("..\\..\\xls-export\\" + time.strftime("%Y%m%d") + "-" + time.strftime("%H%M%S") + "-process-output.csv", "wb")
        f.write(fileStr)
        f.close()

class JiraDataStructuresManager():
    ''' Extracts structural data from Jira for further analysis '''
    options = None
    jira = None
    
    def __init__(self):
        # By default, the client will connect to a JIRA instance started from the Atlassian Plugin SDK.
        # See https://developer.atlassian.com/display/DOCS/Installing+the+Atlassian+Plugin+SDK
        # for details.
        
        self.options = {'server': __JIRA_SERVER__}
        self.jira = JIRA(self.options, basic_auth=(self.cfg.user, self.cfg.pwd))  # a username/password tuple
     
    def getAllSprintNames(self):
        '''get all boards names for internal use.'''
        boards = self.jira.boards()
        sprints = None
        csv = "Board Name; SprintName;State\n"
        
        for board in boards:
            
            try:
                sprints = self.jira.sprints(board.id)  # , False, 0, None, None)   
    
                for s in sprints:
                    csv += board.name + ";" + s.name + ";" + s.state + "\n"
                    
            except Exception:
                pass
            
        return csv
    
    def getSprintListNamesAndState(self, boardName):
        '''It returns the project's associated sprints and status for its usage in other reports. '''
        
        try:
            sprints = self.jira.sprints(boardName, False, 0, None, None)
        except Exception:  # TODO: put the right error handling.
            return "Error: Scrum Board hasn't sprints associated."
        
        csv = "SprintName;State\n"
        
        for s in sprints:
            csv += s.name + ";" + s.state + "\n"
        
        return csv
    
    def getAllProjectsAsCSV(self):
        '''Returns all the projects names and codes as a long CSV string'''
        
        projects = self.jira.projects()
        csv = "Name;Code\n"
        
        for i in projects:
            csv += i.name + ";" + i.key + "\n"
        
        return csv
    
    def getCustomFieldID(self, name):
        '''Getting all the current custom fields ID's and dump it to a CSV file for revision.'''
        
        # Fetch all fields
        fileManager = FileManager()
        allfields = self.jira.fields()
        
        # Make a map from field name -> field id
        nameMap = {field['name']:field['id'] for field in allfields}
    
        stringBuffer = StringIO()
        stringBuffer.write("Field Name;Code\n")
    
        for field in allfields:
            stringBuffer.write(field['name'] + ";" + field['id'] + "\n")
    
        fileManager.getSendToCSVFile(stringBuffer.getvalue())
           
        if (name != None):
            try:
                result = nameMap[name]
            except:
                return None
            return result
        else:
            return None
    
class JiraDataExtractor():

    cfg = None
    def __init__(self):
        '''Getting the configuration data'''
        self.cfg = PropertiesHandler()
        
    def listProjectProgressAndCosts(self, projectName): #TODO: Refactorizar URGENTE!!!
        '''Given a project, passed by parameter, it throws an CSV file with the costs, the progress and current situation.'''
        # By default, the client will connect to a JIRA instance started from the Atlassian Plugin SDK.
        # See https://developer.atlassian.com/display/DOCS/Installing+the+Atlassian+Plugin+SDK
        # for details.
        
        options = {'server': self.cfg.server_url}
        jira = JIRA(options, basic_auth=(self.cfg.user, self.cfg.pwd)) # a username/password tuple
        
        # Get the mutable application properties for this server (requires
        # jira-system-administrators permission)
        #props = jira.application_properties()
        # Find all issues reported by the admin
        fileManager = FileManager()
        
        #Check how many files are required:
        query= 'project=' + projectName  + ' order by "Epic Name"'
        
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
        
                    if ((str(i.fields.customfield_11602) != "None") and (str(i.fields.status)!='Canceled')):
        
                            totalSPs = totalSPs + float(storyPoints)
        
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
        
        fileManager.getSendToCSVFile(stringBuffer.getvalue())
        
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
        stringBuffer.write("Project; " + str(projectName) + "\n")
        stringBuffer.write("Total issues; " + str(totalIssues) + "\n")
        stringBuffer.write("Completed Development SPs; " + str(completedDevelopmentSPs) + "/" + str(totalDevelopmentSPs) + ";" + str(completedDevelopmentSPs/(totalDevelopmentSPs if (totalDevelopmentSPs!=0) else 1)) + "\n")
        stringBuffer.write("Completed Analysis SPs; " + str(completedAnalysisSPs) + "/" + str(totalAnalysisSPs) + ";" + str(completedAnalysisSPs/(totalAnalysisSPs if (totalAnalysisSPs!=0) else 1)) + "\n")
        stringBuffer.write("In Progress SPs; " + str(inprogressDevelopmentSPs) + "/" + str(totalDevelopmentSPs)  + ";" + str(inprogressDevelopmentSPs/(totalDevelopmentSPs if (totalDevelopmentSPs!=0) else 1)) + "\n")
        stringBuffer.write("In Progress SPs; " + str(inprogressAnalysisSPs) + "/" + str(totalAnalysisSPs) + ";" + str(inprogressAnalysisSPs/(totalAnalysisSPs if (totalAnalysisSPs!=0) else 1)) + "\n")
        stringBuffer.write("Total SPs; " + str(totalSPs) + "\n")
        stringBuffer.write("Total HH spent Development; " +str(totalHHSpentDev) + "\n")
        stringBuffer.write("Total HH spent Analysis; " +str(totalHHSpentAnalysis) + "\n")
        stringBuffer.write("Total HH spent; " +str(totalHHSpent) + "\n")
        stringBuffer.write("Total Closed Sprints; " +str(maxSprints) + "\n")
        stringBuffer.write("Error records; " + str(errorCount) + "\n")
        
        fileManager.getSendToOutputFile(stringBuffer.getvalue())
        
        stringBuffer.close()

    def listAllIssuesOfGivenProjectsSet(self):
        '''It gets a list of projects from a configuration file '''
    

# Find the top three projects containing issues reported by admin
        
#*********************************        
# MAIN
#*********************************    
        
#flmng = FileManager()
#jiramng = JiraDataStructuresManager()

#flmng.getSendToOutputFile(jiramng.getAllProjectsAsCSV())
#flmng.getSendToOutputFile(jiramng.getAllSprintNames())

props  = PropertiesHandler()
print(props.server_url)
