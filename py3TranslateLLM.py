#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: py3TranslateLLM.py translates text using Neural Machine Translation (NMT) and Large Language Models (LLM).

Usage: See py3TranslateLLM.py -h', README.md, and the source code below.

License:
- This .py file and the libraries under resources/* are Copyright (c) 2024 gdiaz384 ; License: GNU Affero GPL v3.
- https://www.gnu.org/licenses/agpl-3.0.html
- Exclusion: The libraries under resources/translationEngines/* may each have different licenses.
- For the various 3rd party libraries outside of resources/, see the Readme for their licenses, source code, and project pages.

"""
__version__ = '2024.06.23 alpha'

# Set defaults and static variables.
# Do not change the defaultTextEncoding. This is heavily overloaded.
defaultTextEncoding = 'utf-8'
defaultConsoleEncoding = 'utf-8'

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

validSpreadsheetExtensions = [ '.csv', '.xlsx', '.xls', '.ods', '.tsv' ]
defaultAddress = 'http://localhost'
defaultKoboldCppPort = 5001
defaultPy3translationServerPort = 14366
defaultSugoiPort = 14366
minimumPortNumber = 1
maximumPortNumber = 65535 #16 bit integer -1
defaultPortForHTTP = 80
defaultPortForHTTPS = 443
defaultTimeout = 360 # Per request to translation engine in seconds. Set to 0 to disable.

# LLMs tend to hallucinate, so setting this overly high tends to corrupt the output. It should also be reset back to 0 periodically, like when it gets full, so the corruption of one bad entry does not spread too much.
defaultContextHistoryMaxLength = 6
# This setting only affects LLMs, not NMTs.
defaultEnableBatchesForLLMs = False
# Valid options for defaultBatchSizeLimit are an integer or None. Sensible limits are 100-10000 depending upon hardware. In addition to this setting, translation engines also have internal limiters.
#defaultBatchSizeLimit = None
defaultBatchSizeLimit = 1000
defaultSceneSummaryLength = 50
defaultInputTextEncodingErrorHandler = 'strict'
#defaultOutputTextEncodingErrorHandler = 'namereplace'  # This get set dynamically further below.

defaultLinesThatBeginWithThisAreComments = '#'
defaultAssignmentOperatorInSettingsFile = '='
defaultMetadataDelimiter = '_'
defaultScriptSettingsFileExtension = '.ini'
# if a column begins with one of these entries, then it will be assumed to be invalid for cacheAnyMatch. Case insensitive.
defaultBlacklistedHeadersForCache = [ 'rawText','speaker','metadata' ] #'cache', 'cachedEntry', 'cache entry'

# Currently, these are relative to py3TranslateLLM.py, but it might also make sense to move them either relative to the target or to a system folder intended for holding program data.
# There is no gurantee that being relative to the target is a sane thing to do since that depends upon runtime usage, and centralized backups also make sense. Leaving it as-is makes sense too as long as py3TranslateLLM is not being used as a library. If it is not being used as a library, then a centralized location under $HOME or %localappdata% makes more sense than relative to py3TranslateLLM.py. Same with the default location for the cache file.
# Maybe a good way to check for this is the name = __main__ check?
# It might make sense to create the spreadsheet.translated.backup.[date].xlsx relative to the target spreadsheed or perhaps in a backups folder that is relative to the target. However, cache should be either centralized in an os specific application data directory or stored along with main program.
defaultBackupsFolder = 'backups'
defaultExportExtension = '.xlsx'
defaultCacheFileLocation = defaultBackupsFolder + '/cache' + defaultExportExtension
# Cache is always saved at the end of an operation if there are any new entries, so this is only used for translations that take a very long time.
#defaultMinimumSaveIntervalForCache = 60 # For debugging.
defaultMinimumSaveIntervalForCache = 300 # In seconds. 240 is once every four minutes which means that, at most, only four minutes worth of processing time should be lost due to a program or translation engine error. 300 if 5 min.
defaultMinimumSaveIntervalForMainSpreadsheet = 540 #240 # In seconds. 240 is every 4 minutes. 540 is every 9 minutes
defaultSceneSummaryCacheLocation = defaultBackupsFolder + '/sceneSummaryCache' + defaultExportExtension
defaultMinimumSaveIntervalForSceneSummaryCache = 540

# These two lists do not determine if the values are True/ False by default. Use action='store_true' and 'store_false' in the CLI options to toggle defaults and then update these two lists. These lists ensure the values are toggled correctly if a different than default setting is specified in program.ini when merging the CLI options with the options from the .ini .
booleanValuesTrueByDefault = [ 'cache', 'batches', 'backups']
booleanValuesFalseByDefault = [ 'cacheAnyMatch', 'overrideWithCache', 'reTranslate', 'readOnlyCache', 'sceneSummaryEnableTranslation', 'batchesEnabledForLLMs', 'rebuildCache', 'resume', 'testRun', 'verbose', 'debug', 'version' ]

translationEnginesAvailable = 'cacheOnly, koboldcpp, deepl_api_free, deepl_api_pro, deepl_web, py3translationserver, sugoi, pykakasi, cutlet'
usageHelp = ' Usage: python py3TranslateLLM --help  Example: py3TranslateLLM -te KoboldCpp -f myInputFile.ks \n Translation Engines: ' + translationEnginesAvailable + '.'


# import various libraries that py3TranslateLLM depends on.
import argparse                           # Used to add command line options.
import os, os.path                        # Extract extension from filename, and test if file exists.
#from pathlib import Path             # Override file in file system with another and create subfolders.
#import pathlib.Path                     # Does not work. Why not? Maybe because Path is a class and not a Path.py file? So 'from' crawls into files? Maybe from 'requires' it. Like Path must be a class inside of pathlib instead of a file named Path.py. 'import' does not seem to care whether it is importing files or classes. They are both made available. But 'from' might.
import pathlib                               # Works.   #dir(pathlib) does list 'Path', so just always use as pathlib.Path Constructor is pathlib.Path(mystring). Remember to convert it back to a string if printing it out.
import sys                                    # End program on fail condition.
import io                                      # Manipulate files (open/read/write/close).
import random                              # Used to get a random number. Used when writing out cache to write it to a temporary file.
#from io import IOBase                 # Test if variable is a file object (an "IOBase" object).
#import datetime                           # Used to get current date and time.
import time                                   # Used to write out cache no more than once every 300s and also limit writes to mySpreadsheet.backup.xlsx .

# Technically, these two are optional for parseOnly. To support or not support such a thing... probably yes. # Update: Maybe.
#from collections import deque  # Used to hold rolling history of translated items to use as context for new translations.
#import collections                         # Newer syntax. For collections.deque. Used to hold rolling history of translated items to use as context for new translations.
import queue
import hashlib                              # Allow calculating the sha1 hash for batches of entries when using the experimental sceneSummary feature.

import requests                            # Do basic http stuff, like submitting post/get requests to APIs. Must be installed using: 'pip install requests' # Update: Moved to functions.py # Update: Also imported here because it can be useful to parse exceptions (errors) when submitting entries for translation.

#import openpyxl                           # Used as the core internal data structure and to read/write xlsx files. Must be installed using pip. # Update: Moved to chocolate.py
import resources.chocolate as chocolate # Implements openpyxl. A helper/wrapper library to aid in using openpyxl as a datastructure.
import resources.dealWithEncoding as dealWithEncoding   # dealWithEncoding implements the 'chardet' library which is installed with 'pip install chardet'  Same with 'pip install charamel' and 'pip install charset-normalizer'
import resources.functions as functions  # Moved most generic functions here to increase code readability and enforce function best practices for logic not directly relevant to main().

# The above syntax assumes all of the libraries are under resources. To import the libraries directly regardless of where they are on the file system:
# import sys
# import pathlib
# sys.path.append( str( pathlib.Path('C:/resources/chocolate.py').resolve().parent ) )
# import chocolate

#from resources.functions import * # Do not use this syntax if at all possible. The * is fine, but the 'from' breaks everything because it copies everything instead of pointing to the original resources which makes updating library variables borderline impossible.

try:
    import tqdm                             # Optional library to add pretty progress bars.
    tqdmAvailable = True
except:
    tqdmAvailable = False

#Using the 'namereplace' error handler for text encoding requires Python 3.5+, so use an older one if necessary.
if sys.version_info.minor >= 5:
    defaultOutputTextEncodingErrorHandler = 'namereplace'
elif sys.version_info.minor < 5:
    defaultOutputTextEncodingErrorHandler = 'backslashreplace'    


# So, py3translateLLM.py also supports reading program settings from py3translateLLM.ini in addition to the command prompt.
# Rule is that settings from the command line take #1 precedence
# Then #2) entries from .ini
# Then #3) settings hardcoded in .py
# So, initialize all non-boolean CLI settings to None. Then, only change them using settings.ini or defaultSettings if they are still None after reading from CLI. Any settings that are not None were set using the CLI, so leave them alone.
# For boolean values, they are all False by default. Only change to True if the scriptSettingsDictionary set them to True. Well, that means any CLI settings as intended to be default of 'False' will be overriden to True. Well, that is a user error. Let them deal with it since they were the ones that decided to change the default settings.

def createCommandLineOptions():
    # Add command line options.
    commandLineParser=argparse.ArgumentParser( description='Description: Translates text using various NMT and LLM models.' + usageHelp )
    commandLineParser.add_argument( '-te', '--translationEngine', help='Specify translation engine to use, options=' + translationEnginesAvailable + '.', type=str )

    commandLineParser.add_argument( '-f', '--fileToTranslate', help='Either the raw file to translate or the spreadsheet file to resume translating from, including path.', default=None, type=str )
    commandLineParser.add_argument( '-fe', '--fileToTranslateEncoding', help='The encoding of the input file. Default=' + str( defaultTextEncoding ), default=None, type=str )
    commandLineParser.add_argument( '-of', '--outputFile', help='The file to insert translations into, including path. Default is same as input file.', default=None, type=str )
    commandLineParser.add_argument( '-ofe', '--outputFileEncoding', help='The encoding of the output file. Default is same as input file.', default=None, type=str)

    commandLineParser.add_argument( '-pf', '--promptFile', help='This file has the prompt for the LLM.', default=None, type=str )
    commandLineParser.add_argument( '-pfe', '--promptFileEncoding', help='Specify encoding for prompt file, default=' + str( defaultTextEncoding ), default=None, type=str )
    commandLineParser.add_argument( '-mf', '--memoryFile', help='This file has the memory for the LLM. Optional.', default=None, type=str )
    commandLineParser.add_argument( '-mfe', '--memoryFileEncoding', help='Specify encoding for the memory file, default=' + str( defaultTextEncoding ), default=None, type=str )

    commandLineParser.add_argument( '-lcf', '--languageCodesFile', help='Specify a custom name and path for languageCodes.csv. Default=\'' + str( defaultLanguageCodesFile ) + '\'.', default=None, type=str )
    commandLineParser.add_argument( '-lcfe', '--languageCodesFileEncoding', help='The encoding of file languageCodes.csv. Default=' + str( defaultTextEncoding ), default=None, type=str )
    commandLineParser.add_argument( '-sl', '--sourceLanguage', help='Specify language of source text. Default=' + str( defaultSourceLanguage ), default=None, type=str )
    commandLineParser.add_argument( '-tl', '--targetLanguage', help='Specify language of source text. Default=' + str( defaultTargetLanguage ), default=None, type=str )

    commandLineParser.add_argument( '-cnd', '--characterNamesDictionary', help='The file name and path of characterNames.csv', default=None, type=str )
    commandLineParser.add_argument( '-cnde', '--characterNamesDictionaryEncoding', help='The encoding of file characterNames.csv. Default=' + str( defaultTextEncoding ), default=None, type=str )
    commandLineParser.add_argument( '-revd', '--revertAfterTranslationDictionary', help='The file name and path of revertAfterTranslation.csv', default=None, type=str )
    commandLineParser.add_argument( '-revde', '--revertAfterTranslationDictionaryEncoding', help='The encoding of file revertAfterTranslation.csv. Default=' + str( defaultTextEncoding ), default=None, type=str )
    commandLineParser.add_argument( '-pred', '--preTranslationDictionary', help='The file name and path of preTranslation.csv', default=None, type=str)
    commandLineParser.add_argument( '-prede', '--preTranslationDictionaryEncoding', help='The encoding of file preTranslation.csv. Default=' + str( defaultTextEncoding ), default=None, type=str)
    commandLineParser.add_argument( '-postd', '--postTranslationDictionary', help='The file name and path of postTranslation.csv.', default=None, type=str )
    commandLineParser.add_argument( '-postde', '--postTranslationDictionaryEncoding', help='The encoding of file postTranslation.csv. Default=' + str( defaultTextEncoding ), default=None, type=str )
    # Update: postWritingToFileDictionary might only make sense for text files.
    commandLineParser.add_argument( '-postwd', '--postWritingToFileDictionary', help='The file name and path of postWritingToFile.csv.', default=None, type=str )
    commandLineParser.add_argument( '-postwde', '--postWritingToFileDictionaryEncoding', help='The encoding of file postWritingToFile.csv. Default=' + str( defaultTextEncoding ), default=None, type=str )

    commandLineParser.add_argument( '-c', '--cache', help='Toggles cache. Specifying this will disable using or updating the cache file for translated entries. Default=Use the cache file to fill in previously translated entries and update it with new entries to speed up future translations.', action='store_false' )
    commandLineParser.add_argument( '-cf', '--cacheFile', help='The location of the cache file. Must be in a spreadsheet format like .xlsx. Default=' + str( defaultCacheFileLocation ), default=None, type=str )
    commandLineParser.add_argument( '-cam', '--cacheAnyMatch', help='Use all translation engines when considering the cache. Default=Only consider the current translation engine as valid for cache hits.', action='store_true' )
    commandLineParser.add_argument( '-owc', '--overrideWithCache', help='Override any already translated lines in the spreadsheet with results from the cache. Default=Do not override already translated lines. This setting is overwritten by reTranslate.', action='store_true' )
    commandLineParser.add_argument( '-rt', '--reTranslate', help='Translate all lines even if they already have translations or are in the cache. Update the cache with the new translations. Default=Do not translate cells that already have entries. Use the cache to fill in previously translated lines. This setting takes precedence over overrideWithCache.', action='store_true' )
    commandLineParser.add_argument( '-roc', '--readOnlyCache', help='Opens the cache file in read-only mode and disables updates to it or rebuilding it. This dramatically decreases the memory used by the cache file. Default=Read and write to the cache file. This setting takes precedence over rebuildCache.', action='store_true' )
    commandLineParser.add_argument( '-rbc', '--rebuildCache', help='This rebuilds the cache, removing blank lines and duplicates, based upon an existing spreadsheet if there is any error detected when generating it. Use this if the cache ever becomes corrupt. Rebuilding the cache lowers memory usage. The first column will be used as the untranslated data. Default=Error out if there is any error reading the cache file. The cache cannot be rebuilt if readOnlyCache is enabled.', action='store_true' )

    commandLineParser.add_argument( '-ch', '--contextHistory', help='Toggles context history setting. Specifying this will toggle keeping track of or submitting history of previously translated entries to the translation engine. Default=Keep track of previously translated entries and submit them to the translation engines that support history to improve the quality of future translations.', action='store_false' )
    commandLineParser.add_argument( '-chml', '--contextHistoryMaxLength', help='The number of previous translations that should be sent to the translation engine to provide context for the current translation. Sane values are 2-10. Set to 0 to disable contextHistory. Not all translation engines support context. Default=' + str( defaultContextHistoryMaxLength ), default=None, type=int )

    commandLineParser.add_argument( '-ssp', '--sceneSummaryPrompt', help='Experimental feature. The location of the sceneSummaryPrompt.txt file, a text file used to generate a summary of the untranslated text prior to translation. Only valid with specific translation engines. Specifying this text file will enable generating a scene summary prior to translation to potentially boost translation quality. Due to the highly experimental nature of this feature, translations are disabled by default when this feature is enabled in order to provide time to quality check the generated summary before attempting translation and to potentially one engines/APIs to generate the summary and another for the subsequent translation. After quality checking the generated summaries, use -sset --sceneSummaryEnableTranslation to enable translations when using this feature. Actually using the summary during translation requires the following string to be present in either the memory.txt or prompt.txt file: {sceneSummary} Default=Do not generate a summary prior to translation.', default=None, type=str )
    commandLineParser.add_argument( '-sspe', '--sceneSummaryPromptEncoding', help='Experimental feature. The encoding of the sceneSummaryPrompt.txt file. Default=' + defaultTextEncoding, default=None, type=str )
    commandLineParser.add_argument( '-ssl', '--sceneSummaryLength', help='Experimental feature. The number of entries that should be summarized at any one time. If batches are enabled, batches and this will be reduced to the same number depending on whichever is lower. Set to 0 to disable limits when generating a summary. Default=' + str( defaultSceneSummaryLength ), default=None, type=int )
    commandLineParser.add_argument( '-sset', '--sceneSummaryEnableTranslation', help='Enable the use of summaries of untranslated text when translating data. This setting always requires a sceneSummaryPrompt.txt file. sceneSummaryCache.xlsx will be used as cache. Default= Do not translate when generating a summary. The summary will be inserted in place of {sceneSummary} of memory.txt and prompt.txt', action='store_true' )
    commandLineParser.add_argument( '-sscf', '--sceneSummaryCacheFile', help='Experimental feature. The location of the sceneSummaryCache.xlsx file which stores a cache of every previously generated summary. Default=' + defaultSceneSummaryCacheLocation, default=None, type=str )

    commandLineParser.add_argument( '-b', '--batches', help='Toggles if entries should be submitted for translations engines that support them. Enabling batches disables context history. Default=Batches are automatically enabled for NMTs that support batches and web APIs like DeepL, but disabled for LLMs. Specifying this will disable them globally for all engines.', action='store_false' )
    commandLineParser.add_argument( '-bllm', '--batchesEnabledForLLMs', help='For translation engines that support both batches and single translations, should batches be enabled? Batches are automatically enabled for NMTs that support batches and DeepL regardless of this setting. Enabling batches for LLMs disables context history. Default=' + str( defaultEnableBatchesForLLMs ), action='store_true' )
    commandLineParser.add_argument( '-bsl', '--batchSizeLimit', help='Specify the maximum number of translations that should be sent to the translation engine if that translation engine supports batches. Not all translation engines support batches. Set to 0 to not place any limits on the size of batches. If the scene summary feature is enabled, this and sceneSummaryLength will be reduced to the same number depending on whichever is lower. Default=' + str( defaultBatchSizeLimit ), default=None, type=int )

    commandLineParser.add_argument( '-a', '--address', help='Specify the protocol and IP for NMT/LLM server, Example: http://192.168.0.100', default=None,type=str )
    commandLineParser.add_argument( '-port', '--port', help='Specify the port for the NMT/LLM server. Example: 5001', default=None, type=int )
    commandLineParser.add_argument( '-to', '--timeout', help='Specify the maximum number of seconds each individual request can take before quiting. Default=' + str( defaultTimeout ), default=None, type=int )

    commandLineParser.add_argument( '-bk', '--backups', help='This setting toggles writing backup files for mainSpreadsheet. This setting does not affect cache. Default=Write mainSpreadsheet to backups/[date]/* periodically for use with --resume. Specifying this will disable creating backups.', action='store_false' )
    commandLineParser.add_argument( '-r', '--resume', help='Attempt to resume previously interupted operation. No gurantees. Not currently implemented.', action='store_true' )
    commandLineParser.add_argument( '-tr', '--testRun', help='Specifying this will read all input files and import the translation engine, but there will be no translation or output files written. Default=Translate contents and write output.', action='store_true' )
    commandLineParser.add_argument( '-sf', '--settingsFile', help='The is the '+ defaultScriptSettingsFileExtension + ' file from which to read program settings. Default= The name of the program ' + defaultScriptSettingsFileExtension + ' Example: py3TranslateLLM.ini This file must be encoded as ' + defaultTextEncoding, default=None, type=str )

    commandLineParser.add_argument( '-ieh', '--inputErrorHandling', help='If the wrong input codec is specified, how should the resulting conversion errors be handled? See: docs.python.org/3.7/library/codecs.html#error-handlers Default=\'' + str( defaultInputTextEncodingErrorHandler ) + '\'.', default=None, type=str )
    commandLineParser.add_argument( '-oeh', '--outputErrorHandling', help='How should output conversion errors between incompatible encodings be handled? See: docs.python.org/3.7/library/codecs.html#error-handlers Default=\'' + str( defaultOutputTextEncodingErrorHandler ) + '\'.', default=None, type=str )

    commandLineParser.add_argument( '-ce', '--consoleEncoding', help='Specify encoding for standard output. Default=' + str( defaultConsoleEncoding ), default=None,type=str )

    commandLineParser.add_argument( '-vb', '--verbose', help='Print more information.', action='store_true' )
    commandLineParser.add_argument( '-d', '--debug', help='Print too much information.', action='store_true' )
    commandLineParser.add_argument( '-v', '--version', help='Print version information and exit.', action='store_true' )

    # Import options from command line options.
    commandLineArguments = commandLineParser.parse_args()
    #print( 'debugSettingFromCLI = '+ str( commandLineArguments.debug ) )

    if commandLineArguments.version == True:
        print( __version__ )
        sys.exit( 0 )

    userInput = {}
    userInput[ 'translationEngine' ] = commandLineArguments.translationEngine
    userInput[ 'fileToTranslate' ] = commandLineArguments.fileToTranslate
    userInput[ 'outputFile '] = commandLineArguments.outputFile
    userInput[ 'promptFile' ] = commandLineArguments.promptFile
    userInput[ 'memoryFile' ] = commandLineArguments.memoryFile

    userInput[ 'languageCodesFile' ] = commandLineArguments.languageCodesFile
    userInput[ 'sourceLanguage' ] = commandLineArguments.sourceLanguage
    userInput[ 'targetLanguage' ] = commandLineArguments.targetLanguage

    userInput[ 'characterNamesDictionary' ] = commandLineArguments.characterNamesDictionary
    userInput[ 'revertAfterTranslationDictionary' ] = commandLineArguments.revertAfterTranslationDictionary
    userInput[ 'preTranslationDictionary' ] = commandLineArguments.preTranslationDictionary
    userInput[ 'postTranslationDictionary' ] = commandLineArguments.postTranslationDictionary
    userInput[ 'postWritingToFileDictionary' ] = commandLineArguments.postWritingToFileDictionary

    userInput[ 'cache' ] = commandLineArguments.cache
    userInput[ 'cacheFile' ] = commandLineArguments.cacheFile
    userInput[ 'cacheAnyMatch' ] = commandLineArguments.cacheAnyMatch
    userInput[ 'overrideWithCache' ] = commandLineArguments.overrideWithCache
    userInput[ 'reTranslate' ] = commandLineArguments.reTranslate
    userInput[ 'readOnlyCache' ] = commandLineArguments.readOnlyCache
    userInput[ 'rebuildCache' ] = commandLineArguments.rebuildCache

    userInput[ 'contextHistory' ] = commandLineArguments.contextHistory
    userInput[ 'contextHistoryMaxLength' ] = commandLineArguments.contextHistoryMaxLength

    userInput[ 'sceneSummaryPrompt' ] = commandLineArguments.sceneSummaryPrompt
    userInput[ 'sceneSummaryLength' ] = commandLineArguments.sceneSummaryLength
    userInput[ 'sceneSummaryEnableTranslation' ] = commandLineArguments.sceneSummaryEnableTranslation
    userInput[ 'sceneSummaryCacheFile' ] = commandLineArguments.sceneSummaryCacheFile

    userInput[ 'batches' ] = commandLineArguments.batches
    userInput[ 'batchesEnabledForLLMs' ] = commandLineArguments.batchesEnabledForLLMs
    userInput[ 'batchSizeLimit' ] = commandLineArguments.batchSizeLimit

    userInput[ 'address' ] = commandLineArguments.address  #Must be reachable. How to test for that?
    userInput[ 'port' ] = commandLineArguments.port                #Port should be conditionaly guessed. If no port specified and an address was specified, then try to guess port as either 80, 443, or default settings depending upon protocol and translationEngine selected.
    userInput[ 'timeout' ] = commandLineArguments.timeout

    userInput[ 'backups' ] = commandLineArguments.backups
    userInput[ 'resume' ] = commandLineArguments.resume
    userInput[ 'testRun' ] = commandLineArguments.testRun
    userInput[ 'settingsFile' ] = commandLineArguments.settingsFile

    userInput[ 'inputErrorHandling' ] = commandLineArguments.inputErrorHandling
    userInput[ 'outputErrorHandling' ] = commandLineArguments.outputErrorHandling

    userInput[ 'consoleEncoding' ] = commandLineArguments.consoleEncoding
    userInput[ 'verbose' ] = commandLineArguments.verbose
    userInput[ 'debug' ] = commandLineArguments.debug
    userInput[ 'version' ] = commandLineArguments.version

    # Add stub encoding options. All of these are most certainly None, but they need to exist for locals() to find them so they can get updated.
    userInput[ 'fileToTranslateEncoding' ] = commandLineArguments.fileToTranslateEncoding
    userInput[ 'outputFileEncoding' ] = commandLineArguments.outputFileEncoding
    userInput[ 'promptFileEncoding' ] = commandLineArguments.promptFileEncoding
    userInput[ 'memoryFileEncoding' ] = commandLineArguments.memoryFileEncoding

    userInput[ 'languageCodesFileEncoding' ] = commandLineArguments.languageCodesFileEncoding

    userInput[ 'characterNamesDictionaryEncoding' ] = commandLineArguments.characterNamesDictionaryEncoding
    userInput[ 'revertAfterTranslationDictionaryEncoding' ] = commandLineArguments.revertAfterTranslationDictionaryEncoding
    userInput[ 'preTranslationDictionaryEncoding' ] = commandLineArguments.preTranslationDictionaryEncoding
    userInput[ 'postTranslationDictionaryEncoding' ] = commandLineArguments.postTranslationDictionaryEncoding
    userInput[ 'postWritingToFileDictionaryEncoding' ] = commandLineArguments.postWritingToFileDictionaryEncoding

    userInput[ 'sceneSummaryPromptEncoding' ] = commandLineArguments.sceneSummaryPromptEncoding

    # Basically, the final value of consoleEncoding is unclear because the settings.ini has not been read yet, but it needs to be used immediately, so remember to update it later.
    # if the user specified one at the CLI, use that setting, otherwise use the hardcoded defaults.
    if userInput[ 'consoleEncoding' ] != None:
        userInput[ 'tempConsoleEncoding' ] = userInput[ 'consoleEncoding' ]
    else:
        userInput[ 'tempConsoleEncoding' ] = defaultConsoleEncoding

    if userInput[ 'debug' ] == True:
        print( ( 'userInput (CLI)=' + str( userInput ) ).encode( userInput[ 'tempConsoleEncoding' ] ) )

    return userInput


# Settings specified at the command prompt take precedence, but py3translateLLM.ini still needs to be parsed.
# This function parses that file and places the settings discovered into a dictionary. That dictionary can then be used along with the command line options to determine the program settings prior to validation of those settings. The settings after validation are the final program settings.
def mergeUserInputSettings( userInput, scriptSettingsFile = __file__  ):
    if tempConsoleEncoding in userInput:
        consoleEncoding = userInput[ 'tempConsoleEncoding' ]
        userInput.pop( 'tempConsoleEncoding' )
    else:
        consoleEncoding = userInput[ 'consoleEncoding' ]

    # In order to read from settings.ini, the name of the current script must first be determined.
    #currentScriptFullFileNameAndPath=os.path.realpath( __file__ ) # Old code. This returns a string and the full path of the currently running script including the name and extension. 
    currentScriptPathObject = pathlib.Path( __file__ ).absolute()
    userInput[ 'currentScriptPathOnly' ] = str( currentScriptPathObject.parent ) # Does not include last / and this will return one subfolder up if it is called on a folder.
    userInput[ 'currentScriptNameWithoutPath' ] = currentScriptPathObject.name
    userInput[ 'currentScriptNameWithoutPathOrExt' ] = currentScriptPathObject.stem
    userInput[ 'currentScriptNameWithPathNoExt' ] = userInput[ 'currentScriptPathOnly' ] + '/' + userInput[ 'currentScriptNameWithoutPathOrExt' ]

    userInput[ 'backupsFolder' ] = userInput[ 'currentScriptPathOnly' ] + '/' + defaultBackupsFolder

    if scriptSettingsFile == __file__ :
        scriptSettingsFileFullNameAndPath = userInput[ 'currentScriptNameWithPathNoExt' ] + defaultScriptSettingsFileExtension
    else:
        scriptSettingsFileFullNameAndPath = str( pathlib.Path( scriptSettingsFile ).absolute() )
    scriptSettingsFileNameOnly = pathlib.Path( scriptSettingsFileFullNameAndPath ).name

    if ( userInput[ 'verbose' ] == True) or ( userInput[ 'debug' ] == True):
        print( str( currentScriptPathObject ).encode(consoleEncoding) )
        print( ( 'currentScriptPathOnly=' + str( userInput[ 'currentScriptPathOnly' ] ) ).encode(consoleEncoding) )
        print( ( 'currentScriptNameWithoutPath=' + str( userInput[ 'currentScriptNameWithoutPath' ] ) ).encode(consoleEncoding) )
        print( ( 'currentScriptNameWithoutPathOrExt=' + str( userInput[ 'currentScriptNameWithoutPathOrExt' ] ) ).encode(consoleEncoding) )

    if functions.checkIfThisFileExists( scriptSettingsFileFullNameAndPath ) != True:
        return userInput

    print( ( 'Settings file found. Reading settings from: ' + scriptSettingsFileNameOnly ).encode(consoleEncoding) )

    # This function reads program settings from text files using a predetermined list of rules using code at resources/functions.readSettingsFromTextFile()
    # The text file uses the syntax: setting=value, # are comments, empty/whitespace lines ignored.
    # This function builds a dictionary and then returns it to the caller.
    # Syntax: def readSettingsFromTextFile( fileNameWithPath, fileNameEncoding, consoleEncoding=defaultConsoleEncoding, errorHandlingType=defaultInputTextEncodingErrorHandler, debug=debug ):
    # Usage: functions.readSettingsFromTextFile( myfile, myfileEncoding )
    scriptSettingsDictionary = functions.readSettingsFromTextFile( scriptSettingsFileFullNameAndPath, defaultTextEncoding, consoleEncoding=consoleEncoding ) # Other settings can be specified, but are basically completely unknown at this point, so just use hardcoded defaults instead.

    # Since both userInput and scriptSettingsDictionary are dictionaries, just merge them directly if the CLI value is not None. Hummmmmm. # Update: This is not viable due to the existence of booleans.
    # One alternative to this is to remove all boolean types from the CLI and have them as 'None'. Then update them to be booleans later based upon a predefined list. Which is simpler?
    # Current algorithim:
    # Use scriptSettingsDictionary as the base for processing/finding values to merge and userInput (CLI) as the final output. If the value was not specified at the CLI, override the value in userInput (CLI) with all non-boolean settings in scriptSettingsDictionary.
    # For booleans, booleans need to be handled in a special way. Check each boolean individually in both dictionaries to determine the final value. Once the final value is determined, update/integrate the value in the userInput dictionary to become the final value.

    # Send the userInput dictionary to the translationEngine in case it is useful there. This potentially half-makes sense for API keys and engine specific variables so that the main program does not have to worry about them. Does that make sense, or should main program always worry about engine specific variables in order to validate them? Are there any examples of engine variables that main program should not validate besides API keys?
    # Answer: Any values related to pre or post processing text should not be validated. In addition, the API of certain translation engines should be able to be changed without main program needing any direct update. Updating the engine and perhaps adding an engine specific value in the .ini should be enough to update as it is. Since updating main program should not be necessary for translation engine API changes, especially minor changes, therefore no validation should be done at all for engine specific variables. This includes pykakasi/cutlet's romaji format. TODO: Remove such ill-advised validation attempts from the CLI and .ini. Update: Done.
    if not isinstance( scriptSettingsDictionary, dict ):
        print( ( 'Warning: Unable to read settings from \'' + str( scriptSettingsFileFullNameAndPath ) + '\'' ).encode( consoleEncoding ) )
        return userInput

    for key,value in scriptSettingsDictionary:
        # The types have already been converted. 'none' => None  Do not worry about it here.
        # Merge any unrecognized values literally.
        if not key in userInput:
            userInput[ key ] = value
        else:
            # There is something at the CLI that corresponds to a key extracted from scriptSettingsDictionary. Might be None or some type of value.
            # Deal with booleans first.
            # if the CLI's value of the key in scriptSettingsDictionary is a boolean, then treat the key from scriptSettingsDictionary as a boolean.
            if isinstance( userInput[ key ], bool ):
                # Sanity check. The value extracted from the scriptSettingsDictionary must also be a boolean.
                assert( isinstance( value, bool ) )
                # if the existing value is true by default,
                if key in booleanValuesTrueByDefault:
                    # and the key in scriptSettingsDictionary is also true, then do nothing.
                    if value == True:
                        pass
                    # else if the key in scriptSettingsDictionary is false, then update it.
                    # elif value == False:
                    else:
                        userInput[ key ] = value
                # elif the existing value is false by default:
                elif key in booleanValuesFalseByDefault:
                    # and the key in scriptSettingsDictionary is true, then update it.
                    if value == True:
                        userInput[ key ]  = value
                    # else if the key in scriptSettingsDictionary is false, then do nothing
                    # elif value == False:
                    else:
                        pass
                # else if the key is in not in either booleanValuesTrueByDefault or booleanValuesFalseByDefault, then something is wrong. The value needs to be added to one of those two lists.
                else:
                    print( ( 'Error: Unable to merge .ini and CLI settings because the key \''+ key + '\'could not be found in either booleanValuesTrueByDefault or booleanValuesFalseByDefault. Please update the appropriate list and try again.' ).encode( consoleEncoding ) )
                    sys.exit( 1 )
            # User specified something at the CLI that is not a boolean. Always use that instead. Valid types are str and int.
            elif userInput[ key ] != None:
                pass
            # User did not specify anything in the text file. Do nothing.
            # There are some values that must be specified or the program cannot function. For those values, validateUserInput() should be used instead to check each individual value and combinations of values and error out if a valid combination does not exist. This function is only responsible for merging the input, so do nothing here.
            elif key == None:
                pass
            else:
                # The userInput[ key ] value is None, and also the setting specified in the scriptSettingsDictionary is not None. In this case, update the value with whatever was specified at the .ini but not at the CLI.
                userInput[ key ] = value

    # if version was specified in the .ini, then print out version string and exit.
    if userInput[ 'version' ] == True:
        print( __version__ )
        sys.exit( 0 )

    return userInput


# This should set all of the defaults if values are still None and validate the input combination as required by the chosen translation engine.
def validateUserInput( userInput=None ):

    # Now that they have been merged, rename the variable names to be more descriptive.
    userInput[ 'fileToTranslateFileName' ] = userInput[ 'fileToTranslate' ]
    userInput[ 'outputFileName' ] = userInput[ 'outputFile' ]
    userInput[ 'promptFileName' ] = userInput[ 'promptFile' ]
    userInput[ 'memoryFileName' ] = userInput[ 'memoryFile' ]

    userInput[ 'languageCodesFileName' ] = userInput[ 'languageCodesFile' ]
    userInput[ 'sourceLanguageRaw' ] = userInput[ 'sourceLanguage' ]
    userInput[ 'targetLanguageRaw' ] = userInput[ 'targetLanguage' ]

    userInput[ 'characterNamesDictionaryFileName' ] = userInput[ 'characterNamesDictionary' ]
    userInput[ 'revertAfterTranslationDictionaryFileName' ] = userInput[ 'revertAfterTranslationDictionary' ]
    userInput[ 'preDictionaryFileName' ] = userInput[ 'preTranslationDictionary' ]
    userInput[ 'postDictionaryFileName' ] = userInput[ 'postTranslationDictionary' ]
    userInput[ 'postWritingToFileDictionaryFileName' ] = userInput[ 'postWritingToFileDictionary' ]

    userInput[ 'cacheEnabled' ] = userInput[ 'cache' ]
    userInput[ 'cacheFileName' ] = userInput[ 'cacheFile' ]

    userInput[ 'contextHistoryEnabled' ] = userInput[ 'contextHistory' ]

    userInput[ 'sceneSummaryPromptFileName' ] = userInput[ 'sceneSummaryPrompt' ]
    userInput[ 'sceneSummaryCacheFileName' ] = userInput[ 'sceneSummaryCacheFile' ]

    userInput[ 'batchesEnabled' ] = userInput[ 'batches' ]

    userInput[ 'backupsEnabled' ] = userInput[ 'backups' ]

    # Remove old value names.
    userInput.pop( 'fileToTranslate' )
    userInput.pop( 'outputFile' )
    userInput.pop( 'promptFile' )
    userInput.pop( 'memoryFile' )

    userInput.pop( 'languageCodesFile' )
    userInput.pop( 'sourceLanguage' )
    userInput.pop( 'targetLanguage' )

    userInput.pop( 'characterNamesDictionary' )
    userInput.pop( 'revertAfterTranslationDictionary' )
    userInput.pop( 'preTranslationDictionary' )
    userInput.pop( 'postTranslationDictionary' )
    userInput.pop( 'postWritingToFileDictionary' )

    userInput.pop( 'cache' )
    userInput.pop( 'cacheFile' )

    userInput.pop( 'contextHistory' )

    userInput.pop( 'sceneSummaryPrompt' )
    userInput.pop( 'sceneSummaryCacheFile' )

    userInput.pop( 'batches' )

    userInput.pop( 'backups' )


    # Some values need to be set to hardcoded defaults if they were not specified at the command prompt or in settings.ini, so fill in any missing None entries here.
    if userInput[ 'translationEngine' ] == None:
        print( 'Error: Please specify a translation engine. ' + usageHelp )
        sys.exit( 1 )

    if userInput[ 'fileToTranslateFileName' ] == None:
        print( 'Error: Please specify a --fileToTranslate (-f).' )
        sys.exit( 1 )

    # This cannot be set here because fileToTranslateFileExtensionOnly has not been determined yet which means this is a derived value.
    #if userInput[ 'outputFileName' ] == None:
        # if no outputFileName was specified, then set it the same as the input file with 'translation' and the date appended.
        #userInput[ 'outputFileName' ] = userInput[ 'fileToTranslateFileName' ] + '.translated.' + functions.getDateAndTimeFull() + userInput[ 'fileToTranslateFileExtensionOnly' ]

    if userInput[ 'languageCodesFileName' ] == None:
        userInput[ 'languageCodesFileName' ] = userInput[ 'currentScriptPathOnly' ] + '/' + defaultLanguageCodesFile

    if userInput[ 'sourceLanguageRaw' ] == None:
        userInput[ 'sourceLanguageRaw' ] = defaultSourceLanguage
    if userInput[ 'targetLanguageRaw' ] == None:
        userInput[ 'targetLanguageRaw' ] = defaultTargetLanguage

    if userInput[ 'cacheFileName' ] == None:
        userInput[ 'cacheFileName' ] = userInput[ 'currentScriptPathOnly' ] + '/' + defaultCacheFileLocation

    if userInput[ 'contextHistoryMaxLength' ] == None:
        userInput[ 'contextHistoryMaxLength' ] = defaultContextHistoryMaxLength

    if userInput[ 'sceneSummaryLength' ] == None:
        userInput[ 'sceneSummaryLength' ] = defaultSceneSummaryLength
    if userInput[ 'sceneSummaryCacheFileName' ] == None:
        userInput[ 'sceneSummaryCacheFileName' ] = userInput[ 'currentScriptPathOnly' ] + '/' + defaultSceneSummaryCacheLocation

    if userInput[ 'batchSizeLimit' ] == None:
        userInput[ 'batchSizeLimit' ] = defaultBatchSizeLimit

    # if using py3translationserver or sugoi, address must be specified, but default to using http://localhost. Warn user later.
    addressIsDefault = False
    if userInput[ 'address' ] == None:
        userInput[ 'address' ] = defaultAddress
        addressIsDefault = True
    # if port not specified, then set port to default port based upon translation engine. Warn user later.
    portIsDefault = False
    if userInput[ 'port' ] == None:
        if userInput[ 'translationEngine' ].lower() == 'koboldcpp':
            userInput[ 'port' ] = defaultKoboldCppPort
            portIsDefault = True
        elif userInput[ 'translationEngine' ].lower() == 'py3translationserver':
            userInput[ 'port' ] = defaultPy3translationServerPort
            portIsDefault = True
        elif userInput[ 'translationEngine' ].lower() == 'sugoi':
            userInput[ 'port' ] = defaultSugoiPort
            portIsDefault = True
    if userInput[ 'timeout' ] == None:
        userInput[ 'timeout' ] = defaultTimeout

    # Old code. Probably useful for later for use with different translation engines.
    #if port == None:
        # Try to guess port from protocol and warn user.
        # split address using : and return everything before:
    #    protocol = address.split(':')[0]
    #    if protocol.lower() == 'http':
    #        port = defaultPortForHTTP
    #    elif protocol.lower() == 'https':
    #        port = defaultPortForHTTPS
    #    else:
    #        print( ( 'Port not specified and unable to guess port from protocol \'' + protocol + '\' of address \'' + address + '\' Please specify a valid port number between 1-65535.').encode(consoleEncoding) )
    #    sys.exit( 1 )
    #    print( ('Warning: No port was specified. Defaulting to port \''+port+'\' based on protocol \''+protocol+'\'. This is probably incorrect.') )

    if userInput[ 'inputErrorHandling' ] == None:
        userInput[ 'inputErrorHandling' ] = defaultInputTextEncodingErrorHandler
    if userInput[ 'outputErrorHandling' ] == None:
        userInput[ 'outputErrorHandling' ] = defaultOutputTextEncodingErrorHandler

    # if consoleEncoding is still None after reading both the CLI and the settings.ini, then just set it to the default value.
    if userInput[ 'consoleEncoding' ] == None:
        userInput[ 'consoleEncoding' ] = defaultConsoleEncoding
        consoleEncoding = defaultConsoleEncoding
    else:
        consoleEncoding = userInput[ 'consoleEncoding' ]

    if userInput[ 'debug' ] == True:
        userInput[ 'verbose' ] = True
        print( ( 'translationEngine=' + str( userInput[ 'translationEngine' ] ) ).encode( consoleEncoding ) )
        #print( ( 'fileToTranslateEncoding=' + str( userInput[ 'fileToTranslateEncoding' ] ) ).encode( consoleEncoding ) )


    # Add derived values like file paths and inferred values.
    # Determine file paths now. Will be useful later.
    # pathlib.Path() does not mind mixing / and \ so always use /.
    fileToTranslatePathObject = pathlib.Path( userInput[ 'fileToTranslateFileName' ] ).absolute()
    #fileToTranslateFileNameWithPathNoExt, fileToTranslateFileExtensionOnly = os.path.splitext( fileToTranslateFileName ) # Old code.
    userInput[ 'fileToTranslateFileExtensionOnly' ] = fileToTranslatePathObject.suffix   # .txt  .ks  .ts .csv .xlsx .xls .ods
    userInput[ 'fileToTranslatePathOnly' ] = str( fileToTranslatePathObject.parent )  # pathlib.Path().parent returns not-a-string. Does not include final / at the end and will return one subfolder up if it is called on a folder.
    userInput[ 'fileToTranslateFileNameWithoutPath' ] = fileToTranslatePathObject.name # pathlib.Path().name returns a string.
    userInput[ 'fileToTranslateFileNameWithoutPathOrExt' ] = fileToTranslatePathObject.stem # pathlib.Path().stem returns a string.
    userInput[ 'fileToTranslateFileNameWithPathNoExt' ] = userInput[ 'fileToTranslatePathOnly' ] + '/' + userInput[ 'fileToTranslateFileNameWithoutPathOrExt' ]

    if userInput[ 'verbose' ] == True:
        print( str( fileToTranslatePathObject ).encode(consoleEncoding) )
        print( ( 'fileToTranslateFileExtensionOnly=' + userInput[ 'fileToTranslateFileExtensionOnly' ] ).encode(consoleEncoding) )
        print( ( 'fileToTranslatePathOnly=' + userInput[ 'fileToTranslatePathOnly' ] ).encode(consoleEncoding) )
        print( ( 'fileToTranslateFileNameWithoutPath=' + userInput[ 'fileToTranslateFileNameWithoutPath' ] ).encode(consoleEncoding) )
        print( ( 'fileToTranslateFileNameWithoutPathOrExt=' + userInput[ 'fileToTranslateFileNameWithoutPathOrExt' ] ).encode(consoleEncoding) )
        print( ( 'fileToTranslateFileNameWithPathNoExt=' + userInput[ 'fileToTranslateFileNameWithPathNoExt' ] ).encode(consoleEncoding) )

    if userInput[ 'fileToTranslateFileExtensionOnly' ] in validSpreadsheetExtensions:
        userInput[ 'fileToTranslateIsASpreadsheet' ] = True
    else:
        userInput[ 'fileToTranslateIsASpreadsheet' ] = False

    # fileToTranslateFileExtensionOnly was only just determined which means outputFileName which uses it is a derived value.
    if userInput[ 'outputFileName' ] == None:
        # If no outputFileName was specified, then set it the same as the input file with 'translation' and the date appended.
        userInput[ 'outputFileName' ] = userInput[ 'fileToTranslateFileName' ] + '.translated.' + functions.getDateAndTimeFull() + userInput[ 'fileToTranslateFileExtensionOnly' ]

    userInput[ 'outputFileNameWithoutPathOrExt' ] = pathlib.Path( userInput[ 'outputFileName' ] ).stem
    userInput[ 'outputFileExtensionOnly' ] = pathlib.Path( userInput[ 'outputFileName' ] ).suffix

    #userInput[ 'promptFileContents' ] = None
    #userInput[ 'memoryFileContents' ] = None

    cacheFileNameObject = pathlib.Path( str(userInput[ 'cacheFileName' ] ) ).absolute()
    userInput[ 'cacheFilePathOnly' ] = str( cacheFileNameObject.parent )
    userInput[ 'cacheFileExtensionOnly' ] = cacheFileNameObject.suffix

    if userInput[ 'sceneSummaryPromptFileName' ] == None:
        userInput[ 'sceneSummaryEnabled' ] = False
    else:
        userInput[ 'sceneSummaryEnabled' ] = True
    sceneSummaryCachePathObject = pathlib.Path( str( userInput[ 'sceneSummaryCacheFileName' ] ) )
    userInput[ 'sceneSummaryCacheFilePathOnly' ] = str( sceneSummaryCachePathObject.parent )
    userInput[ 'sceneSummaryCacheExtensionOnly' ] = sceneSummaryCachePathObject.suffix

    #userInput[ 'sceneSummaryPromptFileContents' ] = None


    # Now that command line options and .ini have been parsed, and None values filled in, update the settings for the imported libraries.
    # The libraries must be imported using the syntax: import resources.libraryName as libraryName . Otherwise, if using the 'from libraryName import...' syntax, a copy is made which makes it, near?, impossible to update these variables correctly.
    chocolate.verbose = userInput[ 'verbose' ]
    chocolate.debug = userInput[ 'debug' ]
    chocolate.consoleEncoding = userInput[ 'consoleEncoding' ]
    chocolate.inputErrorHandling = userInput[ 'inputErrorHandling' ]
    chocolate.outputErrorHandling = userInput[ 'outputErrorHandling' ]

    functions.verbose = userInput[ 'verbose' ]
    functions.debug = userInput[ 'debug' ]
    functions.consoleEncoding = userInput[ 'consoleEncoding' ]
    functions.inputErrorHandling = userInput[ 'inputErrorHandling' ]
    functions.outputErrorHandling = userInput[ 'outputErrorHandling' ]
    functions.linesThatBeginWithThisAreComments = defaultLinesThatBeginWithThisAreComments
    functions.assignmentOperatorInSettingsFile = defaultAssignmentOperatorInSettingsFile

    dealWithEncoding.verbose = userInput[ 'verbose' ]
    dealWithEncoding.debug = userInput[ 'debug' ]
    dealWithEncoding.consoleEncoding = userInput[ 'consoleEncoding' ]


    # Start to validate input settings and input combinations from parsed imported command line option values.
    # Certain files must be present, like fileToTranslateFileName and usually languageCodesFileName.
    # Reading from text files is easy since the only thing that needs to be checked is if they exist.
    # Update: py3TranslateLLM only accepts spreadsheet inputs in order to divide the logic between parsing files and translating spreadsheets. There is only very basic line-by-line logic for i/o related to text files included in chocolate.Strawberry(). Use py3AnyText2Spreadsheet to create spreadsheets from raw text files for more complicated cases (.epub, subtitles, .ks, .scn.txt).
    # if output is .txt, .ks... if input is not a spreadsheet, then output is writing to text file, so set output encoding and extension based upon input.
    # if the user specified a spreadsheet as input and a text file as output, then export whatever the column of mainSpreadsheet to whatever the current translation engine is.

    # Start checking if files exist or not, combinations of settings, and mode specific settings.
    # Syntax:
    #def verifyThisFileExists( myFile, nameOfFileToOutputInCaseOfError=None ):
    #def checkIfThisFolderExists( myFolder ):
    # Usage:
    # Errors out if myFile does not exist.
    #functions.verifyThisFileExists( 'myfile.csv', 'myfile.csv' )
    #functions.verifyThisFolderExists( myVar, 'myVar' )
    #functions.verifyThisFolderExists( myVar )

    # Returns True or False depending upon if a file or folder was specified.
    #functions.checkIfThisFileExists( 'myfile.csv' )
    #functions.checkIfThisFolderExists( myVar )

    # Verify translationEngine
    # The syntax below all of the libraries are under resources/translationEngines/*. To import the libraries directly regardless of where they are on the file system:
    # import sys
    # import pathlib
    # sys.path.append( str( pathlib.Path('C:/resources/translationEngines/koboldCppEngine.py').resolve().parent ) )
    # import koboldCppEngine

    userInput[ 'mode' ] = None
    userInput[ 'translationEngineIsAnLLM' ] = False
    implemented = False
    #validate input from command line options
    # This section should probably be updated with more helpful error messages like what to do if the engines did not import correctly. pip install pykakasi ...etc
    if ( userInput[ 'translationEngine' ].lower() == 'parseonly' ): # Is this mode still valid? # Update: This should be renamed to enable a test run mode.
        userInput[ 'mode' ] = 'parseOnly'
        implemented=True
    elif ( userInput[ 'translationEngine' ].lower() == 'koboldcpp' ):
        userInput[ 'mode' ] = 'koboldcpp'
        import resources.translationEngines.koboldCppEngine as koboldCppEngine
        userInput[ 'translationEngineIsAnLLM' ] = True
        implemented=True
    elif ( userInput[ 'translationEngine' ].lower() == 'deepl_api_free' ) or ( userInput[ 'translationEngine' ].lower() == 'deepl-api-free' ):
        userInput[ 'mode' ] = 'deepl_api_free'
        import resources.translationEngines.deepLApiFreeEngine as deepLApiFreeEngine
        #import deepl
    elif ( userInput[ 'translationEngine' ].lower() == 'deepl_api_pro' ) or ( userInput[ 'translationEngine' ].lower() == 'deepl-api-pro' ):
        userInput[ 'mode' ] = 'deepl_api_pro'
        import resources.translationEngines.deepLApiProEngine as deepLApiProEngine
    elif ( userInput[ 'translationEngine' ].lower() == 'deepl_web' ) or ( userInput[ 'translationEngine' ].lower() == 'deepl-web' ):
        userInput[ 'mode' ] = 'deepl_web'
        import resources.translationEngines.deepLWebEngine as deepLWebEngine
    elif ( userInput[ 'translationEngine' ].lower() == 'py3translationserver' ):
        userInput[ 'mode' ] = 'py3translationserver'
        import resources.translationEngines.py3translationServerEngine as py3translationServerEngine
        implemented = True
    elif ( userInput[ 'translationEngine' ].lower() == 'sugoi' ):
        userInput[ 'mode'] = 'sugoi'
        # Sugoi has a default port association and only supports Jpn->Eng translations, so having a dedicated entry for it is still useful for input validation, especially since it only supports a subset of the py3translationserver API.
        import resources.translationEngines.sugoiEngine as sugoiEngine
        implemented = True
    elif ( userInput[ 'translationEngine' ].lower() == 'pykakasi' ):
        userInput[ 'mode' ] = 'pykakasi'
        import resources.translationEngines.pykakasiEngine as pykakasiEngine
        implemented = True
        if userInput[ 'cacheEnabled' ] == True:
            print( 'Info: Disabling cache for local pykakasi library.')
            userInput[ 'cacheEnabled' ] = False # Since pykakasi is a local library with a fast dictionary, enabling cache would only make things slower.
    elif ( userInput[ 'translationEngine' ].lower() == 'cutlet' ):
        userInput[ 'mode' ] = 'cutlet'
        import resources.translationEngines.cutletEngine as cutletEngine
        implemented=False
        #cacheEnabled=False # Is enabling cache worth it for cutlet?
    else:
        print( ( 'Error. Invalid translation engine specified: \'' + userInput[ 'translationEngine' ] + '\'' + usageHelp ).encode(consoleEncoding))
        sys.exit( 1 )

    print( ( 'Mode is set to: \'' + str( userInput[ 'mode'] ) + '\'' ).encode(consoleEncoding) )
    if implemented == False:
        print( '\n\'' + mode + '\' not yet implemented. Please pick another translation engine. \n Translation engines: ' + str(translationEnginesAvailable) )
        sys.exit( 1 )

    functions.verifyThisFileExists( userInput[ 'fileToTranslateFileName' ] ) #, 'fileToTranslate'

    if userInput[ 'fileToTranslateIsASpreadsheet' ] == False:
        # if the extension is not .txt or .text, then warn the user about it.
        if not ( ( userInput[ 'fileToTranslateFileExtensionOnly' ] == '.txt' ) or ( userInput[ 'fileToTranslateFileExtensionOnly' ] == '.text' ) ):
            print( ( 'Warning: Unrecognized extension for spreadsheet: ' + str( userInput[ 'fileToTranslateFileExtensionOnly' ] + ' File will be parsed line-by-line as a text file. Consider using a dedicated parser if this is incorrect.' ) ).encode(consoleEncoding) )

    # outputFileName does not need to exist.

    # promptFileName only needs to exist if using an LLM. If using an LLM, make sure it exists. Technically, it is not needed if the summary feature is enabled and also if translations are disabled, but since it will be needed soon after, just require it anyway. In addition, if the user specified it, even if it is not needed, then verify it exists.
    #if userInput[ 'mode' ] == 'koboldcpp':
    if ( userInput[ 'translationEngineIsAnLLM' ] == True ) or ( userInput[ 'promptFileName' ] != None ):
        functions.verifyThisFileExists( userInput[ 'promptFileName' ] )

    # memoryFileName never has to exist, but if it is specified, then make sure it exists.
    if userInput[ 'memoryFileName' ] != None:
        functions.verifyThisFileExists( userInput[ 'memoryFileName' ] )

    functions.verifyThisFileExists( userInput[ 'languageCodesFileName' ] )
    if not pathlib.Path( userInput[ 'languageCodesFileName' ] ).suffix in validSpreadsheetExtensions:
        print( ('\n Error: languageCodesFile must have a spreadsheet extension instead of \''+ pathlib.Path( userInput[ 'languageCodesFileName' ] ).suffix +'\'').encode(consoleEncoding) )
        print( 'validSpreadsheetExtensions=' + str(validSpreadsheetExtensions) )
        print( ( 'cacheFile: \'' + str( userInput[ 'languageCodesFileName' ] ) ).encode(consoleEncoding) )
        sys.exit(1)

    # The target language is required to be present, but source language can be optional for NMTs, LLMs, and DeepL.
    # The problem with not specifying the source language, even if the translationEngine itself does not need it, is that the source language is still used for selecting the correct sheet in the cache.xlsx workbook. So only cache == disabled would be valid. The same is true for the summary feature. Therefore, always require it and add an "Unknown" option to the languageCodes.csv for user to use if they are unsure.
    if userInput[ 'sourceLanguageRaw' ] == None:
        print( 'Error: A source language must be specified.' )
        sys.exit(1)
    if userInput[ 'targetLanguageRaw' ] == None:
        print( 'Error: A target language must be specified.' )
        sys.exit(1)

    # TODO: Some of this should be moved to the deepLTranslationEngine, but that engine needs to be implemented first.
    if userInput[ 'sourceLanguageRaw' ] != None:
        # Substitute a few language entries to certain defaults due to collisions and aliases.
        if userInput[ 'sourceLanguageRaw' ].lower() == 'english':
            userInput[ 'sourceLanguageRaw' ] = 'English (American)'
        elif userInput[ 'sourceLanguageRaw' ].lower() == 'castilian':
            userInput[ 'sourceLanguageRaw' ] = 'Spanish'
        elif userInput[ 'sourceLanguageRaw' ].lower() == 'chinese':
            userInput[ 'sourceLanguageRaw' ] = 'Chinese (simplified)'
        elif userInput[ 'sourceLanguageRaw' ].lower() == 'portuguese':
            userInput[ 'sourceLanguageRaw' ] = 'Portuguese (European)'
    if userInput[ 'targetLanguageRaw' ] != None:
        # Substitute a few language entries to certain defaults due to collisions and aliases.
        if userInput[ 'targetLanguageRaw' ].lower() == 'english':
            userInput[ 'targetLanguageRaw' ] = 'English (American)'
        elif userInput[ 'targetLanguageRaw' ].lower() == 'castilian':
            userInput[ 'targetLanguageRaw' ] ='Spanish'

    # if any dictionaries were specified, then make sure they exist.
    if userInput[ 'characterNamesDictionaryFileName' ] != None:
        functions.verifyThisFileExists( userInput[ 'characterNamesDictionaryFileName' ] )
    if userInput[ 'revertAfterTranslationDictionaryFileName' ] != None:
        functions.verifyThisFileExists( userInput[ 'revertAfterTranslationDictionaryFileName' ] )
    if userInput[ 'preDictionaryFileName' ] != None:
        functions.verifyThisFileExists( userInput[ 'preDictionaryFileName' ] )
    if userInput[ 'postDictionaryFileName' ] != None:
        functions.verifyThisFileExists( userInput[ 'postDictionaryFileName' ] )
    if userInput[ 'postWritingToFileDictionaryFileName' ] != None:
        functions.verifyThisFileExists( userInput[ 'postWritingToFileDictionaryFileName' ] )

    # The cache file does not need to exist. if it does not exist, then it will be created dynamically when it is needed as a chocolate.Strawberry(), so only verify the extension.
    if userInput[ 'cacheEnabled' ] == True:
        # Verify cache file extension is .xlsx. Shouldn't .csv also work? .csv would be harder for user to edit but might take less space on disk. Need to check. # Update: It was backwards. .csv files take more space on disk but can be potentially the most compatible. They might compress the best via lzma2 with python's zip library. In practice, .ods should be the most compatible in exchange for larger file size compared to .xlsx, but .ods support is not yet implemented in chocolate library.
        if not userInput[ 'cacheFileExtensionOnly' ] in validSpreadsheetExtensions:
            print( ('\n Error: cacheFile must have a spreadsheet extension instead of \''+ userInput[ 'cacheFileExtensionOnly' ] +'\'').encode(consoleEncoding) )
            print( 'validSpreadsheetExtensions=' + str(validSpreadsheetExtensions) )
            print( ( 'cacheFile: \'' + str( userInput[ 'cacheFileName' ] ) ).encode(consoleEncoding) )
            sys.exit(1)

        # overrideWithCache means to ignore the current translation and fill it in with entries from the cache. reTranslate means to ignore the current translation and fill it in with fresh entries from the translation engine. These settings directly conflict. When then conflict, reTranslate should take precedence.
        if ( userInput[ 'overrideWithCache' ] == True ) and ( userInput[ 'reTranslate' ] == True ):
            userInput[ 'overrideWithCache' ] = False

        # readOnlyCache means to not write/alter the current cache.xlsx. rebuildCache means to alter the current cache.xlsx. When these settings conflict, disable rebuildCache.
        if ( userInput[ 'readOnlyCache' ] == True ) and ( userInput[ 'rebuildCache' ] == True ):
            userInput[ 'rebuildCache' ] = False

    #if contextHistoryMaxLength was specified as == 0, then disable it.
    if userInput[ 'contextHistoryMaxLength' ] == 0:
        userInput[ 'contextHistoryEnabled'] = False

    if userInput[ 'sceneSummaryPromptFileName' ] != None:
        functions.verifyThisFileExists( userInput[ 'sceneSummaryPromptFileName' ] )

    if userInput[ 'sceneSummaryEnabled' ] == True:
        # if a cache file was specified, then verify the extension is .xlsx # Update: Shouldn't .csv also work? CSV would be harder for user to edit but might take less space on disk. Need to check.

        if not userInput[ 'sceneSummaryCacheExtensionOnly' ] in validSpreadsheetExtensions:
            print( ( '\n Error: cacheFile must have a spreadsheet extension instead of \'' + userInput[ 'sceneSummaryCacheExtensionOnly' ] + '\'' ).encode(consoleEncoding) )
            print( ( 'sceneSummaryCacheFile: \'' + str( userInput[ 'sceneSummaryCacheFileName' ] ) ).encode(consoleEncoding) )
            sys.exit(1)

    if ( userInput[ 'sceneSummaryEnabled' ] == True ) and ( userInput[ 'batchesEnabled' ] == True ):
        if ( userInput[ 'sceneSummaryLength' ] == 0 ) or ( userInput[ 'sceneSummaryLength' ] > userInput[ 'batchSizeLimit' ] ):
            userInput[ 'sceneSummaryLength' ] = userInput[ 'batchSizeLimit' ]
        elif ( userInput[ 'batchSizeLimit' ] == 0 ) or ( userInput[ 'batchSizeLimit' ] > userInput[ 'sceneSummaryLength' ] ):
            userInput[ 'batchSizeLimit' ] = userInput[ 'sceneSummaryLength' ]
        assert( userInput[ 'batchSizeLimit' ] == userInput[ 'sceneSummaryLength' ] )

    if userInput[ 'verbose' ] == True:
        print( 'sceneSummaryLength=' + str( userInput[ 'sceneSummaryLength' ] ) )
        print( 'batchSizeLimit=' + str( userInput[ 'batchSizeLimit' ] ) )

    if userInput[ 'batchesEnabled' ] == False:
        userInput[ 'batchesEnabledForLLMs' ] = False


    # if using parseOnly...
    if userInput[ 'mode' ] == 'parseOnly':
        pass


    # if using cacheOnly...
    if userInput[ 'mode' ] == 'cacheOnly':
        pass


    # Check for local LLMs/NMTs. Warn if defaulting to default address or default port. Validate specific port assignment.
    if ( userInput[ 'mode' ] == 'koboldcpp' ) or ( userInput[ 'mode' ] == 'py3translationserver' ) or ( userInput[ 'mode' ] == 'sugoi' ):
        if addressIsDefault == True:
            print( ( 'Warning: No address was specified for: '+ userInput[ 'mode' ] +'. Defaulting to: '+ defaultAddress +' This is probably incorrect.' ).encode(consoleEncoding) )
        if portIsDefault == True:
                print( 'Warning: No port specified for ' + userInput[ 'mode' ] + ' translation engine. Using default port of: ' + str( userInput[ 'port' ] ) )
        try:
            assert userInput[ 'port' ] >= minimumPortNumber #1
            assert userInput[ 'port' ] <= maximumPortNumber #65535
        except:
            print( ( 'Error: Unable to verify port number: \'' + str( userInput[ 'port' ] ) + '\' Must be '+ str(minimumPortNumber) + '-' + str(maximumPortNumber) + '.').encode(consoleEncoding) )
            sys.exit(1)


    # if using deepl_api_free, pro
    #if ( userInput[ 'mode' ] == 'deepl_api_free' ) or ( userInput[ 'mode' ] == 'deepl_api_pro' ):
        # API key must exist.
        # Maybe check both environmental variable and also a file?
        # The deepL library also requires it, so how does it need to be specified? Does it check any environmental variable for it?
        # Let the deepLEngine library worry about it. It should fail to switch to ready state without a valid API key.
        # Syntax: os.environ[ 'CT2_VERBOSE' ] = '1'


    # if using deepl_web... TODO validate anything it needs
        #probably the external chrome.exe right? Maybe requests library and scraping library.
        #Might need G-Chrome, + chromedriver.exe, and also a library wrapper, like Selenium.
        #Could require Chromium to be downloaded to resources/chromium/[platform]/chrome[.exe]


    #if userInput[ 'mode' ] == 'pykakasi':
        #pass


    #if userInput[ 'mode' ] == 'cutlet':
        #pass


    # Set encodings last using dealWithEncoding.py helper library.
    # API: def ofThisFile( myFileName, userInputForEncoding=None, fallbackEncoding=defaultTextFileEncoding ):
    # Usage: newEncoding = dealWithEncoding.ofThisFile(myFileName, rawCommandLineOption, fallbackEncoding)
    #.csv's work normally since those are both plaintext and spreadsheets but reading encoding from .xlsx, .xls, and .ods is not possible without either hardcoding a specific encoding or using the designated libraries. dealWithEncoding should deal with it. If asked what the encoding of a binary spreadsheet format, then it should just return what the user specified at the command prompt or the default/fallbackEncoding.

    # For the output file encoding, if the user specified an input file encoding, use the input file's encoding for the output file.
    if ( userInput[ 'fileToTranslateEncoding' ] != None ) and ( userInput[ 'outputFileEncoding' ] == None ):
        userInput[ 'outputFileEncoding' ] = userInput[ 'fileToTranslateEncoding' ]

    userInput[ 'fileToTranslateEncoding' ] = dealWithEncoding.ofThisFile( userInput[ 'fileToTranslateFileName' ], userInput[ 'fileToTranslateEncoding' ], defaultTextEncoding )
    # For the outputfile, use the input file encoding as a fallback.
    userInput[ 'outputFileEncoding' ] = dealWithEncoding.ofThisFile( userInput[ 'outputFileName' ], userInput[ 'outputFileEncoding' ], userInput[ 'fileToTranslateEncoding' ] )

    userInput[ 'promptFileEncoding' ] = dealWithEncoding.ofThisFile( userInput[ 'promptFileName' ], userInput[ 'promptFileEncoding' ], defaultTextEncoding)
    userInput[ 'memoryFileEncoding' ] = dealWithEncoding.ofThisFile( userInput[ 'memoryFileName' ], userInput[ 'memoryFileEncoding' ], defaultTextEncoding)

    userInput[ 'languageCodesFileEncoding' ] = dealWithEncoding.ofThisFile( userInput[ 'languageCodesFileName' ], userInput[ 'languageCodesFileEncoding' ], defaultTextEncoding)

    userInput[ 'characterNamesDictionaryEncoding' ] = dealWithEncoding.ofThisFile( userInput[ 'characterNamesDictionaryFileName' ], userInput[ 'characterNamesDictionaryEncoding' ], defaultTextEncoding )
    userInput[ 'revertAfterTranslationDictionaryEncoding' ] = dealWithEncoding.ofThisFile( userInput[ 'revertAfterTranslationDictionaryFileName' ], userInput[ 'revertAfterTranslationDictionaryEncoding' ], defaultTextEncoding )
    userInput[ 'preDictionaryEncoding' ] = dealWithEncoding.ofThisFile( userInput[ 'preDictionaryFileName' ], userInput[ 'preTranslationDictionaryEncoding' ], defaultTextEncoding )
    userInput[ 'postDictionaryEncoding' ] = dealWithEncoding.ofThisFile( userInput[ 'postDictionaryFileName' ], userInput[ 'postTranslationDictionaryEncoding' ], defaultTextEncoding )
    userInput[ 'postWritingToFileDictionaryEncoding' ] = dealWithEncoding.ofThisFile( userInput[ 'postWritingToFileDictionaryFileName' ], userInput[ 'postWritingToFileDictionaryEncoding' ], defaultTextEncoding )

    userInput[ 'sceneSummaryPromptEncoding' ] = dealWithEncoding.ofThisFile( userInput[ 'sceneSummaryPromptFileName' ], userInput[ 'sceneSummaryPromptEncoding' ], defaultTextEncoding )

    return userInput


def readInputFiles( userInput=None ):
    # consoleEncoding should be a global variable by this point in the code.
    global consoleEncoding

    if ( userInput[ 'verbose' ] == True ) or ( userInput[ 'debug' ] == True ):
        print( ( 'verbose=' + str( userInput[ 'verbose' ] ) ).encode(consoleEncoding) )
        print( ( 'debug=' + str( userInput[ 'debug'] ) ).encode(consoleEncoding) )
        print( ( 'sourceLanguageRaw=' + str( userInput[ 'sourceLanguageRaw' ] ) ).encode(consoleEncoding) )
        print( ( 'targetLanguageRaw=' + str( userInput[ 'targetLanguageRaw' ] ) ).encode(consoleEncoding) )

    # Instantiate basket of Strawberries. Start with languageCodes.csv  # languageCodes.csv, cache.xlsx, sceneSummaryCache.xlsx, and mainSpreadsheet are chocolate.Strawberry() instances. For the various dictionary.csv files, use Python dictionaries instead. The prompt files are regular files (strings).
    # languageCodes.csv could also be a dictionary with key=[ list ] or multidimensional array [[][][]], but then searching through that would be annoying, so leave as a chocolate.Strawberry().
    # Read in and process languageCodes.csv
    # Format specificiation for languageCodes.csv
    # Name of language in English, ISO 639 Code, ISO 639-2 Code
    # https://www.loc.gov/standards/iso639-2/php/code_list.php
    # Language list (Mostly) only languages supported by DeepL are currently listed, case insensitive.
    # Syntax:
    # The first row is entirely headers (column labels). Entries start from the 2nd row (row[1] if python list, row[2] if spreadsheet data structure):
    # Spec:
    # column 0) [ languageNameReadable, 
    # column 1) TwoLetterLanguageCodeThatIsNotAlwaysTwoLetters,
    # column 2) ThreeLetterLanguageCodeThatIsNotAlwaysThreeLetters,
    # column 3) DoesDeepLSupportThisLanguageTrueOrFalse,
    # column 4) DoesThisLanguageNeedACustomSourceLanguageTrueOrFalse (for single source language but many target language languages like EN->EN-US/EN-GB)
    # column 5) If #4 is True, then the full name source language
    # column 6) If #4 is True, then the two letter code of the source language
    # column 7) If #4 is True, then the three letter code of the source language
    # Examples for 5-7: English, EN, ENG; Portuguese, PT-PT, POR
    # Each row/entry is/has eight columns total.

    # Skip reading languageCodesFileName if mode is parseOnly. # Update: parseOnly mode is not really supported anymore. It should probably be renamed to dryRun mode or --testRun where the purpose is to check for parsing errors in everything, including the languageCodes.csv and cache.xlsx files.
    #if userInput[ 'mode' ] != 'parseOnly':
    if userInput[ 'verbose' ] == True:
        print('languageCodesFileName=' + userInput[ 'languageCodesFileName' ] )
        print('languageCodesFileEncoding=' + userInput[ 'languageCodesFileEncoding' ] )

    global languageCodesSpreadsheet
    languageCodesSpreadsheet = chocolate.Strawberry( myFileName=userInput[ 'languageCodesFileName' ], fileEncoding=userInput[ 'languageCodesFileEncoding' ], removeWhitespaceForCSV=True )

    #sourceLanguageCellRow, sourceLanguageCellColumn = languageCodesSpreadsheet.searchColumnsCaseInsensitive( 'lav')
    #sourceLanguageCellRow, sourceLanguageCellColumn = languageCodesSpreadsheet.searchColumnsCaseInsensitive( 'japanese' )
    sourceLanguageCellRow, sourceLanguageCellColumn = languageCodesSpreadsheet.searchColumnsCaseInsensitive( userInput[ 'sourceLanguageRaw' ] )
    if (sourceLanguageCellRow == None) or (sourceLanguageCellColumn == None):
        print( ( 'Error: Unable to find source language \'' + str(sourceLanguageRaw) + '\' in file: ' + str(languageCodesFileName) ).encode(consoleEncoding) )
        sys.exit(1)
    print( ( 'Using sourceLanguage \'' + str(sourceLanguageRaw) + '\' found at \'' + str(sourceLanguageCellColumn) + str(sourceLanguageCellRow) + '\' of: ' + languageCodesFileName ).encode(consoleEncoding) )

    userInput[ 'sourceLanguageFullRow' ] = languageCodesSpreadsheet.getRow( sourceLanguageCellRow )
    userInput[ 'internalSourceLanguageName' ] = userInput[ 'sourceLanguageFullRow' ][0]
    userInput[ 'internalSourceLanguageTwoCode' ] = userInput[ 'sourceLanguageFullRow' ][1]
    userInput[ 'internalSourceLanguageThreeCode' ] = userInput[ 'sourceLanguageFullRow' ][2]
    if userInput[ 'debug' ] == True:
        print( str( userInput[ 'sourceLanguageFullRow' ] ).encode(consoleEncoding) )
        print( ('internalSourceLanguageName=' + userInput[ 'internalSourceLanguageName' ] ).encode(consoleEncoding) )
        print( ('internalSourceLanguageTwoCode=' + userInput[ 'internalSourceLanguageTwoCode' ] ).encode(consoleEncoding) )
        print( ('internalSourceLanguageThreeCode=' + userInput[ 'internalSourceLanguageThreeCode' ] ).encode(consoleEncoding) )

    targetLanguageCellRow, targetLanguageCellColumn = languageCodesSpreadsheet.searchColumnsCaseInsensitive( userInput[ 'targetLanguageRaw' ] )
    if ( targetLanguageCellRow == None ) or ( targetLanguageCellColumn == None ):
        print( ( 'Error: Unable to find target language \'' + userInput[ 'targetLanguageRaw' ] + '\' in file: '+ userInput[ 'languageCodesFileName' ] ).encode(consoleEncoding) )
        sys.exit(1)

    print( ( 'Using targetLanguage \'' + userInput[ 'targetLanguageRaw' ] + '\' found at \'' + str( targetLanguageCellColumn ) + str( targetLanguageCellRow ) + '\' of: ' + userInput[ 'languageCodesFileName'] ).encode(consoleEncoding) )

    userInput[ 'targetLanguageFullRow' ] = languageCodesSpreadsheet.getRow( targetLanguageCellRow )
    userInput[ 'internalDestinationLanguageName' ] = userInput[ 'targetLanguageFullRow' ][0]
    userInput[ 'internalDestinationLanguageTwoCode' ] = userInput[ 'targetLanguageFullRow' ][1]
    userInput[ 'internalDestinationLanguageThreeCode' ] = userInput[ 'targetLanguageFullRow' ][2]
    if userInput[ 'debug' ] == True:
        print( str( userInput[ 'targetLanguageFullRow'] ).encode(consoleEncoding) )
        print( ( 'internalDestinationLanguageName=' + userInput[ 'internalDestinationLanguageName' ] ).encode(consoleEncoding) )
        print( ( 'internalDestinationLanguageTwoCode=' + userInput[ 'internalDestinationLanguageTwoCode' ] ).encode(consoleEncoding) )
        print( ( 'internalDestinationLanguageThreeCode=' + userInput[ 'internalDestinationLanguageThreeCode' ] ).encode(consoleEncoding) )


    # Read in all other files and then the dictionaries.
    # revertAfterTranslationDictionaryFileName, preDictionaryFileName, postDictionaryFileName, postWritingToFileDictionaryFileName
    if userInput[ 'promptFileName' ] != None:
        with open( userInput[ 'promptFileName' ], 'rt', encoding=userInput[ 'promptFileEncoding' ], errors=userInput[ 'inputErrorHandling' ] ) as myFileHandle:
            userInput[ 'promptFileContents' ] = myFileHandle.read()
    else:
        userInput[ 'promptFileContents' ] = None       

    if userInput[ 'memoryFileName' ] != None:
        with open( userInput[ 'memoryFileName' ], 'rt', encoding=userInput[ 'memoryFileEncoding' ], errors=userInput[ 'inputErrorHandling'] ) as myFileHandle:
            userInput[ 'memoryFileContents' ] = myFileHandle.read()
    else:
            userInput[ 'memoryFileContents'] = None

    if userInput[ 'sceneSummaryPromptFileName' ] != None:
        with open( userInput[ 'sceneSummaryPromptFileName' ], 'rt', encoding=userInput[ 'sceneSummaryPromptEncoding' ], errors=userInput[ 'inputErrorHandling'] ) as myFileHandle:
            userInput[ 'sceneSummaryFileContents' ] = myFileHandle.read()
    else:
        userInput[ 'sceneSummaryFileContents' ] = None


    # Read in character dictionary.
    # This will either be 'None' if there was some sort of input error, like if the user did not specify one, or it will be a dictionary containing the charaName=value.
    if userInput[ 'characterNamesDictionaryFileName' ] != None:
        userInput[ 'characterNamesDictionary'] = functions.importDictionaryFromFile( userInput[ 'characterNamesDictionaryFileName' ], userInput[ 'characterNamesDictionaryEncoding' ] )
    else:
        userInput[ 'characterNamesDictionary'] = None

    # Read in revertAfterTranslationDictionary.
    # The value entry in key=value in the revertAfterTranslationDictionary can be '' or None. Basically, this signifies that key contains a string that should be reverted after translation.
    if userInput[ 'revertAfterTranslationDictionaryFileName' ] != None:
        userInput[ 'revertAfterTranslationDictionary' ] = functions.importDictionaryFromFile( userInput[ 'revertAfterTranslationDictionaryFileName' ], userInput[ 'revertAfterTranslationDictionaryEncoding' ] )
    else:
        userInput[ 'revertAfterTranslationDictionary' ] = None

    # Read in pre dictionary.
    if userInput[ 'preDictionaryFileName' ] != None:
        userInput[ 'preDictionary' ] = functions.importDictionaryFromFile( userInput[ 'preDictionaryFileName' ], userInput[ 'preDictionaryEncoding' ] )
    else:
        userInput[ 'preDictionary' ] = None

    # Read in post dictionary.
    if userInput[ 'postDictionaryFileName' ] != None:
        userInput[ 'postDictionary' ] = functions.importDictionaryFromFile( userInput[ 'postDictionaryFileName' ], userInput[ 'postDictionaryEncoding' ] )
    else:
        userInput[ 'postDictionary' ] = None

    # Read in afterWritingToFile dictionary.
    if userInput[ 'postWritingToFileDictionaryFileName' ] != None:
        userInput[ 'postWritingToFileDictionary' ] = functions.importDictionaryFromFile( userInput[ 'postWritingToFileDictionaryFileName' ], userInput[ 'postWritingToFileDictionaryEncoding' ] )
    else:
        userInput[ 'postWritingToFileDictionary' ] = None

    if userInput[ 'debug' ] == True:
        print( ( 'promptFileContents=' + str( userInput[ 'promptFileContents' ] ) ).encode(consoleEncoding) )
        print( ( 'memoryFileContents=' + str( userInput[ 'memoryFileContents' ] ) ).encode(consoleEncoding) )
        print( ( 'sceneSummaryFileContents=' + str( userInput[ 'sceneSummaryFileContents' ] ) ).encode(consoleEncoding) )

        print( ( 'characterNamesDictionary=' + str( userInput[ 'characterNamesDictionary' ] ) ).encode(consoleEncoding) )
        print( ( 'revertAfterTranslationDictionary=' + str( userInput[ 'revertAfterTranslationDictionary' ] ) ).encode(consoleEncoding) )
        print( ( 'preDictionary=' + str( userInput[ 'preDictionary'] ) ).encode(consoleEncoding) )
        print( ( 'postDictionary=' + str( userInput[ 'postDictionary'] ) ).encode(consoleEncoding) )
        print( ( 'postWritingToFileDictionary=' + str( userInput[ 'postWritingToFileDictionary' ] ) ).encode(consoleEncoding) )

    return userInput


def backupMainSpreadsheet( userInput=None, programSettings=None, outputName=None, force=False ):
    consoleEncoding = userInput[ 'consoleEncoding' ]

    # backupsEnabled is specified by the user. force=True is specified by the programmer. Therefore, backupsEnabled has priority in order to respect the user's decision. force=True is not allowed to override that.
    if userInput[ 'backupsEnabled' ] != True:
        return None

    if ( int( time.perf_counter() - programSettings[ 'timeThatBackupOfMainSpreadsheetWasLastSaved' ] ) > defaultMinimumSaveIntervalForMainSpreadsheet ) or ( force == True ):
        programSettings[ 'mainSpreadsheet' ].export( userInput[ 'outputName' ] )
        programSettings[ 'timeThatBackupOfMainSpreadsheetWasLastSaved' ] = time.perf_counter()


def backupSceneSummaryCache( userInput=None, programSettings=None, force=False ):
    consoleEncoding = userInput[ 'consoleEncoding' ]

    if ( userInput[ 'readOnlyCache' ] == True ) or ( programSettings[ 'sceneSummaryCacheWasUpdated' ] == False ):
        return

    if ( int( time.perf_counter() - programSettings[ 'timeThatSceneSummaryCacheWasLastSaved' ] ) > defaultMinimumSaveIntervalForCache ) or ( force == True ):

        #Syntax: randomNumber = random.randrange( 0, 500000 )
        temporaryFileNameAndPath = userInput[ 'sceneSummaryCacheFilePathOnly' ] + '/' + 'sceneSummaryCache.temp.' + str( random.randrange( 0, 500000 ) ) + userInput[ 'sceneSummaryCacheExtensionOnly' ]
        programSettings[ 'sceneSummaryCache' ].export( outputFileNameWithPath=temporaryFileNameAndPath )

        if functions.checkIfThisFileExists( temporaryFileNameAndPath ) == True:
            #Replace any existing cache with the temporary one.
            pathlib.Path( temporaryFileNameAndPath ).replace( userInput[ 'sceneSummaryCacheFileName' ] )
            #print( ( 'Wrote sceneSummaryCache to disk at: ' + userInput[ 'sceneSummaryCacheFileName' ] ).encode( consoleEncoding ) )
        else:
            print( ( 'Warning: Error writing temporary sceneSummaryCache file at:' + temporaryFileNameAndPath ).encode( consoleEncoding ) )

        programSettings[ 'timeThatSceneSummaryCacheWasLastSaved' ] = time.perf_counter()


def backupCache( userInput=None, programSettings=None, force=False ):
    consoleEncoding = userInput[ 'consoleEncoding' ]
    #global cache
    #global timeThatCacheWasLastSaved
    #global cacheWasUpdated
    #global cacheFilePathOnly

    if ( userInput[ 'readOnlyCache' ] == True ) or ( programSettings[ 'cacheWasUpdated' ] == False ):
        return

    if ( int( time.perf_counter() - programSettings[ 'timeThatCacheWasLastSaved' ] ) > defaultMinimumSaveIntervalForCache ) or ( force == True ):

        #Syntax: randomNumber = random.randrange( 0, 500000 )
        temporaryFileNameAndPath = userInput[ 'cacheFilePathOnly' ] + '/' + 'cache.temp.' + str( random.randrange( 0, 500000 ) ) + userInput[ 'cacheFileExtensionOnly' ]
        programSettings[ 'cache' ].export( outputFileNameWithPath=temporaryFileNameAndPath )

        if functions.checkIfThisFileExists( temporaryFileNameAndPath ) == True:
            #Replace any existing cache with the temporary one.
            pathlib.Path( temporaryFileNameAndPath ).replace( userInput[ 'cacheFileName' ] )
            #print( ( 'Wrote cache to disk at: ' + userInput[ 'cacheFileName' ] ).encode(consoleEncoding) )
        else:
            print( ( 'Warning: Error writing temporary cache file at:' + temporaryFileNameAndPath ).encode(consoleEncoding) )

        programSettings[ 'timeThatCacheWasLastSaved' ] = time.perf_counter()


# rawEntries is a list of strings, metadata is filename_startLineNumber+1_endLineNumberRaw+1 as a string, summaryData is the actual summary.
# programSettings should have
def updateSceneSummaryCache( userInput=None, programSettings=None, rawEntries=None, metadata=None, summaryData=None ):
    consoleEncoding = userInput[ 'consoleEncoding' ]
    #global sceneSummaryCache

    if userInput[ 'readOnlyCache' ] == True:
        return

    # What format should sceneSummaryCache take?
    # entry, engine # What is entry? A hash? 50 raw text entries? How about the sha1 hash?
    # Since that is too cryptic and since 50 raw texts is too long, then there must also be a metadata column to make the data human readable and debuggable.
    # entry, metadata, engine
    # entry is the sha1 hash of the rawEntries list, engine is the translation engine from translationEngine.model, and metadata is filename_startLineNumber+1_endLineNumberRaw+1
    # The +1 is to correct for the header in the spreadsheet which is removed from the data during processing.

    # Calculate sha1 hash from rawEntries.
    tempString = ''
    for entry in rawEntries:
        tempString = tempString + entry
    if len( tempString ) == 0:
        print( 'Warning: Unable to parse empty list when updating sceneSummaryCache.' )
        return None
    hash = str( hashlib.sha1( tempString.encode( consoleEncoding ) ).hexdigest() )

    # tempSearchResult can be a row number (as a string) or None if the string was not found.
    tempSearchResult = programSettings[ 'sceneSummaryCache' ].searchCache( hash )

    # if rawEntries is not in the cache
    if tempSearchResult == None:
        # then just append a new row with one entry, retrieve that row number, then set the appropriate column's value.
        # This returns the row number of the found entry as a string.
        tempSearchResult = programSettings[ 'sceneSummaryCache' ].addToCache( hash )
        programSettings[ 'sceneSummaryCache' ].setCellValue( currentCacheColumn + str( tempSearchResult ) , summaryData )
        programSettings[ 'sceneSummaryCache' ].setCellValue( 'B' + str( tempSearchResult ) , metadata ) # Hardcode metadata into the second column.
        if programSettings[ 'sceneSummaryCacheWasUpdated' ] == False:
            programSettings[ 'sceneSummaryCacheWasUpdated' ] = True

    # elif the rawEntries is in the sceneSummaryCache
    # elif tempSearchResult != None:
    else:
        # then get the appropriate cell, the currentCacheColumn + tempSearchResult.
        currentCellAddress = programSettings[ 'currentSceneSummaryCacheColumn' ] + str( tempSearchResult )

        # if the cell's value is None,
        if programSettings[ 'sceneSummaryCache' ].getCellValue( currentCellAddress ) == None:
            # then replace the value.
            programSettings[ 'sceneSummaryCache' ].setCellValue( currentCellAddress, summaryData )
            programSettings[ 'sceneSummaryCache' ].setCellValue( 'B' + str( tempSearchResult ) , metadata ) # Hardcode metadata into the second column.
            if programSettings[ 'sceneSummaryCacheWasUpdated' ] == False:
                programSettings[ 'sceneSummaryCacheWasUpdated' ] = True
        # elif the cell's value is not empty
        else:
            # Then only update the sceneSummaryCache if reTranslate == True
            if userInput[ 'reTranslate' ] == True:
                #print( 'Updated sceneSummaryCache')
                programSettings[ 'sceneSummaryCache' ].setCellValue( currentCellAddress, summaryData )
                programSettings[ 'sceneSummaryCache' ].setCellValue( 'B' + str( tempSearchResult ) , metadata ) # Hardcode metadata into the second column.
                if programSettings[ 'sceneSummaryCacheWasUpdated' ] == False:
                    programSettings[ 'sceneSummaryCacheWasUpdated' ] = True

    if userInput[ 'debug' ] == True:
        #sceneSummaryCache.printAllTheThings()
        print( ( 'Updated sceneSummaryCache at row ', tempSearchResult ).encode( consoleEncoding )  )

    if userInput[ 'readOnlyCache' ] != True:
        backupSceneSummaryCache( userInput=userInput )


# Expects two strings.
def updateCache( userInput=None, programSettings=None, untranslatedEntry=None, translation=None ):
    consoleEncoding = userInput[ 'consoleEncoding' ]
    #global cache
    #global currentCacheColumn

    if userInput[ 'readOnlyCache' ] == True:
        return

    # tempSearchResult can be a row number (as a string) or None if the string was not found.
    tempSearchResult = programSettings[ 'cache' ].searchCache( untranslatedEntry )

    # if the untranslatedEntry is not in the cache
    if tempSearchResult == None:
        # then just append a new row with one entry, retrieve that row number, then set the appropriate column's value.
        # This returns the row number of the found entry as a string.
        tempSearchResult = cache.addToCache( untranslatedEntry )
        programSettings[ 'cache' ].setCellValue( programSettings[ 'currentCacheColumn' ] + str(tempSearchResult) , translation )
        # The idea here is to limit the number of times cacheWasUpdated will be set to True which can be tens of thousands of times in a very short span of time which could potentially trigger a memory write out operation that many times depending upon how sub-programmer level caching is handled. Since CPUs are fast, and CPUs have cache for frequently used variables, this should be faster than writing out to main memory. Whether or not this optimization actually makes sense depends a lot on hardware which makes this questionabe to implement.
        if programSettings[ 'cacheWasUpdated' ] == False:
            programSettings[ 'cacheWasUpdated' ] = True

    # elif the untranslatedEntry is in the cache
    # elif tempSearchResult != None:
    else:
        # then get the appropriate cell, the currentCacheColumn + tempSearchResult.
        currentCellAddress = programSettings[ 'currentCacheColumn' ] + str( tempSearchResult )

        # if the cell's value is None
        if programSettings[ 'cache' ].getCellValue( currentCellAddress ) == None:
            # then replace the value
            programSettings[ 'cache' ].setCellValue( currentCellAddress, translation )
            if programSettings[ 'cacheWasUpdated' ] == False:
                programSettings[ 'cacheWasUpdated' ] = True
        # elif the cell's value is not empty
        else:
            # Then only update the cache if reTranslate == True
            if userInput[ 'reTranslate' ] == True:
                #print( 'Updated cache')
                cache.setCellValue( currentCellAddress, translation )
                if programSettings[ 'cacheWasUpdated' ] == False:
                    programSettings[ 'cacheWasUpdated' ] = True

    if userInput[ 'debug' ] == True:
        #cache.printAllTheThings()
        print( ( 'Updated cache at row ', tempSearchResult ).encode(consoleEncoding)  )

    backupCache()


def getSummary( userInput=None, programSettings=None, untranslatedList=[] ):
    global consoleEncoding
    global cache
    global cacheForSummary
    global mainSpreadsheet

    # Summary needs its own prompt and has its own translationEngine function call. Unlke the other functions, it also returns a summary as a string.
    # programSettings[ 'translationEngine' ].getSummary( untranslatedList, settings=userInput.copy() )

    return None

def batchTranslate( userInput=None, programSettings=None, untranslatedList=[], sceneSummary=None ):
    consoleEncoding = userInput[ 'consoleEncoding' ]
    #global cache
    #global cacheForSummary
    #global mainSpreadsheet
    #global currentCacheColumn
    #global translationEngine

    #translationEngine.batchTranslate()

    translateMe = []
    tempRequestList = []
    tempList = []
    if userInput[ 'cacheEnabled' ] == True:
        tempList = programSettings[ 'cache' ].getColumn( 'A' )
        # cacheHitCounter is only used for sanity checking.
        cacheHitCounter = 0

    if ( userInput[ 'cacheEnabled' ] == True ) and ( userInput[ 'reTranslate' ] != True ) and ( len(tempList) > 1 ):
        # Implement cache here. Create a list that will store the raw entry, whether there was a cache hit, and the value from the cache.
        # if there was not a cache hit, then add to a different list that will store the entries to translate as a batch.

        # Syntax: tempRequestList.append( [ 'rawEntry', thisValueIsFromCache, 'translatedData' ] )
        # Take every list entry from untranslatedList
        for untranslatedEntry in untranslatedList:

            # if entryInList/translatedData exists as a key in translationCacheDictionary,
            # if entryInList/untranslatedData exists in the cache's first column
            tempRowForCacheMatch = programSettings[ 'cache' ].searchCache( untranslatedEntry )
            if tempRowForCacheMatch != None:
                # then check if the appropriate column in the cache is a match.
                # This will return either None or the cell's contents.
                tempCellContents = programSettings[ 'cache' ].getCellValue( currentCacheColumn + str( tempRowForCacheMatch ) )
                if tempCellContents != None:
                    # if there is a match, then a perfect hit exists, so append the translatedEntry to tempRequestList
                    tempRequestList.append( [ untranslatedEntry , True, tempCellContents ] )
                    cacheHitCounter += 1

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
                    if ( userInput [ 'cacheAnyMatch' ] == True ) and ( len(validColumnLettersForCacheAnyMatch) > 0 ):
                    # if len(list) != 0, If it is 0, then do not bother. The length of that list could be 0 because even though the current model should always be added to cache and it could be returned, the current model should be blacklisted since the relevant cell was already checked.

                        # create a tempList=None
                        tempList = []
                        # for every column letter in the list
                        for columnLetter in validColumnLettersForCacheAnyMatch:
                            # prepend row, tempRowForCacheMatch, and return the individual cell contents.
                            # if the cell contents are not None,
                                # then tempList = [ rawEntry, thisValueIsFromCache=True, translatedData ]
                            # Keep updating the tempList to favor the right-most translation engine.

                            tempCellContents = programSettings[ 'cache' ].getCellValue( columnLetter + str( tempRowForCacheMatch ) )
                            if tempCellContents != None:
                                tempList.append( [ untranslatedEntry, True, tempCellContents ] )

                        # if tempList != None:
                        if len(tempList) > 0:
                            # then take the contents of the right-most/last list in tempList and append them to tempRequestList
                            # tempRequestList.append( [tempList[ 0 ], tempList[ 1 ], tempList[ 2 ] ] )
                            # len( tempList ) returns the number of items in a list. To get the last item, take the total items and subtract 1 because indexes start with 0.
                            tempRequestList.append( tempList[ len( tempList ) - 1 ] )
                            cacheHitCounter += 1

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

        assert( ( len(translateMe) + cacheHitCounter ) == len( untranslatedList ) )

    # if the cache is not enabled, if the user specified to reTranslate all lines, if the cache is too small, then skip
    #elif ( cacheEnabled != True ) or ( reTranslate == True ) or ( len( cache.getColumn( 'A' ) ) <=1 ):
    else:
        # Without copy(), this just creates a pointer to the original list, which means modifying the second list will also modify the original list which is not intended behavior here.
        translateMe = untranslatedList.copy()

    postTranslatedList = []
    if debug == True:
        print( ( 'translateMe=' + str( translateMe ) ).encode(consoleEncoding) )
    # Only attempt to translate entries if there was at least one entry not found in the cache.
    if len( translateMe ) > 0:

        # Perform replacements specified by preDictionary.
        if userInput[ 'preDictionary' ] != None:
            for index,entry in enumerate( translateMe ):
                for key,items in userInput[ 'preDictionary' ].items():
                    if translateMe[ index ].find( key ) != -1:
                        translateMe[ index ] = translateMe[ index ].replace( key, item )

        # Perform replacements specified by revertAfterTranslationDictionary.
        if userInput[ 'revertAfterTranslationDictionary' ]  != None:
            for index,entry in enumerate( translateMe ):
                for key,item in userInput[ 'revertAfterTranslationDictionary' ].items():
                    if translateMe[ index ].find( key ) != -1:
                        translateMe[ index ] = translateMe[ index ].replace( key, item )

        # Core logic.
        settings = userInput.copy()
        settings[ 'sceneSummary' ] = sceneSummary
        postTranslatedList = programSettings[ 'translationEngine' ].batchTranslate( translateMe, settings=settings )

    if debug==True:
        print( ( 'postTranslatedListRaw=' + str(postTranslatedList) ).encode(consoleEncoding) )

    # Perform replacements specified by revertAfterTranslationDictionary, in reverse.
    if userInput[ 'revertAfterTranslationDictionary' ] != None:
        for index,entry in enumerate( translateMe ):
            for key,item in userInput[ 'revertAfterTranslationDictionary' ].items():
                if translateMe[index].find( item ) != -1:
                    translateMe[ index ] = translateMe[ index ].replace( item, key )

        if debug==True:
            print( ( 'postTranslatedListAfterRevertAfterTranslationDictionaryChanges=' + str(postTranslatedList) ).encode(consoleEncoding) )

    finalTranslatedList=[]
    if userInput[ 'cacheEnabled' ] == True:

        # First, populate finalTranslatedList which requires merging the newly translated entries with the entries obtained from the cache.
        if userInput[ 'reTranslate' ] != True:
            # if every entry was found in the cache
            if len( postTranslatedList ) == 0:
                #then set finalTranslatedList to all the translated entries that were added to tempRequestList.
                for entry in tempRequestList:
                    finalTranslatedList.append( entry[ 2 ] )
            # if cache was empty prior to submitting entries, then it will still be empty here. Only the header will be returned len( ~cache )==1, then there is nothing to merge, so set the output to the postTranslatedList.
            elif len( cache.getColumn('A') ) <= 1:
                finalTranslatedList=postTranslatedList.copy()
            else:
                counter=0
                # Need to merge processed items, postTranslatedList, with tempRequestList for finalTranslatedList.
                # iterate over postTranslatedList, for every entry 
                for entry in tempRequestList:
                    # if the valueIsFromCache == True
                    if entry[ 1 ] == True:
                        #append entry[ 2 ] to final finalTranslatedList
                        finalTranslatedList.append( entry[ 2 ] )
                    # elif the valueIsNotFromCache, valueIsFromCache == False
                    else:
                        # then append the recently translated value, postTranslatedList[ counter ]
                        finalTranslatedList.append( postTranslatedList[ counter ] )
                        # and increase the counter.
                        counter += 1
                    # go to next entry

        #if reTranslate == True, then len(tempRequestList) == 0, so do not bother trying to read entries from it. Just set output to postTranslatedList.
        #elif reTranslate == True:
        else:
            finalTranslatedList = postTranslatedList.copy()

        if userInput[ 'debug' ] == True:
            print( 'len( finalTranslatedList )=' + str( len( finalTranslatedList ) ) )
            print( 'len( untranslatedList )=' + str( len( untranslatedList ) ) )

    #elif cacheEnabled != True:
    else:
        finalTranslatedList = postTranslatedList.copy()

    assert( len( finalTranslatedList ) == len( untranslatedList ) )

    # next, update the cache
    if cacheEnabled == True:
        if ( len( postTranslatedList) != 0 ) and ( readOnlyCache == False ):
            # untranslatedList and finalTranslatedList need to be added to the cache file now.

            for counter,untranslatedString in enumerate( untranslatedList ):
                updateCache( userInput=userInput, programSettings=programSettings, untranslatedEntry=untranslatedString, translation=finalTranslatedList[ counter ] )

    # Check with postDictionary, a Python dictionary for possible updates.
    if userInput[ 'postDictionary' ] != None:
        #print( 'pie2' )
        for counter,entry in enumerate(finalTranslatedList):
            for key,item in postDictionary.items():
                #print( 'key=', key, 'item=', item )
                if finalTranslatedList[counter].find( key ) != -1:
                    if debug == True:
                        print( ( 'found key=' + key + ' at line=' + str(counter) ).encode(consoleEncoding) )
                    finalTranslatedList[ counter ] = finalTranslatedList[ counter ].replace( key, item )

    return finalTranslatedList


def translate( userInput=None, programSettings=None, untranslatedList=None ):
    consoleEncoding = userInput[ 'consoleEncoding' ]
    #global cache
    #global currentCacheColumn
    #global cacheForSummary
    #global mainSpreadsheet
    #global translationEngine

    # Process each entry individually.
    #currentMainSpreadsheetColumn

    #if debug == True:
    #print( 'BATCH MODE DISABLED.' )
    #print( 'reTranslate=', reTranslate )

#    if cacheEnabled == True:
#        tempList=cache.getColumn('A') ) > 1
#    if ( cacheEnabled == True ) and ( reTranslate != True ) and ( len(tempList) > 1 ):
# len( cache.getColumn('A') ) > 1


    # if the translation engine supports history, then initalize contextHistory up to the length specified by contextHistoryMaxLength. If contextHistoryMaxLength == 0 then it was already disabled,so check for that. contextHistoryMaxLength is always an integer.
    if ( userInput[ 'contextHistoryEnabled' ] == True ) and ( translationEngine.supportsHistory == True):
        contextHistory = None
        #https://docs.python.org/3.7/library/queue.html#module-queue
        contextHistory=queue.Queue( maxsize = userInput[ 'contextHistoryMaxLength' ] )
        # To add an entry, contextHistory.put( item )
        # To remove the oldest, contextHistory.get()
        # To get every item without modifying the queue
        #for i in range( contextHistory.qsize() ):
            #print( contextHistory.queue[i] )
        # To check if the queue is full,
        #if contextHistory.full() == True:



    if tqdmAvailable == False:
        tempIterable = untranslatedList
    if tqdmAvailable == True:
        tempIterable = tqdm.tqdm( untranslatedList )

    # for every cell in A, try to translate it.
    for rawUntranslatedEntry in tempIterable:
        translatedEntry = None

        # Sanity check.
        assert( rawUntranslatedEntry == programSettings[ 'mainSpreadsheet' ].getCellValue( 'A' + str( programSettings[ 'currentRow'] ) ) )

        currentTranslatedCellAddress = programSettings[ 'currentMainSpreadsheetColumn' ] + str( programSettings[ 'currentRow' ] )

        # Get speaker, if any.
        tempSpeakerName = programSettings[ 'mainSpreadsheet' ].getRow( programSettings[ 'currentRow' ] )
        if len( tempSpeakerName ) > 1:
            tempSpeakerName = tempSpeakerName[1]
            if ( tempSpeakerName == '' ) or ( not isinstance( tempSpeakerName, str ) ):
                tempSpeakerName = None
        else:
            tempSpeakerName = None

        # Use characterNamesDictionary to translate character names prior to submission to translationEngine.
        # The character names should have already been translated prior to this during parsing, but if not, then apply a band-aid fix here to translate them prior to submission to the translationEngine so the translationEngine code does not have to worry about it as much. This code should be harmless if the names are already translated.
        if ( tempSpeakerName != None ) and ( userInput[ 'characterNamesDictionary' ] != None ):
            if tempSpeakerName in userInput[ 'characterNamesDictionary' ]:
                tempSpeakerName = userInput[ 'characterNamesDictionary' ][ tempSpeakerName ]

        # if the current cell contents are already translated, then just continue onto the next entry unless retranslate is specified.
        currentMainSpreadsheetCellContents = programSettings[ 'mainSpreadsheet' ].getCellValue( currentTranslatedCellAddress )
        if ( currentMainSpreadsheetCellContents != None ) and ( reTranslate != True ):
            # Update the contextHistory queue.
            if ( userInput[ 'contextHistoryEnabled' ] == True ) and ( translationEngine.supportsHistory == True):
                if contextHistory.full() == True():
                    # This is probably not ideal. The entire queue should be emptied manually using .get() maybe in a while loop?
                    contextHistory = queue.Queue( maxsize=userInput[ 'contextHistoryMaxLength' ] )
                contextHistory.put( [ rawUntranslatedEntry,currentMainSpreadsheetCellContents, tempSpeakerName  ] )

            # It is not clear where the translation already in the spreadsheet came from so do not update cache. # Update: Well, it could be determined by reading the header in the current column and looking up the same column in the cache. Will they always match perfectly or is it possible they will not match perfectly? If they always match perfectly, the model in the mainSpreadsheet and the model in cache.xlsx, then it may be possible to update the cache.
            # if the header (translation engine) of the current column in the mainSpreadsheet matches the header (translation engine) of the cache header
            # They should always match, right?
            if userInput[ 'cacheEnabled' ] == True:
                if programSettings[ 'mainSpreadsheet' ].getCellValue( programSettings[ 'currentMainSpreadsheetColumn' ] + '1' ) == programSettings[ 'cache' ].getCellValue( programSettings[ 'currentCacheColumn' ] + '1' ):
                    # then update the cache with what was found in the mainSpreadsheet
                    updateCache( userInput=userInput, programSettings=programSettings, untranslatedEntry=rawUntranslatedEntry, translation=currentMainSpreadsheetCellContents )

            programSettings[ 'currentRow' ] += 1
            continue
        #elif ( currentMainSpreadsheetCellContents == None ) or ( userInput[ 'reTranslate' ] == True ):
        #else:
            # else if userInput[ 'retranslate' ] is specified

        if userInput[ 'cacheEnabled' ] == True:
           # search column A in cache for raw untranslated there is a match
            tempRowNumberForCache = cache.searchCache( rawUntranslatedEntry )
            if userInput[ 'debug' ] == True:
                cache.printAllTheThings()
                print( 'tempRowNumberForCache=' + str( tempRowNumberForCache ) )

        if userInput[ 'debug' ] == True:
            print( 'rawUntranslatedEntry=' + rawUntranslatedEntry )
            #sys.exit()

        # First check if cache is enabled, and reTranslate != True. If they are, then check cache for value.
        if ( userInput[ 'cacheEnabled' ] == True ) and ( userInput[ 'reTranslate' ] != True ):

            tempAddress=None
            # if tempRowNumberForCache == None, that means the untranslated string does not appear in the cache.
            if tempRowNumberForCache != None:
                tempAddress = currentCacheColumn + str( tempRowNumberForCache )

                # if cache hit confirmed, then set this to translatedEntry=
                # get cell back and check if that cell is not None. If it is None, then that means the untranslated string does appear in the cache, but not for that exact model. A different entry might be valid with cache any match.
                translatedEntry = cache.getCellValue( tempAddress )
                #print( 'translatedEntryFromCache=' + str( translatedEntry ) )
                if translatedEntry == '':
                    translatedEntry=None

                # if translatedEntry != None, then it has already been translated using a perfect hit in the cache. Just move on to the next step.
                # if translatedEntry == None, then there is not a perfect cache hit, so expand the search if cacheAnyMatch is enabled.
                # if cache is any row, then return all rows in Strawberry() and check if any are not None.
                if ( translatedEntry == None ) and ( cacheAnyMatch == True ) and ( len(userInput[ 'validColumnLettersForCacheAnyMatch' ] ) > 0 ):
                    for columnLetter in userInput[ 'validColumnLettersForCacheAnyMatch' ]:
                        tempCellContents = cache.getCellValue( columnLetter + str( tempRowNumberForCache ) )
                        if tempCellContents != None:
                            # Keep updating translatedEntry to favor the right-most translation engine.
                            translatedEntry = tempCellContents
        #elif ( cacheEnabled != True ) or ( reTranslate == True ):
        #else:

        # if there is no match in the cache or cache is disabled, then the fun begins
        if translatedEntry == None:
            # Remove all \n's in the line? Actually, this level of preparsing should be left to the translation engine code itself.

            # A temporary variable is needed here because otherwise the original entry is lost after all the replacement dictionaries and the cache ends up getting corrupted by revertAfterTranslationDictionary as a result.
            untranslatedEntry = rawUntranslatedEntry

            # Perform replacements specified by revertAfterTranslationDictionary.
            if userInput[ 'revertAfterTranslationDictionary' ] != None:
                for key,item in userInput[ 'revertAfterTranslationDictionary' ].items():
                    if untranslatedEntry.find( key ) != -1:
                        untranslatedEntry = untranslatedEntry.replace( key, item )

            # Perform replacements specified by preDictionary.
            if userInput[ 'preDictionary' ] != None:
                for key,items in userInput[ 'preDictionary' ].items():
                    if untranslatedEntry.find( key ) != -1:
                        untranslatedEntry = untranslatedEntry.replace( key, item )

            # translate entry
            # submit the line to the translation engine, along with the current dequeue # TODO: Add options to specify history length of dequeue to the CLI. # Update: Added.
            tempHistory = []

            if ( userInput[ 'contextHistoryEnabled' ] == True ) and ( translationEngine.supportsHistory == True ) :
                for i in range( contextHistory.qsize() ):
                    tempHistory.append( contextHistory.queue[i] )

            if len( tempHistory ) == 0:
                tempHistory = None

            settings = {}
            settings[ 'speakerName' ] = tempSpeakerName
            settings[ 'contextHistory' ] = tempHistory
            settings[ 'sceneSummary' ] = sceneSummary

            try:
                translatedEntry = translationEngine.translate( untranslatedEntry, settings=settings )
            except Exception as exception:
                print( 'Error: Internal engine error in for translationEngine=' + userInput[ 'mode' ] )
                print( exception.__class__.__name__ )
                translatedEntry = None
                if exception.__class__.__name__ != requests.exceptions.JSONDecodeError:
                    raise exception
  
            # once it is back check to make sure it is not None or another error value
            if ( translatedEntry == None ) or ( translatedEntry == '' ):
                print( ( 'Unable to translate: ' + untranslatedEntry).encode(consoleEncoding) )
                programSettings[ 'currentRow' ] += 1
                continue

        # History should be updated before revertAfterTranslationDictionary is applied otherwise there will be invalid data submitted to the translation engine.
        # Conversely, it should not be added to the cache until after reversion takes place because the cache should hold a translation that represents the original data as closely as possible.
        # Add it to the dequeue, murdering the oldest entry in the dequeue.
        # Update the contextHistory queue.
        if ( userInput[ 'contextHistoryEnabled' ] == True ) and ( translationEngine.supportsHistory == True):
            if contextHistory.full() == True:
                #contextHistory.get()
                # LLMs tend to start hallucinating pretty fast and old history can corrupt new entries quickly, so just wipe history every once in a while as a workaround. Theoretically, it could make sense to keep history at max for a while and then wipe it later, but for now, just wipe it whenever it hits max.
                # This is probably not ideal. The entire queue should be emptied manually using .get() maybe in a while loop?
                contextHistory=queue.Queue( maxsize=userInput[ 'contextHistoryMaxLength' ] )
            contextHistory.put( [ rawUntranslatedEntry, translatedEntry, tempSpeakerName ] )

        # perform replacements specified by revertAfterTranslationDictionary, in reverse
        if userInput[ 'revertAfterTranslationDictionary' ] != None:
            for key,item in userInput[ 'revertAfterTranslationDictionary' ].items():
                if translatedEntry.find( item ) != -1:
                    translatedEntry = translatedEntry.replace( item, key )

        # if cache is enabled, then add the untranslated line and the translated line as a pair to the cache file.
        if ( userInput[ 'cacheEnabled' ] == True ) and ( userInput[ 'readOnlyCache' ] == False ):
            updateCache( userInput=userInput, programSettings=programSettings, untranslatedEntry=rawUntranslatedEntry, translation=translatedEntry )

        # Check with postDictionary, a Python dictionary for possible updates.
        if userInput[ 'postDictionary' ] != None:
            for key,items in userInput[ 'postDictionary' ].items():
                if translatedEntry.find( key ) != -1:
                    translatedEntry = translatedEntry.replace( key, item )

        # then write translation to mainSpreadsheet cell.
        mainSpreadsheet.setCellValue( currentTranslatedCellAddress , translatedEntry )

        if userInput[ 'backupsEnabled' ] == True:
            # Create a backup. Backups are on a minimum timer, so calling this a lot should not be an issue.
            backupMainSpreadsheet( userInput=userInput, outputName=userInput[ 'backupsFilePathWithNameAndDate' ] )

        # and move on to next cell
        programSettings[ 'currentRow' ] += 1
        continue


def main( userInput=None ):

    if not isinstance( userInput, dict ):
        # Define command line options.
        # userInput is a dictionary.
        userInput = createCommandLineOptions()
        if userInput[ 'settingsFile' ] != None:
            userInput = mergeInput( userInput, userInput[ 'settingsFile' ] )
        else:
            userInput = mergeInput( userInput, __name__ )

    # Verify input.
    userInput = validateUserInput( userInput )

    consoleEncoding = userInput[ 'consoleEncoding' ]

    if userInput[ 'debug' ] ==True:
        print( ( 'userInput (validated)=' + str(userInput) ).encode( consoleEncoding ) )

    # read input files
    # This should also read in all of the input prompt files into dictionaries using the settings in userInput.
    userInput = readInputFiles( userInput )

    # Initialize programSettings dictionary. Instead of making everything global, the idea is to organize variables, including class instances, into this dictionary and pass the dictionary around. This should split variables into 1) userInput, 2) programSettings, or 3) local function variables. Passing the programSettings dictionary as an argument to a function passes a pointer to it in CPython, so there should be no performance ramifications compared to global variables.
    programSettings = {}

    # Initialize some counters and other variables.
    # How can these values be copied without having them all point to the same object? Does time.perf_counter() have some sort of .copy() utility method? Well, it should not matter because a new object is created whenever they need to be updated. Having them all point to the same object initially should not matter.
    currentTime = time.perf_counter()
    programSettings[ 'timeThatBackupOfMainSpreadsheetWasLastSaved' ] = currentTime
    programSettings[ 'timeThatSceneSummaryCacheWasLastSaved' ] = currentTime
    programSettings[ 'timeThatCacheWasLastSaved' ] = currentTime

    programSettings[ 'cacheWasUpdated' ] = False
    programSettings[ 'sceneSummaryCacheWasUpdated' ] = False
    programSettings[ 'currentRow' ] = 2 # Start with row 2. Rows start with 1 instead of 0 and row 1 is always headers. Therefore, row 2 is the first row number with untranslated/translated pairs.

    # Next turn fileToTranslateFileName into a data structure. How? Read the file, then create data structure from that file.
    # chocolate.Strawberry() is a wrapper class for the onenpyxl.workbook class with additional methods.
    # The interface has no concept of workbooks vs spreadsheets. That distinction is handled only inside the class. Syntax:
    # mainSpreadsheet = chocolate.Strawberry()

    # if main file is a spreadsheet, then it will be read in as a native data structure. Otherwise, if the main file is a .txt file, then it will be parsed as line-by-line by the class.
    # Basically, the user is responsible for proper parsing if line-by-line parsing does not work right. Proper parsing is outside the scope of py3TranslateLLM.
    # Create data structure using fileToTranslateFileName. Whether it is a text file or spreadsheet file is handled internally.
    #global mainSpreadsheet
    programSettings[ 'mainSpreadsheet' ] = chocolate.Strawberry( userInput[ 'fileToTranslateFileName' ], fileEncoding=userInput[ 'fileToTranslateEncoding' ], removeWhitespaceForCSV=False, addHeaderToTextFile=False )

    #Before doing anything, just blindly create a backup. #This code should probably be moved into a local function so backups can be created easier. Update: Done. Use     backupMainSpreadsheet( userInput=userInput, outputName=outputName, force=False):

    #backupsFolder does not have / at the end
    backupsFolderWithDate = backupsFolder + '/' + functions.getYearMonthAndDay()
    pathlib.Path( backupsFolderWithDate ).mkdir( parents = True, exist_ok = True )
    #mainDatabaseWorkbook.save( 'backups/' + functions.getYearMonthAndDay() + '/rawUntranslated-' + currentDateAndTimeFull+'.xlsx')
    # This variable is derivative of the fileToTranslateFileNameWithoutPath, hence not incorrect to consider it part of userInput as a derivative variable.
    userInput[ 'backupsFilePathWithNameAndDate' ] = backupsFolderWithDate + '/'+ userInput[ 'fileToTranslateFileNameWithoutPath' ] + '.raw.' + functions.getDateAndTimeFull() + defaultExportExtension
    #mainSpreadsheet.exportToXLSX( userInput[ 'backupsFilePathWithNameAndDate' ] )
    # TODO: There should be a CLI setting to not create backups. # Update: Done.
    if userInput[ 'backupsEnabled' ] == True:
        backupMainSpreadsheet( userInput=userInput, outputName=userInput[ 'backupsFilePathWithNameAndDate' ], force=True )

    # Should subsequent backups always be created as .xlsx or should they, after the initial backup, use the user's chosen spreadsheet format? Answer: Maybe let the user decide via a CLI flag but default to .xlsx? Alternatively, could set the option as a default boolean toggle in the script, but that might be annoying during actual usage. TODO: Implement this as a CLI option later in order to respect the user's decision.
    userInput[ 'backupsFilePathWithNameAndDate' ] = backupsFolderWithDate + '/'+ userInput[ 'fileToTranslateFileNameWithoutPath '] + '.backup.' + functions.getDateAndTimeFull() + defaultExportExtension
    #print( ( 'Wrote backup to: ' + backupsFilePathWithNameAndDate ).encode(consoleEncoding) )

    if userInput[ 'debug' ] == True:
        print( ( 'fileToTranslateFileNameWithoutPathOrExt=' + userInput[ 'fileToTranslateFileNameWithoutPathOrExt' ] ).encode(consoleEncoding) )
        print( ( 'Today=' + functions.getYearMonthAndDay() ).encode(consoleEncoding) )
        print( ( 'Yesterday=' + functions.getYesterdaysDate() ).encode(consoleEncoding) )
        print( ( 'CurrentTime=' + functions.getCurrentTime() ).encode(consoleEncoding) )
        print( ( 'DateAndTime=' + functions.getDateAndTimeFull() ).encode(consoleEncoding) )

    #Now that the main data structure has been created, the spreadsheet is ready to be translated.
    if userInput[ 'mode' ] == 'parseOnly':
        programSettings[ 'mainSpreadsheet' ].export( userInput[ 'outputFileName' ], fileEncoding=userInput[ 'outputFileEncoding' ], columnToExportForTextFiles='A' )

        #work complete. Exit.
        print( 'Work complete.' )
        sys.exit( 0 )

    #Now need to translate stuff.

    # Cache should always be added. This potentially creates a situation where cache is not valid when going from one title to another or where it is used for translating entries for one character that another character spoke, but that is fine since that is a user decision to keep cache enabled despite the slight collisions.
    # Currently, cache does not consider multiple languages. It may be a good idea to specify a specific 'sheet' to load or work from based upon the source and destination 3-letter language names when initalizing it. Something like... source_target, jpn_eng, chi_eng, eng_spn Update: Cache now consideres multiple languages. Each sheet in the workbook is a different sourceLanguage_targetLanguage pair marked by 3 letter words.

    print( 'cacheEnabled=', userInput[ 'cacheEnabled' ] )

    if userInput[ 'cacheEnabled' ] == True:
        #First, initialize cache.xlsx file under backups/
        # Has same structure as mainSpreadsheet except for no speaker and no metadata. Still has a header row of course. Multiple columns with each one as a different translation engine.
        #if the path for cache does not exist, then create it.
        pathlib.Path( userInput[ 'cacheFilePathOnly' ] ).mkdir( parents = True, exist_ok = True )

        # if cache.xlsx exists, then the cache file will be read into a chocolate.Strawberry(), otherwise, a new one will be created only in memory.
        # Initialize Strawberry(). Very tempting to hardcode utf-8 here, but... will avoid.
        global cache
        programSettings[ 'cache' ] = chocolate.Strawberry( myFileName = userInput[ 'cacheFileName' ], fileEncoding = defaultTextEncoding, spreadsheetNameInWorkbook = userInput[ 'internalSourceLanguageThreeCode' ] + '_' + userInput[ 'internalDestinationLanguageThreeCode' ], readOnlyMode = userInput[ 'readOnlyCache' ] )

        if functions.checkIfThisFileExists( userInput[ 'cacheFileName' ] ) != True:
            # if the Strawberry is brand new, add header row.
            cache.appendRow( [ 'rawText' ] )

        # Build the index from all entries in the first column.
        # TODO: This should be more flexible. If there is an error initalizing it, then call cache.rebuildCache() and try again.
        # However, that might be a mistake if the user specified the wrong option or file by mistake, so require user confirmation via a CLI flag for this exact action.
        # if cli option not enabled
        programSettings[ 'cache' ].initializeCache() # This enables the use of searchCache() and addToCache() methods.
        # else, do a try: except: block that includes rebuilding it.

        #originalNumberOfEntriesInCache = len( cache.getColumn( 'A' ) )

        # Debug code.
        if userInput[ 'debug' ] == True:
            cache.printAllTheThings()
    #    if readOnlyCache != True:
    #        cache.export(cacheFileName)

        if userInput[ 'verbose' ] == True:
            print( ( 'Cache is available at: ' + str( userInput[ 'cacheFileName' ] ) ).encode( consoleEncoding ) )


    # Implement KoboldAPI first, then DeepL, .
    # Update: Implement py3translationserver, then Sugoi, then KoboldCPP's API, then DeepL API, then DeepL Web, then OpenAI's API (generic).
    # Update (again): Implement py3translationserver, then KoboldCpp, then DeepL API Free, then Google-T, then Groq + mixtral8x7b API, then sugoi.
    # Check current engine.
        # Echo request? Some firewalls block echo requests.
        # Maybe just assume it exists and poke it with various requests until it is obvious to the user that it is not responding?


    # py3translationServer must be reachable Check by getting currently loaded model. This is required for the cache and mainSpreadsheet.
    if userInput[ 'mode' ] == 'py3translationserver':

        # Build settings dictionary for this translation engine.
        settingsDictionary = {}
        settingsDictionary[ 'address' ] = userInput[ 'address' ]
        settingsDictionary[ 'port' ] = userInput[ 'port' ]

        programSettings[ 'translationEngine' ]=py3translationServerEngine.Py3translationServerEngine( sourceLanguage=userInput[ 'sourceLanguageFullRow' ], targetLanguage=userInput[ 'targetLanguageFullRow' ], characterDictionary=userInput[ 'characterNamesDictionary' ], settings=settingsDictionary )

        #Check if the server is reachable. If not, then exit. How? The py3translationServer should have both the version and model available at http://localhost:14366/api/v1/model and version, and should have been set during initalization, so verify they are not None.
        # Update: Moved this code inside the translation engine itself and made it accessible as translationEngine.reachable which is a boolean, which is checked below.
    #    if translationEngine.model == None:
    #        print( 'translationEngine.model is None' )
    #        sys.exit(1)
    #    elif translationEngine.version == None:
    #        print( 'translationEngine.version is None' )
    #        sys.exit(1)

    # SugoiNMT server must be reachable.
    elif userInput[ 'mode' ] == 'sugoi':
        settingsDictionary = {}
        settingsDictionary[ 'address' ] = userInput[ 'address' ]
        settingsDictionary[ 'port' ] = userInput[ 'port' ]
        programSettings[ 'translationEngine' ]= sugoiNMTEngine.sugoiNMTEngine( sourceLanguage=userInput[ 'sourceLanguageFullRow' ], targetLanguage=userInput[ 'targetLanguageFullRow' ], settings=settingsDictionary)

    # KoboldCpp's API must be reachable. Check by getting currently loaded model. This is required for the cache and mainSpreadsheet.
    elif userInput[ 'mode' ] ==' koboldcpp':

        #assert( promptFileContents != None )
        assert( isinstance( userInput[ 'promptFileContents' ], str ) )

        # Build settings dictionary for this translation engine.
        settingsDictionary = {}
        settingsDictionary[ 'address' ] = userInput[ 'address' ]
        settingsDictionary[ 'port' ] = userInput[ 'port' ]
        settingsDictionary[ 'prompt' ] = userInput[ 'promptFileContents' ]
        if userInput[ 'memoryFileName' ] != None:
            settingsDictionary[ 'memory' ] = userInput[ 'memoryFileContents' ]

        programSettings[ 'translationEngine' ] = koboldCppEngine.KoboldCppEngine( sourceLanguage=userInput[ 'sourceLanguageFullRow' ], targetLanguage=userInput[ 'targetLanguageFullRow' ], characterDictionary=userInput[ 'characterNamesDictionary' ], settings=settingsDictionary )

    elif userInput[ 'mode' ] == 'pykakasi':
        # Build settings dictionary for this translation engine.
        settingsDictionary={}
        if userInput[ 'romajiFormat' ] != None:
            settingsDictionary[ 'romajiFormat' ] = userInput[ 'romajiFormat' ]

        programSettings[ 'translationEngine' ] = pykakasiEngine.PyKakasiEngine( sourceLanguage=userInput[ 'sourceLanguageFullRow' ], targetLanguage=userInput[ 'targetLanguageFullRow' ], characterDictionary=userInput[ 'characterNamesDictionary' ], settings=settingsDictionary)

    elif userInput[ 'mode' ] == 'cutlet':
        # Build settings dictionary for this translation engine.
        settingsDictionary={}
        if userInput[ 'romajiFormat' ] != None:
            settingsDictionary[ 'romajiFormat' ] = userInput[ 'romajiFormat' ]

        programSettings[ 'translationEngine' ] =cutletEngine.CutletEngine( sourceLanguage=userInput[ 'sourceLanguageFullRow' ], targetLanguage=userInput[ 'targetLanguageFullRow' ], characterDictionary=userInput[ 'characterNamesDictionary' ], settings=settingsDictionary)


    # DeepL has already been imported, and it must have an API key. (already checked for)
        #Must have internet access then. How to check?
        # Added functions.checkIfInternetIsAvailable() function that uses requests/socket to fetch a web page or resolve an address.
        # assert( functions.checkIfInternetIsAvailable() == True )

    if programSettings[ 'translationEngine' ].reachable != True:
        print( 'TranslationEngine \''+ mode +'\' is not reachable. Check the connection or API settings and try again.' )
        sys.exit(1)


    # This will return the column letter of the model if the model is already in the spreadsheet. Otherwise, if it is not found, then it will return None.
    #global currentMainSpreadsheetColumn
    programSettings[ 'currentMainSpreadsheetColumn' ] = programSettings[ 'mainSpreadsheet' ].searchHeaders( programSettings[ 'translationEngine' ].model )
    if programSettings[ 'currentMainSpreadsheetColumn' ] == None:
        # Then the model is not currently in the spreadsheet, so need to add it. Update currentMainSpreadsheetColumn after it has been updated.
        headers = programSettings[ 'mainSpreadsheet' ].getRow( 1 )
        headers.append( programSettings[ 'translationEngine' ].model )
        programSettings[ 'mainSpreadsheet' ].replaceRow( 1, headers )
        programSettings[ 'currentMainSpreadsheetColumn' ] = programSettings[ 'mainSpreadsheet' ].searchHeaders( programSettings[ 'translationEngine' ].model )
        if programSettings[ 'currentMainSpreadsheetColumn' ] == None:
            print( 'unspecified error.' )
            sys.exit(1)


    if userInput [ 'cacheEnabled' ] == True:
        # Prepare some static data for cacheAnyMatch so that it does not have to be prepared while in the loop on every loop.
        if userInput[ 'cacheAnyMatch' ] == True:
            #global blacklistedHeadersForCacheAnyMatch
            programSettings[ 'blacklistedHeadersForCacheAnyMatch' ] = defaultBlacklistedHeadersForCache
            programSettings[ 'blacklistedHeadersForCacheAnyMatch' ].append( programSettings[ 'translationEngine' ].model )

            # To help with a case insensitive search, make everything lowercase.
            for counter,blacklistedHeader in enumerate( programSettings[ 'blacklistedHeadersForCacheAnyMatch' ] ):
                programSettings[ 'blacklistedHeadersForCacheAnyMatch' ][ counter ] = blacklistedHeader.lower()

            if userInput[ 'cacheAnyMatch' ] == True:
                # Return the cache header row.
                headers = programSettings[ 'cache' ].getRow( 1 )
                programSettings[ 'validColumnLettersForCacheAnyMatch' ] = []
                for header in headers:
                    if str( header ).lower() not in programSettings[ 'blacklistedHeadersForCacheAnyMatch' ]:
                        # This should append the column letter, not the literal text, to the list.
                        programSettings[ 'validColumnLettersForCacheAnyMatch' ].append( programSettings[ 'cache' ].searchHeaders( header ) )

        #Set currentCacheColumn.
        programSettings[ 'currentCacheColumn' ] = programSettings[ 'cache' ].searchHeaders( programSettings[ 'translationEngine' ].model )
        if programSettings[ 'currentCacheColumn' ] == None:
            # Then the model is not currently in the cache, so need to add it. Update currentCacheColumn after it has been updated.
            headers = programSettings[ 'cache' ].getRow( 1 )
            headers.append( translationEngine.model )
            cache.replaceRow( 1, headers )
            currentCacheColumn = cache.searchHeaders( translationEngine.model )
            if currentCacheColumn == None:
                print( 'unspecified error .' )
                sys.exit( 1 )


    # if requiresPrompt = True and supportsBatches = True, then is an LLM,
        # if batchesEnabledForLLMs, then batchModeEnabled=True
        # if batchesEnabledForLLMs == False, then batchModeEnabled=False
    # requiresPrompt = False and supportsBatches = True, then is an NMT, then batchModeEnabled=True
    # if requiresPrompt = True and supportsBatches = False, then is an LLM, then batchModeEnabled=False
    # requiresPrompt = False and supportsBatches = False, then is an NMT, then batchModeEnabled=False

    if programSettings[ 'translationEngine' ].supportsBatches == False:
        batchModeEnabled=False
    # can be an NMT or LLM.
    # elif translationEngine.supportsBatches == True:
    elif programSettings[ 'translationEngine' ].requiresPrompt == False:
        # is an NMT, always enable batches.
        batchModeEnabled=True
    # elif translationEngine.supportsBatches == True:
    # elif translationEngine.requiresPrompt == True:
    else:
        # is an LLM that supports batches, only enable batches if batchesEnabledForLLMs == True
        if userInput[ 'batchesEnabledForLLMs' ] == True:
            batchModeEnabled=True
        else:
            batchModeEnabled=False

    untranslatedEntriesColumnFull = programSettings[ 'mainSpreadsheet' ].getColumn( 'A' )

    if debug == True:
        # Debug code.
        for counter,untranslatedString in enumerate( untranslatedEntriesColumnFull ):
            assert( untranslatedString == programSettings[ 'mainSpreadsheet' ].getCellValue( 'A' + str( counter + 1 )) )
            #print( 'pie' )
        #print( 'pie0' )
        print( len( untranslatedEntriesColumnFull ) )

    untranslatedEntriesColumnFull.pop(0) # This removes the header and returns the header.

    if debug == True:
        print( len( untranslatedEntriesColumnFull ) )
        # Debug code.
        for counter,untranslatedString in enumerate( untranslatedEntriesColumnFull ):
            assert( untranslatedString == programSettings[ 'mainSpreadsheet' ].getCellValue( 'A' + str( counter + 2 ) ) )

        currentRow=2 
        for listCounter,untranslatedString in enumerate( untranslatedEntriesColumnFull ):
            try:
                assert( untranslatedString == programSettings[ 'mainSpreadsheet' ].getCellValue( 'A' + str( currentRow )) )
            except:
                print( 'Mismatch:')
                print( ( 'untranslatedString=' + str( untranslatedString ) ).encode( consoleEncoding ) )
                print( ( 'mainSpreadsheet.getCellValue( A' + str( currentRow ) + ' )=' + mainSpreadsheet.getCellValue( 'A' + str( currentRow ) ) ).encode(consoleEncoding) )
                raise
            currentRow += 1

    # Debug code.
    #batchModeEnabled=False



    if batchModeEnabled == True:

        # Moved.
        #if userInput[ 'batchSize' ] > userInput[ 'summarySize' ]:
        #    userInput[ 'batchSize' ] = userInput[ 'summarySize' ]
        #elif userInput[ 'summarySize' ] > userInput[ 'batchSize' ]:
        #    userInput[ 'summarySize' ] = userInput[ 'batchSize' ]
        if userInput[ 'sceneSummaryEnabled' ] == True:
            assert( userInput[ 'batchSize' ] == userInput[ 'summarySize' ] )

        # range( start, stop, stepAmount ):
        #for i in range(0, len(untranslatedList), maxBatchSize ):
        #    translateBatchFunction( untranslatedList[ i : i + maxBatchSize ]  )
        #    print( untranslatedList[ i : i + maxBatchSize ]  )

        for i in range( 0, len( programSettings[ 'untranslatedEntriesColumnFull' ] ), userInput[ 'maxBatchSize'] ):
            if userInput[ 'sceneSummaryEnabled' ] != None:
                # This either returns none or a string.
                sceneSummary = getSceneSummary( userInput=userInput, programSettings=programSettings, untranslatedList=untranslatedList[ i : i + maxBatchSize ] )
            else:
                sceneSummary=None

            if ( sceneSummaryEnabled == False ) or ( ( sceneSummaryEnabled == True ) and ( sceneSummaryEnableTranslation == True ):
                translatedList = batchTranslate( userInput=userInput, programSettings=programSettings, untranslatedList=untranslatedList[ i : i + maxBatchSize ], sceneSummary=sceneSummary )


                # Always replacing the target column is only valid for batchMode == True and also if overrideWithCache == True. Otherwise, any entries that have already been translated, should not be overriden and batch replacements are impossible since each individual entry needs to be processed for non-batch modes.
                if overrideWithCache == True:
                    translatedList.insert( 0, translationEngine.model ) # Put header back. This returns None.
                    programSettings[ 'mainSpreadsheet' ].replaceColumn( programSettings[ 'currentMainSpreadsheetColumn' ] , translatedList ) # Batch replace the entire column.
                #if overrideWithCache != True:
                else:
                    # Consider each entry individually.

                    #print('pie pie')
                    #print('len(untranslatedList)=',len(untranslatedList) )
                    #print('reTranslate=',reTranslate)


                    for listCounter,untranslatedString in enumerate( untranslatedList ):
                        # Searching might be pointless here because the entries should be ordered. It should be possible to simply increment both untranslatedList and translatedList with the same counter.
                        #tempSearchResult = programSettings[ 'cache' ].searchCache( untranslatedString )
                        assert( untranslatedString == mainSpreadsheet.getCellValue( 'A' + str( programSettings[ 'currentRow' ] ) ) )

                        currentTranslatedCellAddress= programSettings[ 'currentMainSpreadsheetColumn' ] + str( programSettings[ 'currentRow' ] )

                        # Check with postDictionary, a Python dictionary for possible updates.
            #            if postDictionary != None:
            #                for key,items in postDictionary.items():
            #                    if translatedList[listCounter].find( key ) != -1:
            #                        translatedList[listCounter]=translatedList[listCounter].replace( key, item )

                        #print( currentTranslatedCellAddress, end='' )
                        # Check if the entry is current None. if entry is none
                        if ( programSettings[ 'mainSpreadsheet' ].getCellValue( currentTranslatedCellAddress ) == None ) or ( userInput[ 'reTranslate' ] == True ):
                            # then always update the entry.
                            programSettings[ 'mainSpreadsheet' ].setCellValue( currentTranslatedCellAddress, translatedList[ listCounter ] )
                            #print( ( 'updated ' + currentTranslatedCellAddress + ' with: ' + translatedList[ listCounter ] ).encode( consoleEncoding ) )
                        # if entry is not none
                        #else:
                            # then do not override entry. Do nothing here. If it was appropriate to override the entry, then overrideWithCache== True and this code would never execute since it would have all been done already.
                            # reTraslate could still be True, but in that case update 
                        programSettings[ 'currentRow' ] += 1

                #backupMainSpreadsheet( userInput=userInput, outputName=backupsFilePathWithNameAndDate, force=True )






        # if there is a limit to how large a batch can be, then the server should handle that internally.
        # Update: Technically yes, but it could also make sense to limit batch sizes on the application side, like if translating tens of thousands of lines or more, so there should also be a batchSize UI element in addition to any internal engine batch size limitations. Implemented as batchSizeLimit , now just need to implement the batch limiting code.
        #currentMainSpreadsheetColumn

    #elif batchModeEnabled == False:
    else:
        translate( userInput=userInput, programSettings=programSettings, untranslatedList=untranslatedEntriesColumnFull, summary=None)


    if debug == True:
        print( 'mainSpreadsheet.printAllTheThings():' )
        programSettings[ 'mainSpreadsheet' ].printAllTheThings()

    if userInput[ 'testRun' ] != True:
        programSettings[ 'mainSpreadsheet' ].export( userInput[ 'outputFileName' ], fileEncoding=userInput[ 'outputFileEncoding' ], columnToExportForTextFiles=currentMainSpreadsheetColumn )

    # https://openpyxl.readthedocs.io/en/stable/optimized.html
    # readOnlyMode requires manually closing the spreadsheet after use.
    if userInput[ 'cacheEnabled' ] == True:
        if userInput[ 'readOnlyCache' ] == True:
            programSettings[ 'cache' ].close()
        # There is a bug where cacheWasUpdated is getting set to True even if it is never updated sometimes.
        elif programSettings[ 'cacheWasUpdated' ] == True:
            backupCache( userInput=userInput, programSettings=programSettings, force=True )


if __name__ == '__main__':
    main()
    print( 'end reached' )
    sys.exit(0)

