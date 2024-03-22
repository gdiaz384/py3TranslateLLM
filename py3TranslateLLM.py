#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
py3TranslateLLM.py translates text using Neural net Machine Translation (NMT) and Large Language Models (LLM).

For usage, see py3TranslateLLM.py -h', README.md, and the source code below.

License:
- For the various libraries used, see the Readme for their licenses and project pages.
- This .py file and the libraries under resources/ are C* gdiaz384 and licensed as GNU Affero GPL v3.
- https://www.gnu.org/licenses/agpl-3.0.html Summary:
- Feel free to use this program, modify it, and distribute it to an unlimited extent, but if you distribute binary files of this program outside of your organization, then please make the source code for those binaries available.
- The imperative to make source code available also applies if using this program as part of a server if that server is publically accessible.
"""

#set defaults and static variables
versionString='2024.03.20 pre-alpha'

#Do not change the defaultTextEncoding. This is heavily overloaded.
defaultTextEncoding = 'utf-8'
defaultTextEncodingForKSFiles = 'shift-jis'
defaultConsoleEncodingType = 'utf-8'

#These default paths are relative to the location of py3TranslateLLM.py, -not- relative to the current path of the command prompt.
defaultLanguageCodesFile = 'resources/languageCodes.csv'
defaultSourceLanguage = None
#defaultSourceLanguage = 'Japanese'
defaultTargetLanguage = None
#defaultTargetLanguage = 'English'
# Valid options are 'English (American)' or 'English (British)'
defaultEnglishLanguage = 'English (American)'
# Valid options are 'Chinese (simplified)' or 'Chinese (traditional)'
defaultChineseLanguage = 'Chinese (simplified)'
# Valid options are 'Portuguese (European)' or 'Portuguese (Brazilian)'
defaultPortugueseLanguage = 'Portuguese (European)'


defaultAddress = 'http://localhost'
defaultKoboldCppPort = 5001
defaultPy3TranslationServerPort = 14366
defaultSugoiPort = 14366
minimumPortNumber = 1
maximumPortNumber = 65535 #16 bit integer -1
defaultPortForHTTP = 80
defaultPortForHTTPS = 443

defaultContextHistoryLength = 6
defaultInputEncodingErrorHandler = 'strict'
#defaultOutputEncodingErrorHandler = 'namereplace'

defaultLinesThatBeginWithThisAreComments = '#'
defaultAssignmentOperatorInSettingsFile = '='
defaultMetadataDelimiter = '_'
defaultScriptSettingsFileExtension = '.ini'
# if a column begins with one of these entries, then it will be assumed to be invalid for cacheAnyMatch. Case insensitive.
defaultBlacklistedHeadersForCache = [ 'rawText','speaker','metadata' ] #'cache', 'cachedEntry', 'cache entry'

# Currently, these are relative to py3TranslateLLM.py, but it might also make sense to move them either relative to the target or to a system folder intended for holding program data.
# There is no gurantee that being relative to the target is a sane thing to do since that depends upon runtime usage, and centralized backups also make sense. Leaving it as-is makes sense too as long as py3TranslateLLM is not being used as a library. If it is not being used as a library, then a centralized location under $HOME or %localappdata% makes more sense than relative to py3TranslateLLM.py. Same with the default location for the cache file.
# Maybe a good way to check for this is the name = __main__ check?
defaultBackupsFolder='backups'
defaultExportExtension='.xlsx'
defaultCacheFileLocation=defaultBackupsFolder + '/cache' + defaultExportExtension


translationEnginesAvailable='parseOnly, koboldcpp, deepl_api_free, deepl_api_pro, deepl_web, py3translationserver, sugoi'
usageHelp=' Usage: python py3TranslateLLM --help  Example: py3TranslateLLM -mode KoboldCpp -f myInputFile.ks \n Translation Engines: '+translationEnginesAvailable+'.'


#import various libraries that py3TranslateLLM depends on
import argparse                           # Used to add command line options.
import os, os.path                        # Extract extension from filename, and test if file exists.
#from pathlib import Path           # Override file in file system with another and create subfolders.
#import pathlib.Path                    # Does not work. Why not? Maybe because Path is a class and not a Path.py file? So 'from' crawls into files? Maybe from 'requires' it. Like Path must be a class inside of pathlib instead of a file named Path.py. 'import' does not seem to care whether it is importing files or classes. They are both made available. But 'from' might.
import pathlib                               # Works.   #dir(pathlib) does list 'Path', so just always use as pathlib.Path Constructor is pathlib.Path(mystring). Remember to convert it back to a string if printing it out.
import sys                                     # End program on fail condition.
import io                                        # Manipulate files (open/read/write/close).
#from io import IOBase               # Test if variable is a file object (an "IOBase" object).
#import datetime                          # Used to get current date and time.

# Technically, these two are optional for parseOnly. To support or not support such a thing... probably yes. # Update: Maybe.
#from collections import deque  # Used to hold rolling history of translated items to use as context for new translations.
import collections                         # Newer syntax. For collections.deque. Used to hold rolling history of translated items to use as context for new translations.
#import requests                            # Do basic http stuff, like submitting post/get requests to APIs. Must be installed using: 'pip install requests' # Update: Moved to functions.py

#import openpyxl                           # Used as the core internal data structure and to read/write xlsx files. Must be installed using pip. # Update: Moved to chocolate.py
import resources.chocolate as chocolate # Implements openpyxl. A helper/wrapper library to aid in using openpyxl as a datastructure.
import resources.dealWithEncoding as dealWithEncoding   # dealWithEncoding implements the 'chardet' library which is installed with 'pip install chardet'
import resources.py3TranslateLLMfunctions as py3TranslateLLMfunctions  # Moved most generic functions here to increase code readability and enforce function best practices.
#from resources.py3TranslateLLMfunctions import * # Do not use this syntax if at all possible. The * is fine, but the 'from' breaks everything because it copies everything instead of pointing to the original resources which makes updating library variables borderline impossible.
import resources.translationEngines as translationEngines

#Using the 'namereplace' error handler for text encoding requires Python 3.5+, so use an older one if necessary.
sysVersion=int(sys.version_info[1])
if sysVersion >= 5:
    defaultOutputEncodingErrorHandler='namereplace'
elif sysVersion < 5:
    defaultOutputEncodingErrorHandler='backslashreplace'    
else:
    sys.exit('Unspecified error.'.encode(defaultConsoleEncodingType))


# So, py3translateLLM.py also supports reading program settings from py3translateLLM.ini in addition to the command prompt.
# Rule is that settings from the command line take #1 precedence
# Then #2) entries from .ini
# Then #3) settings hardcoded in .py
# So, initialize all non-boolean CLI settings to None. Then, only change them using settings.ini or defaultSettings if they are still None after reading from CLI. Any settings that are not None were set using the CLI, so leave them alone.
# For boolean values, they are all False by default. Only change to True if the scriptSettingsDictionary set them to True. Well, that means any CLI settings as intended to be default of 'False' will be overriden to True. Well, that is a user error. Let them deal with it since they were the ones that decided to change the default settings.


# Add command line options.
commandLineParser=argparse.ArgumentParser(description='Description: CLI wrapper script for various NMT and LLM models.' + usageHelp)
commandLineParser.add_argument('-mode', '--translationEngine', help='Specify translation engine to use, options=' + translationEnginesAvailable+'.', type=str)

commandLineParser.add_argument('-f', '--fileToTranslate', help='Either the raw file to translate or the spreadsheet file to resume translating from, including path.', default=None, type=str)
commandLineParser.add_argument('-fe', '--fileToTranslateEncoding', help='The encoding of the input file. Default='+str(defaultTextEncoding), default=None, type=str)
commandLineParser.add_argument('-o', '--outputFile', help='The file to insert translations into, including path. Default is same as input file.', default=None, type=str)
commandLineParser.add_argument('-ofe', '--outputFileEncoding', help='The encoding of the output file. Default is same as input file.', default=None, type=str)

#commandLineParser.add_argument('-pfile', '--parsingSettingsFile', help='This file defines how to parse raw text and .ks files. It is required for text and .ks files. If not specified, a template will be created.', default=None, type=str)
#commandLineParser.add_argument('-pfe', '--parsingSettingsFileEncoding', help='Specify encoding for parsing definitions file, default='+str(defaultTextEncoding), default=None, type=str)

commandLineParser.add_argument('-p', '--promptFile', help='This file has the prompt for the LLM.', default=None, type=str)
commandLineParser.add_argument('-pe', '--promptFileEncoding', help='Specify encoding for prompt file, default='+str(defaultTextEncoding), default=None, type=str)

commandLineParser.add_argument('-lcf', '--languageCodesFile', help='Specify a custom name and path for languageCodes.csv. Default=\''+str(defaultLanguageCodesFile)+'\'.', default=None, type=str)
commandLineParser.add_argument('-lcfe', '--languageCodesFileEncoding', help='The encoding of file languageCodes.csv. Default='+str(defaultTextEncoding), default=None, type=str)
commandLineParser.add_argument('-sl', '--sourceLanguage', help='Specify language of source text. Default='+str(defaultSourceLanguage), default=None, type=str)
commandLineParser.add_argument('-tl', '--targetLanguage', help='Specify language of source text. Default='+str(defaultTargetLanguage), default=None, type=str)

commandLineParser.add_argument('-cn', '--characterNamesDictionary', help='The file name and path of characterNames.csv', default=None, type=str)
commandLineParser.add_argument('-cne', '--characterNamesDictionaryEncoding', help='The encoding of file characterNames.csv. Default='+str(defaultTextEncoding), default=None, type=str)
commandLineParser.add_argument('-pred', '--preTranslationDictionary', help='The file name and path of preTranslation.csv', default=None, type=str)
commandLineParser.add_argument('-prede', '--preTranslationDictionaryEncoding', help='The encoding of file preTranslation.csv. Default='+str(defaultTextEncoding), default=None, type=str)
commandLineParser.add_argument('-postd', '--postTranslationDictionary', help='The file name and path of postTranslation.csv.', default=None, type=str)
commandLineParser.add_argument('-postde', '--postTranslationDictionaryEncoding', help='The encoding of file postTranslation.csv. Default='+str(defaultTextEncoding), default=None, type=str)
# Update: postWritingToFileDictionary might only make sense for text files.
commandLineParser.add_argument('-postwd', '--postWritingToFileDictionary', help='The file name and path of postWritingToFile.csv.', default=None, type=str)
commandLineParser.add_argument('-postwde', '--postWritingToFileDictionaryEncoding', help='The encoding of file postWritingToFile.csv. Default='+str(defaultTextEncoding), default=None, type=str)

commandLineParser.add_argument('-c', '--cache', help='Toggles cache setting. Specifying this will disable using or updating the cache file. Default=Use the cache file to fill in previously translated entries and update it with new entries.', action='store_true')
commandLineParser.add_argument('-cf', '--cacheFile', help='The location of the cache file. Must be in .xlsx format. Default=' + str(defaultCacheFileLocation), default=None, type=str)
commandLineParser.add_argument('-cam', '--cacheAnyMatch', help='Use all translation engines when considering the cache. Default=Only consider the current translation engine as valid for cache hits.', action='store_true')
commandLineParser.add_argument('-oc', '--overrideWithCache', help='Override any already translated lines in the spreadsheet with results from the cache. Default=Do not override already translated lines.', action='store_true')
commandLineParser.add_argument('-rt', '--reTranslate', help='Translate all lines even if they already have translations or are in the cache. Update the cache with the new translations. Default=Do not retranslate and use the cache to fill in previously translated lines.', action='store_true')
commandLineParser.add_argument('-rc', '--readOnlyCache', help='Opens the cache file in read-only mode and disables updates to it. This dramatically decreases the memory used by the cache file. Default=Read and write to the cache file.', action='store_true')

commandLineParser.add_argument('-hl', '--contextHistoryLength', help='The number of previous translations that should be sent to the translation engine to provide context for the current translation. Sane values are 2-10. Set to 0 to disable. Not all translation engines support context. Default='+str(defaultContextHistoryLength), default=None, type=int)
#commandLineParser.add_argument('-lbl', '--lineByLineMode', help='Store and translate lines one at a time. Disables grouping lines by delimitor and paragraph style translations.', action='store_true')
commandLineParser.add_argument('-r', '--resume', help='Attempt to resume previously interupted operation. No gurantees.', action='store_true')

commandLineParser.add_argument('-a', '--address', help='Specify the protocol and IP for NMT/LLM server, Example: http://192.168.0.100', default=None,type=str)
commandLineParser.add_argument('--port', help='Specify the port for the NMT/LLM server. Example: 5001', default=None, type=str)

commandLineParser.add_argument('-ieh', '--inputErrorHandling', help='If the wrong input codec is specified, how should the resulting conversion errors be handled? See: docs.python.org/3.7/library/codecs.html#error-handlers Default=\'' + str(defaultInputEncodingErrorHandler) + '\'.', default=None, type=str)
commandLineParser.add_argument('-eh', '--outputErrorHandling', help='How should output conversion errors between incompatible encodings be handled? See: docs.python.org/3.7/library/codecs.html#error-handlers Default=\'' + str(defaultOutputEncodingErrorHandler) + '\'.', default=None, type=str)

commandLineParser.add_argument('-ce', '--consoleEncoding', help='Specify encoding for standard output. Default='+str(defaultConsoleEncodingType), default=None,type=str)

commandLineParser.add_argument('-vb', '--verbose', help='Print more information.', action='store_true')
commandLineParser.add_argument('-d', '--debug', help='Print too much information.', action='store_true')
commandLineParser.add_argument('-v', '--version', help='Print version information and exit.', action='store_true')    


#import options from command line options
commandLineArguments=commandLineParser.parse_args()
#print( 'debugSettingFromCLI='+str(commandLineArguments.debug) )

translationEngine=commandLineArguments.translationEngine
fileToTranslate=commandLineArguments.fileToTranslate
#parsingSettingsFile=commandLineArguments.parsingSettingsFile
outputFile=commandLineArguments.outputFile
promptFile=commandLineArguments.promptFile

languageCodesFile=commandLineArguments.languageCodesFile
sourceLanguage=commandLineArguments.sourceLanguage
targetLanguage=commandLineArguments.targetLanguage

characterNamesDictionary=commandLineArguments.characterNamesDictionary
preTranslationDictionary=commandLineArguments.preTranslationDictionary
postTranslationDictionary=commandLineArguments.postTranslationDictionary
postWritingToFileDictionary=commandLineArguments.postWritingToFileDictionary

cache=commandLineArguments.cache
cacheFile=commandLineArguments.cacheFile
cacheAnyMatch=commandLineArguments.cacheAnyMatch
overrideWithCache=commandLineArguments.overrideWithCache
reTranslate=commandLineArguments.reTranslate
readOnlyCache=commandLineArguments.readOnlyCache

contextHistoryLength=commandLineArguments.contextHistoryLength
#lineByLineMode=commandLineArguments.lineByLineMode
resume=commandLineArguments.resume

address=commandLineArguments.address  #Must be reachable. How to test for that?
port=commandLineArguments.port                #Port should be conditionaly guessed. If no port specified and an address was specified, then try to guess port as either 80, 443, or default settings depending upon protocol and translationEngine selected.

inputErrorHandling=commandLineArguments.inputErrorHandling
outputErrorHandling=commandLineArguments.outputErrorHandling

consoleEncoding=commandLineArguments.consoleEncoding
verbose=commandLineArguments.verbose
debug=commandLineArguments.debug
version=commandLineArguments.version


# Basically, the final value of consoleEncoding is unclear because the settings.ini has not been read yet,
# but it needs to be used immediately for '--version', so add a temporary console encoding variable: tempConsoleEncoding.
# If the user specified one at the CLI, use that setting, otherwise use the hardcoded defaults.
if commandLineArguments.consoleEncoding != None:
    tempConsoleEncoding=commandLineArguments.consoleEncoding
else:
    tempConsoleEncoding=defaultConsoleEncodingType
if debug == True:
    print( ('tempConsoleEncoding='+tempConsoleEncoding).encode(tempConsoleEncoding) )
if version == True:
    sys.exit( (versionString).encode(tempConsoleEncoding) )


#Add stub encoding options. All of these are most certainly None, but they need to exist for locals() to find them so they can get updated.
fileToTranslateEncoding=commandLineArguments.fileToTranslateEncoding
outputFileEncoding=commandLineArguments.outputFileEncoding
promptFileEncoding=commandLineArguments.promptFileEncoding

#parsingSettingsFileEncoding=commandLineArguments.parsingSettingsFileEncoding
languageCodesFileEncoding=commandLineArguments.languageCodesFileEncoding

characterNamesDictionaryEncoding=commandLineArguments.characterNamesDictionaryEncoding
preTranslationDictionaryEncoding=commandLineArguments.preTranslationDictionaryEncoding
postTranslationDictionaryEncoding=commandLineArguments.postTranslationDictionaryEncoding
postWritingToFileDictionaryEncoding=commandLineArguments.postWritingToFileDictionaryEncoding


# Settings specified at the command prompt take precedence, but py3translateLLM.ini still needs to be pased.
# This function parses that file and places the settings discovered into a dictionary. That dictionary can then be used along with
# the command line options to determine the program settings (prior to validation of those settings).
# This function reads program settings from text files using a predetermined list of rules.
# The text file uses the syntax: setting=value, # are comments, empty/whitespace lines ignored.
# This function builds a dictionary and then returns it to the caller.

#def readSettingsFromTextFile(fileNameWithPath, fileNameEncoding, consoleEncoding=defaultConsoleEncodingType, errorHandlingType=defaultInputEncodingErrorHandler,debug=debug):
#Usage: readSettingsFromTextFile(myfile, myfileEncoding)


# In order to read from settings.ini, the name of the current script must first be determined.
# Old code:
#currentScriptName = __file__
#currentScriptName = os.path.basename(__file__)  #Returns only the filename of the current script.
#print('file='+__file__) #Returns filename and also the path sometimes.
#This might error out if there is no extension, or maybe it will just return an empty string for the extension.
#currentScriptNameOnly, currentScriptExtensionOnly = os.path.splitext(currentScriptName)
#scriptSettingsFileFullNameAndPath=currentScriptNameOnly+defaultScriptSettingsFileExtension

# Newer code that focuses on using pathlib.Path() its methods:
currentScriptPathObject = pathlib.Path( __file__ ).absolute()
currentScriptPathOnly = str(currentScriptPathObject.parent) #Does not include last / and this will return one subfolder up if it is called on a folder.
currentScriptNameWithoutPath = currentScriptPathObject.name
currentScriptNameWithoutPathOrExt = currentScriptPathObject.stem
currentScriptNameWithPathNoExt = currentScriptPathOnly + '/' + currentScriptNameWithoutPathOrExt

#backupsFolder=currentScriptPathOnly + '/backups'  #does not include last /   Edit: Should probably not hardcode this. Use a default instead.
backupsFolder=currentScriptPathOnly + '/' + defaultBackupsFolder
scriptSettingsFileFullNameAndPath = currentScriptNameWithPathNoExt + defaultScriptSettingsFileExtension
scriptSettingsFileNameOnly = pathlib.Path(scriptSettingsFileFullNameAndPath).name


if (verbose == True) or (debug == True):
    print( str(currentScriptPathObject).encode(tempConsoleEncoding) )
    print( ('currentScriptPathOnly=' + str(currentScriptPathOnly)).encode(tempConsoleEncoding) )
    print( ('currentScriptNameWithoutPath=' + str(currentScriptNameWithoutPath)).encode(tempConsoleEncoding) )
    print( ('currentScriptNameWithoutPathOrExt=' + str(currentScriptNameWithoutPathOrExt)).encode(tempConsoleEncoding) )


scriptSettingsDictionary=None
#if exist scriptSettingsFileFullNameAndPath
#if os.path.isfile(scriptSettingsFileFullNameAndPath) == True:
if py3TranslateLLMfunctions.checkIfThisFileExists(scriptSettingsFileFullNameAndPath) == True:
    print( ('Settings file found. Reading settings from: '+scriptSettingsFileNameOnly).encode(tempConsoleEncoding) )
    scriptSettingsDictionary=py3TranslateLLMfunctions.readSettingsFromTextFile(scriptSettingsFileFullNameAndPath,defaultTextEncoding, consoleEncoding=tempConsoleEncoding) #Other settings can be specified, but are basically completely unknown at this point, so just use hardcoded defaults instead.


if scriptSettingsDictionary != None:
    # For every entry in dictionary, if the variable referenced by the key's value (current variable's value in script) == None, then set key equal to dictionary's.
    # There is no way to say the above in Python. Batch yes, Python no.
    # Looping through the dictionary /might/ work if this dictionary was read first and then the CLI was allowed to blindly override the values, but that would require changing the order and coming up with yet another fix for --debug flag not working.
#    for x, y in scriptSettingsDictionary.items():
#        print(x)
#        if x == None:
#            print(pie)
    #Since looping does not work, then just dumbly go through each value one by one. This also means the user cannot add arbitrary values or change other settings than the settings explicitly specified here. However, this creates an arbitrary dependency on the .ini file. If the .ini file exists, then every CLI option must also be present there, or attempting to access values not present gives a KeyError.
#    if translationEngine == None:
#        translationEngine = scriptSettingsDictionary['translationEngine']
#    if commandLineArguments.fileToTranslateEncoding == None:
#        #basically, If an encoding was specified at the command prompt, do nothing. But if an encoding was not specified, then just blindly set it to whatever it was set to in the dictionary. No, also wrong. Need to check if dictionary has the entry first.
#        commandLineArguments.fileToTranslateEncoding = scriptSettingsDictionary['fileToTranslateEncoding']
#   Okay, try looping method again.

    #Proxy the dictionary to avoid calling locals() multiple times per loop and in a loop.
    tempDict = locals()
    for x, y in scriptSettingsDictionary.items():
        #if y != None:
        if debug == True:
            print( ('Processing Key: '+str(x)+'='+str(y)+' Current value='+str(tempDict[x]) ).encode(tempConsoleEncoding) )

        #So... locals() returns a dictionary containing all of the currently available variables in the script and their values.
        #That dictionary can then be accessed like any other dictionary, as in myDict['key'], but key has to be a string value already present in the dictionary. Is that because it returns the value of the key? myDictionary['key']='value' works fine for assignment, but not here.
        #In other words, the values accessed this way must already exist, regardless of doing a comparison or assignment operator for them.

        #print (locals()[x])  #This prints the value of the script's variable name 'x', with the name of x derived from the .ini file.
        #Which means that value, the current value in the script, can be compared with None, and only update the variable name conditionally.
        #Since the variable name referenced by x already exists in the module/global scope, but not locally, this is not considered a local assignment.
        #And since it is just getting a value from a dictionary, it is valid to assign values after it. Invoking a function without a sub property on the left side of an assignment always results in an error: function()=value   #Errors out, but this still works: local()[x] = y
        #if locals()[x] == None:
        #    local()[x] = y
        if tempDict[x] == None:
            #Do not bother updating if the new value would be None too.
            if y != None:
                if (verbose == True) or (debug == True):
                    print( ('Updating variable: '+str(x)+' to \''+str(y)+'\'').encode(tempConsoleEncoding) )
                tempDict[x] = y
        # The boolean values will never be updated by the above loop since the base value is always False instead of None. So check for that.
        elif tempDict[x] == False:
            #If the new value is false, or anything else, ignore it, but if the user set it to 'True', then set the variable to True.
            if str(y).lower() == 'true':
                if (verbose == True) or (debug == True):
                    print( ('Updating variable: '+str(x)+' to \'True\'').encode(tempConsoleEncoding) )
                tempDict[x] = True

# if consoleEncoding is still None after reading both the CLI and the settings.ini, then just set it to the default value.
if consoleEncoding == None:
    consoleEncoding=defaultConsoleEncodingType
# if version was specified in the .ini, then print out version string and exit.
if version == True:
    sys.exit( (versionString).encode(consoleEncoding) )
if debug == True:
    print( ('translationEngine='+str(translationEngine)).encode(consoleEncoding) )
    print( ('fileToTranslateEncoding='+str(fileToTranslateEncoding)).encode(consoleEncoding) )

#The variable names needed to be exact for the local()[x] dictionary shenanigans to work, but now that they have been updated, rename them to be more descriptive. The variable names for encoding options will be fixed later.
fileToTranslateFileName=fileToTranslate
#parseSettingsFileName=parsingSettingsFile
outputFileName=outputFile
promptFileName=promptFile

languageCodesFileName=languageCodesFile
sourceLanguageRaw=sourceLanguage
targetLanguageRaw=targetLanguage

charaNamesDictionaryFileName=characterNamesDictionary
preDictionaryFileName=preTranslationDictionary
postDictionaryFileName=postTranslationDictionary
postWritingToFileDictionaryFileName=postWritingToFileDictionary

cacheEnabled=cache
cacheFileName=cacheFile


# Now that command line options and .ini have been parsed, update settings for imported libraries.
#The libraries must be imported using the syntax: import resources.libraryName as libraryName . Otherwise, if using the 'from libraryName import...' syntax, a copy is made which makes it, near?, impossible to update these variables.
dealWithEncoding.verbose=verbose
dealWithEncoding.debug=debug
dealWithEncoding.consoleEncoding=consoleEncoding

chocolate.verbose=verbose
chocolate.debug=debug
chocolate.consoleEncoding=consoleEncoding
chocolate.inputErrorHandling=inputErrorHandling
chocolate.outputErrorHandling=outputErrorHandling
chocolate.metadataDelimiter=defaultMetadataDelimiter

py3TranslateLLMfunctions.verbose=verbose
py3TranslateLLMfunctions.debug=debug
py3TranslateLLMfunctions.consoleEncoding=consoleEncoding
py3TranslateLLMfunctions.inputErrorHandling=inputErrorHandling
py3TranslateLLMfunctions.outputErrorHandling=outputErrorHandling
py3TranslateLLMfunctions.linesThatBeginWithThisAreComments=defaultLinesThatBeginWithThisAreComments
py3TranslateLLMfunctions.assignmentOperatorInSettingsFile=defaultAssignmentOperatorInSettingsFile


if fileToTranslateFileName == None:
    sys.exit( ('Error: Please specify a --fileToTranslate (-f).').encode(consoleEncoding) )
# Determine file paths. Will be useful later.
fileToTranslatePathObject=pathlib.Path(fileToTranslateFileName).absolute()

fileToTranslateFileExtensionOnly=fileToTranslatePathObject.suffix   # .txt  .ks  .ts .csv .xlsx .xls .ods
fileToTranslatePathOnly=str(fileToTranslatePathObject.parent)  # Does not include final / and will return one subfolder up if it is called on a folder.
fileToTranslateFileNameWithoutPath=fileToTranslatePathObject.name
fileToTranslateFileNameWithoutPathOrExt=fileToTranslatePathObject.stem
fileToTranslateFileNameWithPathNoExt=fileToTranslatePathOnly + '/' + fileToTranslateFileNameWithoutPathOrExt

#Old code:
#fileToTranslateFileNameWithPathNoExt, fileToTranslateFileExtensionOnly = os.path.splitext(fileToTranslateFileName)
#fileToTranslateFileNameWithPathNoExt=str(pathlib.Path(os.path.realpath(__file__)).parent)
#fileToTranslateFileNameWithoutPathOrExt=pathlib.Path(fileToTranslateFileName).stem  #This returns a string, but Path().parent returns not-a-string.
#currentScriptFullFileNameAndPath=os.path.realpath(__file__) #Returns a string and the full path of the currently running script including the name and extension.
#currentScriptBasePath=str(pathlib.Path(currentScriptFullFileNameAndPath).parent) # Does not include / at the end. Path() does not mind mixing / and \ so always use /.

if (verbose == True) or (debug == True):
    print( str(fileToTranslatePathObject).encode(consoleEncoding) )
    print( ('fileToTranslateFileExtensionOnly=' + fileToTranslateFileExtensionOnly).encode(consoleEncoding) )
    print( ('fileToTranslatePathOnly=' + fileToTranslatePathOnly).encode(consoleEncoding) )
    print( ('fileToTranslateFileNameWithoutPath=' + fileToTranslateFileNameWithoutPath).encode(consoleEncoding) )
    print( ('fileToTranslateFileNameWithoutPathOrExt=' + fileToTranslateFileNameWithoutPathOrExt).encode(consoleEncoding) )
    print( ('fileToTranslateFileNameWithPathNoExt=' + fileToTranslateFileNameWithPathNoExt).encode(consoleEncoding) )


# Start to validate input settings and input combinations from parsed imported command line option values.
# Some values need to be set to hardcoded defaults if they were not specified at the command prompt or in settings.ini.
# Others must be present, like certain files.

# Verify translationEngine
mode=None
implemented=False
#validate input from command line options
if translationEngine == None:
    sys.exit( ('Error: Please specify a translation engine. '+usageHelp).encode(consoleEncoding) )
elif (translationEngine.lower()=='parseonly'):
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
elif (translationEngine.lower()=='py3translationserver'):
    mode='py3translationserver'
    implemented=True
elif (translationEngine.lower()=='sugoi') :
    mode='sugoi'
    #Sugoi has a default port association and only supports Jpn->Eng translations, so having a dedicated entry for it is still useful for input validation, especially since it only supports a subset of the py3translationserver API.
    implemented=True
else:
    sys.exit(('\n Error. Invalid translation engine specified: "' + translationEngine + '"' + usageHelp).encode(consoleEncoding))

print(('Mode is set to: \''+str(mode)+'\'').encode(consoleEncoding))
if implemented == False:
    sys.exit( ('\n\"'+mode+'\" not yet implemented. Please pick another translation engine. \n Translation engines: '+ translationEnginesAvailable).encode(consoleEncoding) )


# Certain files must always exist, like fileToTranslateFileName, and usually languageCodesFileName.
# parseSettingsFileName is only needed if read or writing to text files. Reading from text files is easy to check.
# But how to check if writing to them? If output is .txt, .ks, .ts, then writing to text file. Output can also be based upon input. For output, parseOnly must not be specified, so this output text file check should not be checked with the parseOnly block. Alternatively: The only time parseSettingsFileName is not needed is when writting to output files.
# Updated py3TranslateLLM to only accept spreadsheet inputs in order to divide the logic between parsing files and translating spreadsheets.
# Use py3AnyText2Spreadsheet to create spreadsheets from raw text files from now on.
#Errors out if myFile does not exist.
"""
#Syntax:
def verifyThisFileExists(myFile,nameOfFileToOutputInCaseOfError=None):
def checkIfThisFolderExists(myFolder):

#Usage:
py3TranslateLLMfunctions.verifyThisFileExists('myfile.csv','myfile.csv')
py3TranslateLLMfunctions.verifyThisFolderExists(myVar, 'myVar')

py3TranslateLLMfunctions.checkIfThisFileExists('myfile.csv')
py3TranslateLLMfunctions.checkIfThisFolderExists(myVar)
"""


if languageCodesFileName == None:
    languageCodesFileName = currentScriptPathOnly + '/' + defaultLanguageCodesFile

if cacheFileName != None:
    # if a cache file was specified, then verify the extension is .xlsx # Update: Shouldn't .csv also work? CSV would be harder for user to edit but might take less space on disk. Need to check.
    if (pathlib.Path(str(cacheFileName)).suffix) != '.xlsx' and (pathlib.Path(str(cacheFileName)).suffix != '.csv'):
        print( ('\n Error: cacheFile must have a spreadsheet extension: '+ pathlib.Path(str(cacheFileName)).suffix).encode(consoleEncoding) )
        print( ( 'cacheFile: \'' + str(cacheFileName)).encode(consoleEncoding) )
        sys.exit(1)
elif cacheFileName == None:
    cacheFileName = currentScriptPathOnly + '/' + defaultCacheFileLocation
cachePathOnly=str(pathlib.Path(cacheFileName).parent)


py3TranslateLLMfunctions.verifyThisFileExists(fileToTranslateFileName,'fileToTranslateFileName')
#Technically, languageCodesFileName only needs to be present if the mode is not parseOnly.
if mode != 'parseOnly':
    py3TranslateLLMfunctions.verifyThisFileExists(languageCodesFileName,'languageCodesFileName')
    #The cache file does not need to exist. if it does not exist, it will be created dynamically when it is needed as a Strawberry().


#sys.exit( ('\n Error: Please specify a valid input file. \n' + usageHelp).encode(consoleEncoding) )


if fileToTranslateFileExtensionOnly == '.csv':
    fileToTranslateIsASpreadsheet=True
elif fileToTranslateFileExtensionOnly == '.xlsx':
    fileToTranslateIsASpreadsheet=True
elif fileToTranslateFileExtensionOnly == '.xls':
    fileToTranslateIsASpreadsheet=True
elif fileToTranslateFileExtensionOnly == '.ods':
    fileToTranslateIsASpreadsheet=True
else:
    fileToTranslateIsASpreadsheet=False
    print( ( 'Error: Unrecognized extension for a spreadsheet: ' + str(fileToTranslateFileExtensionOnly) ).encode(consoleEncoding) )
    sys.exit(1)


# Either a raw.unparsed.txt must be specified or a raw.untranslated.csv if selecting one of the other engines.
# if using parseOnly, a valid file (raw.unparsed.txt and parseDefinitionsFile.txt) must exist.
if mode == 'parseOnly':
    pass

    # Check if valid parsing definition file exists. Example: parseKirikiri.py
    #py3TranslateLLMfunctions.verifyThisFileExists(parseSettingsFileName,'parseSettingsFileName')

#    if fileToTranslateIsASpreadsheet == True:
#        sys.exit( ('parseOnly is only valid with text files. It is not valid with spreadsheets: ' + str(fileToTranslateFileName)).encode(consoleEncoding) )

#    if parseSettingsFileName != None:
#        if os.path.isfile(parseSettingsFileName) != True:
#            sys.exit(('\n Error: Unable to find input file "' + fileToTranslateFileName + '"\n' + usageHelp).encode(consoleEncoding))
#    elif parseSettingsFileName == None:
#        print('\n Error: A pasing definitions file is required for \'parseOnly\' mode. Please specify a valid pasing file with --parsingSettingsFile (-pfile) .')#Should not error out even without encode(consoleEncoding) since it is using pure ascii.
#        sys.exit((usageHelp).encode(consoleEncoding))
#    else:
#        sys.exit(' Unspecified error.')
    #check to make sure parseOnly was not called with a spreadsheet extension, as those are invalid combinations


# Old code. Probably useful for later for use with different translation engines.
"""
if port == None:
    # Try to guess port from protocol and warn user.
    # split address using : and return everything before:
    protocol=address.split(':')[0]
    if protocol.lower() == 'http':
        port=defaultPortForHTTP
    elif protocol.lower() == 'https':
        port=defaultPortForHTTPS
    else:
        sys.exit( ('Port not specified and unable to guess port from protocol \''+protocol+'\' of address \''+address+'\' Please specify a valid port number between 1-65535.').encode(consoleEncoding) )
    print( ('Warning: No port was specified. Defaulting to port \''+port+'\' based on protocol \''+protocol+'\'. This is probably incorrect.') )
"""


# A prompt file must be specified when using LLMs. If using koboldcpp, make sure it exists.
if mode == 'koboldcpp':
    py3TranslateLLMfunctions.verifyThisFileExists(promptFileName, 'promptFileName')


# Check for local LLMs/NMTs py3translationserver/sugoi without address option. If LLM/NMT with address, then handle port assignment. Warn if defaulting to specific port.
# If using py3translationserver or sugoi, address must be specified, but default to using localhost.
# if port not specified, set port to default sugoi port and warn user.
# Change mode to py3translationserver at the end.
if (mode == 'koboldcpp') or (mode == 'py3translationserver') or (mode == 'sugoi'):
    if address == None:
        address=defaultAddress
        print( ('Warning: No address was specified for: '+ mode +'. Defaulting to: '+ defaultAddress +' This is probably incorrect.').encode(consoleEncoding) )
        #sys.exit( ('Error: Please specify address for sugoi translation engine. Example: http://localhost').encode(consoleEncoding) )
    if port == None:
        if mode == 'koboldcpp':
            print( ('Warning: No port specified for ' + mode + ' translation engine. Using default port of: ' + str(defaultKoboldCppPort)).encode(consoleEncoding) )
            port=defaultKoboldCppPort
        elif mode == 'py3translationserver':
            print( ('Warning: No port specified for ' + mode + ' translation engine. Using default port of: ' + str(defaultPy3TranslationServerPort)).encode(consoleEncoding) )
            port=defaultPy3TranslationServerPort
        elif mode == 'sugoi':
            print( ('Warning: No port specified for ' + mode + ' translation engine. Using default port of: ' + str(defaultSugoiPort)).encode(consoleEncoding) )
            port=defaultSugoiPort
    elif port != None:
        try:
            port=int(port)
            assert port >= minimumPortNumber #1
            assert port <= maximumPortNumber #65535
        except:
            sys.exit( ('Unable to verify port number: \''+str(port)+'\' Must be '+ str(minimumPortNumber)+'-' + str(maximumPortNumber) + '.').encode(consoleEncoding) )


# if using deepl_api_free, pro
if (mode == 'deepl_api_free') or (mode == 'deepl_api_pro'):
    # Library must be available.
    try:
        import deepl
    except:
        sys.exit( ('DeepL\'s python library is not available. Please install using: pip install deepl').encode(consoleEncoding) )
# api key must exist
    # maybe check both environmental variable and also a file?
    # The deepL library also requires it, so how does it need to be specified? Does it check any environmental variable for it?


# if using deepl_web... TODO validate anything it needs
    #probably the external chrome.exe right? Maybe requests library and scraping library.
    #Might need G-Chrome, + chromedriver.exe, and also a library wrapper, like Selenium.
    #Could require Chromium to be downloaded to resources/chromium/[platform]/chrome[.exe]
    # Syntax: os.environ['CT2_VERBOSE'] = '1'


if outputFileName == None:
    # If no outputFileName was specified, then set it the same as the input file. This will have the date and appropriate extension appended to it later.
    #outputFileName=fileToTranslateFileName
    #Update: Just do it here instead.
    outputFileName=fileToTranslateFileName + '.translated.' + py3TranslateLLMfunctions.getDateAndTimeFull() + defaultExportExtension 

outputFileNameWithoutPathOrExt=pathlib.Path(outputFileName).stem
outputFileExtensionOnly=pathlib.Path(outputFileName).suffix

if sourceLanguageRaw == None:
    sourceLanguageRaw = defaultSourceLanguage
if targetLanguageRaw == None:
    targetLanguageRaw = defaultTargetLanguage

#The target language is required to be present, but source language can be optional for LLMs and DeepL.
if sourceLanguageRaw != None:
    #Substitute a few language entries to certain defaults due to collisions and aliases.
    if sourceLanguageRaw.lower() == 'english':
        sourceLanguageRaw = 'English (American)'
    elif sourceLanguageRaw.lower() == 'castilian':
        sourceLanguageRaw = 'Spanish'
    elif sourceLanguageRaw.lower() == 'chinese':
        sourceLanguageRaw = 'Chinese (simplified)'
    elif sourceLanguageRaw.lower() == 'portuguese':
        sourceLanguageRaw = 'Portuguese (European)'

if (targetLanguageRaw == None) and (mode != 'parseOnly'):
    sys.exit('Error: A target language must be specified if not using parseOnly mode.')
elif (targetLanguageRaw != None):
    if targetLanguageRaw.lower() == 'english':
        targetLanguageRaw = 'English (American)'
    elif targetLanguageRaw.lower() == 'castilian':
        targetLanguageRaw='Spanish'


if contextHistoryLength == None:
    contextHistoryLength=defaultContextHistoryLength
elif contextHistoryLength != None:
    #if contextHistoryLength was specified, then assert that it is a number.
    contextHistoryLength=int(contextHistoryLength)


#Set encodings Last
##Set Encodings for files using dealWithEncoding.py helper library as dealWithEncoding.ofThisFile(myfile). 

#TODO: Clean this up. Very old code.
#First one is a special case since the encoding must be changed to shift-jis in the case of .ks (file extension).
#If an encoding was not specified for inputFile, and the extension is .ks, then default to shift-jis encoding and warn user of change.
#if an input file name was specified, then
if fileToTranslateFileName != None:
    #fileToTranslateFileNameWithPathNoExt, fileToTranslateFileExtensionOnly = os.path.splitext(fileToTranslateFileName)#Moved further up, made global/module wide. #Edit, moved into a function that is always called. Also checks for == None condition and errors out the program if not specified.
    #print(fileToTranslateFileNameWithPathNoExt)
    #print('Extension:'+fileToTranslateFileExtensionOnly)
    #if no encoding was specified, then...
    if commandLineArguments.fileToTranslateEncoding == None:
        if fileToTranslateFileExtensionOnly == '.ks':
            fileToTranslateEncoding=defaultTextEncodingForKSFiles #set encoding to shift-jis
            print(('Warning: KAG3 (.ks) input file specified, but no encoding was specified. Defaulting to '+defaultTextEncodingForKSFiles+' instead of '+defaultTextEncoding+'. If this behavior is not desired or produces corrupt input, please specify an encoding using --fileToTranslateEncoding (-fe) option instead.').encode(consoleEncoding))
        else:
            #If a file was specified, and if an encoding was not specified, and if the file is not a .ks file, then try to detect encoding
            #fileToTranslateEncoding=defaultTextEncoding#set encoding to default encoding
            fileToTranslateEncoding = dealWithEncoding.ofThisFile(fileToTranslateFileName, fileToTranslateEncoding, defaultTextEncoding)
    else:
        fileToTranslateEncoding=commandLineArguments.fileToTranslateEncoding#set encoding to user specified encoding
else:
    fileToTranslateEncoding=defaultTextEncoding#if an input file name was not specified, set encoding to default encoding


#outputFileName
outputFileEncoding=defaultTextEncoding
#For the output file encoding:  
#if the user specified an input file, use the input file's encoding for the output file
#if the user did not specify an input file, then the program cannot run, but they might have specified a spreadsheet (.csv, .xlsx, .xls, .ods)
#.csv's work normally since those are both plaintext and spreadsheets but reading encoding from .xlsx, .xls, and .ods is not possible without either hardcoding a specific encoding or using the designated libraries. dealWithEncoding should deal with it. If asked what the encoding of a binary spreadsheet format, then just return what the user specified at the command prompt or the default/fallbackEncoding.

#set rest of encodings using dealWithEncoding.ofThisFile(myFileName, rawCommandLineOption, fallbackEncoding):

#parsingSettingsFileEncoding=commandLineArguments.parsingSettingsFileEncoding
#parseSettingsFileEncoding = dealWithEncoding.ofThisFile(parseSettingsFileName, parsingSettingsFileEncoding, defaultTextEncoding)

promptFileEncoding = dealWithEncoding.ofThisFile(promptFileName, promptFileEncoding, defaultTextEncoding)

#languageCodesEncoding=commandLineArguments.languageCodesFileEncoding
languageCodesEncoding = dealWithEncoding.ofThisFile(languageCodesFileName, languageCodesFileEncoding, defaultTextEncoding)

#charaNamesDictionaryEncoding=commandLineArguments.characterNamesDictionaryEncoding
charaNamesDictionaryEncoding = dealWithEncoding.ofThisFile(charaNamesDictionaryFileName, characterNamesDictionaryEncoding, defaultTextEncoding)

#preDictionaryEncoding=commandLineArguments.preTranslationDictionaryEncoding
preDictionaryEncoding = dealWithEncoding.ofThisFile(preDictionaryFileName, preTranslationDictionaryEncoding, defaultTextEncoding)

#postDictionaryEncoding=commandLineArguments.postTranslationDictionaryEncoding
postDictionaryEncoding = dealWithEncoding.ofThisFile(postDictionaryFileName, postTranslationDictionaryEncoding, defaultTextEncoding)

#postWritingToFileDictionaryEncoding=commandLineArguments.postWritingToFileDictionaryEncoding
postWritingToFileDictionaryEncoding = dealWithEncoding.ofThisFile(postWritingToFileDictionaryFileName, postWritingToFileDictionaryEncoding, defaultTextEncoding)


##### Input validation is /finally/ done.  ######


if (verbose == True) or (debug == True):
    print( ('verbose='+str(verbose)).encode(consoleEncoding) )
    print( ('debug='+str(debug)).encode(consoleEncoding) )
    print( ('sourceLanguageRaw='+str(sourceLanguageRaw)).encode(consoleEncoding) )
    print( ('targetLanguageRaw='+str(targetLanguageRaw)).encode(consoleEncoding) )

#Instantiate basket of Strawberries. Start with languageCodes.csv  #Edit: Only languageCodes.csv is a Strawberry(). For the various dictionary.csv files, use Python dictionaries instead.
#languageCodes.csv could also be a dictionary or multidimension array, but then searching through it would be annoying, so leave as a Strawberry.
#Read in and process languageCodes.csv
#Format specificiation for languageCodes.csv
#Name of language in English, ISO 639 Code, ISO 639-2 Code
#https://www.loc.gov/standards/iso639-2/php/code_list.php
#Language list (Mostly) only languages supported by DeepL are currently listed, case insensitive.
#Syntax:
#The first row is entirely headers (column labels). Entries start from the 2nd row (row[1] if python list, row[2] if spreadsheet data structure):
#row 0) [languageNameReadable, 
#row 1) TwoLetterLanguageCodeThatIsNotAlwaysTwoLetters,
#row 2) ThreeLetterLanguageCodeThatIsNotAlwaysThreeLetters,
#row 3) DoesDeepLSupportThisLanguageTrueOrFalse,
#row 4) DoesThisLanguageNeedACustomSourceLanguageTrueOrFalse (for single source language but many target language languages like EN->EN-US/EN-GB)
#row 5) If #4 is True, then the full name source language
#row 6) If #4 is True, then the two letter code of the source language
#row 7) If #4 is True, then the three letter code of the source language
#Examples for 5-7: English, EN, ENG; Portuguese, PT-PT, POR
#Each row/entry is/has eight columns total.

#Old code:
#languageCodesWorkbook = chocolate.importFromCSV(languageCodesFileName)
#languageCodesSpreadsheet = languageCodesWorkbook.active

# skip reading languageCodesFileName if mode is parseOnly.
# Update: parseOnly mode is not really supported anymore. It should probably be renamed to dryRun mode where the purpose is to check for parsing errors in everything, including the languageCodes.csv and cache.xlsx files.
if mode != 'parseOnly':
    print('languageCodesFileName='+languageCodesFileName)
    print('languageCodesEncoding='+languageCodesEncoding)

    languageCodesSpreadsheet=chocolate.Strawberry(myFileName=languageCodesFileName,fileEncoding=languageCodesEncoding,removeWhitespaceForCSV=True)

    # replace this code with dedicated search functions from chocolate.Strawberry()
    # use....Strawberry().searchColumnsCaseInsensitive(spreadsheet, searchTerm)
    #languageCodesSpreadsheet

    #Source language is optional.
    if sourceLanguageRaw != None:
        #sourceLanguageCellRow, sourceLanguageCellColumn = languageCodesSpreadsheet.searchColumnsCaseInsensitive('lav')
        #sourceLanguageCellRow, sourceLanguageCellColumn = languageCodesSpreadsheet.searchColumnsCaseInsensitive('japanese')
        sourceLanguageCellRow, sourceLanguageCellColumn = languageCodesSpreadsheet.searchColumnsCaseInsensitive(sourceLanguageRaw)

        if (sourceLanguageCellRow == None) or (sourceLanguageCellColumn == None):
            sys.exit( ('Error: Unable to find source language \''+str(sourceLanguageRaw)+'\' in file: '+ str(languageCodesFileName)).encode(consoleEncoding) )

        print( ('Using sourceLanguage \''+sourceLanguageRaw+'\' found at \''+str(sourceLanguageCellColumn)+str(sourceLanguageCellRow)+'\' of: '+languageCodesFileName).encode(consoleEncoding) )

        sourceLanguageFullRow = languageCodesSpreadsheet.getRow(sourceLanguageCellRow)
        if debug == True:
            print( str(sourceLanguageFullRow).encode(consoleEncoding) )

        internalSourceLanguageName=sourceLanguageFullRow[0]
        internalSourceLanguageTwoCode=sourceLanguageFullRow[1]
        internalSourceLanguageThreeCode=sourceLanguageFullRow[2]
        if debug == True:
            print( ('internalSourceLanguageName='+internalSourceLanguageName).encode(consoleEncoding) )
            print( ('internalSourceLanguageTwoCode='+internalSourceLanguageTwoCode).encode(consoleEncoding) )
            print( ('internalSourceLanguageThreeCode='+internalSourceLanguageThreeCode).encode(consoleEncoding) )

    #Target language is optional when using parseOnly mode.
    if targetLanguageRaw != None:
        #targetLanguageCellRow, targetLanguageCellColumn = languageCodesSpreadsheet.searchColumnsCaseInsensitive('pie')
        targetLanguageCellRow, targetLanguageCellColumn = languageCodesSpreadsheet.searchColumnsCaseInsensitive(targetLanguageRaw)
        if (targetLanguageCellRow == None) or (targetLanguageCellColumn == None):
            sys.exit( ('Error: Unable to find target language \''+targetLanguageRaw+'\' in file: '+ languageCodesFileName).encode(consoleEncoding) )

        print( ('Using targetLanguage \''+targetLanguageRaw+'\' found at \''+str(targetLanguageCellColumn)+str(targetLanguageCellRow)+'\' of: '+languageCodesFileName).encode(consoleEncoding) )

        targetLanguageFullRow = languageCodesSpreadsheet.getRow(targetLanguageCellRow)
        if debug == True:
            print( str(targetLanguageFullRow).encode(consoleEncoding) )

        internalDestinationLanguageName=targetLanguageFullRow[0]
        internalDestinationLanguageTwoCode=targetLanguageFullRow[1]
        internalDestinationLanguageThreeCode=targetLanguageFullRow[2]
        if debug == True:
            print( ('internalDestinationLanguageName='+internalDestinationLanguageName).encode(consoleEncoding) )
            print( ('internalDestinationLanguageTwoCode='+internalDestinationLanguageTwoCode).encode(consoleEncoding) )
            print( ('internalDestinationLanguageThreeCode='+internalDestinationLanguageThreeCode).encode(consoleEncoding) )


# Read in all other dictionaries.
# charaNamesDictionaryFileName, preDictionaryFileName, postDictionaryFileName, postWritingToFileDictionaryFileName

# read in character dictionary
# This will either be 'None' if there was some sort of input error, like if the user did not specify one, or it will be a dictionary containing the charaName=value or other data that should be reverted after translation.
#The value entry in key=value in the charaNamesDictionary can be '' or None. Basically, this signifies that key contains a string that, if at the start of a line, means that line should not be ignored for paragraph consideration, but that it also should not be altered when submitting text for translation.
charaNamesDictionary = py3TranslateLLMfunctions.importDictionaryFromFile(charaNamesDictionaryFileName, charaNamesDictionaryEncoding)

#read in pre dictionary
preDictionary = py3TranslateLLMfunctions.importDictionaryFromFile(preDictionaryFileName, preDictionaryEncoding)

#read in post dictionary
postDictionary = py3TranslateLLMfunctions.importDictionaryFromFile(postDictionaryFileName, postDictionaryEncoding)

#read in afterWritingToFile dictionary
postWritingToFileDictionary = py3TranslateLLMfunctions.importDictionaryFromFile(postWritingToFileDictionaryFileName, postWritingToFileDictionaryEncoding)

if verbose == True:
    print( ('charaNamesDictionary='+str(charaNamesDictionary)).encode(consoleEncoding) )
    print( ('preDictionary='+str(preDictionary)).encode(consoleEncoding) )
    print( ('postDictionary='+str(postDictionary)).encode(consoleEncoding) )
    print( ('postWritingToFileDictionary='+str(postWritingToFileDictionary)).encode(consoleEncoding) )


# Next turn the main inputFile into a data structure.
# How? Read the file, then create data structure from that file.
# This returns a very special dictionary where the value in key=value is a special list and then add data row by row using the dictionary values #Edit, moved to chocolate.py so as to not have to do that. All spreadsheets that require a parseFile will therefore always be Strawberries from the chocolate library. # Update: No more parsefiles. That functionality has been moved to seperate program so chocolate.Strawberry() only understands spreadsheets and line-by-line parsing of text files.
# Strawberry is a wrapper class for the onenpyxl.workbook class with additional methods.
# The interface has no concept of workbooks vs spreadsheets. That distinction is handled only inside the class. Syntax:
# mainSpreadsheet=chocolate.Strawberry()
# py3TranslateLLMfunctions.parseRawInputTextFile

# if main file is a spreadsheet, then it be read in as a native data structure. Otherwise, if the main file is a .txt file, then it will be parsed as line-by-line.
# Basically, the user is responsible for proper parsing if line-by-line parsing does not work right. Proper parsing is outside the scope of py3TranslateLLM
# Create data structure using fileToTranslateFileName. Whether it is a text file or spreadsheet file is handled internally.
mainSpreadsheet=chocolate.Strawberry( fileToTranslateFileName, fileEncoding=fileToTranslateEncoding, removeWhitespaceForCSV=False, addHeaderToTextFile=False)

#Before doing anything, just blindly create a backup. #This code should probably be moved into a local function so backups can be created easier.
#backupsFolder does not have / at the end
backupsFolderWithDate=backupsFolder + '/' + py3TranslateLLMfunctions.getYearMonthAndDay()
pathlib.Path( backupsFolderWithDate ).mkdir( parents = True, exist_ok = True )
#mainDatabaseWorkbook.save( 'backups/' + py3TranslateLLMfunctions.getYearMonthAndDay() + '/rawUntranslated-' + currentDateAndTimeFull+'.xlsx')
backupsFilePathWithNameAndDate = backupsFolderWithDate + '/'+ fileToTranslateFileNameWithoutPathOrExt +'.raw.' + py3TranslateLLMfunctions.getDateAndTimeFull() + '.xlsx'
mainSpreadsheet.exportToXLSX( backupsFilePathWithNameAndDate )
#print( ('Wrote backup to: ' + backupsFilePathWithNameAndDate).encode(consoleEncoding) )

if debug == True:
    print( ('fileToTranslateFileNameWithoutPathOrExt=' + fileToTranslateFileNameWithoutPathOrExt).encode(consoleEncoding) )
    print( ( 'Today=' + py3TranslateLLMfunctions.getYearMonthAndDay() ).encode(consoleEncoding) )
    print( ( 'Yesterday=' + py3TranslateLLMfunctions.getYesterdaysDate() ).encode(consoleEncoding) )
    print( ( 'CurrentTime=' + py3TranslateLLMfunctions.getCurrentTime() ).encode(consoleEncoding) )
    print( ( 'DateAndTime=' + py3TranslateLLMfunctions.getDateAndTimeFull() ).encode(consoleEncoding) )


#Now that the main data structure has been created, the spreadsheet is ready to be translated.
if mode == 'parseOnly':
    mainSpreadsheet.export(outputFileName,fileEncoding=outputFileEncoding,columnToExportForTextFiles='A')

    #work complete. Exit.
    print( 'Work complete.' )
    sys.exit(0)

    # Old code. This functionality was moved to chocolate.Strawberry().export() as indicated above.
    #The outputFileName will match fileToTranslateFileName if an output file name was not specified. If one was specified, then assume it had an extension.
    if outputFileName == fileToTranslateFileName:
        mainSpreadsheet.exportToXLSX( outputFileName + '.raw.' + py3TranslateLLMfunctions.getDateAndTimeFull() + '.xlsx' )
        mainSpreadsheet.exportToCSV( outputFileName + '.raw.' + py3TranslateLLMfunctions.getDateAndTimeFull() + '.csv', fileEncoding=outputFileEncoding, errors=outputErrorHandling)
    elif outputFileExtensionOnly == '.csv':
        #Should probably try to handle the path in a sane way.
        mainSpreadsheet.exportToCSV(outputFileName)
    elif outputFileExtensionOnly == '.xlsx':
        mainSpreadsheet.exportToXLSX(outputFileName)
    elif outputFileExtensionOnly == '.xls':
        mainSpreadsheet.exportToXLS(outputFileName)
    elif outputFileExtensionOnly == '.ods':
        mainSpreadsheet.exportToODS(outputFileName)
    elif outputFileExtensionOnly == '.txt':
        mainSpreadsheet.exportToTextFile(outputFileName,'A')


#Now need to translate stuff.

# Cache should always be added. This potentially creates a situation where cache is not valid when going from one title to another or where it is used for translating entries for one character that another character spoke, but that is fine since that is a user decision to keep cache enabled despite the slight collisions.

if cacheEnabled == True:
    #First, initialize cache.xlsx file under backups/
    # Has same structure as mainSpreadsheet except for no speaker and no metadata. Still has a header row of course. Multiple columns with each one as a different translation engine.
    #if the path for cache does not exist, then create it.
    pathlib.Path( cachePathOnly ).mkdir( parents = True, exist_ok = True )

    # if cache.xlsx exists, then the cache file will be read into a chocolate.Strawberry(), otherwise, a new one will be created only in memory.
    # Initalize Strawberry(). Very tempting to hardcode utf-8 here, but... will avoid.
    cache=chocolate.Strawberry( myFileName=cacheFileName, fileEncoding=defaultTextEncoding, readOnlyMode=readOnlyCache )

    if py3TranslateLLMfunctions.checkIfThisFileExists(cacheFileName) != True:
        # if the Strawberry is brand new, add header row.
        cache.appendRow( ['rawText'] )

    if debug == True:
        cache.printAllTheThings()

    if readOnlyCache != True:
        cache.export(cacheFileName)

    # Prepare some static data for cacheAnyMatch so that it does not have to be prepared while in the loop on every loop.
    if cacheAnyMatch == True:
        blacklistedHeadersForCacheAnyMatch=defaultBlacklistedHeadersForCache
        blacklistedHeadersForCacheAnyMatch.append(translationEngine.model)

        # To help with a case insensitive search, make everything lowercase.
        counter=0
        for blacklistedHeader in blacklistedHeadersForCacheAnyMatch:
            blacklistedHeadersForCacheAnyMatch[counter]=blacklistedHeader.lower()
            counter+=1

        if cacheAnyMatch == True:
            # Return the cache header row.
            headers = cache.getRow( 1 )
            validColumnLettersForCacheAnyMatch=[]
            for header in headers:
                if str(header).lower() not in blacklistedHeadersForCacheAnyMatch:
                    # This should append the column letter, not the literal text, to the list.
                    validColumnLettersForCacheAnyMatch.append( cache.searchHeaders(header) )


# Implement KoboldAPI first, then DeepL, .
# Update: Implement py3translationserver, then Sugoi, then KoboldCPP's API then DeepL API, then DeepL Web, then OpenAI's API.
# Check current engine.
    # Echo request? Some firewalls block echo requests.
    # Maybe just assume it exists and poke it with various requests until it is obvious to the user that it is not responding?

# py3translationServer must be reachable Check by getting currently loaded model. This is required for the cache and mainSpreadsheet.
if mode == 'py3translationserver':
    translationEngine=translationEngines.Py3translationServerEngine(sourceLanguage=sourceLanguageFullRow, targetLanguage=targetLanguageFullRow, address=address, port=port)
    #Check if the server is reachable. If not, then exit. How? The py3translationServer should have both the version and model available at http://localhost:14366/api/v1/model and version, and should have been set during initalization, so verify they are not None.

    if translationEngine.model == None:
        print( 'translationEngine.model is None' )
        sys.exit(1)
    elif translationEngine.version == None:
        print( 'translationEngine.version is None' )
        sys.exit(1)


# SugoiNMT server must be reachable.

# KoboldAPI must be reachable. Check by getting currently loaded model. This is required for the cache and mainSpreadsheet.
    #if not exist model in main spreadsheet,
    #then add it to headers and return current column for model.
    #else, return current column for model.

# DeepL has already been imported, and it must have an API key. (already checked for)
    #Must have internet access then. How to check?
    # Added py3TranslateLLMfunctions.checkIfInternetIsAvailable() function.


if translationEngine.reachable != True:
    print( 'TranslationEngine \''+ mode +'\' is not reachable. Check the connection settings and try again.' )
    sys.exit(1)


# This will return the column letter of the model if the model is already in the spreadsheet. Otherwise, if it is not found, then it will return None.
currentMainSpreadsheetColumn = mainSpreadsheet.searchHeaders(translationEngine.model)
if currentMainSpreadsheetColumn == None:
    # Then the model is not currently in the spreadsheet, so need to add it. Update currentMainSpreadsheetColumn after it has been updated.
    headers = mainSpreadsheet.getRow( 1 )
    headers.append( translationEngine.model )
    mainSpreadsheet.replaceRow( 1, headers )
    currentMainSpreadsheetColumn = mainSpreadsheet.searchHeaders(translationEngine.model)
    if currentMainSpreadsheetColumn == None:
        print( 'unspecified error.' )
        sys.exit(1)


if cacheEnabled == True:
    # Check cache as well.
        #return the cache's column for model.
        #if not exist currentModel in cache,
        #then add it to headers
        #and return the cache's updated column for model.
    currentCacheColumn = cache.searchHeaders(translationEngine.model)
    if currentCacheColumn == None:
        # Then the model is not currently in the cache, so need to add it. Update currentCacheColumn after it has been updated.
        headers = cache.getRow(1)
        headers.append(translationEngine.model)
        cache.replaceRow( 1, headers )
        currentCacheColumn = cache.searchHeaders(translationEngine.model)
        if currentCacheColumn == None:
            print( 'unspecified error .' )
            sys.exit(1)


if translationEngine.supportsBatches == True:
    #translationEngine.batchTranslate()
    # if there is a limit to how large a batch can be, then the server should handle that internally.
    # Update: Technically yes, but it could also make sense to limit batch sizes on the application side, like if translating tens of thousands of lines or more, so there should also be a batchSize UI element in addition to any internal engine batch size limitations.
    #currentMainSpreadsheetColumn
    untranslatedEntriesColumnFull=mainSpreadsheet.getColumn('A')
    untranslatedEntriesColumnFull.pop(0) #This removes the header and returns the header.

    translateMe=[]
    tempRequestList=[]
    tempList=[]
    if cacheEnabled == True:
        tempList=cache.getColumn('A')
    if ( cacheEnabled == True ) and ( reTranslate != True ) and ( len(tempList) > 1 ):
        # Implement cache here. Create a list that will store the raw entry, whether there was a cache hit, and the value from the cache.
        # if there was not a cache hit, then add to a different list that will store the entries to translate as a batch.

        # Syntax: tempRequestList.append( [ 'rawEntry', thisValueIsFromCache, 'translatedData' ] )
        # Take every list entry from untranslatedEntriesColumnFull
        for untranslatedEntry in untranslatedEntriesColumnFull:

            # if entryInList/translatedData exists as a key in translationCacheDictionary,
            # if entryInList/untranslatedData exists in the cache's first column
            tempRowForCacheMatch=cache.searchFirstColumn( untranslatedEntry )
            if tempRowForCacheMatch != None:
                # then check if the appropriate column in the cache is a match.
                # This will return either None or the cell's contents.
                tempCellContents = cache.getCellValue( currentCacheColumn + str(tempRowForCacheMatch) )
                if tempCellContents != None:
                    # if there is a match, then a perfect hit exists, so append the translatedEntry to tempRequestList
                    tempRequestList.append( [ untranslatedEntry , True, tempCellContents ] )

                # elif the cache for that cell is currently empty, then the untranslatedEntry exists in the cache, but there was no cache hit for that model.
                elif tempCellContents == None:
                #else:

                    # Check if other models should be considered cache hits regardless of not being perfect matches.
                    # determine which columns should be considered to have possible matches
                    # Maybe check all entries past the first 3 blindly? Not valid for spreadsheets without speaker or metadata
                    # How about checking header for known bad headers and putting all other column letters into a list?
                    #cache.convertColumnNumberToColumnLetter()
                    # Known bad headers are...  rawText speaker metadata and currentModel
                    # Update: Moved header code up and out of function.
                    if ( cacheAnyMatch == True ) and ( len(validColumnLettersForCacheAnyMatch) > 0 ):
                    # if len(list) != 0, If it is 0, then do not bother. The length of that list could be 0 because even though the current model should always be added to cache and it could be returned, the current model should be blacklisted since the relevant cell was already checked.

                        # create a tempList=None
                        tempList=[]
                        # for every column letter in the list
                        for columnLetter in validColumnLettersForCacheAnyMatch:
                            # prepend row, tempRowForCacheMatch, and return the individual cell contents.
                            # if the cell contents are not None,
                                # then tempList = [rawEntry, thisValueIsFromCache=True, translatedData]
                            # Keep updating the tempList to favor the right-most translation engine.

                            tempCellContents = cache.getCellValue( columnLetter + str(tempRowForCacheMatch) )
                            if tempCellContents != None:
                                tempList.append( [ untranslatedEntry, True, tempCellContents ] )

                        # if tempList != None:
                        if len(tempList) > 0:
                            # then take the contents of the right-most/last list in tempList and append them to tempRequestList
                            # tempRequestList.append( [tempList[0], tempList[1], tempList[2] ] )
                            # len(tempList) returns the number of items in a list. To get the last item, take the total items and subtract 1 because indexes start with 0.
                            tempRequestList.append( tempList[ len(tempList) - 1 ] )

                    # else only perfect hits should be considered
                    # elif cacheAnyMatch == False:
                    else:
                        tempRequestList.append( [ untranslatedEntry , False, untranslatedEntry ] )
                        translateMe.append( untranslatedEntry )

            #else untranslatedEntry is not in the cache
            #elif tempRowForCacheMatch == None:
            else:
                # The rawEntry does not exist in the cache.
                tempRequestList.append( [ untranslatedEntry , False, untranslatedEntry ] )
                translateMe.append( untranslatedEntry )

            # Old code:
#            if entry in translationCacheDictionary.keys():
                # then add entry/i to tempRequestDictionary with thisValueIsFromCache=True
                #tempRequestDictionary[entry]=[True,translationCacheDictionary[entry]]
#                tempRequestList.append( [ i, True, translationCacheDictionary[entry] ] )
#            else:
                # Otherwise, it needs to be processed.
                # Create a list of all the values where thisValueIsFromCache == False. Maybe create this during parsing?
                # Add it to the dictionary with thisValueIsFromCache=False
#                tempRequestList.append( [ entry, False, entry ] )
                # Append it to the translateMe list.
#                translateMe.append(entry)

    # if the cache is not enabled, if the user specified to reTranslate all lines, if the cache is too small, then skip
    #elif ( cacheEnabled != True ) or ( reTranslate == True ) or ( len(cache.getColumn('A')) <=1 ):
    else:
        translateMe=untranslatedEntriesColumnFull

    postTranslatedList = []
    if debug==True:
        print( ( 'translateMe=' + str(translateMe) ).encode(consoleEncoding) )
    # Only attempt to translate entries if there was at least one entry not found in the cache.
    if len(translateMe) > 0:
        # There should probably be batch size limiter logic here.
        postTranslatedList = translationEngine.batchTranslate( translateMe )
    if debug==True:
        print( ( 'postTranslatedList=' + str(postTranslatedList) ).encode(consoleEncoding) )

    finalTranslatedList=[]
    if cacheEnabled == True:
        # if every entry was found in the cache

        #if reTranslate == True, then len(tempRequestList) == 0, so do not bother trying to read entries from it. Just set output to postTranslatedList.
        if reTranslate != True:
            if len(postTranslatedList) == 0:
                #then set finalTranslatedList to all the translated entries that were added to tempRequestList.
                for i in tempRequestList:
                    finalTranslatedList.append( tempRequestList[2] )
            # if cache is empty, so only the header is returned. There is nothing to merge, so set the output to the postTranslatedList.
            elif len( cache.getColumn('A') ) == 1:
                finalTranslatedList=postTranslatedList
            else:
                counter=0
                # Need to merge processed items, postTranslatedList, with tempRequestList for finalTranslatedList.
                # iterate over postTranslatedList, for every entry 
                for translation in postTranslatedList:
                    # if the valueIsFromCache == True
                    if tempRequestList[1] == True:
                        #append entry[2] to final finalTranslatedList
                        finalTranslatedList.append( tempRequestList[2] )
                    # elif the valueIsNotFromCache, valueIsFromCache==False
                    else:
                        # then append the recently translated value, postTranslatedList[counter]
                        finalTranslatedList.append( postTranslatedList[counter] )
                        # and increase the counter.
                        counter += 1
                    # go to next entry

        #elif reTranslate == True:
        else:
            finalTranslatedList=postTranslatedList

        if debug == True:
            print( 'len(finalTranslatedList)=' + str(len(finalTranslatedList)) )
            print( 'len(untranslatedEntriesColumnFull=' + str(len(untranslatedEntriesColumnFull)) )
        assert( len(finalTranslatedList) == len(untranslatedEntriesColumnFull) )

        if ( len(postTranslatedList) != 0 ) and ( readOnlyCache == False ):
            # finalTranslatedList and untranslatedEntriesColumnFull need to be added to the cache file now.
            counter=0
            tempSearchResult = '':
            #for every entry
            for untranslatedString in untranslatedEntriesColumnFull:
                # tempSearchResult can be a row number (as a string) or None if the string was not found.
                tempSearchResult=cache.searchFirstColumn( untranslatedString )
                #if the untranslatedString is not in the cache
                if tempSearchResult == None:
                    #then just append a new row with one entry, retrieve that row number, then set the appropriate column's value.
                    cache.appendRow( [ untranslatedString ] )
                    # This returns the row number of the found entry as a string.
                    tempSearchResult=cache.searchFirstColumn( untranslatedString )
                    cache.setCellValue( currentCacheColumn + str(tempSearchResult) , finalTranslatedList[counter] )

                # elif the untranslatedString is in the cache
                # elif tempSearchResult != None:
                else:
                    #, then get the appropriate cell, the currentCacheColumn + temporaryRow.
                    currentCellAddress=currentCacheColumn + str(tempSearchResult)
                    # if the cell's value is None
                    if cache.getCellValue(currentCellAddress) == None:
                        # then replace the value
                        cache.setCellValue( currentCellAddress, finalTranslatedList[counter] )
                    # elif the cell's value is not empty
                    else:
                        # Only update the cache if overrideWithCache == True
                        if overrideWithCache == True:
                            cache.setCellValue( currentCellAddress, finalTranslatedList[counter] )
                counter += 1

        if readOnlyCache != True:
            cache.export(cacheFileName)

    #if reTranslate == True, always update all entries in the cache
    else:
        finalTranslatedList=postTranslatedList


# Old code.
#    counter=0
#    for rawTextEntry in untranslatedEntriesColumnFull:
#        if cache. rawTextEntry
#cache.searchFirstColumn('searchTerm') #can be used to check only the first column. Returns either None if not found or currentRow number if it was found.


    # Always replacing the target column is only valid for batchMode == True and also if overrideWithCache == True. Otherwise, any entries that have already been translated, should not be overriden and batch replacements are impossible since each individual entry needs to be processed for non-batch modes.
    if overrideWithCache == True:
        finalTranslatedList.insert( 0, translationEngine.model ) # Put header back. This returns None.
        mainSpreadsheet.replaceColumn( currentMainSpreadsheetColumn , finalTranslatedList ) # Batch replace the entire column.

    #if overrideWithCache != True:
    else:
        # Consider each entry individually.
        listCounter=0
        currentRow=2 # Start with row 2. Rows start with 1 instead of 0 and row 1 is always headers. Therefore, row 2 is the first row number with untranslated/translated pairs. 
        for untranslatedString in untranslatedEntriesColumnFull:
            #Searching might be pointless here because the entries should be ordered. It should be possible to simply increment both untranslatedEntriesColumnFull and finalTranslatedList.
            #tempSearchResult=cache.searchFirstColumn( untranslatedString )

            currentTranslatedCellAddress=currentMainSpreadsheetColumn + str(currentRow)
            # Check if the entry is current None. if entry is none
            if mainSpreadsheet.getCellValue(currentTranslatedCellAddress) == None:
                # then always update the entry
                mainSpreadsheet.setCellValue(currentTranslatedCellAddress, value)
            # if entry is not none
                # then do not override entry

else:
    #translationEngine.translate()
    pass

# Now that all entries have been translated, process them to put them into the spreadsheet data structure in the specified column.
# if overrideWithCache == True: then always output cell contents even if the cell's contents already exist.

mainSpreadsheet.export(outputFileName,fileEncoding=outputFileEncoding,columnToExportForTextFiles=currentMainSpreadsheetColumn)
#mainSpreadsheet.printAllTheThings()

#Now have two column letters for both currentMainSpreadsheetColumn and currentCacheColumn.
#currentCacheColumn can be None if cache is disabled. cache might also be set to read only mode.

# Read in raw untranslated cell from column A in spearsheet.
# create counter, currentRow=1
# get column A, the untranslated column
# for every cell in A, try to translate it.
    # first check cache
    # if cache enabled
        # search column A in cache for raw untranslated there is a match
        # if cache is normal, get cell back and check if that cell is not None
        # if cache is any row, then return all rows in Strawberry() and check if any are not None. Select right-most cell as final value.
        # if cache hit confirmed, then set this to postTranslatedText=
        # check with postTranslationDictionary, a Python dictionary for possible updates
        # and then write cache hit to mainSpreadsheet cell
        # and move on to next cell
    # if there is no match, then the fun begins
        # remove all \n's in the line
        # perform replacements specified by charaNamesDictionary
        # perform replacements specified by preTranslationDictionary
        # submit the line to the translation engine, along with the current dequeue #TODO: add options to specify history length of dequeue to the CLI
        # once it is back check to make sure it is not None or another error value
        # add it to the dequeue, murdering the oldest entry in the dequeue
        # perform replacements specified by charaNamesDictionary, in reverse
        # If cache enabled, add the untranslated line and the translated line as a pair to the cache file.
            # The untranslated line belongs in a new row. Really? Always? Well it is not gurantted to be unique because the line may have been translated before but not using that particular translation engine. So the cache cell may need to be filled, but on a previous entry. So.... search for the cell (already did earlier). Save if there was a hit or not. Check if None. If none, then append. If not none, then use existing row. Do not fill in untranslated text. Instead only add translated text in column currently in use by current translation engine/model.
            #the translated line belongs in the column specified.
        # s

#when done processing text, currentRow+=1
#How to check how much time has passed? To see if periodic output should be written. Could also do it programatically every twenty or so lines, but would be better if the minute did not match at least.















# https://openpyxl.readthedocs.io/en/stable/optimized.html
# readOnlyMode requires closing the spreadsheet after use.
if readOnlyCache == True:
    cache.close()

print('end reached')
sys.exit(0)
"""

#CharaNamesDictionary time to shine
CharacterNames=['[＠クロエ]','Chloe']#change this to a dictionary
#If an ignored line starts with a character name, that could create problems, so swap names first, then parse lines into main database.
#if one was specified, import character definitions file, and perform swaps while inputfile is still in memory but has not yet been parsed line by line.
#inputFileContents.replaceStuffHere()

#somehow this line needs to run
#inputFileContents=inputFileContents.replace('[＠クロエ]','Chloe')


#initialize main data structure
#mainDatabaseWorkbook = Workbook()
#mainDatabaseSpreadsheet = mainDatabaseWorkbook.active

#This will hold raw untranslated text, number of lines each entry was derived from, and columns containing maybe translated data. Maximum columns supported = 9[?]. Columns 0 and 1 are reserved for Raw untranslated text and [1] is reserved for the number of lines that column 0 represents, even if it is always 1 because line-by-line parsing (lineByLineMode) is specified.
#Alternatively, lineByLineMode can instead specify to feed each line into the translator but the paragraphDelimiter=emptyLine can support multiple lines in the main data structure. That might be more flexible, or make things worse. Leave it to user to decide on a case-by-case basis by allowing for this possibility.
#class Database:
#    def __init__(self):

# The mainSpreadsheet data structure should hold:
# Column 1) each paragraph.raw.text (with \n's inside of it)
# Column 2) Reserved for the speaker of the line (if any) as this singular piece of metadata is very important and should also be user editable. Leave as empty if None.
# Column 3) metadata possibilities:
    #The # of lines #1 was taken from? This can be computed dynamically since the untranslated text is being stored verbetum. Metadata could say... 3 lines, from line #'s 23, 24, 25
    #The line number the first entry for the paragraph was sourced from. When replacing lines, the line numbers will change if the entries are not 1:1 so this might be less useful than it seems. It could be a hint as to approximately where the untranslated lines are from however, but how is that useful?
    #maybe the last line as well
    # possibly whether the line has been translated or not? It might be hard to figure out otherwise, but this is also more of an efficiency thing than actually needed. Can figure it out easily enough by knowing the current translation engine or getting a list of the available translation engines and checking the cell contents returned in getRow(7) for the None value of the appropriate columns.
    #other arbitary data to be decided later like booleans
    #Has the file been processed with characterDictionary? It is not *entirely* invalid to have a toggle for this and to put the post characterDictionary untranslated text in column 1. But it is a better idea not to have this and instead just output any post charaDictionary text into another column so that both are available if that is desired. The text to submit to the translation engine still needs to be computed dynamically anyway. However, without it and without outputting to another column, then py3stringReplace should be updated to support .csv files already.
# Metadata problems:
    # Metadata can also just be overtly missing in the case of imported spreadsheet files, so it is also just fundamentally unreliable.
    # The number of lines in the source cell can also be determined dynamically by counting line breaks.
    # Which lines to replace in the destination can be determined dynamically. 
        # Replacements can be done either globally (for line-by-line reading) or sequentially as well.
    # Already translated or not decision should be computed dynamically and on a line-by-line basis (raw + chosen translator engine determined from header to calculate target cell) in order to support resume operations and cache, so do not add this to metadata.
# Metadata Decision: reserve column 3 for metadata for future use in case special processing or data is ever needed for certain types of source files, but do not use it yet since no information needs to be there to process file except for the character name and character name metadata is important enough to have its own column.
# Old: For now use the following string:  'numberOfSourceLines_WasADictionaryUsedTrueOrFalse' ex. '2_False_'
# New: for now use: dictionary[key]=[characterName,str(currentParagraphLineCount)]    So a dictionary containing a [list] filled with the character name and currentParagraphLineCount
# Column 4) all translations, each with its own entry and an associated header for which type it is (Kobold+model; py3translationserver/sugoi)
# Aside: For DeepL, DeepL API Free/Pro and DeepL Web should all be the same right? Free, Pro, and Web versions all support dictionaries, but doing dictionary + document translation requires pro. Documents will be parsed prior to using the API, so this limitation does not apply here, thus all DeepL translations should be the same. DeepL's native dictionary system is also unlikely to be implemented here especially considering they are hard to work with (not mutable). Edit: DeepL dictionaries might end up being implemented here after all to deal with certain special cases because that is the only way to tell the DeepL translation engine to always translate a particular string a certain way, and that is a very useful capability.
# Potentially, koboldcpp LLM could return different models. Use the returned model header name. All data should be put in that column. Determine correct header as in: DeepL, or koboldcpp/model in a case sensitive way. More examples:
# headers=['rawText', 'metadata', 'DeepL', 'koboldcpp/Mixtral-13B.Q8_0','Google']


#Add headers
initialHeaders=['rawText','speaker','metadata']
mainDatabaseSpreadsheet.append(initialHeaders)

# printAllTheThings(mainDatabaseSpreadsheet)

# start parsing input file line by line
# print(inputFileContents.encode(consoleEncoding))
# print(inputFileContents.partition('\n')[0].encode(consoleEncoding)) #prints only first line



# parseRawInputTextFile() accepts an (input file name, the encoding for that text file, parseFileDictionary as a Python dictionary, the character dictionary as a Python dictionary) and returns a dictionary where the key is the dialogue, and the value is a list. The first value in the list is the character name, (or None for no chara name), and the second is metadata as a string using the specified delimiter.
# This could also be a multidimension array, such as a list full of list pairs [ [ [],[ [][][] ] ] , [ [],[ [][][] ] ] ]  because the output is highly regular, but that would allow duplicates.  Executive decision was made to disallow duplicates for files since that is correct almost always. However, it does mess with the metadata sometimes by having the speaker be potentially incorrect.
temporaryDict=parseRawInputTextFile(inputFile,inputFileEncoding,parseFileDictionary, characterDictionary)

temporaryDict={}        #Dictionaries do not allow duplicates, so insert all entries into a dictionary first to de-duplicate entries, then read dictionary into first column (skip first line/row in target spreadsheet)
#thisdict.update({"x": "y"}) #add to/update dictionary
#thisdict["x"]="y"              #add to/update dictionary
#for x, y in thisdict.items():
#  print(x, y) 


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
pathlib.Path('backups/'+currentDateFull).mkdir(parents=True, exist_ok=True)
#mainDatabaseWorkbook.save('backups/'+currentDateFull+'/rawUntranslated-'+currentDateAndTimeFull+'.xlsx')
#print(inputFileContents.partition('\n')[0].encode(consoleEncoding)) #prints only first line

# Once all lines are input into a dictionary, if specified, read the preDictionary.csv and perform replacements prior to submission to translation engine.
# For DeepL, run DeepL's special code to replace braces {{ }}  {{{ }}}  with special markers that the DeepL engine can escape before submission to the translation engine.


#do in memory replacements for CharaNames
#Replace [＠クロエ] with Chloe, but keep a record that it was replaced in order to replace it back after translation.
#Should be read from a c.csv that includes
#1) Information that should be preserved in the final translation as-is, but that will also be submitted to the translation engine for consideration so the position of the name or other string can influence the translation itself.
#To alter specific strings in the text before submission to the translation engine that will also be kept in the translated text, use preDictionary.csv. To alter specific parts of the text after translation, use postDictionary.csv.

# For character names, either:
# Need to know, gender (m, f, u), since that might influence the translation.  Can also append that information to prompt for LLM models.
# Could also ask user to specify a replacement name. This might be a better idea.



#The input file must be either a raw file (.ks, .txt, .ts) or a spreadsheet file (.csv, .xlsx, .xls, .ods), so the encoding for the spreadsheets... is that always utf-8?
#Raw files can be spreadsheets with one column, but spreadsheet files cannot be raw files. So include a switch that signifies to process text files as psudo .csv spreadsheets? No. Just have user convert them to .csv manually instead. Then no special handling is needed for 'special' \n deliminated .csv's. This feature can be added later if requested.
#However, when using files exported from other programs. There will be no metadata. Instead of adding a cli flag, fallback to line-by-line mode instead and warn user about it. Fallback to line by line mode should also occur if the metadata is corrupted. Is that really necessary? Lines count can be found based upon column 1 entries, and word wrap settings only need the parsedefintions file. That is sperate from translating, which can still be done using previously obtained paragraphs. Speaker will be missing.


"""
