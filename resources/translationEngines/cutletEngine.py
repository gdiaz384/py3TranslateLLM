#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: These plugins define various translation engines to use when translating text. The idea is to expose a semi-uniform interface. These plugins assume the data will be input as either a single string or as a batch. Batches are a single Python list where each entry is a string.

This plugin requires the cutlet library.
The cutlet library requires and uses the fugashi library as an MeCab wrapper for unidic.
"MeCab is an open-source text segmentation library for Japanese written text." -Wiki
Unidic is some sort of big dictionary supported by NINJAL: https://clrd.ninjal.ac.jp/unidic/about_unidic.html
UniDicとは、国立国語研究所の規定した斉一（せいいつ）な言語単位（短単位）と、 階層的見出し構造に基づく電子化辞書の 
Translation: "UniDic is a uniform language unit (short unit) defined by the National Institute for Japanese Language and Linguistics, and an electronic dictionary based on a hierarchical heading structure."
What does that even mean?

Recommended - Full install - Unidic 3.1.0 - ~750 MB:
python -m pip install cutlet fugashi unidic
python -m unidic download

Not recommended - Minimalistic install - Unidic 2.1.2 - ~250 MB:
python -m pip install cutlet fugashi[unidic-lite] unidic-lite

The point of MeCab + Unidic is accuracy. If accuracy is not important, then use pykakasi instead. Pykakasi makes the Minimalistic install of the older and smaller Unidic version self-contradictory because pykakasi is much faster and smaller while still being reasonably accurate relative to its size and speed.

Usage: See below. Like at the bottom.
PyPi:
https://pypi.org/project/cutlet/
https://pypi.org/project/fugashi/
https://pypi.org/project/unidic/
https://pypi.org/project/unidic-lite/

Source code:
https://github.com/polm/cutlet
https://github.com/polm/fugashi
https://github.com/polm/unidic-py
https://github.com/polm/unidic-lite

Licenses:
This plugin is copyright (c) 2024 gdiaz384; License: GNU AGPLv3.
This plugin uses the cutlet library that requires the fugashi library for MeCab and then either the unidic library or unidic-lite library. These libraries are all subject to their own licenses.
Cutlet - MIT: https://github.com/polm/cutlet/blob/master/LICENSE
Fugashi - MIT: https://github.com/polm/fugashi/blob/master/LICENSE
"fugashi is a wrapper for MeCab, and fugashi wheels include MeCab binaries. MeCab is copyrighted free software by Taku Kudo <taku@chasen.org> and Nippon Telegraph and Telephone Corporation, and is redistributed under the BSD License."
MeCab - BSD: https://github.com/polm/fugashi/blob/master/LICENSE.mecab
Unidic-py - MIT/WTFPL - https://github.com/polm/unidic-py/blob/master/LICENSE
UniDic 3.1.0 - BSD/LGPL/GPL - "The modern Japanese UniDic is available under the GPL, LGPL, or BSD license, see here. UniDic is developed by NINJAL, the National Institute for Japanese Language and Linguistics. UniDic is copyrighted by the UniDic Consortium and is distributed here under the terms of the BSD License."
https://github.com/polm/unidic-py/blob/master/LICENSE.unidic
UniDic-lite - MIT/WTFPL - https://github.com/polm/unidic-lite/blob/master/LICENSE
"Unidic 2.1.2 is copyright the UniDic Consortium and distributed under the terms of the BSD license."
UniDic 2.1.2 - BSD - https://github.com/polm/unidic-lite/blob/master/LICENSE.unidic
"""
__version__ = '2024.08.13'

#set defaults
#printStuff = True
verbose = False
debug = False
consoleEncoding = 'utf-8'

validPykakasiRomajiFormats = [ 'hepburn', 'kunrei', 'passport', 'hira', 'kana' ]
validCutletRomajiFormats = [ 'hepburn', 'kunrei', 'nihon' ]

# romajiFormat can be 'hepburn', 'kunrei', 'passport' # Technically, 'hira' and 'kana' are valid as well for pykakasi
defaultRomajiFormat = 'hepburn'
punctuationList = [ '。', '「', '」', '、', '…', '？', '♪']

import sys


class CutletEngine:
    # Insert any custom code to pre process the untranslated text here. This is very dataset specific.
    # https://www.w3schools.com/python/python_strings_methods.asp
    def preProcessText( self, untranslatedText ):
        #return untranslatedText

        untranslatedText=untranslatedText.strip()               # Remove any whitespaces along the edges.
        if untranslatedText.find( r'\n' ) != -1:
            untranslatedText=untranslatedText.replace( r'\n',' ' ).strip() # if there are any hardcoded new lines, replace them with a single empty space.

        if untranslatedText.find( '\n' ) != -1:
            untranslatedText=untranslatedText.replace( '\n',' ' ).strip() # Remove new lines and replace them with a single empty space.

        if untranslatedText.find( '  ' ) != -1:
            untranslatedText=untranslatedText.replace( '  ',' ' ).replace( '  ', ' ' )  # In the middle, replace any two blank spaces with a single blank space.

        if self.characterDictionary != None:
            for key,value in self.characterDictionary.items():
                if untranslatedText.find( key ) != -1:
                    untranslatedText = untranslatedText.replace( key, value )

        return untranslatedText


    # Insert any custom code to post process the output text here. This is very dataset specific.
    def postProcessText( self, rawTranslatedText, untranslatedText, speakerName=None ):
        rawTranslatedText = rawTranslatedText.strip()

        if rawTranslatedText.find( '  ' ) != -1:
            rawTranslatedText=rawTranslatedText.replace( '  ',' ' ).replace( '  ', ' ' )  # In the middle, replace any two blank spaces with a single blank space.

        # Dataset specific fixes go here.

        return rawTranslatedText

        # Old code.
        if rawTranslatedText.find( '( ' ) != -1:
           rawTranslatedText=rawTranslatedText.replace( '( ', '「' )
        if rawTranslatedText.find( '(' ) != -1:
           rawTranslatedText=rawTranslatedText.replace( '(', '「' )

        if rawTranslatedText.find( ' )' ) != -1:
           rawTranslatedText=rawTranslatedText.replace( ' )', '」' )
        if rawTranslatedText.find( ')' ) != -1:
           rawTranslatedText=rawTranslatedText.replace( ')', '」' )

        return rawTranslatedText


    # sourceLanguage and targetLanguage are lists that have the full language, the two letter language codes, the three letter language codes, and some meta information useful for other translation engines.
    def __init__( self, sourceLanguage=None, targetLanguage=None, characterDictionary=None, settings={} ): 

        # Set generic API static values for this engine.
        self.supportsBatches = True
        self.supportsHistory = False
        self.requiresPrompt = False
        self.promptOptional = False
        self.supportsCreatingSummary = False

        # Set generic API variables for this engine.
        self.model = None
        self.version = None

        # Process generic input.
        self.characterDictionary = characterDictionary
        self.sourceLanguage = sourceLanguage
        self.targetLanguage = targetLanguage

        # Debug code.
        if debug == True:
            print( ( 'settings=' + str( settings ) ).encode( consoleEncoding ) )

        # romajiFormat can be
        # validCutletRomajiFormats = [ 'hepburn', 'kunrei', 'nihon' ]
        self.romajiFormat = None
        if 'romajiFormat' in settings:
            if settings[ 'romajiFormat' ] != None:
                if not settings[ 'romajiFormat' ].lower() in validCutletRomajiFormats:
                    print( ( 'Warning: romajiFormat \'' + settings[ 'romajiFormat' ].lower() + '\' is not valid with Cutlet library. Using default value \''+ defaultRomajiFormat +'\' instead.' ).encode( consoleEncoding ) )
                else:
                    self.romajiFormat = settings[ 'romajiFormat' ].lower()
        if self.romajiFormat == None:
            self.romajiFormat = defaultRomajiFormat

        # Process engine specific input and associated variables.
        self.reachable = False
        # Some sort of test to check if the server is reachable goes here. Maybe just try to get model/version and if they are returned, then the server is declared reachable?

        # Model is what determines the translation quality.
        # Version is the version information for the current engine.
        self.model = None
        self.version = None
        print( 'Importing cutlet... ', end='' )
        try:
            import cutlet
            try:
                from importlib import metadata as importlib_metadata
            except ImportError:
                import importlib_metadata
            self.version = importlib_metadata.distribution( 'cutlet' ).version
            try: 
                import unidic
            except ImportError:
                import unidic_lite as unidic
            self.model = 'cutlet/' + unidic.VERSION + '/' + self.romajiFormat # cutlet/unidic-3.1.0+2021-08-31/hepburn, cutlet/2.1.2/kunrei
            self.converter = cutlet.Cutlet( self.romajiFormat )
            print( 'Success.')
            if 'use_foreign_spelling' in settings:
                if isinstance( settings[ 'use_foreign_spelling' ], bool ):
                    self.converter.use_foreign_spelling = settings[ 'use_foreign_spelling' ]
                    print( 'self.converter.use_foreign_spelling=', self.converter.use_foreign_spelling )

        #except requests.exceptions.ConnectTimeout:
        except ImportError:
            print( 'Failure.')
            print( 'Unable to import cutlet. Please install it with \n \'pip install cutlet fugashi unidic\' \n \'python -m unidic download\' \nand try again.' )

        if self.model != None:
            self.reachable = True


    # This expects a python list where every entry is a string.
    def batchTranslate( self, untranslatedList, settings=None ):
        #debug=True
        if debug == True:
            print( 'len(untranslatedList)=' , len( untranslatedList ) )
            print( ( 'untranslatedList=' + str( untranslatedList ) ).encode( consoleEncoding ) )

        translatedList = []
        for entry in untranslatedList:
            # Lazy.
            translatedList.append( self.translate( entry ) )

        try:
            assert( len( untranslatedList ) == len( translatedList ) )
        except:
            print( 'Warning: Library did not return same about entries sent to it. Returning None.' )
            print( 'len( untranslatedList )=' + str( len( untranslatedList ) ) )
            print( 'len( translatedList )=' + str( len( translatedList ) ) )
            return None

        if debug == True:
            print( 'len(translatedList)=' , len( translatedList ) )
            print( ( 'translatedList=' + str( translatedList ) ).encode( consoleEncoding ) )

        return translatedList


    # This expects a string to translate.
    def translate( self, untranslatedString, settings=None ):
        assert( isinstance( untranslatedString, str ) )

        untranslatedStringAfterPreProcessing = self.preProcessText(untranslatedString)

        translatedString = self.converter.romaji( untranslatedStringAfterPreProcessing )
 
        return self.postProcessText( translatedString, untranslatedString )


"""
TODO: Integrate this code above.
if ( userInput[ 'mode' ] == 'pykakasi' ) and ( userInput[ 'romajiFormat' ] != None ):
    userInput[ 'romajiFormat' ] = userInput[ 'romajiFormat' ].lower()

    if userInput[ 'romajiFormat' ] in validPykakasiRomajiFormats:
        pass
    else:
        print( ( 'Warning: romajiFormat \'' + userInput[ 'romajiFormat' ] + '\' is not valid with pykakasi. Reverting to default.' ).encode(consoleEncoding) )
        userInput[ 'romajiFormat' ] = None


if ( userInput[ 'mode' ] == 'cutlet' ) and ( userInput[ 'romajiFormat' ] != None ):
    userInput[ 'romajiFormat' ] = userInput[ 'romajiFormat' ].lower()
    if userInput[ 'romajiFormat' ] in validCutletRomajiFormats:
        pass
    else:
        print( ( 'Warning: romajiFormat \'' + userInput[ 'romajiFormat' ] + '\' is not valid with cutlet. Reverting to default.' ).encode(consoleEncoding) )
        userInput[ 'romajiFormat' ] = None
    if userInput[ 'romajiFormat' ] == 'kunreisiki':
        userInput[ 'romajiFormat' ] = 'kunrei'
    elif userInput[ 'romajiFormat' ] == 'nihonsiki':
        userInput[ 'romajiFormat' ] = 'nihon'

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
