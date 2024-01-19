#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: A small helper library to help with dealing with text encoding in files. Uses the chardet library if it is available.

Usage: See below. Like at the bottom.

License: See main program.

##stop reading now##

"""
#set defaults
version = '0.1 2024Jan19'
printStuff=True
debug=False
#debug=True
consoleEncoding='utf-8'

#These must be here or the library will crash even if these modules have already been imported by main program.
import os.path                                   #Test if file exists.
from pathlib import Path                  #It is not clear how this is useful here, but it might be required. IDK.
import sys                                         #End program on fail condition.
try:
    import chardet                              #Detect character encoding from files using heuristics.
    chardetLibraryAvailable=True
except:
    chardetLibraryAvailable=False

def detectEncoding(myFileName):
    #import chardet
    detector=chardet.UniversalDetector()
    with open(myFileName, 'rb') as openFile:
        for line in openFile:
            detector.feed(line)
            if detector.done == True:
                openFile.close()
                break
    temp=detector.result['encoding']
    if printStuff == True:
        if debug == True:
            print((myFileName+':'+str(detector.result)).encode(consoleEncoding))
    return temp

#returns a string containing the encoding to use, relied on detectEncoding(filename) but code was merged down
#if (no encoding specified) and (automaticallyDetectEncoding == True): 
#def handleDeterminingFileEncoding(myFileName, rawCommandLineOption, defaultEncoding):
def ofThisFile(myFileName, rawCommandLineOption, fallbackEncoding):
    #elif (encoding was specified):
    if rawCommandLineOption != None:
        #set encoding to user specified encoding
        return rawCommandLineOption
    #if (no encoding specified for file...):
    elif rawCommandLineOption == None:
        #if the file was not specified at the command prompt and neither was the encoding, then just return the fallbackEncoding
        if myFileName == None:
            return fallbackEncoding
        #check if the file exists
        if os.path.isfile(myFileName) != True:
            #if the user did not specify an encoding and if the file does not exist, then just return the fallbackEncoding
            if printStuff == True:
                print(('Warning: The file:\"'+myFileName+'" does not exist. Returning:\"'+fallbackEncoding+'"').encode(consoleEncoding))
            return fallbackEncoding
        #Assume file exists now.
        #chardetLibraryAvailable=False   #debug code
        #if automaticallyDetectEncoding library is available:
        if chardetLibraryAvailable == True:
            #set encoding to detectEncoding(myFileName)
            #actually, since this is a library anyway and the conditional import statement was moved elsewhere, then just move the function here to avoid breaking up the code pointlessly
            detector=chardet.UniversalDetector()
            with open(myFileName, 'rb') as openFile:
                for line in openFile:
                    detector.feed(line)
                    if detector.done == True:
                        openFile.close()
                        break
            temp=detector.result['encoding']
            if printStuff == True:
                if debug == True:
                    print((myFileName+':'+str(detector.result)).encode(consoleEncoding))
                print(('Warning: Using automatic encoding detection for file:\"'+str(myFileName)+'" as:\"'+str(temp)+'"').encode(consoleEncoding))
            #temp=detectEncoding(myFileName)
            #So sometimes, like when detecting an ascii only file or a utf-8 file filled with only ascii, the chardet library will return with a confidence of 0.0 and the result will be None. When that happens, try to catch it and change the result from None to the default encoding. The assumption is that this also happens if the confidence value is below some threshold like <0.2 or <0.5.
            if temp == None:
                if (printStuff == True) and (debug == True):
                    print(('Warning: Unable to detect encoding of file \''+myFileName+'\' with high confidence. Using the following fallback encoding:\''+fallbackEncoding+'\'').encode(consoleEncoding))
                temp=fallbackEncoding
            return temp
        elif chardetLibraryAvailable == False:
            #set encoding to default value
            if (printStuff == True) and (debug == True):
                print(('Warning: Using default text encoding for file:\"'+str(myFileName)+'" as:\"'+str(fallbackEncoding)+'"').encode(consoleEncoding))
            return fallbackEncoding
        else:
            sys.exit('Unspecified error.'.encode(consoleEncoding))
    else:
        sys.exit('Unspecified error.'.encode(consoleEncoding))



"""
#Usage examples, assuming this library is in a subfolder named 'resources':
defaultEncoding='utf-8'
try:
    import resources.dealWithEncoding as dealWithEncoding   #deal text files having various encoding methods
    dealWithEncodingLibraryIsAvailable=True
except:
    dealWithEncodingLibraryIsAvailable=False

myFileName = 'myFile.txt'

if dealWithEncodingLibraryIsAvailable == True:
    #Update internal library variables to match main program settings.
    dealWithEncoding.debug=debug
    dealWithEncoding.consoleEncoding=consoleEncoding

    inputEncodingType = dealWithEncoding.ofThisFile(myFileName=inputFileName, rawCommandLineOption=command_Line_arguments.inputEncoding, fallbackEncoding=defaultEncodingType)

    #or, to use only positional arguments
    inputEncodingType = dealWithEncoding.ofThisFile(inputFileName, command_Line_arguments.inputEncoding, defaultEncodingType)

    #or, To detect encoding of a file with the chardet library that has already been determined to exist, and does not consider user preferences, fallback encoding, or a return of None from the chardet library:
    inputEncodingType= dealWithEncoding.detectEncoding(inputFileName)
else:
    inputEncodingType=defaultEncoding

print(inputFileName+' will use encoding type: '+inputEncodingType)

"""
