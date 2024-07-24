#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: A helper library that has many functions that py3TranslateLLM relies on.

Importing: 
import resources.functions as functions
# Or to import directly:
import sys
import pathlib
sys.path.append( str( pathlib.Path( 'C:\\resources\\functions.py' ).resolve().parent) )
import functions

Library Usage:
functions.verifyThisFileExists(file)

Function Usage: See each function for usage instructions.

Notes: Only functions that do not use module-wide variables and have return values are listed here. Functions without return values and those that rely on module specific variables that would be cumbersome to pass around should still be in the main program.

Copyright (c) 2024 gdiaz384; License: See main program.

"""
__version__ = '2024.07.24'

#set defaults
#printStuff = True
verbose = False
debug = False
#debug = True

consoleEncoding = 'utf-8'
defaultTextFileEncoding = 'utf-8'   # Settings that should not be left as a default setting should have default prepended to them.

linesThatBeginWithThisAreComments = '#'
assignmentOperatorInSettingsFile = '='
# Why yahoo? They are unlikely to go anywhere any time soon.
#domainWithoutProtocolToResolveForInternetConnectivity = 'yahoo.com'
domainWithProtocolToResolveForInternetConnectivity = 'https://yahoo.com'
defaultTimeout = 10

inputErrorHandling = 'strict'
#outputErrorHandling = 'namereplace'    # This gets updated dynamically later.

translationEnginesAvailable = 'cacheOnly, koboldcpp, py3translationserver, sugoi, deepl_api_free, deepl_api_pro, deepl_web, pykakasi, cutlet'
usageHelp = ' Usage: python py3TranslateLLM --help  Example: py3TranslateLLM -te KoboldCpp -f myInputFile.ks.xlsx \n Translation Engines: ' + translationEnginesAvailable + '.'


#These must be here or the library will crash even if these modules have already been imported by main program.
import sys                                   # End program on fail condition.
import os, os.path                      # Extract extension from filename, and test if file exists.
#import pathlib                            # For pathlib.Path Override file in file system with another and create subfolders. Sane path handling.
import requests                          # Check if internet exists. # Update: Changed to socket library instead, so this is not needed anymore.
#import socket
#import io                                      # Manipulate files (open/read/write/close).
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
if sys.version_info.minor >= 5:
    outputErrorHandling = 'namereplace'
elif sys.version_info.minor < 5:
    outputErrorHandling = 'backslashreplace'


#Question: how does os.path.splitext(fileName) actually work? Answer: If the extension does not exist, then it returns an empty string '' object for the extension. A None comparison will not work, but...   if myFileExtOnly == '':   ... will return true and conditionally execute.
#Returns True or False depending upon if file exists or not.
def checkIfThisFileExists( myFile ):
    #Check if name of file was never set or if the entered data is not a file.
    if (myFile == None) or ( os.path.isfile( str( myFile ) ) != True ):
        return False
    return True

def checkIfThisFolderExists(myFolder):
    if ( myFolder == None ) or ( os.path.isdir( str( myFolder ) ) != True ):
        return False
    return True

#Usage:
#checkIfThisFileExists( 'myfile.csv' )
#checkIfThisFileExists( myVar )


# Errors out if myFile does not exist.
def verifyThisFileExists( myFile, nameOfFileToOutputInCaseOfError=None ):
    if nameOfFileToOutputInCaseOfError == None:
        nameOfFileToOutputInCaseOfError = myFile
    # Check if name of file was never set.
    if myFile == None:
        print( ( 'Error: Please specify a valid file for: ' + str( nameOfFileToOutputInCaseOfError ) + usageHelp ).encode( consoleEncoding ) )
        sys.exit( 1 )
    if os.path.isfile( myFile ) != True:
        print( ( 'Error: Unable to find file \'' + str( nameOfFileToOutputInCaseOfError ) + '\' ' + usageHelp ).encode( consoleEncoding ) )
        sys.exit( 1 )

# Errors out if myFolder does not exist.
def verifyThisFolderExists( myFolder, nameOfFileToOutputInCaseOfError=None ):
    if nameOfFileToOutputInCaseOfError == None:
        nameOfFileToOutputInCaseOfError = myFolder
    if myFolder == None:
        print( ( 'Error: Please specify a valid folder for: ' + str( nameOfFileToOutputInCaseOfError ) + usageHelp ).encode( consoleEncoding ) )
        sys.exit( 1 )
    if os.path.isdir( myFolder ) != True:
        print( ( 'Error: Unable to find folder \'' + str( nameOfFileToOutputInCaseOfError ) + '\' ' + usageHelp ).encode( consoleEncoding ) )
        sys.exit( 1 )

#Usage:
#verifyThisFileExists( 'myfile.csv', 'myfile.csv' )
#verifyThisFileExists( myVar, 'myVar')
#verifyThisFileExists( myVar )


# This function reads program settings from text files using a predetermined list of rules.
# The text file uses the syntax: setting=value, # are comments, empty/whitespace lines ignored.
# This function builds a dictionary and then returns it to the caller.
def readSettingsFromTextFile( fileNameWithPath, fileNameEncoding=defaultTextFileEncoding, consoleEncoding=consoleEncoding, errorHandlingType=inputErrorHandling, debug=debug ):
    if fileNameWithPath == None:
        print( ( 'Cannot read settings from None entry: ' + fileNameWithPath ).encode( consoleEncoding ) )
        return None

    verifyThisFileExists( fileNameWithPath )

    #Newer, simplier syntax. Read entire file into memory.
    with open( fileNameWithPath, 'rt', encoding=fileNameEncoding, errors=inputErrorHandling ) as myFileHandle:
        inputFileContents = myFileHandle.read().splitlines()

    # The file was specified, it exists, and it was read from successfully. The contents are in inputFileContents.
    # Now turn inputFileContents into a dictionary.
    tempDictionary = {}
    for myLine in inputFileContents:
        # The line should be ignored if the first character is a comment character (after removing whitespace) or if there is only whitespace
        if ( myLine.strip() == '' ) or ( myLine.strip().startswith( linesThatBeginWithThisAreComments.strip() ) ) :
            continue # continue to the next iteration of the loop. This is similar to break and return in that it changes the control flow but in a softer way.

        # if line should not be ignored, then a delimiter must exist to separate the key=value pairs. By default that is =. Exit due to malformed data if not found.
        if myLine.find( assignmentOperatorInSettingsFile ) == -1:
            print( ( 'Error: Malformed data was found processing file: ' + fileNameWithPath + ' Missing: \'' + assignmentOperatorInSettingsFile + '\'' ).encode( consoleEncoding ) )
            sys.exit( 1 )

        # if the line should not be ignored, then use = as a delimiter set each side as key = value in a temporaryDictionary
        # Example:  paragraphDelimiter=emptyLine   #ignoreLinesThatStartWith=[ * ; 【     #wordWrap=45   #alwaysAddAfterTranslationEndOfLine=None
        key, value = myLine.split( assignmentOperatorInSettingsFile, 1 )
        key = key.strip()
        value = value.strip()
        if value.lower() == '':
            print( ( 'Warning: Error reading key\'s value \'' + key + '\' in file: ' + str(fileNameWithPath) + ' Using None as fallback.' ).encode( consoleEncoding ) )
            value = None
        elif value.lower() == 'none':
            value = None
        elif value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.lower().count( ' ' ) > 0: # 'ignorelinesthatstartwith' # ignoreLinesThatStartWith This is a list that contains multiple entries.
            # then every item that is not blank space is a valid list value.
            tempList = value.split( ' ' )
            value = []
            # Extra whitespace between entries is hard to spot in the file and can produce malformed list entries, so parse each entry individually.
            for i in tempList:
                if i != '':
                    if i.lower() == 'true':
                        value.append( True )
                    elif i.lower() == 'false':
                        value.append( False )
                    elif i.lower() == 'none':
                        value.append( None )
                    else:
                        try:
                            value.append( int( i ) ) # This will error out with data like '1.23', so floats get left as a string.
                        except:
                            value.append( i )
        else:
            try:
                value = int( value )
            except:
                pass
        tempDictionary[ key ] = value

    #Finished reading entire file, so return resulting dictionary.
    if debug == True:
        print( ( fileNameWithPath + ' was turned into this dictionary=' + str( tempDictionary ) ).encode( consoleEncoding ) )
    return tempDictionary


def getCurrentMonthFromNumbers( x ):
    x = str( x )
    if ( x == '1' ) or ( x == '01' ):
        return 'Jan'
    elif ( x == '2' ) or ( x == '02' ):
        return 'Feb'
    elif ( x == '3' ) or ( x == '03' ):
        return 'Mar'
    elif ( x == '4' ) or ( x == '04' ):
        return 'April'
    elif ( x == '5' ) or ( x == '05' ):
        return 'May'
    elif ( x == '6' ) or ( x == '06' ):
        return 'June'
    elif ( x == '7' ) or ( x == '07' ):
        return 'July'
    elif ( x == '8' ) or ( x == '08' ):
        return 'Aug'
    elif ( x == '9' ) or ( x == '09' ):
        return 'Sept'
    elif ( x == '10' ):
        return 'Oct'
    elif ( x == '11' ):
        return 'Nov'
    elif ( x == '12' ):
        return 'Dec'
    else:
        print( 'Unspecified error..' )
        sys.exit( 1 )


# These functions return the current date, time, yesterday's date, and full (day+time)
def getYearMonthAndDay():
    today = datetime.datetime.today()

    #debug code
    #print( datetime.today().strftime( '%Y-%m-%d' ) )
    #print( today.strftime( '%d/%m/%Y %H:%M:%S' ) )

    currentYear = str( today.strftime( '%Y' ) )
    #currentMonth = getCurrentMonthFromNumbers( today.strftime( '%m' ) )
    currentMonth = str( today.strftime( '%m' ) )
    currentDay = str( today.strftime( '%d' ) )
    return currentYear + '-' + currentMonth + '-' + currentDay


def getYesterdaysDate():
    yesterday = datetime.datetime.today() - datetime.timedelta( 1 )

    # Debug code.
    #print( datetime.yesterday().strftime( '%Y-%m-%d' ) )
    #print( yesterday.strftime( '%d/%m/%Y %H:%M:%S' ) )

    currentYear = str( yesterday.strftime( '%Y' ) )
    #currentMonth = getCurrentMonthFromNumbers( yesterday.strftime( '%m' ) )
    currentMonth = str( yesterday.strftime( '%m' ) )
    currentDay = str( yesterday.strftime( '%d' ) )
    return currentYear + '-' + currentMonth + '-' + currentDay


def getCurrentTime():
    today = datetime.datetime.today()

    currentHour = today.strftime( '%H' )
    currentMinutes = today.strftime( '%M' )
    currentSeconds = today.strftime( '%S' )
    return currentHour + '-' + currentMinutes + '-' + currentSeconds


def getDateAndTimeFull():
    #currentDateAndTimeFull = currentDateFull + '-' + currentTimeFull
    return getYearMonthAndDay() + '.' + getCurrentTime()

#if ( verbose == True ) or ( debug == True ):
#    print( currentDateAndTimeFull.encode( consoleEncoding ) )


# Returns True if internet is available. Returns false otherwise.
def checkIfInternetIsAvailable():
    try:
        requests.get( domainWithProtocolToResolveForInternetConnectivity , allow_redirects=True, timeout=( 5, defaultTimeout ) )
        return True
    except:
        return False


def importDictionaryFromFile( myFile, encoding=defaultTextFileEncoding ):
    if checkIfThisFileExists( myFile ) != True:
        return None
    #else it exists, so find the extension and call the appropriate import function for that fileType
    myFileNameOnly, myFileExtensionOnly = os.path.splitext( myFile )
    if ( myFileExtensionOnly == None ) or ( myFileExtensionOnly == '' ):
        return None
    elif myFileExtensionOnly == '.csv':
        return importDictionaryFromCSV( myFile, myFileEncoding=encoding, ignoreWhitespace=False)
    elif myFileExtensionOnly == '.xlsx':
        return importDictionaryFromXLSX( myFile, myFileEncoding=encoding )
    elif myFileExtensionOnly == '.xls':
        return importDictionaryFromXLS( myFile, myFileEncoding=encoding )
    elif myFileExtensionOnly == '.ods':
        return importDictionaryFromODS( myFile, myFileEncoding=encoding )
    elif myFileExtensionOnly == '.tsv':
        return importDictionaryFromTSV( myFile, myFileEncoding=encoding, ignoreWhitespace=False )
    else:
        print( ( 'Warning: Unrecognized extension for file: ' + str( myFile ) ).encode( consoleEncoding ) )
        return None
        # Alternatively, this could assume it is dealing with a text file that conforms to the key=value pairs syntax that also has # as comments. These files should also return dictionaries or None if there are any malformed entries. However, since that is less clear, a Warning: should probably be printed here since this code is not really meant to be called this way. Then again, having flexible code is a good thing. 
        # readSettingsFromTextFile() would need to be updated to soft-fail by returning None instead of crashing the program on malformed data. Does updating it that way make sense? A strict=True, flag could be added to toggle this behavior without changing existing calling code, but changing the source to be strict about it is probably for the better.


# Even if importing to a Python dictionary from .csv .xlsx .xls .ods .tsv, the rule is that the first entry for spreadsheets is headers, so the first key=value entry must be skipped regardless.
def importDictionaryFromCSV( myFile, myFileEncoding=defaultTextFileEncoding, ignoreWhitespace=False ):
    tempDict={}

    # 'with' is correct. Do not use 'while'.
    with open( myFile, 'rt', newline='', encoding=myFileEncoding, errors=inputErrorHandling ) as myFileHandle:
        csvReader = csv.reader( myFileHandle )
        for currentLine,line in enumerate( csvReader ):
            # Skip first line.
            if currentLine == 0:
                pass
            elif currentLine != 0:
                if ignoreWhitespace == True:
                    for i in range( len(line) ):
                        line[ i ] = line[ i ].strip()
                if line[ 1 ] == '':
                    line[ 1 ] = None
                elif line[ 1 ].lower() == 'none':
                    line[ 1 ] = None
                elif line[ 1 ].lower() == 'true':
                    line[ 1 ] = True
                elif line[ 1 ].lower() == 'false':
                    line[ 1 ] = False
                else:
                    try:
                        line[ 1 ] = int( line[ 1 ] )
                    except:
                        pass
                tempDict[ line[ 0 ] ] = line[ 1 ]

    return tempDict


def importDictionaryFromXLSX( myFile, myFileEncoding=defaultTextFileEncoding ):
    print( 'Hello world.')
    workbook = openpyxl.load_workbook( filename=myFile ) #, data_only=)
    spreadsheet = workbook.active


def importDictionaryFromXLS( myFile, myFileEncoding=defaultTextFileEncoding ):
    print( 'Hello world.' )


def importDictionaryFromODS( myFile, myFileEncoding=defaultTextFileEncoding ):
    print( 'Hello world.' )


def importDictionaryFromTSV( myFile, myFileEncoding=defaultTextFileEncoding, ignoreWhitespace=False ):
    print( 'Hello world.' )


"""
# TODO: This section.
# Usage examples, assuming this library is in a subfolder named 'resources':
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
