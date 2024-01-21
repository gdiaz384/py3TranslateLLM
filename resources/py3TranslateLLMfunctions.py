#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: A helper/wrapper library to aid in using openpyxl as a data structure.

Usage: See below. Like at the bottom.

License: See main program.

##stop reading now##

"""
#set defaults
printStuff=True
verbose=False
debug=False
#debug=True
consoleEncoding='utf-8'
inputErrorHandling='strict'
#outputErrorHandling='namereplace'
linesThatBeginWithThisAreComments='#'
assignmentOperatorInSettingsFile='='
#metadataDelimiter='_'

#These must be here or the library will crash even if these modules have already been imported by main program.
import os, os.path                      #Extract extension from filename, and test if file exists.
from pathlib import Path            #Override file in file system with another and create subfolders.
import sys                                   #End program on fail condition.
import io                                      #Manipulate files (open/read/write/close).
import datetime                          #Used to get current date and time.
import csv                                    #Read and write to csv files. Example: Read in 'resources/languageCodes.csv'
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


#Returns True or False depending upon if file exists or not.
def checkIfThisFileExists(myFile):
    #Check if name of file was never set.
    if myFile == None:
        return False
    if os.path.isfile(myFile) != True:
        return False
    else:
        return True
#Usage:
#checkIfThisFileExists('myfile.csv')
#checkIfThisFileExists(myVar)


#Errors out if myFile does not exist.
def verifyThisFileExists(myFile,nameOfFileToOutputInCaseOfError=None):
    #Check if name of file was never set.
    if myFile == None:
        sys.exit(('\n Error: Please specify a valid file for: '+str(nameOfFileToOutputInCaseOfError) + usageHelp).encode(consoleEncoding))
    #Check if file exists. Example: 'scratchpad/ks_testFiles/A01.ks'
    if os.path.isfile(myFile) != True:
        sys.exit( (' Error: Unable to find file \'' + str(nameOfFileToOutputInCaseOfError) + '\' ' + usageHelp).encode(consoleEncoding) )
#Usage:
#verifyThisFileExists('myfile.csv','myfile.csv')
#verifyThisFileExists(myVar, 'myVar')




#This function reads program settings from text files using a predetermined list of rules.
#The text file uses the syntax: setting=value, # are comments, empty/whitespace lines ignored.
#This function builds a dictionary and then returns it to the caller.
def readSettingsFromTextFile(fileNameWithPath, fileNameEncoding, consoleEncoding=consoleEncoding, errorHandlingType=inputErrorHandling,debug=debug):
    #print('Hello World'.encode(consoleEncoding))
    #return 'pie'
    if fileNameWithPath == None:
        print( ('Cannot read settings from null entry: '+fileNameWithPath ).encode(consoleEncoding) )
        return None

    #check if file exists   'scratchpad/ks_testFiles/A01.ks'
    if os.path.isfile(fileNameWithPath) != True:
        sys.exit( ('\n Error: Unable to find input file \''+ fileNameWithPath + '\'' + usageHelp).encode(consoleEncoding) )
    #then read entire file into memory
    #If there is an error reading the contents into memory, just close it.
    try:
        inputFileHandle = open(fileNameWithPath,'r',encoding=fileNameEncoding, errors=errorHandlingType) #open in read only text mode #Will error out if file does not exist.
        #open() works with both \ and / to traverse folders.
        inputFileContents=inputFileHandle.read()
    finally:
        inputFileHandle.close()#Always executes, probably.

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

        inputFileContents=inputFileContents.partition('\n')[2] #Finished processing line, so remove current line from string to prepare to process next line.

    #Finished reading entire file, so return resulting dictionary.
    if debug == True:
        print( (fileNameWithPath+' was turned into this dictionary='+str(tempDictionary)).encode(consoleEncoding) )
    return tempDictionary


#parseRawInputTextFile() accepts an (input file name, the encoding for that text file, parseFileDictionary as a Python dictionary, the character dictionary as a Python dictionary) and returns a dictionary where the key is the dialogue, and the value is a list. The first value in the list is the character name, (or None for no chara name), and the second is metadata as a string using the specified delimiter.
#This could also be a multidimension array, such as a list full of list pairs [ [ [],[ [][][] ] ] , [ [],[ [][][] ] ] ] because the output is highly regular, but that would allow duplicates. Executive decision was made to disallow duplicates for files since that is correct almost always. However, it does mess with the metadata sometimes by having the speaker be potentially incorrect.

def parseRawInputTextFile(inputFile,inputFileEncoding,characterDictionary):

    #The file has already been checked to exist and the encoding correctly determined, so just open it and read contents into a string. Then use that epicly long string for processing.
    #Goal is to fill this string:
    inputFileContents=''

    #TODO: Put stuff here. 
    #maybe....
    #openpyxlHelpers.importFromTextFile(fileName, fileNameEncoding, parseFile, parseFileEncoding)
    #What are valid inputs? .csv, .xlsx, .xls, .ods, .txt, .ks, .ts (t-script)
    #.csv, .xlsx, .xls, .ods are spreadsheet formats that follow a predefined format. They do not have parse files.
    #Therefore only .txt, .ks and .ts are valid inputs for openpyxlHelpers.importFromTextFile()

    #Read entire file into memory
    #If there is an error reading the contents into memory, just close it.
    try:
        inputFileHandle = open(fileToTranslateFileName,'r',encoding=inputFileEncoding,errors=inputFileEncoding) #open in read only text mode #Will error out if file does not exist. io.open() works with both \ and / to traverse folders.
        inputFileContents=inputFileHandle.read()
    finally:
        inputFileHandle.close()#always executes, probably


    temporaryDict={}        #Dictionaries do not allow duplicates, so insert all entries into a dictionary first to de-duplicate entries, then read dictionary into first column (skip first line/row in target spreadsheet)
    #thisdict.update({"x": "y"}) #add to/update dictionary
    #thisdict["x"]="y"              #add to/update dictionary
    #for x, y in thisdict.items():
    #  print(x, y) 

    temporaryString=None #set it to None (null) to initialize
    currentParagraphLineCount=0
    #while line is not empty (at least \n is present)
    while inputFileContents != '' :
        myLine=inputFileContents.partition('\n')[0] #returns first line of string to process in the current loop

        #debug code
        #print only if debug option specified
        if debug == True:
            print(myLine.encode(consoleEncoding)) #prints line that is currently being processed
        #myLine[:1]#this gets only the first character of a string #what will this output if a line contains only whitespace or only a new line #answer: '' -an empty string for new lines, but probably the whitespace for lines with whitespace
        if myLine[:1].strip() != '':#if the first character is not empty or filled with whitespace
            if debug == True:
                print(myLine[:1].encode(consoleEncoding))

        thisLineIsValid=True
        #if the line is empty, then always skip it. Regardless of paragraphDelimiter == emptyLine or newLine, empty lines signify a new paragraph start, or it would be too difficult to tell when one paragraph ends and another starts.
        if myLine.strip()[:1] == '':
            thisLineIsValid=False
            #if paragraphDelimiter == 'emptyLine': #Old code.  if paragraphDelimiter='newLine', then this is the same as line-by-line mode, right?
        #else the line is not empty or filled with only whitespace.
        else:
            #if the first character is an ignore character or if the first character is whitespace, then set thisLineIsValid=False
            for i in ignoreLinesThatStartWith:
                if myLine.strip()[:1] == i:   #This should strip whitespace first, and then compare because sometimes dialogue can be indented but still be valid. Valid syntax: myLine.strip()[:1] 
                    #It is possible that this line is still valid if the first non-whitespace characters in the line are an entry from the charaname dictionary.
                    #TODO. Need to check for this.
                    #This will print the full string without returning an error. Use this logic to do a string comparison of myLine with the keys in characterDictionary.
                    #x = 'pie2'
                    #print(x[:9])
                    thisLineIsValid=False


                        #There is some code at the bottom of the main .py that will need to be integrated into this spot.



        if thisLineIsValid == False: 
            #then commit any currently working string to databaseDatastructure, add to temporary dictionary to be added later
            if temporaryString != None:
                #The True/False means, if True, the current line has been modified by a dictionary and so is not a valid line to insert into cache, ...if that feature ever materializes.
                temporaryDict[temporaryString]=str(currentParagraphLineCount)+'!False'
            #and start a new temporaryString
            temporaryString=None
            #and reset currentParagraphLineCount
            currentParagraphLineCount=0
        #while myLine[:1] != the first character is not an ignore character, #while the line is valid to feed in as input, then
        elif thisLineIsValid != True:
            #if the newLine after .strip() == '' #an empty string
                #then end of paragraph reached. Commit any changes to temporaryString if there are any
                #and break out of loop
            #if temporaryString is not empty, then append \n to temporaryString, and
            if temporaryString != None:
                #then append \n first, and then add line to temporaryString
                temporaryString=temporaryString+'\n'+myLine.strip()
                #increment currentParagraphLineCount by 1
                currentParagraphLineCount+=1
            #else if temporaryString is currently empty
            elif temporaryString == None:
                #then just append to temporaryString without \n
                temporaryString = myLine.strip()
                #and increment counter
                currentParagraphLineCount+=1
            else:
                sys.exit('Unspecified error.'.encode(consoleEncoding))
            #if max paragraph limit has been reached
            if (currentParagraphLineCount >= maximumNumberOfLinesPerParagraph) or (paragraphDelimiter == 'newLine'):  
                #then commit currently working string to databaseDatastructure, #add to temporary dictionary to be added later
                #The True/False means, if True, the current line has been modified by a dictionary and so is not a valid line to insert into cache, ...if that feature ever materializes.
                temporaryDict[temporaryString]=str(currentParagraphLineCount)+'!False'
                #and start a new temporaryString
                temporaryString=None
                #and reset counter
                currentParagraphLineCount=0
        else:
            sys.exit('Unspecified error.'.encode(consoleEncoding))

        #remove the current line from inputFileContents, in preparating for reading the next line of inputFileContents
        inputFileContents=inputFileContents.partition('\n')[2] #removes first line from string
        #continue processing file onto next line normally without database insertion code until file is fully processed and dictionary is filled
        #Once inputFileContents == '', the loop will end and the dictionary can then be fed into the main database.

    #debug code
    if inputFileContents == '' :
        print('inputFileContents is now empty of everything including new lines.'.encode(consoleEncoding))
        #feed temporaryDictionary into spreadsheet #Edit: return dictionary instead.
        return temporaryDict



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

##TODO: Update this into functions so it returns the current day, time, and full (day+time)
#print(datetime.today().strftime('%Y-%m-%d'))
today=datetime.datetime.today()
#print(today.strftime("%d/%m/%Y %H:%M:%S"))
currentYear=today.strftime('%Y')
currentMonth=getCurrentMonthFromNumbers(today.strftime('%m'))
currentDay=today.strftime('%d')
currentDateFull=currentYear+currentMonth+currentDay

currentHour=today.strftime('%H')
currentMinutes=today.strftime('%M')
currentSeconds=today.strftime('%S')
currentTimeFull=currentHour+'-'+currentMinutes+'-'+currentSeconds

currentDateAndTimeFull=currentDateFull+'-'+currentTimeFull

if (verbose == True) or (debug == True):
    print(currentDateAndTimeFull.encode(consoleEncoding))









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
    with open(myFile, newline='', encoding=myFileEncoding, errors=inputErrorHandling) as myFileHandle:
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

def importDictionaryFromXLS(myFile, myFileEncoding):
    print('Hello World'.encode(consoleEncoding))

def importDictionaryFromXLS(myFile, myFileEncoding):
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
