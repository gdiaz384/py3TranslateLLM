#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: This library defines various translation engines to use when translating text. The idea is to expose a semi-uniform interface. These libraries assume the data will be input as either a single string or as a batch. Batches are a single Python list where each entry is a string.

Usage: See below. Like at the bottom.

Copyright (c) 2024 gdiaz384; License: See main program.

"""
__version__='2024.04.30'

#set defaults
#printStuff=True
verbose=False
debug=False
consoleEncoding='utf-8'

# https://huggingface.co/TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF/tree/main
mixtral8x7bInstructModels=['mixtral-8x7b-instruct-v0.1.Q2_K', 'mixtral-8x7b-instruct-v0.1.Q3_K_M', 'mixtral-8x7b-instruct-v0.1.Q4_0', 'mixtral-8x7b-instruct-v0.1.Q4_K_M', 'mixtral-8x7b-instruct-v0.1.Q5_0', 'mixtral-8x7b-instruct-v0.1.Q5_K_M', 'mixtral-8x7b-instruct-v0.1.Q6_K', 'mixtral-8x7b-instruct-v0.1.Q8_0']
# Change to lower case.
for counter,entry in enumerate(mixtral8x7bInstructModels):
    mixtral8x7bInstructModels[counter]=entry.lower()


import requests


class KoboldCppEngine:
    # Insert any custom code to pre process the output text here. This is very model, prompt, and dataset specific.
    # https://www.w3schools.com/python/python_strings_methods.asp
    def preProcessText(self, untranslatedText):
        #return untranslatedText

        # Example:
        untranslatedText=untranslatedText.replace('\\n',' ') # Remove new lines and replace them with a single empty space.
        untranslatedText=untranslatedText.replace('\n',' ') # Remove new lines and replace them with a single empty space.
        untranslatedText=untranslatedText.strip()               # Remove any whitespaces along the edges.
        untranslatedText=untranslatedText.replace('  ',' ')  # In the middle, replace any two blank spaces with a single blank space.

        return untranslatedText


    # Insert any custom code to post process the output text here. This is very model and prompt specific.
    def postProcessText(self, rawTranslatedText, untranslatedText):
        #return rawTranslatedText

        # Mixtral8x7b-Instruct example:
        if self._modelOnly in mixtral8x7bInstructModels:
            # if the translation has new lines, then truncate the result.
            rawTranslatedText=rawTranslatedText.partition('\n')[0]

            # if the translation has an underscore _, then truncate the result.
            if rawTranslatedText.find('_') != -1:
                rawTranslatedText=rawTranslatedText.partition('_')[0]

            # if the translation has ( ) but the source does not, then truncate the result.
            if ( rawTranslatedText.find('(') != -1 ): #and ( rawTranslatedText.find(')') != -1 ) #sometimes the ending ) gets cut off by a stop_sequence token.
                if ( untranslatedText.find( '(' ) == -1 ) and ( untranslatedText.find( '（' ) == -1 ):
                    index=rawTranslatedText.rfind( '(' )
                    rawTranslatedText=rawTranslatedText[ :index ].strip()

            # if the translation has exactly two double quotes on the edges but the source does not, then remove them.
            if ( rawTranslatedText[ 0:1 ] == '"' ) and ( rawTranslatedText[ -1: ] == '"' ) and ( rawTranslatedText.count('"') == 2 ):
                if untranslatedText[ 0:1 ] == '「' :
                    pass
                elif untranslatedText[ 0:1 ] == '"' :
                    pass
                elif untranslatedText.count( '「' ) > 1:
                    pass
                elif untranslatedText.count( '"' ) > 2:
                    pass
                else:
                    rawTranslatedText=rawTranslatedText[ 1:-1 ]

#        elif self._modelOnly == another model:
#        elif:
#            pass

        return rawTranslatedText


#class KoboldCppEngine:
    # Address is the protocol and the ip address or hostname of the target server.
    # sourceLanguage and targetLanguage are lists that have the full language, the two letter language codes, the three letter language codes, and some meta information useful for other translation engines.
    def __init__(self, sourceLanguage=None, targetLanguage=None, address=None, port=None, timeout=360, prompt=None): 
        self.sourceLanguage=sourceLanguage
        self.targetLanguage=targetLanguage
        self.supportsBatches=True
        self.supportsHistory=True
        self.timeout=timeout
        self.requiresPrompt=True
        self.promptOptional=False
        self.address=address
        self.port=port
        self.addressFull=self.address + ':' + str(self.port)
        self._modelOnly=None

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
                self._modelOnly = self.model.partition('/')[2].lower()
                self.version = requests.get( self.addressFull + '/api/extra/version', timeout=10 ).json()
                self.version = self.version['result'] + '/' + self.version['version']
                self._maxContextLength = int(requests.get( self.addressFull + '/api/extra/true_max_context_length', timeout=10 ).json()['value'])
                print( 'Success.')
                print( ( 'koboldcpp model=' + self.model ).encode(consoleEncoding) )
                print( ( 'koboldcpp version=' + self.version ).encode(consoleEncoding) )
                print( ( 'koboldcpp maxContextLength=' + str(self._maxContextLength) ).encode(consoleEncoding) )
            #except requests.exceptions.ConnectTimeout:
            except:
                print( 'Failure.')
                print( 'Unable to connect to KoboldCpp API. Please check the connection settings and try again.' )

        if self.model != None:
            self.reachable=True


    # This expects a python list where every entry is a string.
    def batchTranslate(self, untranslatedList):
        print('Hello, world!')
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

    
    # This expects a string to translate. contextHistory should be a list. Maybe the context list should be an untranslated-translated string pair?
    def translate(self, untranslatedString, contextHistory=None):
        # assert( type(untranslatedString) == str )

        untranslatedString=self.preProcessText(untranslatedString)

        # Syntax:
        # http://localhost:5001/api
        # reqDict={'prompt':promptString+'How are you?'}
        # requests.post( 'http://192.168.1.100:5001/api/v1/generate',json=reqDict, timeout=120 ).json()
        # {'results': [{'text': '\n\nBien, gracias.'}]}

        # Build prompt.
        # First build history string from history list.
        if contextHistory != None:
            tempHistory=''
            for entry in contextHistory:
                tempHistory=tempHistory + ' ' + entry

        # Next build tempPrompt using history string based on {history} tag in prompt.
        if self.prompt.find('{history}') != -1:
            if contextHistory != None:
                tempPrompt=self.prompt.replace('{history}',tempHistory[1:])
            else:
                tempPrompt=self.prompt.replace('{history}','')
        else:
            tempPrompt=self.prompt
            #print('Warning: Unable to process history. Make sure {history} is in the prompt.')

#        if contextHistory == None:
#            tempPrompt=self.prompt

        if tempPrompt.find('{untranslatedText}') != -1:
            tempPrompt = tempPrompt.replace('{untranslatedText}',untranslatedString)
        else:
            tempPrompt = tempPrompt + untranslatedString

        # Build request.
        requestDictionary={}
        requestDictionary[ 'prompt' ]=tempPrompt # The prompt.
        requestDictionary[ 'max_length' ]=150 # The number of tokens to generate. Default is 100. Typical lines are 5-30 tokens. Very long responses usually mean the LLM is hallucinating.
        requestDictionary[ 'max_context_length' ]=self._maxContextLength # The maximum number of tokens in the current prompt. The global maximum for any prompt is set at runtime inside of KoboldCpp.
        requestDictionary[ 'stop_sequence' ]=[ 'Translation note:', 'Note:', 'Translation notes:', '\n' ] # This should not be hardcoded.
        #requestDictionary[ 'authorsnote' ]= # This will be added at the end of the prompt. Highest possible priority.
        #requestDictionary[ 'memory' ]=tempHistory[1:]

#        if contextHistory != None:
#            tempHistory=''
#            for entry in contextHistory:
#                tempHistory=tempHistory + ' ' + entry
        #requestDictionary['authorsnote']=

        # Submit the request for translation.
        # Maybe add some code here to deal with server busy messages?
        returnedRequest=requests.post(self.addressFull + '/api/v1/generate', json=requestDictionary, timeout=(10, self.timeout) )
        if returnedRequest.status_code != 200:
            print('Unable to translate entry. ')
            print('Status code:',returnedRequest.status_code)
            print( ('Headers:',returnedRequest.headers).encode(consoleEncoding) )
            print( ('Body:',returnedRequest.content).encode(consoleEncoding) )
            return None

        # Extract the translated text from the request.
        # {'results': [{'text': '\n\nBien, gracias.'}]}
        translatedText=returnedRequest.json()['results'][0]['text'].strip()

        debug = True
        if debug == True:
            print( ('rawTranslatedText=' + translatedText).encode(consoleEncoding) )

        # Submit the text for post processing which cleans up the formatting beyond just .strip().
        translatedText=self.postProcessText( translatedText, untranslatedString )

        if debug == True:
            print( ('postProcessedTranslatedText=' + translatedText).encode(consoleEncoding) )

        return translatedText


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
