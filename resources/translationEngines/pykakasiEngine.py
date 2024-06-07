#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: These plugins define various translation engines to use when translating text. The idea is to expose a semi-uniform interface. These plugins assume the data will be input as either a single string or as a batch. Batches are a single Python list where each entry is a string. This plugin requires the pykakasi library. Install using `pip install pykakasi`.

"If you need to get a correctness of sentence recognition in Japanese, you are recommended to see modern NLP libraries rather than pykakasi.
PyKakasi is designed to be light weight, simple, stupid and low footprint. It does not run actual modern morphological analysis, 形態素解析, but just use vocabulary match with longest-match algorithm." -miurahr https://codeberg.org/miurahr/pykakasi/issues/153

"No kakasi use very simpler algorythm [for tokenization] than MeCab, it can be incorrect.
When you need a better quality, please choice MeCab or other modern tokenizer. When you need light weight and speed or portability but correctness is second, pykakasi is for you." -miurahr https://codeberg.org/miurahr/pykakasi/issues/157

https://pykakasi.readthedocs.io/en/latest/api.html
Despite the 'old' 1.2 API being depreciated in pykakasi 2.1, the 'new' API just does not work right. It consistently messes up punctuation and trunkates the output after the first word making it completely unusable. Always use the old API.
Also note that roman->hira/kana conversions are not supported.

Usage: See below. Like at the bottom.

Copyright (c) 2024 gdiaz384; License: GNU AGPLv3.
This plugin uses the pykakasi library that is copyright (C) 2010-2024 by Hiroshi Miura and contributors.
pykakasi is licensed as GNU GPLv3: https://codeberg.org/miurahr/pykakasi/src/branch/master/COPYING
See the source code for additional details: https://codeberg.org/miurahr/pykakasi
"""
__version__='2024.05.23'

#set defaults
#printStuff=True
verbose=False
debug=False
consoleEncoding='utf-8'

# romajiFormat can be 'hepburn', 'kunrei', 'passport' # Technically, 'hira' and 'kana' are valid as well.
defaultRomajiFormat='hepburn'
punctuationList=[ '。', '「', '」', '、', '…', '？', '♪']

import sys


class PyKakasiEngine:
    # Insert any custom code to pre process the untranslated text here. This is very dataset specific.
    # https://www.w3schools.com/python/python_strings_methods.asp
    def preProcessText(self, untranslatedText):
        #return untranslatedText

        untranslatedText=untranslatedText.strip()               # Remove any whitespaces along the edges.
        if untranslatedText.find( r'\n' ) != -1:
            untranslatedText=untranslatedText.replace( r'\n',' ' ).strip() # if there are any hardcoded new lines, replace them with a single empty space.

        if untranslatedText.find( '\n' ) != -1:
            untranslatedText=untranslatedText.replace( '\n',' ' ).strip() # Remove new lines and replace them with a single empty space.

        if untranslatedText.find( '  ' ) != -1:
            untranslatedText=untranslatedText.replace( '  ',' ' ).replace( '  ', ' ' )  # In the middle, replace any two blank spaces with a single blank space.

        # Workaround for bug not marked as fixed: https://codeberg.org/miurahr/pykakasi/issues/161
        if untranslatedText.find('·') != -1:
            untranslatedText=untranslatedText.replace( '·', '・' )

        # This workaround should only needed for the new API. The old one works fine.
#        for punctuationMark in punctuationList:
#            if untranslatedText.find(punctuationMark) != -1:
#                untranslatedText=untranslatedText.replace( punctuationMark, '' )

        # This is only used for the old API. The new one always messes up the names no matter what and they need to be fixed in post processing.
        if self.characterDictionary != None:
            for key,value in self.characterDictionary.items():
                if untranslatedText.find( key ) != -1:
                    untranslatedText = untranslatedText.replace( key, value )

        return untranslatedText


    # Insert any custom code to post process the output text here. This is very dataset specific.
    def postProcessText(self, rawTranslatedText, untranslatedText, speakerName=None):

        rawTranslatedText=rawTranslatedText.strip()
        if rawTranslatedText.find( '  ' ) != -1:
            rawTranslatedText=rawTranslatedText.replace( '  ',' ' ).replace( '  ', ' ' )  # In the middle, replace any two blank spaces with a single blank space.

        # Dataset specific fixes go here.
        # This is only used for the new API. The old API can be told not to break things and behave itself.
#        if self.characterDictionaryRomajiToTargetLanguage != None:
#            for key,value in self.characterDictionaryRomajiToTargetLanguage.items():
#                if rawTranslatedText.find( key ) != -1:
#                    rawTranslatedText = rawTranslatedText.replace( key, value )

        if rawTranslatedText.find( '( ' ) != -1:
           rawTranslatedText=rawTranslatedText.replace( '( ', '「' )
        if rawTranslatedText.find( '(' ) != -1:
           rawTranslatedText=rawTranslatedText.replace( '(', '「' )

        if rawTranslatedText.find( ' )' ) != -1:
           rawTranslatedText=rawTranslatedText.replace( ' )', '」' )
        if rawTranslatedText.find( ')' ) != -1:
           rawTranslatedText=rawTranslatedText.replace( ')', '」' )

        return rawTranslatedText


    # Address is the protocol and the ip address or hostname of the target server.
    # sourceLanguage and targetLanguage are lists that have the full language, the two letter language codes, the three letter language codes, and some meta information useful for other translation engines.
    def __init__( self, sourceLanguage=None, targetLanguage=None, characterDictionary=None, settings={} ): 

        # Set generic API static values for this engine.
        self.supportsBatches=True
        self.supportsHistory=False
        self.requiresPrompt=False

        # Set generic API variables for this engine.
        self.model=None
        self.version=None

        # Process generic input.
        self.characterDictionary=characterDictionary
        self.sourceLanguage=sourceLanguage
        self.targetLanguage=targetLanguage

        # Debug code.
        #print('settings=' + str(settings) )
        #sys.exit(0)

        # romajiFormat can be 'hepburn', 'kunrei', 'passport'
        if 'romajiFormat' in settings:
            if settings['romajiFormat'] != None:
                self.romajiFormat=settings['romajiFormat'].lower()
            else:
                self.romajiFormat=defaultRomajiFormat
        else:
            self.romajiFormat=defaultRomajiFormat

        # Process engine specific input and associated variables.
        self.reachable=False
        # Some sort of test to check if the server is reachable goes here. Maybe just try to get model/version and if they are returned, then the server is declared reachable?

        self.model=None
        self.version=None
        print( 'Importing pykakasi... ', end='')
        try:
            import pykakasi
            try:
                from importlib import metadata as importlib_metadata
            except ImportError:
                import importlib_metadata
            self.version = importlib_metadata.distribution('pykakasi').version
            self.model='pykakasi/' + str(self.version) + '/' + self.romajiFormat # pykakasi/2.2.1/hepburn, pykakasi/2.2.1/kunrei
            self.kakasi=pykakasi.kakasi()
            print( 'Success.')

            if (self.romajiFormat == 'hepburn') or (self.romajiFormat == 'kunrei') or (self.romajiFormat == 'passport'):
                # Developer hard coded these for the old API, so have to match the case exactly.
                if self.romajiFormat == 'hepburn':
                    self.kakasi.setMode('r', 'Hepburn')
                elif self.romajiFormat == 'kunrei':
                    self.kakasi.setMode('r', 'Kunrei')
                elif self.romajiFormat == 'passport':
                    self.kakasi.setMode('r', 'Passport')

                # Convert all the things, but...
                self.kakasi.setMode('H','a') # Hiragana.
                self.kakasi.setMode('K','a') # Katakana.
                self.kakasi.setMode('J','a') # Kanji.
                self.kakasi.setMode('E','a') # E is full length roman characters. This converts them back to half length. The developer calls this option 'kigou' which means 'symbol.'
                # ...leave well enough alone.
                self.kakasi.setMode('a',None)

            elif (self.romajiFormat == 'hira'):
                #print('pie')
                # Convert all the things, but...
                #self.kakasi.setMode('H',None) # Hiragana.
                self.kakasi.setMode('K','H') # Katakana.
                self.kakasi.setMode('J','H') # Kanji.
                self.kakasi.setMode('E','H') # E is full length roman characters. This converts them back to half length.
                self.kakasi.setMode('a','H') # Normal half-length roman characters.

            elif (self.romajiFormat == 'kana'):
                # Convert all the things, but...
                self.kakasi.setMode('H','K') # Hiragana.
                #self.kakasi.setMode('K',None) # Katakana.
                self.kakasi.setMode('J','K') # Kanji.
                self.kakasi.setMode('E','K') # E is full length roman characters. This converts them back to half length.
                self.kakasi.setMode('a','K') # Normal half-length roman characters.

            # Add spaces to output.
            self.kakasi.setMode('s',True)

        #except requests.exceptions.ConnectTimeout:
        except ImportError:
            print( 'Failure.')
            print( 'Unable to import py3kakasi. Please install it with \'pip install py3kakasi\' and try again.' )

        if self.model != None:
            self.reachable=True

        # self.characterDictionary uses japanese (Kanji) -> target language conversion, not necessarily romaji names.
        # Since Kanji-> target language has multiple mappings and converting verbatim to romaji will always mess up, especially the capitalization, using manual mapping for characterNames is best for quality.
        # Going further, the target language mapping should be used instead of raw romaji in the output because that is the implied user's intent by including a character dictionary in the first place.
        # However submitting the post-translated name will make pykakashi just ignore it in the output which causes the output to be incorrect. Therefore, submit each name to pykakashi to get the 'incorrect' mapping which can be used to revert that incorrect mapping to the correct name specified by the user.
        self.characterDictionaryRomajiToTargetLanguage=None
        if self.characterDictionary != None:
            self.characterDictionaryRomajiToTargetLanguage={}
            for key,value in characterDictionary.items():
                tempResult=self.kakasi.convert( key )[0][self.romajiFormat]
                self.characterDictionaryRomajiToTargetLanguage[tempResult] = value


    # This expects a python list where every entry is a string.
    def batchTranslate(self, untranslatedList):
        #debug=True
        if debug == True:
            print( 'len(untranslatedList)=' , len(untranslatedList) )
            print( ( 'untranslatedList=' + str(untranslatedList) ).encode(consoleEncoding) )

        translatedList = []
        for entry in untranslatedList:
            translatedList.append( self.translate(entry) )

        # print(len(untranslatedList))
        # print(len(translatedList))
        assert( len(untranslatedList) == len(translatedList) )

        if debug == True:
            print( ( 'translatedList=' + str(translatedList) ).encode(consoleEncoding) )

        return translatedList


    # This expects a string to translate.
    def translate(self, untranslatedString, speakerName=None, contextHistory=None):
        #assert string

        untranslatedStringAfterPreProcessing=self.preProcessText(untranslatedString)

        # New API. Very broken.
        #translatedString=self.kakasi.convert(untranslatedStringAfterPreProcessing)[0][self.romajiFormat]

        # Old API. Works.
        translatedString=self.kakasi.getConverter().do(untranslatedStringAfterPreProcessing)

        return self.postProcessText(translatedString, untranslatedString, speakerName)


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
