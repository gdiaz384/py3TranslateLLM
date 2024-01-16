#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
py3TranslateLLM.py translates text using Neural net Machine Translation (NMT) and Large Language Models (LLM).

For usage, see py3TranslateLLM.py -h', README.md, and the source code below.

License:
- For the various libraries used, see their licenses in their respective project pages.
- This .py file is C* gdiaz384 and licensed as GNU Affero GPL v3.
- Feel free to use it, modify it, and distribute it to an unlimited extent, but if you distribute binary files of this program outside of your organization, then please make the source code for those binaries available. The imperative to make source code available also applies if using this program as part of a server if that server is publically accessible.

"""
#import various libraries that py3TranslateLLM depends on
import argparse                 #used to add command line options
import os, os.path              #extract extension from filename, and test if file exists
import sys                         #end program on fail condition
import io                            #manipulate files (open/read/write/close)
from pathlib import Path     #override file in file system with another, experimental library
#from io import IOBase      #test if variable is a file object (an "IOBase" object)
from datetime import datetime #used to get current date and time
from collections import deque #Used to hold rolling history of translated items to use as context for new translations
import requests                #do basic http stuff, like submitting post/get requests to APIs. This library must be installed using: pip install requests
from openpyxl import Workbook #used as the core internal data structure and also to read/write xlsx files
import csv                          #Read and write to csv files. Example: Read in 'resources/languageCodes.csv'
import codecs                 #Improves error handling when dealing with text file codecs.
import resources.dealWithEncoding as dealWithEncoding   #This implements the 'chardet' library which is installed with 'pip install chardet'


#set defaults and static variables
version='v0.1 - 2024Jan16'

defaultTextEncoding='utf-8'
defaultTextEncodingForKSFiles='shift-jis'
defaultConsoleEncodingType='utf-8'
defaultLanguageCodesFile='resources/languageCodes.csv'
defaultSourceLanguage='Japanese'
defaultTargetLanguage='English'
#defaultInvalidOption='invalid'
defaultKoboldCppPort=5001
defaultSugoiPort=14366
#defaultSugoiPort=14467
defaultInputEncodingErrorHandler='strict'
defaultOutputEncodingErrorHandler='namereplace'

translationEngines='parseOnly, koboldcpp, deepl_api_free, deepl_api_pro, deepl_web, sugoi'
usageHelp='\n Usage: python py3TranslateLLM --help  Example: py3TranslateLLM KoboldCpp -file myInputFile.ks\n Translation Engines: '+translationEngines+'.'

#add command line options
commandLineParser=argparse.ArgumentParser(description='Description: CLI wrapper script for various NMT and LLM models.' + usageHelp)
commandLineParser.add_argument('translationEngine', help='Specify translation engine to use, options='+translationEngines+'.',type=str)

commandLineParser.add_argument('-file', '--fileToTranslate', help='The raw file name to translate, including path.',default=None,type=str)
commandLineParser.add_argument('-fe', '--fileToTranslateEncoding', help='Specify input file encoding, default='+defaultTextEncoding,type=str)
commandLineParser.add_argument('-pfile', '--parsingDefinitions', help='This file defines how to parse raw text and .ks files. It is required for text and .ks files. If not specified, a template will be created.', default=None,type=str)
commandLineParser.add_argument('-pfe', '--parsingDefinitionsEncoding', help='Specify encoding for parsing definitions file, default='+defaultTextEncoding,type=str)
commandLineParser.add_argument('-sl', '--sourceLanguage', help='Specify language of source text. Default='+defaultSourceLanguage, default=defaultSourceLanguage,type=str)
commandLineParser.add_argument('-tl', '--targetLanguage', help='Specify language of source text. Default='+defaultTargetLanguage, default=defaultTargetLanguage,type=str)

commandLineParser.add_argument('-cn', '--characterNamesDictionary', help='The file name and path of characterNames.csv',default=None,type=str)
commandLineParser.add_argument('-cne', '--characterNamesDictionaryEncoding', help='The encoding of file characterNames.csv, Default='+defaultTextEncoding,type=str)
commandLineParser.add_argument('-pred', '--preTranslationDictionary', help='The file name and path of preTranslation.csv',default=None,type=str)
commandLineParser.add_argument('-prede', '--preTranslationDictionaryEncoding', help='The encoding of file preTranslation.csv. Default='+defaultTextEncoding,type=str)
commandLineParser.add_argument('-postd', '--postTranslationDictionary', help='The file name and path of postTranslation.csv.',default=None,type=str)
commandLineParser.add_argument('-postde', '--postTranslationDictionaryEncoding', help='The encoding of file postTranslation.csv. Default='+defaultTextEncoding,type=str)
commandLineParser.add_argument('-lcf', '--languageCodesFile', help='Specify a custom name and path for languageCodes.csv. Default=\''+defaultLanguageCodesFile+'\'.',default=defaultLanguageCodesFile,type=str)
commandLineParser.add_argument('-lcfe', '--languageCodesFileEncoding', help='The encoding of file languageCodes.csv, default='+defaultTextEncoding,type=str)

commandLineParser.add_argument('-lbl', '--lineByLineMode', help='Store and translate lines one at a time. Disables grouping lines by delimitor and paragraph translations.',action='store_true')
commandLineParser.add_argument('-r', '--resume', help='Attempt to resume previously interupted operation. No gurantees.',action='store_true')
commandLineParser.add_argument('-a', '--address', help='Specify the protocol and IP for NMT/LLM server, Example: http://192.168.0.100',default=None,type=str)
commandLineParser.add_argument('-p', '--port', help='Specify the port for the NMT/LLM server. Example: 5001',default=None,type=str)

commandLineParser.add_argument('-ieh', '--inputErrorHandling', help='If the wrong input codec is specified, how should the resulting conversion errors be handled? See: docs.python.org/3.7/library/codecs.html#error-handlers Default=\''+defaultInputEncodingErrorHandler+'\'.',default=defaultInputEncodingErrorHandler,type=str)
commandLineParser.add_argument('-eh', '--outputErrorHandling', help='How should output conversion errors between incompatible encodings be handled? See: docs.python.org/3.7/library/codecs.html#error-handlers Default=\''+defaultOutputEncodingErrorHandler+'\'.',default=defaultOutputEncodingErrorHandler,type=str)
commandLineParser.add_argument('-ce', '--consoleEncoding', help='Specify encoding for standard output, default='+defaultConsoleEncodingType,default=defaultConsoleEncodingType,type=str)
commandLineParser.add_argument('-vb', '--verbose', help='Print more information.',action='store_true')
commandLineParser.add_argument('-d', '--debug', help='Print too much information.',action='store_true')
commandLineParser.add_argument('-v', '--version', help='Print version information and exit.',action='store_true')    

#import options from command line options
commandLineArguments=commandLineParser.parse_args()

consoleEncoding=commandLineArguments.consoleEncoding


if commandLineArguments.version == True:
    sys.exit('\n '+version)
translationEngine=commandLineArguments.translationEngine

fileToTranslateFileName=commandLineArguments.fileToTranslate
#Overall: If an encoding was not specified for inputFile, and the extension is .ks, then default to shift-jis encoding and warn user of change.
#if an input file name was specified, then
if fileToTranslateFileName != None:
    fileToTranslateFileNameOnly, fileToTranslateFileNameExtensionOnly = os.path.splitext(fileToTranslateFileName)
    #print(fileToTranslateFileNameOnly)
    #print('Extension:'+fileToTranslateFileNameExtensionOnly)
    #if no encoding was specified, then...
    if commandLineArguments.fileToTranslateEncoding == None:
        if fileToTranslateFileNameExtensionOnly == '.ks':
            fileToTranslateEncoding=defaultTextEncodingForKSFiles #set encoding to shift-jis
            print('Note: KAG3 (.ks) input file specified, but no encoding was specified. Defaulting to '+defaultTextEncodingForKSFiles+' instead of '+defaultTextEncoding+'. If this behavior is not desired or produces corrupt input, please specify an encoding using --fileToTranslateEncoding (-fe) option instead.')
        else:
            #If a file was specified, and if an encoding was not specified, and if the file is not a .ks file, then try to detect encoding
            #fileToTranslateEncoding=defaultTextEncoding#set encoding to default encoding
            fileToTranslateEncoding = dealWithEncoding.ofThisFile(fileToTranslateFileName, commandLineArguments.fileToTranslateEncoding, defaultTextEncoding)
    else:
        fileToTranslateEncoding=commandLineArguments.fileToTranslateEncoding#set encoding to user specified encoding
else:
    fileToTranslateEncoding=defaultTextEncoding#if an input file name was not specified, set encoding to default encoding

parsingDefinitionsFileName=commandLineArguments.parsingDefinitions
parsingDefinitionsEncoding=commandLineArguments.parsingDefinitionsEncoding
sourceLanguageRaw=commandLineArguments.sourceLanguage
targetLanguageRaw=commandLineArguments.targetLanguage

charaNamesDictionaryFileName=commandLineArguments.characterNamesDictionary
#charaNamesDictionaryEncoding=commandLineArguments.characterNamesDictionaryEncoding
preDictionaryFileName=commandLineArguments.preTranslationDictionary
#preDictionaryEncoding=commandLineArguments.preTranslationDictionaryEncoding
postDictionaryFileName=commandLineArguments.postTranslationDictionary
#postDictionaryEncoding=commandLineArguments.postTranslationDictionaryEncoding
languageCodesFileName=commandLineArguments.languageCodesFile
#languageCodesEncoding=commandLineArguments.languageCodesFileEncoding

lineByLineMode=commandLineArguments.lineByLineMode
resume=commandLineArguments.resume
address=commandLineArguments.address  #must be reachable, how to test for that?
port=commandLineArguments.port                #port should be conditionaly guessed, if no port specified and an address was specified, then try to guess port as either 80 or 443 depending upon protocol



verbose=commandLineArguments.verbose
debug=commandLineArguments.debug



#



#parse imported command line option values and continue validating input combinations
#or... either a raw.unparsed.txt or a raw.untranslated.csv if selecting one of the other engines
#or NMT without address option, Also warn about defaulting to specific port.

mode='invalid'
implemented=False
#validate input from command line options
if (translationEngine.lower()=='parseonly'):
    mode='parseOnly'
    implemented=True
elif (translationEngine.lower()=='koboldcpp'):
    mode='koboldcpp'
    implemented=True
elif (translationEngine.lower()=='deepl_api_free') or (translationEngine.lower()=='deepl-api-free'):
    mode='deepl_api_free'
    #import deepl
elif (translationEngine.lower()=='deepl_api_pro') or (translationEngine.lower()=='deepl-api-pro'):
    mode='deepl_api_pro'
elif (translationEngine.lower()=='deepl_web') or (translationEngine.lower()=='deepl-web'):
    mode='deepl_web'
elif (translationEngine.lower()=='sugoi'):
    mode='sugoi'
else:
    sys.exit(('\n Error. Invalid translation engine specified: "' + translationEngine + '"' + usageHelp).encode(consoleEncoding))

print(('Mode is set to: \''+mode+'\'').encode(consoleEncoding))
if implemented == False:
    sys.exit(('\n\"'+mode+'\" not yet implemented. Please pick another translation engine. \n Translation engines: '+ translationEngines).encode(consoleEncoding))


#validate: a valid file (raw.unparsed.txt and parseDefinitionsFile.txt) must exist if using parseOnly 
#fileToTranslateFileNameOnly, fileToTranslateFileNameExtensionOnly = os.path.splitext(fileToTranslateFileName)
if mode == 'parseOnly':
    #check if -file exists   'scratchpad/ks_testFiles/A01.ks'
    if os.path.isfile(fileToTranslateFileName) != True:
        sys.exit(('\n Error: Please specify a valid input file. \n' + usageHelp).encode(consoleEncoding))

    #check if file exists   'scratchpad/ks_testFiles/A01.ks'
    if os.path.isfile(fileToTranslateFileName) != True:
        if fileToTranslateFileName == 'invalid.txt':
            sys.exit(('\n Error: Please specify a valid input file. \n' + usageHelp).encode(consoleEncoding))
        else:
            sys.exit(('\n Error: Unable to find input file "' + fileToTranslateFileName + '"\n' + usageHelp).encode(consoleEncoding))

    #check if valid parsing definition file exists 'scratchpad/ks_testFiles/A01.ks'
    if os.path.isfile(fileToTranslateFileName) != True:
        if fileToTranslateFileName == 'invalid.txt':
            sys.exit(('\n Error: Please specify a valid input file. \n' + usageHelp).encode(consoleEncoding))
        else:
            sys.exit(('\n Error: Unable to find input file "' + fileToTranslateFileName + '"\n' + usageHelp).encode(consoleEncoding))




if sourceLanguageRaw.lower() == 'english':
    sourceLanguageRaw = 'English (American)'
elif sourceLanguageRaw.lower() == 'castilian':
    sourceLanguageRaw = 'Spanish'
elif sourceLanguageRaw.lower() == 'chinese':
    sourceLanguageRaw = 'Chinese (simplified)'
elif sourceLanguageRaw.lower() == 'portuguese':
    sourceLanguageRaw = 'Portuguese (European)'

if targetLanguageRaw.lower() == 'english':
    targetLanguageRaw = 'English (American)'
elif targetLanguageRaw.lower() == 'castilian':
    targetLanguageRaw='Spanish'


###### define various helper functions, especially for main openpyxl data structure ###### 


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

#print(datetime.today().strftime('%Y-%m-%d'))
today=datetime.today()
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

#TODO. Export an existing spreadsheet to a file.
#reference it using the workbook, not the active spreadsheet
def exportToCSV(workBook, nameWithoutExtension):
    print('Hello World'.encode(consoleEncoding))
def exportToXLSX(workBook, nameWithoutExtension):
    print('Hello World'.encode(consoleEncoding))
    #theWorkbook.save(filename="myAwesomeSpreadsheet.xlsx")
    workBook.save(filename=nameWithoutExtension+".xlsx")
def exportToODF(workBook, nameWithoutExtension):
    print('Hello World'.encode(consoleEncoding))


#This function returns a list containing 2 strings that represent a row and column extracted from input Cell address
#such as returning ['5', 'B'] from: <Cell 'Sheet'.B5>   It also works for complicated cases like AB534.
def getRowAndColumnFromCell(myInputCell):
    #print('raw cell data='+str(myInputCell))
    #basically, split the string according to . and then split it again according to > to get back only the CellAddress
    myInputCell=str(myInputCell).split('.', maxsplit=1)[1].split('>')[0]
    index=0
    for i in range(10):
        try:
            int(myInputCell[index:index+1])
            index=i
            break #this break and the assignment above will only execute when the int conversion works
        except:
            #this will execute if there is an error, like int('A')
            #this will not execute if the int conversion succeds
            #print('index='+str(index))
            pass
        index+=1
    currentColumn=myInputCell[:index]#does not include character in string[Index] because index is after the :
    currentRow=myInputCell[index:]#includes character specified by string[index] because index is before the :
    #return ['pie', 'apple']
    return [currentRow, currentColumn]

#Example:
#myRawCell=''
#for row in mySpreadsheet:
#    for i in row:
#        if i.value == 'lots of pies':
#            print(str(i) + '=' + str(i.value))
#            myRawCell=i
#currentRow, currentColumn = getRowAndColumnFromCell(myRawCell)


#helper function that changes the data for a row in mySpreadsheet to what is specified in a python List []
#Note: This is only for modifying existing rows and only for mySpreadsheet. To add a brand new row, use append:
    #Example: newRow = ['pies', 'lots of pies']
    #mySpreadsheet.append(newRow)
#The rowLocation specified is the nth rowLocation, not the [0,1,2,3...row] because rows start with 1
def replaceRow(newRowDataInAList, rowLocation):
    global mySpreadsheet
    print(str(len(newRowDataInAList)).encode(consoleEncoding))
    print(str(range(len(newRowDataInAList))).encode(consoleEncoding))
    for i in range(len(newRowDataInAList)):
        #columns begin with 1 instead of 0, so add 1 when referencing the target column, but not the source
        mySpreadsheet[getCell(mySpreadsheet.cell(row=int(rowLocation), column=i+1))]=newRowDataInAList[i]

#Example: replaceRow(newRow,7)


#this returns either None if there is no cell with the search term, or it will return the raw cell address if it found it, case sensitive
#to determine the row, the column, or both from the raw cell address, call getRowAndColumnFromCell(rawCellAddress)
def searchHeader(spreadsheet, searchTerm):
    cellFound=None
    for row in spreadsheet[1]:
        for i in row:
            if i.value == searchTerm:
                cellFound=i
        #if cellFound != None:
        #    print('found')
        #else:
        #    print('notfound')
        break #stop searching after first row
    return cellFound

#Example:
#cellFound=None
#isFound=searchHeader(mySpreadsheet,searchTerm)
#if isFound == None:
#    print('was not found')
#else:
#    print('searchTerm:\"'+searchTerm+'" was found at:'+str(isFound))


#This returns either None if there is no cell with the search term, or the raw cell address. Case and whitespace sensitive.
#To determine the row, the column, or both from the raw cell address, use getRowAndColumnFromCell(rawCellAddress)
def searchSpreadsheet(spreadsheet, searchTerm):
    for row in spreadsheet.iter_rows():
        for cell in row:
            if cell.value == searchTerm:
                return cell
    return None


#These return either None if there is no cell with the search term, or the raw cell address. Case insensitive. Whitespace sensitive.
#To determine the row, the column, or both from the raw cell address, use getRowAndColumnFromCell(rawCellAddress)
def searchRowsCaseInsensitive(spreadsheet, searchTerm):
    for row in spreadsheet.iter_rows():
        for cell in row:
            if isinstance(cell.value, str):
                if cell.value.lower() == str(searchTerm).lower():
                    return cell
    return None

def searchColumnsCaseInsensitive(spreadsheet, searchTerm):
    for column in spreadsheet.iter_cols():
        for cell in column:
            if isinstance(cell.value, str):
                if cell.value.lower() == str(searchTerm).lower():
                    return cell
    return None


#give this function a spreadsheet object (subclass of workbook) and it will print the contents of that sheet
def printAllTheThings(mySpreadsheetName):
    for row in mySpreadsheetName.iter_rows(min_row=1, values_only=True):
        temp=''
        for cell in row:
            temp=temp+','+str(cell)
        print(temp[1:].encode(consoleEncoding))#ignore first , in output

#Example: printAllTheThings(mySpreadsheet)



#Format specificiation for languageCodes.csv
#Name of language in English, ISO 639 Code, ISO 639-2 Code
#https://www.loc.gov/standards/iso639-2/php/code_list.php
#(Mostly) only languages supported by DeepL are currently listed, case insensitive
#Language list is mostly from DeepL. The Syntax is:
#The first row is entirely headers (column labels). Starting from the 2nd row (row[1]):
#0) [languageNameReadable, 
#1) TwoLetterLanguageCodeThatIsNotAlwaysTwoLetters,
#2) ThreeLetterLanguageCodeThatIsNotAlwaysThreeLetters,
#3) DoesDeepLSupportThisLanguageTrueOrFalse,
#4) DoesThisLanguageNeedACustomSourceLanguageTrueOrFalse (for single source language but many target language languages like EN->EN-US/EN-GB)
#5) If #4 is True, then the full name source language
#6) If #4 is True, then the two letter code of the source language
#7) If #4 is True, then the three letter code of the source language
#Examples for 5-7: English, EN, ENG; Portuguese, PT, POR
#Each row/entry is eight columns total

#import languageCodes.csv, but first check to see if it exists
if os.path.isfile(languageCodesFileName) != True:
    sys.exit(('\n Error. Unable to find languageCodes.csv "' + languageCodesFileName + '"' + usageHelp).encode(consoleEncoding))

languageCodesWorkbook = Workbook()
languageCodesSpreadsheet = languageCodesWorkbook.active

#It looks like quoting fields in csv's that use commas , and new
#lines works but only as double quotes " and not single quotes '
#Spaces are also preserved as-is if they are within the ,
with open(languageCodesFileName, newline='', encoding=languageCodesEncoding) as myFile:
    csvReader = csv.reader(myFile)
    for line in csvReader:
        if debug == True:
            print(str(line).encode(consoleEncoding))
        #clean up whitespace for entities
        for i in range(len(line)):
            line[i]=line[i].strip()
        languageCodesSpreadsheet.append(line)

if debug == True:
    print('')
    print(('The following has been read from ' + str(languageCodesFileName)).encode(consoleEncoding))
    printAllTheThings(languageCodesSpreadsheet)

internalLanguageSourceName=None
internalLanguageSourceTwoCode=None
internalLanguageSourceThreeCode=None
internalLanguageDestinationName=None
internalLanguageDestinationTwoCode=None
internalLanguageDestinationThreeCode=None

sourceLanguageCell=None
#print(sourceLanguageRaw)

#Search for valid sourceLanguageRaw and targetLanguageRaw. Case insensitive.
for column in languageCodesSpreadsheet.iter_cols():
    for cell in column:
        if isinstance(cell.value, str):
            if cell.value.lower() == sourceLanguageRaw.lower():
                sourceLanguageCell=cell
                break
            #else:
                #cellVal=cell.value.lower()
                #print(cellVal)
                #srcLang=sourceLanguageRaw.lower()
                #print(srcLang)
                #print('"'+cellVal+'"!="'+srcLang+'"')

if sourceLanguageCell == None:
    sys.exit(('\n Error. The following language was not found in"' + languageCodesFileName + '":"' + sourceLanguageRaw+'"').encode(consoleEncoding))
else:
    print(('SourceLanguage:'+sourceLanguageRaw+':'+str(sourceLanguageCell)).encode(consoleEncoding))
#Assume sourceLanguageCell has a valid value now.
sourceLanguageRow, sourceLanguageColumn = getRowAndColumnFromCell(sourceLanguageCell)
#print(languageCodesSpreadsheet['A'+sourceLanguageRow].value)

if debug == True:
    print((str(languageCodesSpreadsheet['A'+sourceLanguageRow].value)).encode(consoleEncoding))
    print((str(languageCodesSpreadsheet['B'+sourceLanguageRow].value)).encode(consoleEncoding))
    print((str(languageCodesSpreadsheet['C'+sourceLanguageRow].value)).encode(consoleEncoding))
    print((str(languageCodesSpreadsheet['D'+sourceLanguageRow].value)).encode(consoleEncoding))
    print((str(languageCodesSpreadsheet['E'+sourceLanguageRow].value)).encode(consoleEncoding))
    print((str(languageCodesSpreadsheet['F'+sourceLanguageRow].value)).encode(consoleEncoding))
    print((str(languageCodesSpreadsheet['G'+sourceLanguageRow].value)).encode(consoleEncoding))
    print((str(languageCodesSpreadsheet['H'+sourceLanguageRow].value)).encode(consoleEncoding))

if str(languageCodesSpreadsheet['E'+sourceLanguageRow].value) == 'False':
    internalLanguageSourceName=languageCodesSpreadsheet['A'+sourceLanguageRow].value
    internalLanguageSourceTwoCode=languageCodesSpreadsheet['B'+sourceLanguageRow].value
    internalLanguageSourceThreeCode=languageCodesSpreadsheet['C'+sourceLanguageRow].value
elif str(languageCodesSpreadsheet['E'+sourceLanguageRow].value) == 'True':
    internalLanguageSourceName=languageCodesSpreadsheet['F'+sourceLanguageRow].value
    internalLanguageSourceTwoCode=languageCodesSpreadsheet['G'+sourceLanguageRow].value
    internalLanguageSourceThreeCode=languageCodesSpreadsheet['H'+sourceLanguageRow].value
else:
    print('')
    print((languageCodesSpreadsheet['E'+sourceLanguageRow].value).encode())
    sys.exit('Unspecified error.'.encode(consoleEncoding))

if debug == True:
    print(str(bool(languageCodesSpreadsheet['E'+sourceLanguageRow].value)).encode())
    print(internalLanguageSourceName.encode())
    print(internalLanguageSourceTwoCode.encode())
    print(internalLanguageSourceThreeCode.encode())

targetLanguageCell=None
#print(sourceLanguageRaw)

#targetLanguageCell = searchSpreadsheet(languageCodesSpreadsheet,targetLanguageRaw) #case sensitive, do not use

#Search for valid sourceLanguageRaw and targetLanguageRaw. Case insensitive.
for column in languageCodesSpreadsheet.iter_cols():
    for cell in column:
        if isinstance(cell.value, str):
            if cell.value.lower() == targetLanguageRaw.lower():
                targetLanguageCell=cell
                break
            #else:  #debug code
                #cellVal=cell.value.lower()
                #print(cellVal)
                #srcLang=targetLanguageRaw.lower()
                #print(srcLang)
                #print('"'+cellVal+'"!="'+srcLang+'"')

if targetLanguageCell == None:
    sys.exit(('\n Error. The following language was not found in"' + languageCodesFileName + '":"' + targetLanguageRaw+'"').encode(consoleEncoding))
else:
    print(('TargetLanguage:'+targetLanguageRaw+':'+str(targetLanguageCell)).encode(consoleEncoding))
#Assume targetLanguageCell has a valid value now.
targetLanguageRow, targetLanguageColumn = getRowAndColumnFromCell(targetLanguageCell)
#print(languageCodesSpreadsheet['A'+targetLanguageRow].value)

if debug == True:
    print((str(languageCodesSpreadsheet['A'+targetLanguageRow].value)).encode(consoleEncoding))
    print((str(languageCodesSpreadsheet['B'+targetLanguageRow].value)).encode(consoleEncoding))
    print((str(languageCodesSpreadsheet['C'+targetLanguageRow].value)).encode(consoleEncoding))
    print((str(languageCodesSpreadsheet['D'+targetLanguageRow].value)).encode(consoleEncoding))
    print((str(languageCodesSpreadsheet['E'+targetLanguageRow].value)).encode(consoleEncoding))
    print((str(languageCodesSpreadsheet['F'+targetLanguageRow].value)).encode(consoleEncoding))
    print((str(languageCodesSpreadsheet['G'+targetLanguageRow].value)).encode(consoleEncoding))
    print((str(languageCodesSpreadsheet['H'+targetLanguageRow].value)).encode(consoleEncoding))

if str(languageCodesSpreadsheet['E'+targetLanguageRow].value) == 'False':
    internalLanguageSourceName=languageCodesSpreadsheet['A'+targetLanguageRow].value
    internalLanguageSourceTwoCode=languageCodesSpreadsheet['B'+targetLanguageRow].value
    internalLanguageSourceThreeCode=languageCodesSpreadsheet['C'+targetLanguageRow].value
elif str(languageCodesSpreadsheet['E'+targetLanguageRow].value) == 'True':
    internalLanguageDestinationName=languageCodesSpreadsheet['F'+targetLanguageRow].value
    internalLanguageDestinationTwoCode=languageCodesSpreadsheet['G'+targetLanguageRow].value
    internalLanguageDestinationThreeCode=languageCodesSpreadsheet['H'+targetLanguageRow].value
else:
    print('')
    print(str(languageCodesSpreadsheet['E'+targetLanguageRow].value).encode(consoleEncoding))
    sys.exit('Unspecified error.'.encode(consoleEncoding))

if debug == True:
    print((str(bool(languageCodesSpreadsheet['E'+sourceLanguageRow].value))).encode(consoleEncoding))
    print(str(internalLanguageDestinationName).encode(consoleEncoding))
    print(str(internalLanguageDestinationTwoCode).encode(consoleEncoding))
    print(str(internalLanguageDestinationThreeCode).encode(consoleEncoding))

#check if file exists   'scratchpad/ks_testFiles/A01.ks'
if os.path.isfile(fileToTranslateFileName) != True:
    if fileToTranslateFileName == 'invalid.txt':
        sys.exit(('\n Error: Please specify a valid input file. \n' + usageHelp).encode(consoleEncoding))
    else:
        sys.exit(('\n Error: Unable to find input file "' + fileToTranslateFileName + '"\n' + usageHelp).encode(consoleEncoding))
#then read entire file into memory
#If there is an error reading the contents into memory, just close it.
try:
    inputFileHandle = open(fileToTranslateFileName,'rt',encoding=fileToTranslateEncoding) #open in read only text mode #Will error out if file does not exist, works with both \ and / to traverse folders
    inputFileContents=inputFileHandle.read()
finally:
    inputFileHandle.close()#always executes, probably

#debug code
#print(inputFileHandle.read().encode(consoleEncoding))
#inputFileHandle.close()  #tidy up

#CharaNamesDictionary time to shine
CharacterNames=['[＠クロエ]','Chloe']#change this to a dictionary
#If an ignored line starts with a character name, that could create problems, so swap names first, then parse lines into main database.
#if one was specified, import character definitions file, and perform swaps while inputfile is still in memory but has not yet been parsed line by line.
#inputFileContents.replaceStuffHere()

#somehow this line needs to run
inputFileContents=inputFileContents.replace('[＠クロエ]','Chloe')


#Import parse settings from parsingDefintionsFile, if parsing is required which is if....
#if... parseOnly mode specified, resume has not specified (resume implies there is a file under backup/)
#always parse regardless of mode if one is specified, and then import data from other sources as it becomes available. Keep track of whether or not main data structure exists, or is supposed to be created from resume data (backup/ folder, csv, xls/xlsx, ods).
ignoreLinesThatStartWith=[ '[' , '*' , ';' , '【' ]     #this is a list of strings where each entry contains a character that marks a line to skip processing it, only one character is considered per entry
paragraphDelimitor='emptyLine'         #Valid options: emptyLine, newLine  #Once input has started, when should it stop? Input will stop automatically regardless of this setting when maximumParagraphSize is reached.
maximumNumberOfLinesPerParagraph=3        #Maximum number of lines per paragraph. A sane setting for this is 2-5 lines maximum per paragraph.
#What is the maximum length for translated text before triggering word wrap? The correct setting for this depends on
#the font used, which can sometimes be changed by the user at runtime, and the target language.
#Sane values are 30-60. This setting strongly influences the number of calculated output lines.
wordWrap=45
#The number of untranslated input lines will not always match the number of translated output lines, especially with
#different wordWrap amounts. How should this situation be handled? Valid values are: none, strict, dynamic.
#none=Disable word wrapping and always dump all translated text onto one line. Replace subsequent untranslated lines with empty lines.
#strict=If the number of input lines and translated lines match exactly, then replace as normal. Otherwise, do nothing.
    #The lines with a mismatch will be placed into a 'mixmatch.xlsx' file, and it is the user's responsibility to sort through those lines.
#dynamic=If there are fewer lines after translation, replace the extra untranslated lines with empty lines.
    #If there are more lines after translation, then append the extra lines to the last untranslated line.
wordWrapMode='dynamic'


#initialize main data structure
mainDatabaseWorkbook = Workbook()
mainDatabaseSpreadsheet = mainDatabaseWorkbook.active

#This will hold raw untranslated text, number of lines each entry was derived from, and columns containing maybe translated data. Maximum columns supported = 9[?]. Columns 0 and 1 are reserved for Raw untranslated text and [1] is reserved for the number of lines that column 0 represents, even if it is always 1 because line-by-line parsing (lineByLineMode) is specified.
#Alternatively, lineByLineMode can instead specify to feed each line into the translator but the paragraphDelimitor=emptyLine can support multiple lines in the main data structure. That might be more flexible, or make things worse. Leave it to user to decide on a case-by-case basis by allowing for this possibility.
#class Database:
#    def __init__(self):
#This data structure must somehow hold:
#1) each paragraph.raw.text (with \n's inside of it)
#2) metadata (# of lines #1 was taken from, and possibly the line number of the entry, possibly multiple entries metadata, possibly arbitary data to be decided later like booleans or whether the line has been translated or not), maybe a list?
#Translated or not decision should be computed dynamically and on a line-by-line basis (raw + chosen translator engine determined from header) in order to support resume operations, do not add to metadata
#For now use the following string:  'numberOfSourceLines!WasADictionaryUsedTrueOrFalse' ex. '2!False!'
#3) all translations, each with its own entry and an associated header for which type it is (Kobold+model;
#for DeepL, DeepL API Free/Pro and DeepL Web should all be the same right? Free, Pro, and Web versions all support dictionaries, but doing dictionary + document translation requires pro. Documents will be parsed prior to using the API, so this limitation does not apply here, thus all DeepL translations should be the same. DeepL's native dictionary system is also unlikely to be implemented here especially considering they are hard to work with (not mutable).
#4) potentially, koboldcpp LLM could return different models. Use the returned model header name. All data should be put in that column. Determine correct header as in: DeepL, or koboldcpp/model in a case sensitive way. More examples:
#headers=['rawText', 'metadata', 'DeepL', 'koboldcpp/Mixtral-13B.Q8_0','Google']

#Add headers
initialHeaders=['rawText','metadata']
mainDatabaseSpreadsheet.append(initialHeaders)

#printAllTheThings(mainDatabaseSpreadsheet)

#start parsing input file line by line
#print(inputFileContents.encode(consoleEncoding))
#print(inputFileContents.partition('\n')[0].encode(consoleEncoding)) #prints only first line

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

     #if the first character is an ignore character or if the first character is whitespace, then set invalidLine=True
    invalidLine=False
    for i in ignoreLinesThatStartWith:
        if myLine[:1].strip() == i:
            invalidLine=True
    if myLine[:1].strip() == '':
        if paragraphDelimitor == 'emptyLine': #_if paragraphDelimitor='newLine', then this is the same as line-by-line mode, right?
            invalidLine=True
        pass

    if invalidLine == True: 
        #then commit any currently working string to databaseDatastructure, add to temporary dictionary to be added later
        if temporaryString != None:
            #The True/False means, if True, the current line has been modified by a dictionary and so is not a valid line to insert into cache, ...if that feature ever materializes.
            temporaryDict[temporaryString]=str(currentParagraphLineCount)+'!False'
        #and start a new temporaryString
        temporaryString=None
        #and reset currentParagraphLineCount
        currentParagraphLineCount=0
    #while myLine[:1] != the first character is not an ignore character, #while the line is valid to feed in as input, then
    else:
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
        if (currentParagraphLineCount >= maximumNumberOfLinesPerParagraph) or (paragraphDelimitor == 'newLine'):  
            #then commit currently working string to databaseDatastructure, #add to temporary dictionary to be added later
            #The True/False means, if True, the current line has been modified by a dictionary and so is not a valid line to insert into cache, ...if that feature ever materializes.
            temporaryDict[temporaryString]=str(currentParagraphLineCount)+'!False'
            #and start a new temporaryString
            temporaryString=None
            #and reset counter
            currentParagraphLineCount=0

    #remove the current line from inputFileContents, in preparating for reading the next line of inputFileContents
    inputFileContents=inputFileContents.partition('\n')[2] #removes first line from string
    #continue processing file onto next line normally without database insertion code until file is fully processed and dictionary is filled
    #Once inputFileContents == '', the loop will end and the dictionary can then be fed into the main database.

#debug code
if inputFileContents == '' :
    print('inputFileContents is now empty of everything including new lines.'.encode(consoleEncoding))
    #feed temporaryDictionary into spreadsheet
    currentRow=2
    #for ever item in the dictionary
    #print(str(temporaryDict).encode(consoleEncoding))
    for text, metadata in temporaryDict.items():
        #print(text.encode(consoleEncoding))
        #print(metadata.encode(consoleEncoding))
        #add item to spreadsheet column1 (A) and incrementing rows starting with row #2
        mainDatabaseSpreadsheet['A'+str(currentRow)]=text
        mainDatabaseSpreadsheet['B'+str(currentRow)]=metadata
        #then move on to next item in dictionary and next row
        currentRow+=1

if debug == True:
    printAllTheThings(mainDatabaseSpreadsheet)

#create backup of database when it is initially created
print('')
#print(('creating backup at: backups/'+currentDateFull+'/rawUntranslated-'+currentDateAndTimeFull+'.xlsx').encode(consoleEncoding))
print('')
Path('backups/'+currentDateFull).mkdir(parents=True, exist_ok=True)
#mainDatabaseWorkbook.save('backups/'+currentDateFull+'/rawUntranslated-'+currentDateAndTimeFull+'.xlsx')
#print(inputFileContents.partition('\n')[0].encode(consoleEncoding)) #prints only first line






#once all lines are input into a dictionary, if specified, read the preDictionary.csv and perform replacements prior to submission to translation engine


#Then run DeepL's special code to replace braces {{ }}  {{{ }}}  with special markers that the DeepL engine can escape before submission to the translation engine


#




#do in memory replacements for CharaNames
#Replace [＠クロエ] with Chloe, but keep a record that it was replaced in order to replace it back after translation.
#Should be read from a c.csv that includes
#1) Information that should be preserved in the final translation as-is, but that will also be submitted to the translation engine for consideration so the position of the name or other string can influence the translation itself.
#To alter specific strings in the text before submission to the translation engine that will also be kept in the translated text, use preDictionary.csv. To alter specific parts of the text after translation, use postDictionary.csv.

#For character names, either:
#need to know, gender (m, f, u), since that might influence the translation.  Can also append that information to prompt for LLM models.
#Could also ask user to specify a replacement name. This might be a better idea.

