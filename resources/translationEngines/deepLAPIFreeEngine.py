#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: This library defines various translation engines to use when translating text. The idea is to expose a semi-uniform interface. These libraries assume the data will be input as either a single string or as a batch. Batches are a single Python list where each entry is a string. This library requires the requests library. Install using `pip install requests`.

Usage: See below. Like at the bottom.

Copyright (c) 2024 gdiaz384; License: See main program.

"""
__version__ = '2024.07.14'

#set defaults
#printStuff = True
verbose = False
debug = False
consoleEncoding = 'utf-8'
defaultTimeout = 360

import sys
import requests
# Library must be available.
try:
    import deepl
except:
    print( 'DeepL\'s python library is not available. Please install using: pip install deepl' )
    sys.exit( 1 )

# Environmental variable syntax:
# os.environ[ 'CT2_VERBOSE' ] = '1'


class DeepLApiFreeEngine:
    # Insert any custom code to pre process the untranslated text here. This is very model, prompt, and dataset specific.
    # https://www.w3schools.com/python/python_strings_methods.asp
    def preProcessText(self, untranslatedText):
        #return untranslatedText

        untranslatedText = untranslatedText.strip()               # Remove any whitespaces along the edges.
        if untranslatedText.find( r'\n' ) != -1:
            untranslatedText = untranslatedText.replace( r'\n',' ' ).strip() # if there are any hardcoded new lines, replace them with a single empty space.
        if untranslatedText.find( '\n' ) != -1:
            untranslatedText = untranslatedText.replace( '\n',' ' ).strip() # Remove new lines and replace them with a single empty space.
        if untranslatedText.find( '  ' ) != -1:
            untranslatedText = untranslatedText.replace( '  ',' ' ).replace( '  ', ' ' )  # In the middle, replace any two blank spaces with a single blank space.

        return untranslatedText


    # Insert any custom code to post process the output text here. This is very model and prompt specific.
    def postProcessText( self, rawTranslatedText, untranslatedText, speakerName=None ):
        rawTranslatedText = rawTranslatedText.strip()

        # if the translation has new lines, then truncate the result.
#        if rawTranslatedText.find( '\n' ) != -1:
#            rawTranslatedText = rawTranslatedText.partition( '\n' )[ 0 ].strip()
        if rawTranslatedText.find( '<unk>' ) != -1:
            rawTranslatedText = rawTranslatedText.replace( '<unk>', '' ).strip()
        if rawTranslatedText.find( '  ' ) != -1: # Two blank spaces.
            rawTranslatedText = rawTranslatedText.replace( '  ',' ' ).replace( '  ', ' ' )  # In the middle, replace any two blank spaces with a single blank space.

        # Dataset specific fixes go here.

        return rawTranslatedText


    # Address is the protocol and the ip address or hostname of the target server.
    # sourceLanguage and targetLanguage are lists that have the full language, the two letter language codes, the three letter language codes, and some meta information useful for other translation engines.
    def __init__( self, sourceLanguage=None, targetLanguage=None, characterDictionary=None, settings={} ): 

        # Set generic API static values for this engine.
        self.supportsBatches = True
        self.supportsHistory = False
        self.requiresPrompt = False
        self.promptOptional = True
        self.supportsCreatingSummary = False

        # Set generic API variables for this engine.
        self.model = None
        self.version = None

        # Process generic input.
        self.characterDictionary = characterDictionary
        self.sourceLanguageList = sourceLanguage
        # if DifferentSourceLanguage == True, then use the alternative name.
        if self.sourceLanguageList[ 4 ] == True:
            self.sourceLanguage = self.sourceLanguageList[ 5 ]
        else:
            self.sourceLanguage = self.sourceLanguageList[ 0 ]

        self.targetLanguageList = targetLanguage
        if self.targetLanguageList[ 4 ] == True:
            self.targetLanguage = self.targetLanguageList[ 5 ]
        else:
            self.targetLanguage = self.targetLanguageList[ 0 ]

        #debug=True
        if debug == True:
            print( str( settings ).encode( consoleEncoding ) )
            print( self.sourceLanguage )
            print( self.targetLanguageList )
            print( self.targetLanguage )

        # Process engine specific input and associated variables.
        if 'timeout' in settings:
            self.timeout = settings[ 'timeout' ]
        else:
            self.timeout = defaultTimeout
        # Probe for where the API key is here.

        self.reachable = False
        # Do some sort of test to check if the server is reachable.

        self.model = None
        self.version = None
        print( 'Connecting to DeepL API (Free)... ', end='')
        try:
            # stuff goes here
            pass
            # Set self.model and self.version to something.
            print( 'Success.' )
        except:
            print( 'Failure.' )
            print( 'Unable to connect to py3translationServer. Please check the connection settings and try again.' )

        if self.model != None:
            self.reachable = True


    # This expects a python list where every entry is a string.
    def batchTranslate( self, untranslatedList, settings=None ):
        #debug = True
        if debug == True:
            print( 'len( untranslatedList )=' , len( untranslatedList ) )
            print( ( 'untranslatedList=' + str( untranslatedList ) ).encode( consoleEncoding ) )

        # Preprocess text.
        for counter,entry in enumerate( untranslatedList ):
            #print( str( entry ).encode( consoleEncoding ) )
            untranslatedList[ counter ] = self.preProcessText( entry )

        # Translate the list.
        translatedList = []

        if debug == True:
            print( ( 'translatedListBeforePostProcessing=' + str( translatedList ) ).encode( consoleEncoding ) )

        try:
            assert( len( untranslatedList ) == len( translatedList ) )
        except:
            print( 'Warning: Server did not return same about entries sent to it. Returning None.' )
            print( 'len( untranslatedList )=' + str( len( untranslatedList ) ) )
            print( 'len( translatedList )=' + str( len( translatedList ) ) )
            return None

        # Postprocess text.
        for counter,entry in enumerate( translatedList ):
            translatedList[ counter ] = self.postProcessText( entry, untranslatedList[ counter ] )

        if debug == True:
            print( ( 'translatedListAfterPostProcessing=' + str( translatedList ) ).encode( consoleEncoding ) )

        return translatedList


    # This expects a string to translate.
    def translate( self, untranslatedString, settings=None ):
        #assert type is a string

        return str( self.batchTranslate( [ untranslatedString ] )[ 0 ] ) # Lazy.



"""
Usage and concept art:
# TODO: This section.

import as:
import resources.translationEngines.py3translationServerEngine as py3translationServerEngine
invoke as:
translationEngine=py3translationServerEngine.Py3translationServerEngine(...)


import resources.translationEngines.py3translationServerEngine as py3translationServerEngine

translationEngine=translationEngines.KoboldCppEngine( sourceLanguage, targetLanguage, address, port, prompt )
translationEngine=translationEngines.DeepLAPIFreeEngine( sourceLanguage, targetLanguage, APIKey, deeplDictionary )
translationEngine=translationEngines.DeepLAPIProEngine( sourceLanguage, targetLanguage, APIKey, deeplDictionary )
translationEngine=translationEngines.DeepLWebEngine( sourceLanguage, targetLanguage )
translationEngine=translationEngines.SugoiNMTEngine( sourceLanguage, targetLanguage, address, port )
translationEngine=py3translationServerEngine.Py3translationServerEngine( sourceLanguage, targetLanguage, address, port )

translationEngine.supportsBatches
translationEngine.supportsHistory
translationEngine.supportsPrompt
translationEngine.requiresPrompt
translationEngine.model # For meta information, if model is available, use it, else use version, else just use raw translationEngine.
translationEngine.version
translationEngine.address
translationEngine.port
translationEngine.apiKey
translationEngine.translate(mystring)
translationEngine.translateBatch(myList)

batchesAreAvailable=translationEngine.supportsBatches
if batchesAreAvailable == True:
    # stuff here. Send to translation engine as a list.
else:
    # line by line only

"""
