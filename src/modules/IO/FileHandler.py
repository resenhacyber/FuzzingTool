## FuzzingTool
# 
# Authors:
#    Vitor Oriel C N Borges <https://github.com/VitorOriel>
# License: MIT (LICENSE.md)
#    Copyright (c) 2021 Vitor Oriel
#    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
## https://github.com/NESCAU-UFLA/FuzzingTool

from .OutputHandler import outputHandler as oh

import os
import csv
import json
from datetime import datetime

class FileHandler:
    """Class that handle with the files
       Singleton Class
    """
    __instance = None

    @staticmethod
    def getInstance():
        if FileHandler.__instance == None:
            FileHandler()
        return FileHandler.__instance

    """
    Attributes:
        wordlistFile: The wordlist file
        outputFile: The output file
        report: The report format and name dict
    """
    def __init__(self):
        """Class constructor"""
        if FileHandler.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            FileHandler.__instance = self
        self.__wordlistFile = None
        self.__reportFile = None
        self.__logFile = None
        self.__report = {
            'Type': 'txt',
            'Name': ''
        }
    
    def __del__(self):
        """Class destructor"""
        if self.__logFile: # If the logFile is open, closes the file
            self.__close(self.__logFile)

    def readData(self, dataFileName: str):
        '''Reads the default data of the requests.

        @type dataFileName: str
        @param dataFileName: The filename
        @returns list: The content into data file
        '''
        try:
            with open('./input/'+dataFileName, 'r') as dataFile:
                return [data.rstrip('\n') for data in dataFile]
        except FileNotFoundError:
            oh.errorBox("File '"+dataFileName+"' not found.")

    def getProxiesFile(self):
        """The proxiesFile getter

        @returns file: The proxies file
        """
        return self.__proxiesFile

    def readProxies(self, proxiesFileName: str):
        """Open the proxies file, and read the proxies
        
        @type proxiesFileName: str
        @param proxiesFileName: The name of the proxies file
        @returns list: The list with proxies dictionary
        """
        proxies = []
        try:
            with open('./input/'+proxiesFileName, 'r') as proxiesFile:
                for line in proxiesFile:
                    line = line.rstrip("\n")
                    proxies.append({
                        'http': 'http://'+line,
                        'https': 'https://'+line
                    })
        except FileNotFoundError:
            oh.errorBox("File '"+proxiesFileName+"' not found.")
        return proxies

    def openWordlist(self, wordlistFileName: str):
        """Open the wordlist file

        @type wordlistFileName: str
        @param wordlistFileName: The name of the wordlist file
        """
        try:
            self.__wordlistFile = open('./input/'+wordlistFileName, 'r')
        except FileNotFoundError:
            oh.errorBox("File '"+wordlistFileName+"' not found. Did you put it in the correct directory?")

    def setReport(self, report: dict):
        """The report setter

        @type report: dict
        @param report: The report format and name dict
        """
        self.__report = report

    def getWordlistContentAndLength(self):
        """Get the wordlist content, into a list, and the number of lines in file

        @returns tuple(list, int): The tuple with the wordlist and the number of lines
        """
        wordlist = []
        length = 0
        for line in self.__wordlistFile:
            line = line.rstrip("\n")
            wordlist.append(line)
            length += 1
        self.__close(self.__wordlistFile)
        return (wordlist, length)

    def openLog(self):
        """Open the log file to save the current logs"""
        now = datetime.now()
        logFileName = 'log-'+now.strftime("%Y-%m-%d_%H:%M")+'.txt'
        try:
            self.__logFile = open(f'./logs/{logFileName}', 'w')
        except FileNotFoundError:
            os.system(f'mkdir ./logs')
            self.__logFile = open(f'./logs/{logFileName}', 'w')
        finally:
            oh.infoBox(f'The logs will be saved on \'./logs/{logFileName}\'')

    def writeLog(self, exception: str):
        """Write the exception on the log file

        @type exception: str
        @param exception: The exception to be saved on the log file
        """
        now = datetime.now()
        time = now.strftime("%H:%M:%S")
        self.__logFile.write(time+' | '+exception+'\n')

    def writeReport(self, reportContent: list):
        """Write the vulnerable input and response content into a report

        @param type: list
        @param reportContent: The list with probably vulnerable content
        """
        if reportContent:
            self.__openReport()
            if self.__report['Type'] == 'txt':
                self.__txtWriter(reportContent)
            elif self.__report['Type'] == 'csv':
                self.__csvWriter(reportContent)
            elif self.__report['Type'] == 'json':
                self.__jsonWriter(reportContent)
            self.__close(self.__reportFile)
            oh.infoBox('Results saved')

    def __openReport(self):
        """Opens the report file 
           for store the probably vulnerable response data
        """
        reportType = self.__report['Type']
        reportName = self.__report['Name']
        if not reportName:
            now = datetime.now()
            reportName = now.strftime("%Y-%m-%d_%H:%M")
        try:
            self.__reportFile = open(f'./reports/{reportType}/{reportName}.{reportType}', 'w')
        except FileNotFoundError:
            if not os.path.exists('./reports'):
                os.system('mkdir ./reports')
            os.system(f'mkdir ./reports/{reportType}')
            self.__reportFile = open(f'./reports/{reportType}/{reportName}.{reportType}', 'w')
        finally:
            oh.infoBox(f'Saving results on \'./reports/{reportType}/{reportName}.{reportType}\' ...')

    def __close(self, file: object):
        """Closes the file

        @type file: object
        @param file: The file
        """
        file.close()

    def __txtWriter(self, reportContent: list):
        """The txt report writer

        @param type: list
        @param reportContent: The list with probably vulnerable content
        """
        for content in reportContent:
            for key, value in content.items():
                self.__reportFile.write(key+': '+str(value)+'\n')
            self.__reportFile.write('\n')
    
    def __csvWriter(self, reportContent: list):
        """The csv report writer

        @param type: list
        @param reportContent: The list with probably vulnerable content
        """
        writer = csv.DictWriter(
            self.__reportFile,
            fieldnames=[key for key, value in reportContent[0].items()]
        )
        writer.writeheader()
        for content in reportContent:
            writer.writerow(content)

    def __jsonWriter(self, reportContent: list):
        """The json report writer

        @param type: list
        @param reportContent: The list with probably vulnerable content
        """
        json.dump(reportContent, self.__reportFile)

fileHandler = FileHandler.getInstance()