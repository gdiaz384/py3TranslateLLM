#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: A helper library to aid in using openpyxl as a data structure.

Usage: See below. Like at the bottom.

License: See main program.

"""
__version__='2024.04.27'

#set defaults
#printStuff=True
verbose=False
debug=False
#debug=True
consoleEncoding='utf-8'
defaultTextFileEncoding='utf-8'   # Settings that should not be left as a default setting should have default prepended to them.
linesThatBeginWithThisAreComments='#'
assignmentOperatorInSettingsFile='='
inputErrorHandling='strict'
#outputErrorHandling='namereplace'


translationEngines='parseOnly, koboldcpp, deepl_api_free, deepl_api_pro, deepl_web, fairseq, sugoi'
usageHelp='\n Usage: python py3TranslateLLM --help  Example: py3TranslateLLM -mode KoboldCpp -f myInputFile.ks \n Translation Engines: '+ translationEngines + '.'


#These must be here or the library will crash even if these modules have already been imported by main program.
import os, os.path                      # Extract extension from filename, and test if file exists.
#import pathlib                            # For pathlib.Path Override file in file system with another and create subfolders. Sane path handling.
import requests                          # Check if internet exists.
import sys                                   # End program on fail condition.
import io                                      # Manipulate files (open/read/write/close).
import datetime                          # Used to get current date and time.
import csv                                    # Read and write to csv files. Example: Read in 'resources/languageCodes.csv'
import openpyxl                          # Used as the core internal data structure and to read/write xlsx files. Must be installed using pip.
try:
    import odfpy                           #Provides interoperability for Open Document Spreadsheet (.ods).
    odfpyLibraryIsAvailable=True
except:
    odfpyLibraryIsAvailable=False
try:
    import xlrd                              #Provides reading from Microsoft Excel Document (.xls).
    xlrdLibraryIsAvailable=True
except:
    xlrdLibraryIsAvailable=False
try:
    import xlwt                              #Provides writing to Microsoft Excel Document (.xls).
    xlwtLibraryIsAvailable=True
except:
    xlwtLibraryIsAvailable=False


#Using the 'namereplace' error handler for text encoding requires Python 3.5+, so use an older one if necessary.
sysVersion=int(sys.version_info[1])
if sysVersion >= 5:
    outputErrorHandling='namereplace'
elif sysVersion < 5:
    outputErrorHandling='backslashreplace'    
else:
    sys.exit( 'Unspecified error.'.encode(consoleEncoding) )


#Question: how does os.path.splitext(fileName) actually work? Answer: If the extension does not exist, then it returns an empty string '' object for the extension. A None comparison will not work, but...   if myFileExtOnly == '':   ... will return true and conditionally execute.
#Returns True or False depending upon if file exists or not.
def checkIfThisFileExists(myFile):
    #Check if name of file was never set or if the entered data is not a file.
    if (myFile == None) or (os.path.isfile(str(myFile)) != True):
        return False
    return True

#Usage:
#checkIfThisFileExists('myfile.csv')
#checkIfThisFileExists(myVar)


def checkIfThisFolderExists(myFolder):
    if (myFolder == None) or (os.path.isdir(str(myFolder)) != True):
        return False
    return True


#Errors out if myFile does not exist.
def verifyThisFileExists(myFile,nameOfFileToOutputInCaseOfError=None):
    #Check if name of file was never set.
    #print('pie')
    #print(myFile)
    if myFile == None:
        #print('pie')
        sys.exit( ('Error: Please specify a valid file for: ' + str(nameOfFileToOutputInCaseOfError) + usageHelp).encode(consoleEncoding))
    #Check if file exists. Example: 'scratchpad/ks_testFiles/A01.ks'
    if os.path.isfile(myFile) != True:
        #print('pie')
        sys.exit( (' Error: Unable to find file \'' + str(nameOfFileToOutputInCaseOfError) + '\' ' + usageHelp).encode(consoleEncoding) )

#Usage:
#verifyThisFileExists('myfile.csv','myfile.csv')
#verifyThisFileExists(myVar, 'myVar')


# Errors out if myFolder does not exist.
def verifyThisFolderExists(myFolder, nameOfFileToOutputInCaseOfError=None):
    if myFolder == None:
        sys.exit( ('Error: Please specify a valid folder for: ' + str(nameOfFileToOutputInCaseOfError) + usageHelp).encode(consoleEncoding))
    if os.path.isdir(myFolder) != True:
        sys.exit( (' Error: Unable to find folder \'' + str(nameOfFileToOutputInCaseOfError) + '\' ' + usageHelp).encode(consoleEncoding) )


#This function reads program settings from text files using a predetermined list of rules.
#The text file uses the syntax: setting=value, # are comments, empty/whitespace lines ignored.
#This function builds a dictionary and then returns it to the caller.
def readSettingsFromTextFile(fileNameWithPath, fileNameEncoding, consoleEncoding=consoleEncoding, errorHandlingType=inputErrorHandling,debug=debug):
    if fileNameWithPath == None:
        print( ('Cannot read settings from None entry: '+fileNameWithPath ).encode(consoleEncoding) )
        return None

    #check if file exists   'scratchpad/ks_testFiles/A01.ks'
    if os.path.isfile(fileNameWithPath) != True:
        sys.exit( ('\n Error: Unable to find input file \''+ fileNameWithPath + '\'' + usageHelp).encode(consoleEncoding) )
    #then read entire file into memory
    #If there is an error reading the contents into memory, just close it.
#    try:
#        inputFileHandle = open(fileNameWithPath,'r',encoding=fileNameEncoding, errors=errorHandlingType) #open in read only text mode #Will error out if file does not exist.
        #open() works with both \ and / to traverse folders.
#        inputFileContents=inputFileHandle.read()
#    finally:
#        inputFileHandle.close()#Always executes, probably.

    #Newer, simplier syntax.
    with open( fileNameWithPath, 'r', encoding=fileNameEncoding, errors=inputErrorHandling ) as myFileHandle:
        inputFileContents = myFileHandle.read()

    if not isinstance(inputFileContents, str):
        sys.exit( ('Error: Unable to read from file: '+fileNameWithPath).encode(consoleEncoding) )

    #Okay, so the file was specified, it exists, and it was read from successfully. The contents are in inputFileContents.
    #Now turn inputFileContents into a dictionary.
    tempDictionary={}
    #while line is not empty (at least \n is present)
    while inputFileContents != '' :
        #returns the current line that will be processed
        myLine=inputFileContents.partition('\n')[0] #returns first line of string to process in the current loop

        #The line should be ignored if the first character is a comment character (after removing whitespace) or if there is only whitespace
        ignoreCurrentLine = False
        if (myLine.strip() == '') or ( myLine.strip()[:1] == linesThatBeginWithThisAreComments.strip()[:1] )  :
            ignoreCurrentLine = True

        tempList=[]
        if ignoreCurrentLine == False:
            #If line should not be ignored, then = must exist to use it as a delimitor. exit due to malformed data if not found.
            if myLine.find(assignmentOperatorInSettingsFile) == -1:
                sys.exit( ('Error: Malformed data was found processing file: '+ fileNameWithPath + ' Missing: \''+assignmentOperatorInSettingsFile+'\'').encode(consoleEncoding) )
            #If the line should not be ignored, then use = as a delimiter set each side as key = value in a temporaryDictionary
            #Example:  paragraphDelimiter=emptyLine   #ignoreLinesThatStartWith=[ * ; 【     #wordWrap=45   #alwaysAddAfterTranslationEndOfLine=None
            key, value = myLine.split(assignmentOperatorInSettingsFile,1)
            key=key.strip()
            value=value.strip()
            if value.lower() == '':
                print( ('Warning: Error reading key\'s value \'' +key+ '\' in file: '+str(fileNameWithPath)+' Using None as fallback.').encode(consoleEncoding) )
                value = None
            elif value.lower() == 'none':
                value = None
            elif key.lower() == 'ignorelinesthatstartwith':#ignoreLinesThatStartWith
                #then every item that is not blank space is a valid list value
                tempList = value.split(' ')
                value=[]
                #Extra whitespace between entries is hard to spot in the file and can produce malformed list entries, so parse each entry individually.
                for i in tempList:
                    if i != '':
                        value.append(i.strip())
            elif value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            tempDictionary[key]=value

        #Finished processing line, so remove current line from string to prepare to process next line.
        inputFileContents=inputFileContents.partition('\n')[2] 

    #Finished reading entire file, so return resulting dictionary.
    if debug == True:
        print( (fileNameWithPath+' was turned into this dictionary='+str(tempDictionary)).encode(consoleEncoding) )
    return tempDictionary


def getCurrentMonthFromNumbers(x):
    x = str(x)
    if (x == '1') or (x == '01'):
        return 'Jan'
    elif (x == '2') or (x == '02'):
        return 'Feb'
    elif (x == '3') or (x == '03'):
        return 'Mar'
    elif (x == '4') or (x == '04'):
        return 'April'
    elif (x == '5') or (x == '05'):
        return 'May'
    elif (x == '6') or (x == '06'):
        return 'June'
    elif (x == '7') or (x == '07'):
        return 'July'
    elif (x == '8') or (x == '08'):
        return 'Aug'
    elif (x == '9') or (x == '09'):
        return 'Sept'
    elif (x == '10'):
        return 'Oct'
    elif (x == '11'):
        return 'Nov'
    elif (x == '12'):
        return 'Dec'
    else:
          sys.exit('Unspecified error.'.encode(consoleEncoding))


# These functions return the current date, time, yesterday's date, and full (day+time)
def getYearMonthAndDay():
    today = datetime.datetime.today()

    #debug code
    #print(datetime.today().strftime('%Y-%m-%d'))
    #print(today.strftime("%d/%m/%Y %H:%M:%S"))

    currentYear = str( today.strftime('%Y') )
#    currentMonth = getCurrentMonthFromNumbers(today.strftime('%m'))
    currentMonth = str( today.strftime('%m') )
    currentDay = str( today.strftime('%d') )
    return( currentYear + '-' + currentMonth + '-' + currentDay )


def getYesterdaysDate():
    yesterday = datetime.datetime.today() - datetime.timedelta(1)

    #debug code
    #print(datetime.yesterday().strftime('%Y-%m-%d'))
    #print(yesterday.strftime("%d/%m/%Y %H:%M:%S"))

    currentYear = str( yesterday.strftime('%Y') )
    currentMonth = getCurrentMonthFromNumbers(yesterday.strftime('%m'))
    currentMonth = str( yesterday.strftime('%m') )
    currentDay = str( yesterday.strftime('%d') )
    return( currentYear + '-' + currentMonth + '-' + currentDay )


def getCurrentTime():
    today = datetime.datetime.today()

    currentHour=today.strftime('%H')
    currentMinutes=today.strftime('%M')
    currentSeconds=today.strftime('%S')
    return( currentHour + '-' + currentMinutes + '-' + currentSeconds )


def getDateAndTimeFull():
    #currentDateAndTimeFull=currentDateFull+'-'+currentTimeFull
    return getYearMonthAndDay() + '.' + getCurrentTime()

#if (verbose == True) or (debug == True):
#    print(currentDateAndTimeFull.encode(consoleEncoding))


# Returns true if internet is available. Returns false otherwise.
def checkIfInternetIsAvailable():
    try:
        myRequest = requests.get('https://www.google.com',timeout=10)
        return True
    except requests.ConnectionError:
        return False


def importDictionaryFromFile(myFile,myFileEncoding=None):
    if checkIfThisFileExists(myFile) != True:
        return None
    #else it exists, so find the extension and call the appropriate import function for that fileType
    myFileNameOnly, myFileExtensionOnly = os.path.splitext(myFile)
    if myFileExtensionOnly == None:
        return None
    if myFileExtensionOnly == '':
        return None
    elif myFileExtensionOnly == '.csv':
        return importDictionaryFromCSV(myFile,myFileEncoding,ignoreWhitespace=False)
    elif myFileExtensionOnly == '.xlsx':
        return importDictionaryFromXLSX(myFile,myFileEncoding)
    elif myFileExtensionOnly == '.xls':
        return importDictionaryFromXLS(myFile,myFileEncoding)
    elif myFileExtensionOnly == '.ods':
        return importDictionaryFromODS(myFile,myFileEncoding)
    else:
        print( ('Warning: Unrecognized extension for file: '+str(myFile)).encode(consoleEncoding) )
        return None



#Thinking: There is normally no return, but returnDictionary=True indicates a special flag where the function will instead return a dictionary of columns 1 and 2 as key=value pairs. Perhaps this would be better off split into a seperate function? It does not utilize any of the features nor align with the intent of the Strawberry() class. In addition, Strawberry() takes up a lot of memory because openpyxl data structures take up a lot of memory (~2.5 GB for a 50MB Excel file reportedly) which may become a problem if using an LLM/NMT locally.
#Even if importing to dictionary from .csv/.xlsx/.xls/.ods to a dictionary instead of an openpyxl data structure, the rule is that the first entry is headers, so the first key=value entry must be skipped regardless.
def importDictionaryFromCSV(myFile, myFileEncoding,ignoreWhitespace=False):
    tempDict={}
    
    #print('Hello World'.encode(consoleEncoding))
    #Read entire file into memory
    #If there is an error reading the contents into memory, just close it.
    #try:
    #    inputFileHandle = open(fileToTranslateFileName,'r',encoding=myFileEncoding,errors=inputErrorHandling) #open in read only text mode #Will error out if file does not exist. io.open() works with both \ and / to traverse folders.
    #    myFileContents=inputFileHandle.read()
    #finally:
    #    inputFileHandle.close()

    tempKey=''
    tempValue=''
    index=0
    #'with' is correct. Do not use 'while'.
    with open(myFile, 'r', newline='', encoding=myFileEncoding, errors=inputErrorHandling) as myFileHandle:
        csvReader = csv.reader(myFileHandle)
        currentLine=0
        for line in csvReader:
            #skip first line
            if currentLine == 0:
                currentLine+=1
            elif currentLine != 0:
                if ignoreWhitespace == True:
                    for i in range(len(line)):
                        line[i]=line[i].strip()
                if line[1] == '':
                    line[1] = None
                tempDict[line[0]]=line[1]
 
#                 for i in range(len(line)):
#                    if index == 0:
#                        set tempKey=i
#                        index+=1
#                    elif index == 1:
#                        tempValue=i
#                        tempDict=
#                    else:
#                        sys.exit( 'Unspecified error.'.encode(consoleEncoding) )

    #tempSpreadsheet.append(line)
    #tempSpreadsheet.appendRow(line)
    #self.spreadsheet.append(line)
    return tempDict





def importDictionaryFromXLSX(myFile, myFileEncoding):
    print('Hello World'.encode(consoleEncoding))
    workbook = openpyxl.load_workbook(filename=myFile) #, data_only=)
    spreadsheet=workbook.active


def importDictionaryFromXLS(myFile, myFileEncoding):
    print('Hello World'.encode(consoleEncoding))

def importDictionaryFromODS(myFile, myFileEncoding):
    print('Hello World'.encode(consoleEncoding))




"""
#Usage examples, assuming this library is in a subfolder named 'resources':
defaultEncoding='utf-8'
myFileName = 'myFile.txt'

from resources/py3TranslateLLMfunctions import *

py3TranslateLLMfunctions

if dealWithEncodingLibraryIsAvailable == True:
    #Update internal library variables to match main program settings.
    dealWithEncoding.debug=debug
    dealWithEncoding.consoleEncoding=consoleEncoding

    inputEncodingType = dealWithEncoding.ofThisFile(myFileName=inputFileName, rawCommandLineOption=command_Line_arguments.inputEncoding, fallbackEncoding=defaultEncodingType)

    #or, to use only positional arguments
    inputEncodingType = dealWithEncoding.ofThisFile(inputFileName, command_Line_arguments.inputEncoding, defaultEncodingType)

    #or, To detect encoding of a file with the chardet library that has already been determined to exist, and does not consider user preferences, fallback encoding, or a return of None from the chardet library:
    inputEncodingType= dealWithEncoding.detectEncoding(inputFileName)
else:
    inputEncodingType=defaultEncoding

print(inputFileName+' will use encoding type: '+inputEncodingType)

"""
