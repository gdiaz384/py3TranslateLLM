#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: This library defines various translation engines to use when translating text. The idea is to expose a semi-uniform interface. These libraries assume the data will be input as either a single string or as a batch. Batches are a single Python list where each entry is a string.

Usage: See below. Like at the bottom.

Copyright (c) 2024 gdiaz384; License: See main program.

"""
__version__='2024.04.29'

#set defaults
#printStuff=True
verbose=False
debug=False
consoleEncoding='utf-8'

import requests

#wrapper class for spreadsheet data structure
class KoboldCppEngine:
    # Address is the protocol and the ip address or hostname of the target server.
    # sourceLanguage and targetLanguage are lists that have the full language, the two letter language codes, the three letter language codes, and some meta information useful for other translation engines.
    def __init__(self, sourceLanguage=None, targetLanguage=None, address=None, port=None, timeout=360, prompt=None): 
        self.sourceLanguage=sourceLanguage
        self.targetLanguage=targetLanguage
        self.supportsBatches=True
        self.supportsHistory=True
        self.timeout=timeout
        self.requiresPrompt=True
        self.address=address
        self.port=port
        self.addressFull=self.address + ':' + str(self.port)

        self.prompt=prompt
        self._maxContextLength=None

        if self.prompt == None:
            print( 'Warning: self.prompt is None.' )

        self.reachable=False
        # Some sort of test to check if the server is reachable goes here. Maybe just try to get model/version and if they are returned, then the server is declared reachable?

        self.model=None
        self.version=None
        print( 'Connecting to KoboldCpp API at ' + self.addressFull + ' ... ', end='')
        if (self.address != None) and (self.port != None):
            try:
                self.model = requests.get( self.addressFull + '/api/v1/model', timeout=10 ).json()['result']
                self.version = requests.get( self.addressFull + '/api/extra/version', timeout=10 ).json()
                self.version = self.version['result'] + '/' + self.version['version']
                self._maxContextLength=int(requests.get( self.addressFull + '/api/extra/true_max_context_length', timeout=10 ).json()['value'])
                print( 'Success.')
                print( ( 'koboldcpp version=' + self.version ).encode(consoleEncoding) )
                print( ( 'koboldcpp maxContextLength=' + str(self._maxContextLength) ).encode(consoleEncoding) )
            except requests.exceptions.ConnectTimeout:
            #except:
                print( 'Failure.')
                print( 'Unable to connect to KoboldCpp API. Please check the connection settings and try again.' )

        if self.model != None:
            self.reachable=True


    # This expects a python list where every entry is a string.
    def batchTranslate(self, untranslatedList):
        #debug=True
        if debug == True:
            print( 'len(untranslatedList)=' , len(untranslatedList) )
            print( ( 'untranslatedList=' + str(untranslatedList) ).encode(consoleEncoding) )

        # https://docs.python-requests.org/en/latest/user/advanced/#timeouts
        translatedList = requests.post( self.addressFull, json = dict ([ ('content' , untranslatedList ), ('message' , 'translate sentences') ]), timeout=(10, self.timeout) ).json()

        # strip whitespace
        for counter,entry in enumerate(translatedList):
            translatedList[counter]=entry.strip()

        if debug == True:
            print( ( 'translatedList=' + str(translatedList) ).encode(consoleEncoding) )

        # print(len(untranslatedList))
        # print(len(translatedList))
        assert( len(untranslatedList) == len(translatedList) )

        return translatedList

    
    # This expects a string to translate. contextHistory should be a list.
    def translate(self, untranslatedString, contextHistory=None):
        #http://localhost:5001/api
        #assert string
        #reqDict={'prompt':promptString+'How are you?'}
        #requests.post( 'http://192.168.1.100:5001/api/v1/generate',json=reqDict, timeout=120 ).json()
        #{'results': [{'text': '\n\nBien, gracias.'}]}

        # Build request.
        requestDictionary={}
        requestDictionary['prompt']=self.prompt+untranslatedString
        requestDictionary['max_context_length']=self._maxContextLength
        if contextHistory != None:
            tempHistory=''
            for entry in contextHistory:
                tempHistory=tempHistory + ' ' + entry
            requestDictionary['memory']=tempHistory[1:]
        #else:
        #requestDictionary['authorsnote']=

        # Maybe add some code here to deal with server busy messages?
        returnedRequest=requests.post(self.addressFull + '/api/v1/generate', json=requestDictionary, timeout=(10, self.timeout) )
        if returnedRequest.status_code != 200:
            print('Unable to translate entry. ')
            print('Status code:',returnedRequest.status_code)
            print('Headers:',returnedRequest.headers)
            print('Body:',returnedRequest.content)
            return None

        translatedText=returnedRequest.json()['results'][0]['text'].strip()
        print('translatedText=',translatedText)
        return translatedText

        #return str( self.batchTranslate( [untranslatedString] )[0] ) # Lazy.





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
