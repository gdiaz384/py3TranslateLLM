#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: This library defines various translation engines to use when translating text. The idea is to expose a semi-uniform interface. These libraries assume the data will be input as either a single string or as a batch. Batches are a single Python list where each entry is a string.

Usage: See below. Like at the bottom.

License: See main program.

"""
#set defaults
printStuff=True
verbose=False
debug=False
#debug=True
consoleEncoding='utf-8'
linesThatBeginWithThisAreComments='#'
assignmentOperatorInSettingsFile='='
inputErrorHandling='strict'
#outputErrorHandling='namereplace'

import requests

#wrapper class for spreadsheet data structure
class SugoiNMT:
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
        try:
            self.model= requests.get(self.address + ':' + self.port + '/api/v1/model',timeout=10)
            self.version= requests.get(self.address + ':' + self.port + '/api/v1/version',timeout=10)
        except:
            pass

        


"""
Usage and concept art:


import translationEngines

translationEngine=translationEngines.KoboldCpp( sourceLanguage, targetLanguage, address, port, prompt )
translationEngine=translationEngines.DeepLAPIFree( sourceLanguage, targetLanguage, APIKey, deeplDictionary )
translationEngine=translationEngines.DeepLAPIPro( sourceLanguage, targetLanguage, APIKey, deeplDictionary )
translationEngine=translationEngines.DeepLWeb( sourceLanguage, targetLanguage )
translationEngine=translationEngines.SugoiNMT( sourceLanguage, targetLanguage, address, port )

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
translationEngine.translate_batch(myList)

batchesAreAvailable=translationEngine.supportsBatches
if batchesAreAvailable == True:
    # stuff here
else:
    # line by line only

"""
