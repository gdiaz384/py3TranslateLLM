#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: This is a small helper library to help with dealing with text encoding in files. Uses the chardet library if it is available.

TODO: Consider using https://pypi.org/project/charset-normalizer and/or https://pypi.org/project/charamel/
Update: It looks like chardet already has the best detection rates for cp932, so just do nothing instead. Low priority to update this library.
Ideally, charamel and charset-normalizer should be used if chardet is not available. charamel seems to be more accurate than charset-normalizer, so use that as next highest priority.

Usage: See below. Like at the bottom.

License: See main program.
"""
__version__ = '2024.06.22'


#set defaults
printStuff=True
verbose=False
debug=False
#debug=True
consoleEncoding='utf-8'
defaultTextFileEncoding='utf-8'
# Technically, it should be possible to detect the file name encoding of .zip files even if they are binary files, so do not add them here. .epub files are a type of zip file.
knownBinaryFormats=[
'.7z',
'.dll',
'.exe',
'.msi',
'.ods',
'.rar',
'.xls',
'.xlsx'
]

#These must be here or the library will crash even if these modules have already been imported by main program.
import os.path                                   # Test if file exists.
import sys                                         # End program on fail condition.
try:
    import chardet                              # Detect character encoding from files using heuristics.
    chardetLibraryAvailable=True
except:
    chardetLibraryAvailable=False
try:
    import charamel                            # Detect character encoding from files using machine learning heuristics.
    charamelLibraryAvailable=True
except:
    charamelLibraryAvailable=False
try:
    import charset_normalizer              # Try to figure out which character encoding correctly decodes the text.
    charsetNormalizerLibraryAvailable=True
except:
    charsetNormalizerLibraryAvailable=False


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
            print( (myFileName + ':' + str(detector.result) ).encode(consoleEncoding) )
    return temp


def ofThisFile( myFileName, userInputForEncoding=None, fallbackEncoding=defaultTextFileEncoding ):
    #elif (encoding was specified):
    if userInputForEncoding != None:
        #set encoding to user specified encoding
        return userInputForEncoding

    #if (no encoding specified for file...):
    #elif userInputForEncoding == None:

    # if the file was not specified at the command prompt/.ini and neither was the encoding, then just return the fallbackEncoding
    if myFileName == None:
        return fallbackEncoding

    # Check if the file exists.
    if os.path.isfile(myFileName) != True:
        # if the user did not specify an encoding and if the file does not exist, just return the fallbackEncoding
        if printStuff == True:
            print( ('Warning: The file:\'' + myFileName + '\' does not exist. Returning:\'' + fallbackEncoding + '\'').encode(consoleEncoding) )
        return fallbackEncoding

    # Assume file exists now.

    # So, binary spreadsheet files (.xlsx, .xls, .ods) do not have an associated encoding that can be read by charadet because they are binary files. If the user specified option from the command line/.ini has not been used to return already, then return fallbackEncoding for binary files.
    myFile_NameOnly, myFile_ExtensionOnly = os.path.splitext(myFileName)
    #binaryFile=False
    if myFile_ExtensionOnly in knownBinaryFormats:
        #Files that do not have an extension or unknown extensions will not be caught up in this, so it is fine.
        return fallbackEncoding

    # Debug code.
    #chardetLibraryAvailable=False

    # TODO: Update this part to support charamel and charset normalizer libraries. It would probably be better to dump the chardet code back into a function for modularity reasons.
    #if (no encoding specified) and (automaticallyDetectEncoding == True): 
    #if automaticallyDetectEncoding library is available:
    if chardetLibraryAvailable == True:
        # Set encoding to detectEncoding(myFileName)
        # Actually, since this is a library anyway and the conditional import statement was moved elsewhere, then just move the function here to avoid breaking up the code pointlessly.
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
                print(('Warning: Unable to detect encoding of file \'' + myFileName + '\' with high confidence. Using the following fallback encoding:\''+fallbackEncoding+'\'').encode(consoleEncoding))
            temp=fallbackEncoding
        else:
            if debug == True:
                print((myFileName+':'+str(detector.result)).encode(consoleEncoding))
            print( ('Warning: Using automatic encoding detection for file:\'' + str(myFileName) + '\' as:\'' + str(temp) +'\'').encode(consoleEncoding) )
        #temp=detectEncoding(myFileName)
        return temp

    elif chardetLibraryAvailable == False:
        #set encoding to default value
        if (printStuff == True) and (debug == True):
            print( ('Warning: Using default text encoding for file:\'' + str(myFileName) + '\' as:\'' + fallbackEncoding+'\'').encode(consoleEncoding) )
        return fallbackEncoding


# detectLineEndingsFromFile() detects the newline schema of input files based upon the first \n that occurs in the file, which is the same way Python internally detects them.
# This returns ( 'windows', '\r\n' ) or ( 'unix', '\n' ) or ( 'macintosh', '\r' ) .
# Linux uses unix \n line endings. macintosh \r refers to the very old line ending format used in PPC Macs. OS/X and Intel Macs and newer switched to \n which means most computers use \n .
# The default output for single line input files is unix \n .
def detectLineEndingsFromFile( fileNameWithPath, fileEncoding=defaultTextFileEncoding ):
    with open( fileNameWithPath, 'rt', encoding=fileEncoding, errors='ignore', newline='' ) as myFileHandle:
        inputFileContents = myFileHandle.read()

    # Debug code.
    #print( inputFileContents )
    #print( r'inputFileContents.find(\n)=', inputFileContents.find('\n') )
    #print( inputFileContents[ inputFileContents.find('\n') - 1 : inputFileContents.find('\n')] )
    #print( inputFileContents[ inputFileContents.find('\n') - 1 : inputFileContents.find('\n')].encode('utf-8') )

    lineEndingSchema=None
    lineEndings=None
    index=inputFileContents.find('\n')
    #if no \n:
    if index == -1:
        # Then it can be either a single line, in which case the line ending schema does not really matter
        # or if there are a lot of \r, it can be an old macintosh file:
        if inputFileContents.find('\r') != -1:
            lineEndingSchema='macintosh'
            lineEndings='\r'
        else:
            # Single line. Does not really matter. Default to unix.
            lineEndingSchema='unix'
            lineEndings='\n'
    elif inputFileContents[ index - 1 : index ] == '\r':
        lineEndingSchema='windows'
        lineEndings='\r\n'
    else:
        lineEndingSchema='unix'
        lineEndings='\n'

    return ( lineEndingSchema, lineEndings )


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

print( inputFileName + ' will use encoding type: ' + inputEncodingType )

"""
