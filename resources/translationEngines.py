#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: This library defines various translation engines to use when translating text. The idea is to expose a semi-uniform interface. These libraries assume the data will be input as either a single string or as a batch. Batches are a single Python list where each entry is a string.

Update: It might be better to create a subfolder called translationEngines and then split each engine into its own file. Then it would be imported as:
import resources.translationEngines.py3translationServerEngine as py3translationServerEngine

Usage: See below. Like at the bottom.

License: See main program.

"""
__version__='2024.03.28'

#set defaults
#printStuff=True
verbose=False
debug=False
consoleEncoding='utf-8'

import requests

#wrapper class for spreadsheet data structure
class Py3translationServerEngine:
    # Address is the protocol and the ip address or hostname of the target server.
    # sourceLanguage and targetLanguage are lists that have the full language, the two letter language codes, the three letter language codes, and some meta information useful for other translation engines.
    def __init__(self, sourceLanguage=None, targetLanguage=None, address=None, port=None,timeout=120): 
        self.sourceLanguage=sourceLanguage
        self.targetLanguage=targetLanguage
        self.supportsBatches=True
        self.supportsHistory=False
        self.timeout=timeout
        self.requiresPrompt=False
        self.address=address
        self.port=port

        self.addressFull=self.address + ':' + str(self.port)

        self.reachable=False
        #Some sort of test to check if the server is reachable goes here. Maybe just try to get model/version and if they are turned, the server is declared reachable?

        self.model=None
        self.version=None
        print( 'Connecting to py3translationServer at ' + self.addressFull + ' ...' )
        if (self.address != None) and (self.port != None):
            try:
                self.model = requests.get( self.addressFull + '/api/v1/model', timeout=10 ).text
                self.version = requests.get( self.addressFull + '/api/v1/version', timeout=10 ).text
            except requests.exceptions.ConnectTimeout:
                print( 'Unable to connect to py3translationServer. Please check the connection settings and try again.' )

        if self.model != None:
            self.reachable=True


    # This expects a python list where every entry is.
    def batchTranslate(self, untranslatedList):
        #debug=True
        if debug == True:
            print( 'len(untranslatedList)=' , len(untranslatedList) )
            print( ( 'untranslatedList=' + str(untranslatedList) ).encode(consoleEncoding) )

        # https://docs.python-requests.org/en/latest/user/advanced/#timeouts
        translatedList = requests.post( self.addressFull, json = dict ([ ('content' , untranslatedList ), ('message' , 'translate sentences') ]) , timeout=(10, self.timeout) ).json()

        # strip whitespace
        for counter,translatedList enumerate(translatedList):
            translatedList[counter]=str(translatedList[counter]).strip()

        if debug == True:
            print( ( 'translatedList=' + str(translatedList) ).encode(consoleEncoding) )

        # print(len(untranslatedList))
        # print(len(translatedList))
        assert( len(translatedList) == len(untranslatedList) )

        return translatedList


    # This expects a string to translate.
    def translate(self, untranslatedString):
        return str( self.batchTranslate( [untranslatedString] ) ) # Lazy.


class SugoiNMTEngine:
    # Address is the protocol and the ip address or hostname of the target server.
    # sourceLanguage and targetLanguage are lists that have the full language, the two letter language codes, the three letter language codes, and some meta information useful for other translation engines.
    def __init__(self, sourceLanguage=None, targetLanguage=None, address=None, port=None): 
        self.sourceLanguage=sourceLanguage
        self.targetLanguage=targetLanguage
        self.supportsBatches=True
        self.supportsHistory=False
        self.supportsPrompt=False
        self.requiresPrompt=False
        self.address=address
        self.port=port

        self.model=None
        self.version=None
        if (self.address != None) and (self.port != None):
            try:
                self.model= requests.get(self.address + ':' + self.port + '/api/v1/model',timeout=10)
                self.version= requests.get(self.address + ':' + self.port + '/api/v1/version',timeout=10)
            except:
                pass




"""
Usage and concept art:


import translationEngines

translationEngine=translationEngines.KoboldCppEngine( sourceLanguage, targetLanguage, address, port, prompt )
translationEngine=translationEngines.DeepLAPIFreeEngine( sourceLanguage, targetLanguage, APIKey, deeplDictionary )
translationEngine=translationEngines.DeepLAPIProEngine( sourceLanguage, targetLanguage, APIKey, deeplDictionary )
translationEngine=translationEngines.DeepLWebEngine( sourceLanguage, targetLanguage )
translationEngine=translationEngines.SugoiNMTEngine( sourceLanguage, targetLanguage, address, port )
translationEngine=translationEngines.Py3translationServerEngine( sourceLanguage, targetLanguage, address, port )

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
