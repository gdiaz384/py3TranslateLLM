#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: This is a small helper library to help with dealing with text encoding in files. Uses the chardet library if it is available.

Usage: See below. Like at the bottom.

Copyright (c) 2023-2024 gdiaz384; License: See main program.

"""
__version__='2024.02.27'

#set defaults
printStuff=True
verbose=False
debug=False
#debug=True
consoleEncoding='utf-8'

#These must be here or the library will crash even if these modules have already been imported by main program.
import os.path                                   #Test if file exists.
import sys                                         #End program on fail condition.
try:
    import chardet                              #Detect character encoding from files using heuristics.
    chardetLibraryAvailable=True
except:
    chardetLibraryAvailable=False


#Returns a string containing the encoding to use, relied on detectEncoding(filename) but code was merged down.
#detectEncoding() is never really used, so it should probably just be deleted.
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


def ofThisFile(myFileName, rawCommandLineOption, fallbackEncoding):
    #elif (encoding was specified):
    if rawCommandLineOption != None:
        #set encoding to user specified encoding
        return rawCommandLineOption

    #if (no encoding specified for file...):
    elif rawCommandLineOption == None:

        #if the file was not specified at the command prompt/.ini and neither was the encoding, then just return the fallbackEncoding
        if myFileName == None:
            return fallbackEncoding

        #check if the file exists
        if os.path.isfile(myFileName) != True:
            #if the user did not specify an encoding and if the file does not exist, then just return the fallbackEncoding
            if printStuff == True:
                print(('Warning: The file:\"'+myFileName+'" does not exist. Returning:\"'+fallbackEncoding+'"').encode(consoleEncoding))
            return fallbackEncoding

        #Assume file exists now.

        #So, binary spreadsheet files (.xlsx, .xls, .ods) do not have an associated encoding that can be read by charadet because they are binary files. If the user specified option from the command line/.ini has not been used to return already, then return fallbackEncoding for binary files.
        myFile_NameOnly, myFile_ExtensionOnly = os.path.splitext(myFileName)
        #binaryFile=False
        if (myFile_ExtensionOnly == '.xlsx') or (myFile_ExtensionOnly == '.xls') or (myFile_ExtensionOnly == '.ods'):
            #Files that do not have an extension will not be caught up in this, so it is fine.
            return fallbackEncoding

        #chardetLibraryAvailable=False   #debug code
        #if (no encoding specified) and (automaticallyDetectEncoding == True): 
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
            #So sometimes, like when detecting an ascii only file or a utf-8 file filled with only ascii, the chardet library will return with a confidence of 0.0 and the result will be None. When that happens, try to catch it and change the result from None to the default encoding. The assumption is that this also happens if the confidence value is below some threshold like <0.2 or <0.5.
            if temp == None:
                if (printStuff == True):# and (debug == True):
                    print(('Warning: Unable to detect encoding of file \''+myFileName+'\' with high confidence. Using the following fallback encoding:\''+fallbackEncoding+'\'').encode(consoleEncoding))
                temp=fallbackEncoding
            else:
                if debug == True:
                    print((myFileName+':'+str(detector.result)).encode(consoleEncoding))
                print(('Warning: Using automatic encoding detection for file:\"'+str(myFileName)+'" as:\"'+str(temp)+'"').encode(consoleEncoding))
            #temp=detectEncoding(myFileName)
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
