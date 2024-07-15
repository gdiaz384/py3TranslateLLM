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
defaultTimeoutMulitplierForFirstRun = 4
# Valid options are: autocomplete, instruct, chat.
defaultInstructionFormat = 'autocomplete'

# Sometimes, the translation is returned prepended or appended with certain data that must be removed. If these strings appear at the start or end, then remove them during post processing.
blacklistedStarts=[]
blacklistedEnd=[]

# For 'instruct' models, these are sequences to start and end input. Not using them results in unstable output.
alpacaStartSequence = '\n### Instruction:\n'
alpacaEndSequence = '\n### Response:\n'
vicunaStartSequence = '\nUSER: '
vicunaEndSequence = '\nASSISTANT: '
metharmeStartSequence = '<|user|>'
metharmeEndSequence = '<|model|>'
llama2ChatStartSequence = '\n[INST]'
llama2ChatEndSequence = '[/INST]\n'
chatMLStartSequence = '<|im_end|>\n<|im_start|>user\n'
chatMLEndSequence = '<|im_end|>\n<|im_start|>assistant\n'

defaultInstructionFormatStartSequence = llama2ChatStartSequence
defaultInstructionFormatEndSequence = llama2ChatEndSequence

# The LLM will stop generating output when it generates any of the following text. \n works well for mixtral8x7b.
stopSequenceList=[
'\n'
'[',
'Translation notes:',
'Translation note:',
'Note:',
]

# For 'chat' models, these are sequences that mark user input and the start of the model's output. 
#defaultChatInputName='Narrator'
#defaultChatOutputName='Output'?
# How should the name of the character who is speaking be indicated in Chat models?
# Character's Input:
# Character's Output:?
# The character's name must be part of the input.
# Character: (as input)
# Character: (as output)?
# And then default to Narration: (for 3rd person) or "Internal Voice" (1st person):? That information cannot be known in advance, therefore it must be hardcoded into the prompt and the user must have a way of setting it in order to automatically set up the {history} options properly in a way that are consistent with the user's input. koboldcpp_chat_chatModelInputName and koboldcpp_chat_chatModelOutputName? The names for the variables could be changed to the character speaking like in instruct models as well.
# Could also just ignore the entire problem completely, treat the chatInputName as pure syntax only and conditionally append the speaker name. That would probably work, right? Are chat models smart enough to figure it out? Might depend a lot on prompt formatting, but that is arguably a user issue. A template can just be provided.

defaultChatInputName = 'Input'
defaultChatOutputName = 'Output'


# Add specific models.
# https://huggingface.co/TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF/tree/main
# Apache 2.0 License. Copy center + patent waver.
mixtral8x7bInstructModels=[ 'mixtral-8x7b-instruct-v0.1.Q2_K', 'mixtral-8x7b-instruct-v0.1.Q3_K_M', 'mixtral-8x7b-instruct-v0.1.Q4_0', 'mixtral-8x7b-instruct-v0.1.Q4_K_M', 'mixtral-8x7b-instruct-v0.1.Q5_0', 'mixtral-8x7b-instruct-v0.1.Q5_K_M', 'mixtral-8x7b-instruct-v0.1.Q6_K', 'mixtral-8x7b-instruct-v0.1.Q8_0' ]

# Change to lower case.
for counter,entry in enumerate( mixtral8x7bInstructModels ):
    mixtral8x7bInstructModels[ counter ] = entry.lower()
# Conclusion: Superb quality.


# https://huggingface.co/TheBloke/japanese-stablelm-instruct-gamma-7B-GGUF
# Apache 2.0 License. Based on Mixtral 7B + Japanese data to allow for Japanese input + instruction data.
# Conclusion: Unknown.


# https://huggingface.co/Qwen
# https://huggingface.co/Qwen/Qwen1.5-32B-Chat-GGUF/tree/main
# https://huggingface.co/Qwen/Qwen1.5-72B-Chat-GGUF/tree/main
# Tongyi Qianwen License. Attribution required + commercial use allowed for <100M monthly users.
qwen1_5_32B_chatModels=[ 'qwen1_5-32b-chat-q2_k', 'qwen1_5-32b-chat-q3_k_m', 'qwen1_5-32b-chat-q4_0', 'qwen1_5-32b-chat-q4_k_m','qwen1_5-32b-chat-q5_0', 'qwen1_5-32b-chat-q5_k_m', 'qwen1_5-32b-chat-q6_k', 'qwen1_5-32b-chat-q8_0',]
qwen1_5_72B_chatModels=[ 'qwen1_5-72b-chat-q2_k', ' qwen1_5-72b-chat-q3_k_m', 'qwen1_5-72b-chat-q4_0', 'qwen1_5-72b-chat-q4_k_m',  'qwen1_5-72b-chat-q5_0', 'qwen1_5-72b-chat-q5_k_m', 'qwen1_5-72b-chat-q6_k', 'qwen1_5-72b-chat-q8_0' ]
qwen1_5_chatModels=qwen1_5_32B_chatModels + qwen1_5_72B_chatModels # Magic.
# Problems: This model seems to have been trained on a lot of Chinese data making it odd for Japanese natural language translation since the same unicode means different things due to han unification.
# If it does not know the English word for something, it will output the chinese symbols for it instead like 皇后 instead of 'queen' or 排列 for 'arrange'. It will not consistently output only the target language especially when given mixed language data like Speaker [English]: dialogue [Japanese].
# It also has this weird habit of prepending random data to the output that had nothing to do with the input which makes it impossible to use history since the results get corrupt right away. It seems especially biased toward always outputting ーー. It seems to replace ― with ー perhaps? If any of the previous lines in the prompt/history had it.
# It also seems to output its own stop token right away? Banning the stop token and determining stop tokens manually seems necessary to get it to output anything at all, especially at the API level but often times it will still refuse to produce any output or produce output with only blank spaces.
# If it fails at a trainslation, sometimes it will also just output the input data.
# For OpenCL, while it supports processing the prompt via GPU, the generation is CPU only and is especially slow. That means, it is not actually faster than Mixtral8x7b despite using the GPU. In the typical state of caching the input prompt, it is actually a lot slower (25-33% slower).
# Conclusion: That is A LOT of problems that make it sub-par compared to Mixtral8x7b-instruct for translation, especially Japanese -> English translation. Basically, it just uses more power with less useful output making this model worthless for translation tasks that do not involve translating into Chinese.
# Update: The commercial only qwenLarge model performs fine, but the 32B model is no-go even at q8_0. 72B is untested. So this might just be a quantization issue with the inferior qwen models.


import sys
import requests


class KoboldCppEngine:
    # Insert any custom code to pre process the untranslated text here. This is very model, prompt, and dataset specific.
    # https://www.w3schools.com/python/python_strings_methods.asp
    def preProcessText( self, untranslatedText ):
        #return untranslatedText

        if self._modelOnly in qwen1_5_chatModels:
            untranslatedText = untranslatedText.replace( '―', '' )

        # Example:
        untranslatedText = untranslatedText.replace( r'\n',' ' ) # Remove hardcoded new lines and replace them with a single empty space.
        untranslatedText = untranslatedText.replace( '\n',' ' ) # Remove new lines and replace them with a single empty space.
        untranslatedText = untranslatedText.strip()               # Remove any whitespaces along the edges.
        untranslatedText = untranslatedText.replace( '  ', ' ' ).replace( '  ', ' ' )  # In the middle, replace any two blank spaces with a single blank space.

        return untranslatedText


    # Insert any custom code to post process the output text here. This is very model and prompt specific.
    def postProcessText(self, rawTranslatedText, untranslatedText, speakerName=None):

        if self._modelOnly in qwen1_5_chatModels:
            rawTranslatedText = rawTranslatedText.replace( 'ー', '' )

        rawTranslatedText = rawTranslatedText.strip()

        # For chat formats, strip out chatbot's name.
        if self.instructionFormat == 'chat':
            if rawTranslatedText.startswith( self._chatModelInputName + ':' ):
                rawTranslatedText = rawTranslatedText[ len(self._chatModelInputName) + 1 : ].strip()
            elif rawTranslatedText.startswith( self._chatModelOutputName + ':' ):
                rawTranslatedText = rawTranslatedText[ len( self._chatModelOutputName) + 1 : ].strip()

        # if the translation has new lines, then truncate the result.
        rawTranslatedText=rawTranslatedText.partition( '\n' )[0].strip()

#        if ( self._modelOnly in mixtral8x7bInstructModels ) or ( self._modelOnly.find( 'llama' ) != -1 ):
        if speakerName != None:
            if rawTranslatedText.startswith( speakerName + ':' ):
                rawTranslatedText=rawTranslatedText[ len( speakerName ) + 1: ].strip()

        if self.characterDictionary != None:
            for key,value in self.characterDictionary.items():
                if rawTranslatedText.startswith( key + ':' ):
                    rawTranslatedText = rawTranslatedText[ len( key ) + 1: ].strip()
                elif rawTranslatedText.startswith( value + ':' ):
                    rawTranslatedText = rawTranslatedText[ len( value ) + 1: ].strip()

#        elif self.instructionFormat == 'chat':
#            self._chatModelInputName = defaultChatInputName
#            self._chatModelOutputName = defaultChatOutputName

        return rawTranslatedText


        # Old code:
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
            if ( rawTranslatedText[ 0:1 ] == '"' ) and ( rawTranslatedText[ -1: ] == '"' ) and ( rawTranslatedText.count( '"' ) == 2 ):
                # TODO: This is very lazy logic. Fix this. The checks should also check the last character.
                if untranslatedText[ 0:1 ] == '「' : # last character is also...
                    pass
                elif untranslatedText[ 0:1 ] == '"' : # and last character is also...
                    pass
                elif untranslatedText.count( '「' ) > 1: #fine as-is
                    pass
                elif untranslatedText.count( '"' ) > 2: #fine as-is
                    pass
                # There needs to be another condition here with the curly quotes.
                else:
                    rawTranslatedText=rawTranslatedText[ 1 : -1 ]

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
                rawTranslatedText = rawTranslatedText[ len( 'translation:' ): ].strip()
            if rawTranslatedText.lower().startswith( 'translated text:' ):
                rawTranslatedText = rawTranslatedText[ len( 'translated text:' ): ].strip()
            elif rawTranslatedText.lower().strip().endswith( 'note:' ):#This is more of an 'endswith() operation. string[:len('note:') ] ?
                rawTranslatedText = rawTranslatedText.strip()[ : -len( 'note:' ) ].strip()

#        elif self._modelOnly == another model:
            # Post processing code for another model goes here.
#        elif:
#            pass

        return rawTranslatedText


#class KoboldCppEngine:
    # Address is the protocol and the ip address or hostname of the target server.
    # sourceLanguage and targetLanguage are lists that have the full language, the two letter language codes, the three letter language codes, and some meta information useful for other translation engines.
    def __init__( self, sourceLanguage=None, targetLanguage=None, characterDictionary=None, settings={} ):

        # Set generic API static values for this engine.
        self.supportsBatches = False
        self.supportsHistory = True
        self.requiresPrompt = True
        self.promptOptional = False
        self.supportsCreatingSummary = True

        # Set generic API variables for this engine.
        self.reachable = False  # Some sort of test to check if the server is reachable goes here. Maybe just try to get model/version and if they are returned, then the server is declared reachable?
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
        self.address = settings[ 'address' ]
        self.port = settings[ 'port' ]
        self.addressFull = self.address + ':' + str( self.port )
        self._modelOnly = None
        self._maxContextLength = None
        self._pastFirstTranslation = False

        self.prompt = settings[ 'prompt' ]
        if self.prompt.find( r'{sourceLanguage}' ) != -1:
            self.prompt = self.prompt.replace( r'{sourceLanguage}', self.sourceLanguage )
        if self.prompt.find( r'{targetLanguage}' ) != -1:
            self.prompt = self.prompt.replace( r'{targetLanguage}', self.targetLanguage )
        if debug == True:
            print( self.prompt.encode( consoleEncoding ) )

        if 'memory' in settings:
            self.memory = settings[ 'memory' ]
        else:
            self.memory = None

        if 'instructionFormat' in settings:
            self.instructionFormat = settings[ 'instructionFormat' ]
        else:
            self.instructionFormat = None

        if 'timeout' in settings:
            self.timeout = settings[ 'timeout' ]
        else:
            self.timeout = defaultTimeout

        # Update the generic API variables for this engine with the goal of defining self.reachable, a boolean, correctly.
        print( 'Connecting to KoboldCpp API at ' + self.addressFull + ' ... ', end='')
        if ( self.address != None ) and ( self.port != None ):
            try:
                self.model = requests.get( self.addressFull + '/api/v1/model', timeout=10 ).json()[ 'result' ]
                self._modelOnly = self.model.partition( '/' )[2].lower()
                self.version = requests.get( self.addressFull + '/api/extra/version', timeout=10 ).json()
                self.version = self.version[ 'result' ] + '/' + self.version[ 'version' ]
                self._maxContextLength = int( requests.get( self.addressFull + '/api/extra/true_max_context_length', timeout=10 ).json()[ 'value' ] )
                print( 'Success.')
                print( ( 'koboldcpp model=' + self.model ).encode( consoleEncoding ) )
                print( ( 'koboldcpp version=' + self.version ).encode( consoleEncoding ) )
                print( ( 'koboldcpp maxContextLength=' + str( self._maxContextLength ) ).encode( consoleEncoding ) )
            #except requests.exceptions.ConnectTimeout:
            except:
                print( 'Failure.')
                print( 'Unable to connect to KoboldCpp API. Please check the connection settings and try again.' )
                return

        if self.model != None:
            self.reachable = True

        #format {characterNames} using self.characterDictionary.
        if ( self.characterDictionary != None ) and ( self.prompt.find( r'{characterNames}' ) != -1 ):
            tempCharaString = ''
            for untranslatedName,translatedName in self.characterDictionary.items():
                tempCharaString = tempCharaString + untranslatedName + '=' + translatedName + '\n'
            self.prompt = self.prompt.replace( r'{characterNames}' , tempCharaString )

        # if the instruction format is not known, then try to figure it out from the model name.
        # Valid instruction formats are: autocomplete (default), instruct, chat
        if self.instructionFormat == None:
            # This is not entirely correct. There are some mixtral and llama models that are not instruct models. How is it possible to tell them apart except for a whitelist?
            if ( self._modelOnly in mixtral8x7bInstructModels ) or ( self._modelOnly.find( 'instruct' ) != -1 ) or ( self._modelOnly.find( 'mixtral' ) != -1 ):
                self.instructionFormat = 'instruct'
            elif self._modelOnly.lower().find( 'chat' ) != -1:
                self.instructionFormat = 'chat'
            else:
                print( 'Warning: A valid instruction format was not specified and could not be detected. Using the default instruction format of: ' + defaultInstructionFormat +'. This is probably incorrect. Valid formats are: autocomplete, instruct, and chat.' )
                self.instructionFormat = defaultInstructionFormat

        if self.instructionFormat == 'instruct':
            if ( self._modelOnly in mixtral8x7bInstructModels ) or ( self._modelOnly.find( 'llama' ) != -1 ) or ( self._modelOnly.find( 'mixtral' ) != -1 ):
                self._instructModelStartSequence = llama2ChatStartSequence
                self._instructModelEndSequence = llama2ChatEndSequence
            #TODO: Add more model detection schemes here.
            else:
                self._instructModelStartSequence = defaultInstructionFormatStartSequence
                self._instructModelEndSequence = defaultInstructionFormatEndSequence
        elif self.instructionFormat == 'chat':
            #if (self._modelOnly in qwen1_5_chatModels) or ():
            # Do different chat models prefer different chat names for input/output or can any combination always be used?
            self._chatModelInputName = defaultChatInputName
            self._chatModelOutputName = defaultChatOutputName
        #elif self.instructionFormat == 'autocomplete':
            # What should happen here?

        # Now that the instruction format is known, 
        print( 'instructionFormat=' + self.instructionFormat )


    def getSummary(self, untranslatedList):
        # Update memory to not include {sceneSummary}.
        if self.memory != None:
            tempMemory=self.memory.replace( '{sceneSummary}', '' )
        else:
            tempMemory=''


    # This expects a python list where every entry is a string.
    def batchTranslate(self, untranslatedList):
        print( 'Hello world!' )
        #debug = True
        if debug == True:
            print( 'len( untranslatedList )=' , len( untranslatedList ) )
            print( ( 'untranslatedList=' + str( untranslatedList ) ).encode( consoleEncoding ) )

        # Preprocess text.
        for counter,entry in enumerate( untranslatedList ):
            #print( str( entry ).encode( consoleEncoding ) )
            untranslatedList[ counter ] = self.preProcessText( entry )

        # Translate text.
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

        return None
        #return translatedList


    # This expects a string to translate. contextHistory should be a list of untranslated and translated pairs in sublists.
    # contextHistory= [  [untranslatedString1, translatedString2, speaker], [uString1, tString2, None], [uString1, tString2, speaker]  ]
    def translate( self, untranslatedString, settings=None ):
        #global debug
        #global verbose
        #speakerName=None, contextHistory=None

        # Unpack some variables.
        if isinstance( settings, dict ) == True:
            if speakerName in settings:
                speakerName = settings[ 'speakerName' ]
                assert( isinstance( speakerName, str ) )
            else:
                speakerName = None

            if contextHistory in settings:
                contextHistory = settings[ 'contextHistory' ]
                assert( isinstance( contextHistory, list ) )
            else:
                contextHistory = None
        else:
            settings = {}
            speakerName = None:
            contextHistory = None:


        #Debug code.
        assert( isinstance( untranslatedString, str ) )
        #print( 'contextHistory=' + str(contextHistory))
        # Disable history for certain problematic models.
        if self._modelOnly in qwen1_5_chatModels:
            contextHistory = None

        if speakerName != None:
            #if verbose == True:
            print( ( 'speakerName=' + str( speakerName ) ).encode( consoleEncoding ) )

        untranslatedString = self.preProcessText( untranslatedString )

        # Syntax:
        # http://localhost:5001/api
        # reqDict= { 'prompt' : promptString + 'How are you?' }
        # requests.post( 'http://192.168.1.100:5001/api/v1/generate',json=reqDict, timeout=120 ).json()
        # { 'results' : [ {'text': '\n\nBien, gracias.'} ] }

        # Build prompt.
        # First build history string from history list.
        if contextHistory != None:
            tempHistory = ''
            for entry in contextHistory:
                if self.instructionFormat == 'instruct':
                    if entry[ 2 ] == None:
                        tempHistory = tempHistory + self._instructModelStartSequence + entry[ 0 ] + self._instructModelEndSequence + entry[ 1 ]
                    else:
                        tempHistory = tempHistory + self._instructModelStartSequence + entry[ 2 ] + ': ' + entry[ 0 ] + self._instructModelEndSequence + entry[ 2 ] + ': ' + entry[ 1 ]
                elif self.instructionFormat == 'chat':
                    if entry[ 2 ] == None:
                        tempHistory = tempHistory + self._chatModelInputName + ': ' + entry[ 0 ] + '\n' + self._chatModelOutputName + ': ' + entry[ 1 ] + '\n'
                    else:
                        tempHistory = tempHistory + self._chatModelInputName + ': ' + entry[ 2 ] + ': ' + entry[ 0 ] + '\n' + self._chatModelOutputName + ': ' + entry[ 2 ] + ': ' + entry[ 1 ] + '\n'
                elif self.instructionFormat == 'autocomplete'
                    #TODO: format autocomplete model history here. How? Maybe just use same as chat syntax?
                    pass
                else:
                    print( ( 'Warning: Uncrecognized instructionFormat' + str(self.instructionFormat) ).encode( consoleEncoding ) )

        # Next build tempPrompt using history string based on {history} tag in prompt.
        if self.prompt.find( '{history}' ) != -1:
            if contextHistory != None:
                tempPrompt = self.prompt.replace( r'{history}', tempHistory )
            else:
                tempPrompt = self.prompt.replace( r'{history}', '' ).replace( '\n\n', '\n' )
        else:
            tempPrompt = self.prompt
            if verbose == True:
                print( r'Warning: Unable to process history. Make sure {history} is in the prompt.' )

#        if contextHistory == None:
#            tempPrompt=self.prompt

        # Speakers are no longer being processed like this. The name of the speaker is now integrated into the instruction 
#        if tempPrompt.find(r'{speaker}') != -1:
#            if speakerName != None:
#                tempPrompt = tempPrompt.replace(r'{speaker}', ' by ' + speakerName )
#            else:
#                tempPrompt = tempPrompt.replace(r'{speaker}','')

        if tempPrompt.find( '{untranslatedText}' ) != -1:
            if speakerName == None:
                tempPrompt = tempPrompt.replace( '{untranslatedText}', untranslatedString )
            else:
                tempPrompt = tempPrompt.replace( '{untranslatedText}', str( speakerName ) + ': ' + untranslatedString )
        else:
            if speakerName == None:
                tempPrompt = tempPrompt + untranslatedString
            else:
                tempPrompt = tempPrompt + str(speakerName) + ': ' + untranslatedString

        # Build request.
        requestDictionary={}

        requestDictionary[ 'max_length' ] = 150 # The number of tokens to generate. Default is 100. Typical lines are 5-30 tokens. Very long responses usually mean the LLM is hallucinating.
        requestDictionary[ 'max_context_length' ] = self._maxContextLength # The maximum number of tokens in the current prompt. The global maximum for any prompt is set at runtime inside of KoboldCpp.

        if self.memory != None:
            requestDictionary[ 'memory' ] = self.memory
        requestDictionary[ 'prompt' ] = tempPrompt # The prompt.

        requestDictionary[ 'trim_stop' ] = True
        requestDictionary[ 'stop_sequence' ] = stopSequenceList

        # Was debug code for qwen. Did not work out.
        # TODO: Add default values for temperature, <=0.7, and reptition penalties. Update: This is very model specific, so create some defaults and only add them for recognized models.
        if ( self.instructionFormat == 'chat' ) and ( debug == True ):
            requestDictionary[ 'n' ] = 1
            requestDictionary[ 'temperature' ] = 0.7            
            requestDictionary[ 'rep_pen' ] = 1.1
            requestDictionary[ 'rep_pen_range' ] = 320
            requestDictionary[ 'rep_pen_slope' ] = 0.7
            requestDictionary[ 'sampler_order' ] = [6,0,1,3,4,2,5]
            requestDictionary[ 'top_p' ] = 0.92
            requestDictionary[ 'top_k' ] = 100
            requestDictionary[ 'top_a' ] = 0
            requestDictionary[ 'typical' ] = 1
            requestDictionary[ 'tfs' ] = 1
            requestDictionary[ 'use_default_badwordsids' ] = False
            requestDictionary[ 'quiet' ] = True
            # Add _chatModelInputName as stop sequence for chat models.
            requestDictionary[ 'stop_sequence' ] = [ self._chatModelInputName, self._chatModelInputName + '\n', '\n' + self._chatModelOutputName ]

#        if contextHistory != None:
#            tempHistory=''
#            for entry in contextHistory:
#                tempHistory=tempHistory + ' ' + entry

        #requestDictionary[ 'authorsnote' ] = # This will be added at the end of the prompt. Highest possible priority.
        #requestDictionary[ 'authorsnote' ]=

        if debug == True:
            print( requestDictionary )
            #sys.exit( 0 )

        # Submit the request for translation.
        # Maybe add some code here to deal with server busy messages?
        # This should accept a keyboard interupt, send a quit generating stuff message to the server, and then propogate the interupt to the calling module using raise.

        if self._pastFirstTranslation == False:
            currentTimeout = self.timeout * defaultTimeoutMulitplierForFirstRun
            print( ' timeoutForFirstTranslation=' + str( int( timeoutForFirstTranslation / 60 ) ) + ' minutes' )
        else:
            currentTimeout = self.timeout

#        try:
        returnedRequest = requests.post( self.addressFull + '/api/v1/generate', json=requestDictionary, timeout=( 10, currentTimeout ) )
#        except:
#            print( ( 'Error: unable to translate the following: '+ untranslatedString ).encode( consoleEncoding ) )
#            return None

        if returnedRequest.status_code != 200:
            print( ( 'Unable to translate entry: \'' + str(untranslatedString) + '\'' ).encode( consoleEncoding ) )
            print( 'Status code:', returnedRequest.status_code )
            print( ( 'Headers:', returnedRequest.headers ).encode( consoleEncoding ) )
            print( ( 'Body:', returnedRequest.content ).encode( consoleEncoding ) )
            return None

        # Extract the translated text from the request.
        # { 'results' : [ { 'text' : '\n\nBien, gracias.' } ] }
        translatedText = returnedRequest.json()[ 'results' ][ 0 ][ 'text' ].strip()

        #verbose = True
        #if verbose == True:
        print( ( 'rawTranslatedText=' + translatedText ).encode( consoleEncoding ) )

        # Submit the text for post processing which cleans up the formatting beyond just .strip().
        translatedText = self.postProcessText( translatedText, untranslatedString, speakerName )

        if verbose == True:
            print( ( 'postProcessedTranslatedText=' + translatedText ).encode( consoleEncoding ) )

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
