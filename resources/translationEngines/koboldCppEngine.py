#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: This library defines various translation engines to use when translating text. The idea is to expose a semi-uniform interface. These libraries assume the data will be input as either a single string or as a batch. Batches are a single Python list where each entry is a string. This library requires the requests library. Install using `pip install requests`.

Usage: See below. Like at the bottom.

Copyright (c) 2024 gdiaz384; License: See main program.

"""
__version__='2024.05.06'

#set defaults
#printStuff=True
verbose=False
debug=False
consoleEncoding='utf-8'
defaultTimeout=360
# Valid options are: autocomplete, instruct, chat.
defaultInstructionFormat='autocomplete'
defaultTimeoutMulitplierForFirstRun=4

# For 'instruct' models, these are sequences to start and end input. Not using them results in unstable output.
alpacaStartSequence='\n### Instruction:\n'
alpacaEndSequence='\n### Response:\n'
vicunaStartSequence='\nUSER: '
vicunaEndSequence='\nASSISTANT: '
metharmeStartSequence='<|user|>'
metharmeEndSequence='<|model|>'
llama2ChatStartSequence='\n[INST]'
llama2ChatEndSequence='[/INST]\n'
chatMLStartSequence='<|im_end|>\n<|im_start|>user\n'
chatMLEndSequence='<|im_end|>\n<|im_start|>assistant\n'

defaultInstructionFormatStartSequence=llama2ChatStartSequence
defaultInstructionFormatEndSequence=llama2ChatEndSequence

# For 'chat' models, these are sequences that mark user input and the start of the model's output. 
defaultChatInputName='Input'
defaultChatOutputName='Output'


# https://huggingface.co/TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF/tree/main
# Apache 2.0 License. Copy center + patent waver.
mixtral8x7bInstructModels=[ 'mixtral-8x7b-instruct-v0.1.Q2_K', 'mixtral-8x7b-instruct-v0.1.Q3_K_M', 'mixtral-8x7b-instruct-v0.1.Q4_0', 'mixtral-8x7b-instruct-v0.1.Q4_K_M', 'mixtral-8x7b-instruct-v0.1.Q5_0', 'mixtral-8x7b-instruct-v0.1.Q5_K_M', 'mixtral-8x7b-instruct-v0.1.Q6_K', 'mixtral-8x7b-instruct-v0.1.Q8_0' ]

# Change to lower case.
for counter,entry in enumerate(mixtral8x7bInstructModels):
    mixtral8x7bInstructModels[counter]=entry.lower()

# https://huggingface.co/Qwen
# https://huggingface.co/Qwen/Qwen1.5-32B-Chat-GGUF/tree/main
# https://huggingface.co/Qwen/Qwen1.5-72B-Chat-GGUF/tree/main
# Tongyi Qianwen License. Attribution required + commercial use allowed for <100M monthly users.
qwen15_32B_chatModels=[]
qwen15_72B_chatModels=[]


import sys
import requests


class KoboldCppEngine:
    # Insert any custom code to pre process the untranslated text here. This is very model, prompt, and dataset specific.
    # https://www.w3schools.com/python/python_strings_methods.asp
    def preProcessText(self, untranslatedText):
        #return untranslatedText

        # Example:
        untranslatedText=untranslatedText.replace('\\n',' ') # Remove hardcoded new lines and replace them with a single empty space.
        untranslatedText=untranslatedText.replace('\n',' ') # Remove new lines and replace them with a single empty space.
        untranslatedText=untranslatedText.strip()               # Remove any whitespaces along the edges.
        untranslatedText=untranslatedText.replace('  ',' ').replace('  ',' ')  # In the middle, replace any two blank spaces with a single blank space.

        return untranslatedText


    # Insert any custom code to post process the output text here. This is very model and prompt specific.
    def postProcessText(self, rawTranslatedText, untranslatedText, speakerName=None):

        rawTranslatedText=rawTranslatedText.strip()

        # if the translation has new lines, then truncate the result.
        rawTranslatedText=rawTranslatedText.partition('\n')[0].strip()

        if speakerName != None:
            if rawTranslatedText.startswith( speakerName + ':' ):
                rawTranslatedText=rawTranslatedText[ len(speakerName) + 1: ].strip()

        return rawTranslatedText




        # Mixtral8x7b-instruct example:
        if self._modelOnly in mixtral8x7bInstructModels:


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

            # Remove a few blacklist starts.
            if speakerName != None:
                if rawTranslatedText.startswith( speakerName + ':'):
#                    print( 'rawTextBeforeRemovingSpeaker=' + rawTranslatedText )
                    rawTranslatedText=rawTranslatedText[ len( speakerName )+1: ].strip()
#                    print( 'rawTextAfterRemovingSpeaker=' + rawTranslatedText )
#                elif rawTranslatedText.startswith( speakerName ):
#                    print( 'rawTextBeforeRemovingSpeaker=' + rawTranslatedText )
#                    rawTranslatedText=rawTranslatedText[ len( speakerName ): ].strip()
#                    print( 'rawTextAfterRemovingSpeaker=' + rawTranslatedText )
            if rawTranslatedText.lower().startswith( 'translation:' ):
                rawTranslatedText=rawTranslatedText[ len( 'translation:' ): ].strip()
            if rawTranslatedText.lower().startswith( 'translated text:' ):
                rawTranslatedText=rawTranslatedText[ len( 'translated text:' ): ].strip()
            elif rawTranslatedText.lower().strip().endswith( 'note:' ):#This is more of an 'endswith() operation. string[:len('note:') ] ?
                rawTranslatedText=rawTranslatedText.strip()[ :-len( 'note:' ) ].strip()

#        elif self._modelOnly == another model:
            # Post processing code for another model goes here.
#        elif:
#            pass

        return rawTranslatedText


#class KoboldCppEngine:
    # Address is the protocol and the ip address or hostname of the target server.
    # sourceLanguage and targetLanguage are lists that have the full language, the two letter language codes, the three letter language codes, and some meta information useful for other translation engines.
    def __init__(self, sourceLanguage=None, targetLanguage=None, settings=None, characterDictionary=None): 

#address=None, port=None, timeout=360, prompt=None,

        # Set generic API static values for this engine.
        self.supportsBatches=False
        self.supportsHistory=True
        self.requiresPrompt=True
        self.promptOptional=False

        # Set generic API variables for this engine.
        self.reachable=False  # Some sort of test to check if the server is reachable goes here. Maybe just try to get model/version and if they are returned, then the server is declared reachable?
        self.model=None
        self.version=None

        # Process generic input.
        self.characterDictionary=characterDictionary
        self.sourceLanguageList=sourceLanguage
        # if DifferentSourceLanguage == True, then use the alternative name.
        if self.sourceLanguageList[4] == True:
            self.sourceLanguage=self.sourceLanguageList[5]
        else:
            self.sourceLanguage=self.sourceLanguageList[0]

        self.targetLanguageList=targetLanguage
        if self.targetLanguageList[4] == True:
            self.targetLanguage=self.targetLanguageList[5]
        else:
            self.targetLanguage=self.targetLanguageList[0]

        #debug=True
        if debug == True:
            print( str(settings).encode(consoleEncoding) )
            print(self.sourceLanguage)
            print(self.targetLanguageList)
            print(self.targetLanguage)

        # Process engine specific input and associated variables.
        self.address=settings['address']
        self.port=settings['port']
        self.addressFull=self.address + ':' + str(self.port)
        self._modelOnly=None
        self._maxContextLength=None
        self._pastFirstTranslation=False

        if 'instructionFormat' in settings:
            self.instructionFormat=settings['instructionFormat']
        else:
            self.instructionFormat=None
        if 'timeout' in settings:
            self.timeout=settings['timeout']
        else:
            self.timeout=defaultTimeout
        if 'memory' in settings:
            self.memory=settings['memory']
        else:
            self.memory=None

        self.prompt=settings['prompt']
        if self.prompt.find( r'{sourceLanguage}' ) != -1:
            self.prompt=self.prompt.replace( r'{sourceLanguage}', self.sourceLanguage)

        if self.prompt.find( r'{targetLanguage}' ) != -1:
            self.prompt=self.prompt.replace( r'{targetLanguage}', self.targetLanguage)

        if debug == True:
            print(self.prompt)

        # Update the generic API variables for this engine with the goal of defining self.reachable, a boolean, correctly.
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
                return

        if self.model != None:
            self.reachable=True

        #format {characterNames} using self.characterDictionary.
        if (self.characterDictionary != None) and (self.prompt.find( r'{characterNames}' ) != -1):
            tempCharaString=''
            for untranslatedName,translatedName in self.characterDictionary.items():
                tempCharaString= tempCharaString + untranslatedName + '=' + translatedName + '\n'
            self.prompt=self.prompt.replace( r'{characterNames}' , tempCharaString )

        # if the instruction format is not known, then try to figure it out from the model name.
        # Valid instruction formats are: autocomplete (default), instruct, chat
        if self.instructionFormat == None:
            if self._modelOnly.lower().find('instruct') != -1:
                self.instructionFormat='instruct'
            elif self._modelOnly.lower().find('chat') != -1:
                self.instructionFormat='chat'
            else:
                print( 'Warning: A valid instruction format was not specified and could not be detected. Using the default instruction format of: ' + defaultInstructionFormat +'. This is probably incorrect. Valid formats are: autocomplete, instruct, and chat.')
                self.instructionFormat=defaultInstructionFormat

        if self.instructionFormat == 'instruct':
            if (self._modelOnly in mixtral8x7bInstructModels) or ( self._modelOnly.find('llama') != -1 ):
                self._startSequence=llama2ChatStartSequence
                self._endSequence=llama2ChatEndSequence
            else:
                self._startSequence=defaultInstructionFormatStartSequence
                self._endSequence=defaultInstructionFormatEndSequence
        elif self.instructionFormat == 'chat':
            self._inputName=defaultChatInputName
            self._outputName=defaultChatOutputName

        # Now that the instruction format is known, 



    # This expects a python list where every entry is a string.
    def batchTranslate(self, untranslatedList):
        print('Hello world!')
        global debug
        global verbose
        return

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


    # This expects a string to translate. contextHistory should be a variable list of untranslated and translated pairs in sublists.
    # contextHistory= [  [untranslatedString1, translatedString2, speaker], [uString1, tString2, None], [uString1, tString2, speaker]  ]
    def translate(self, untranslatedString, speakerName=None, contextHistory=None):
        global debug
        global verbose

        timeoutForFirstTranslation=None
        if self._pastFirstTranslation == False:
            self._pastFirstTranslation=True
            timeoutForFirstTranslation=self.timeout * defaultTimeoutMulitplierForFirstRun
        # assert( type(untranslatedString) == str )

        if speakerName != None:
            #if verbose == True:
            print( (' speakerName='+str(speakerName)).encode(consoleEncoding) )

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
                if self.instructionFormat == 'instruct':
                    if entry[2] == None:
                        tempHistory=tempHistory + self._startSequence + entry[0] + self._endSequence + entry[1]
                    else:
                        tempHistory=tempHistory + self._startSequence + entry[2] + ': ' + entry[0] + self._endSequence + entry[2] + ': ' + entry[1]
                elif self.instructionFormat == 'chat':
                    tempHistory=tempHistory + self._inputName + ': ' + entry[0] + '\n' + self._outputName + ': ' + entry[1] + '\n'
                    # TODO finish context history for chat format to include speaker.

        # Next build tempPrompt using history string based on {history} tag in prompt.
        if self.prompt.find( '{history}' ) != -1:
            if contextHistory != None:
                tempPrompt=self.prompt.replace('{history}',tempHistory)
            else:
                tempPrompt=self.prompt.replace('{history}','')
        else:
            tempPrompt=self.prompt
            if verbose == True:
                print('Warning: Unable to process history. Make sure {history} is in the prompt.')

#        if contextHistory == None:
#            tempPrompt=self.prompt

        # Speakers are no longer being processed like this. The name of the speaker is now integrated into the instruction 
#        if tempPrompt.find(r'{speaker}') != -1:
#            if speakerName != None:
#                tempPrompt = tempPrompt.replace(r'{speaker}', ' by ' + speakerName )
#            else:
#                tempPrompt = tempPrompt.replace(r'{speaker}','')

        if tempPrompt.find('{untranslatedText}') != -1:
            if speakerName == None:
                tempPrompt = tempPrompt.replace('{untranslatedText}',untranslatedString)
            else:
                tempPrompt = tempPrompt.replace( '{untranslatedText}', str(speakerName) + ': ' + untranslatedString)
        else:
            if speakerName == None:
                tempPrompt = tempPrompt + untranslatedString
            else:
                tempPrompt = tempPrompt + str(speakerName) + ': ' + untranslatedString

        # Build request.  TODO: Add default values for temperature and reptition penalties.
        requestDictionary={}
        requestDictionary[ 'max_length' ]=150 # The number of tokens to generate. Default is 100. Typical lines are 5-30 tokens. Very long responses usually mean the LLM is hallucinating.
        requestDictionary[ 'max_context_length' ]=self._maxContextLength # The maximum number of tokens in the current prompt. The global maximum for any prompt is set at runtime inside of KoboldCpp.
        if self.memory != None:
            requestDictionary[ 'memory' ]=self.memory
        requestDictionary[ 'prompt' ]=tempPrompt # The prompt.
        requestDictionary[ 'stop_sequence' ]=[ 'Translation note:', 'Note:', 'Translation notes:', '[', '\n' ] # This should not be hardcoded.
        #requestDictionary[ 'authorsnote' ]= # This will be added at the end of the prompt. Highest possible priority.

#        if contextHistory != None:
#            tempHistory=''
#            for entry in contextHistory:
#                tempHistory=tempHistory + ' ' + entry
        #requestDictionary['authorsnote']=

        if debug == True:
            print(requestDictionary)
        #sys.exit()

        # Submit the request for translation.
        # Maybe add some code here to deal with server busy messages?
        try:
            if timeoutForFirstTranslation == None:
                returnedRequest=requests.post(self.addressFull + '/api/v1/generate', json=requestDictionary, timeout=(10, self.timeout) )
            else:
                #if verbose == True:
                print( 'timeoutForFirstTranslation=' + str( int( timeoutForFirstTranslation / 60 ) ) +' seconds' )
                returnedRequest=requests.post(self.addressFull + '/api/v1/generate', json=requestDictionary, timeout=(10, timeoutForFirstTranslation) )
            if returnedRequest.status_code != 200:
                print('Unable to translate entry. ')
                print('Status code:',returnedRequest.status_code)
                print( ('Headers:',returnedRequest.headers).encode(consoleEncoding) )
                print( ('Body:',returnedRequest.content).encode(consoleEncoding) )
                return None
        except:
            print( ('Error: unable to translate the following: '+ untranslatedString ).encode(consoleEncoding) )
            return None

        # Extract the translated text from the request.
        # {'results': [{'text': '\n\nBien, gracias.'}]}
        translatedText=returnedRequest.json()['results'][0]['text'].strip()

        verbose = True
        if verbose == True:
            print( ('rawTranslatedText=' + translatedText).encode(consoleEncoding) )

        # Submit the text for post processing which cleans up the formatting beyond just .strip().
        translatedText=self.postProcessText( translatedText, untranslatedString, speakerName)

        if verbose == True:
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
