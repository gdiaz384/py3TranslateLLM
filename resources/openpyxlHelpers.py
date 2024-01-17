#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Description: A helper/wrapper library to aid in using openpyxl as a data structure.

Usage: See below. Like at the bottom.

License: See main program.

##stop reading now##

"""
#set defaults
printStuff=True
debug=False
#debug=True
consoleEncoding='utf-8'

#These must be here or the library will crash even if these modules have already been imported by main program.
import os.path                            #Extract extension from filename, and test if file exists.
from pathlib import Path            #Override file in file system with another and create subfolders.
import sys                                   #End program on fail condition.
import openpyxl                   #Used as the core internal data structure and also to read/write xlsx files.
import codecs                      #Improves error handling when dealing with text file codecs.
import csv                                    #Read and write to csv files. Example: Read in 'resources/languageCodes.csv'
import codecs                             #Improves error handling when dealing with text file codecs.
try:
    import odfpy                           #Provides interoperability for Open Document Spreadsheet (.ods).
    odfpyLibraryIsAvailable=True
except:
    odfpyLibraryIsAvailable=False
try:
    import xlrd                              #Provides reading from Microsoft Excel Document (.xls).
    xlrdLibraryIsAvailable=True
except:
    xlrdLibraryIsAvailable=False
try:
    import xlwt                              #Provides writing to Microsoft Excel Document (.xls).
    xlwtLibraryIsAvailable=True
except:
    xlwtLibraryIsAvailable=False



#This function returns a list containing 2 strings that represent a row and column extracted from input Cell address
#such as returning ['5', 'B'] from: <Cell 'Sheet'.B5>   It also works for complicated cases like AB534.
def getRowAndColumnFromCell(myInputCell):
    #print('raw cell data='+str(myInputCell))
    #basically, split the string according to . and then split it again according to > to get back only the CellAddress
    myInputCell=str(myInputCell).split('.', maxsplit=1)[1].split('>')[0]
    index=0
    for i in range(10):
        try:
            int(myInputCell[index:index+1])
            index=i
            break #this break and the assignment above will only execute when the int conversion works
        except:
            #this will execute if there is an error, like int('A')
            #this will not execute if the int conversion succeds
            #print('index='+str(index))
            pass
        index+=1
    currentColumn=myInputCell[:index]#does not include character in string[Index] because index is after the :
    currentRow=myInputCell[index:]#includes character specified by string[index] because index is before the :
    #return ['pie', 'apple']
    return [currentRow, currentColumn]

#Example:
#myRawCell=''
#for row in mySpreadsheet:
#    for i in row:
#        if i.value == 'lots of pies':
#            print(str(i) + '=' + str(i.value))
#            myRawCell=i
#currentRow, currentColumn = getRowAndColumnFromCell(myRawCell)


#helper function that changes the data for a row in mySpreadsheet to what is specified in a python List []
#Note: This is only for modifying existing rows and only for mySpreadsheet. To add a brand new row, use append:
    #Example: newRow = ['pies', 'lots of pies']
    #mySpreadsheet.append(newRow)
#The rowLocation specified is the nth rowLocation, not the [0,1,2,3...row] because rows start with 1
def replaceRow(newRowDataInAList, rowLocation):
    global mySpreadsheet
    print(str(len(newRowDataInAList)).encode(consoleEncoding))
    print(str(range(len(newRowDataInAList))).encode(consoleEncoding))
    for i in range(len(newRowDataInAList)):
        #columns begin with 1 instead of 0, so add 1 when referencing the target column, but not the source
        mySpreadsheet[getCell(mySpreadsheet.cell(row=int(rowLocation), column=i+1))]=newRowDataInAList[i]

#Example: replaceRow(newRow,7)


#this returns either None if there is no cell with the search term, or it will return the raw cell address if it found it, case sensitive
#to determine the row, the column, or both from the raw cell address, call getRowAndColumnFromCell(rawCellAddress)
def searchHeader(spreadsheet, searchTerm):
    cellFound=None
    for row in spreadsheet[1]:
        for i in row:
            if i.value == searchTerm:
                cellFound=i
        #if cellFound != None:
        #    print('found')
        #else:
        #    print('notfound')
        break #stop searching after first row
    return cellFound

#Example:
#cellFound=None
#isFound=searchHeader(mySpreadsheet,searchTerm)
#if isFound == None:
#    print('was not found')
#else:
#    print('searchTerm:\"'+searchTerm+'" was found at:'+str(isFound))


#This returns either None if there is no cell with the search term, or the raw cell address. Case and whitespace sensitive.
#To determine the row, the column, or both from the raw cell address, use getRowAndColumnFromCell(rawCellAddress)
def searchSpreadsheet(spreadsheet, searchTerm):
    for row in spreadsheet.iter_rows():
        for cell in row:
            if cell.value == searchTerm:
                return cell
    return None


#These return either None if there is no cell with the search term, or the raw cell address. Case insensitive. Whitespace sensitive.
#To determine the row, the column, or both from the raw cell address, use getRowAndColumnFromCell(rawCellAddress)
def searchRowsCaseInsensitive(spreadsheet, searchTerm):
    for row in spreadsheet.iter_rows():
        for cell in row:
            if isinstance(cell.value, str):
                if cell.value.lower() == str(searchTerm).lower():
                    return cell
    return None

def searchColumnsCaseInsensitive(spreadsheet, searchTerm):
    for column in spreadsheet.iter_cols():
        for cell in column:
            if isinstance(cell.value, str):
                if cell.value.lower() == str(searchTerm).lower():
                    return cell
    return None


#give this function a spreadsheet object (subclass of workbook) and it will print the contents of that sheet
def printAllTheThings(mySpreadsheetName):
    for row in mySpreadsheetName.iter_rows(min_row=1, values_only=True):
        temp=''
        for cell in row:
            temp=temp+','+str(cell)
        print(temp[1:].encode(consoleEncoding))#ignore first , in output

#Example: printAllTheThings(mySpreadsheet)




#TODO. Export an existing spreadsheet to a file.
#Import a file into an existing spreadsheet.
#References/objects are done using workbooks, not the active spreadsheet.
#All files follow the same rule of the first row being reserved for header values and invalid for inputting/outputting actual data.

#this processes raw data using a parse file. It is meant to be loaded into the main workbook for data processing.
def importFromTextFile(fileName, fileNameEncoding, parseFile, parseFileEncoding)

#this reads program settings from text files using a predetermined (hardcoded) list of rules
#The text file following is in a setting=value pattern with # as comments and empty/whitespace lines ignored.
#This function returns builds a dictionary and then returns it to the caller.
def readSettingsFromTextFile()
    print('Hello World'.encode(consoleEncoding))

def importFromCSV(fileNameWithPath):
    print('Hello World'.encode(consoleEncoding))
    #return workbook

    #import languageCodes.csv, but first check to see if it exists
    if os.path.isfile(languageCodesFileName) != True:
        sys.exit(('\n Error. Unable to find languageCodes.csv "' + languageCodesFileName + '"' + usageHelp).encode(consoleEncoding))

    languageCodesWorkbook = Workbook()
    languageCodesSpreadsheet = languageCodesWorkbook.active

    #It looks like quoting fields in csv's that use commas , and new
    #lines works but only as double quotes " and not single quotes '
    #Spaces are also preserved as-is if they are within the , by default, so remove them
    with open(languageCodesFileName, newline='', encoding=languageCodesEncoding) as myFile:
        csvReader = csv.reader(myFile)
        for line in csvReader:
            if debug == True:
                print(str(line).encode(consoleEncoding))
            #clean up whitespace for entities
            for i in range(len(line)):
                line[i]=line[i].strip()
            languageCodesSpreadsheet.append(line)


def exportToCSV(workBook, fileNameWithPath):
    print('Hello World'.encode(consoleEncoding))


def importFromXLSX(workBook, fileNameWithPath):
    print('Hello World'.encode(consoleEncoding))
    #return workbook
def exportToXLSX(workBook, fileNameWithPath):
    print('Hello World'.encode(consoleEncoding))
    #theWorkbook.save(filename="myAwesomeSpreadsheet.xlsx")
    workBook.save(filename=fileNameWithPath")


def importFromXLS(fileNameWithPath):
    print('Hello World'.encode(consoleEncoding))
    #return workbook
def exportToXLS(workBook, fileNameWithPath):
    print('Hello World'.encode(consoleEncoding))


def importFromODF(fileNameWithPath):
    print('Hello World'.encode(consoleEncoding))
    #return workbook
def exportToODF(workBook, fileNameWithPath):
    print('Hello World'.encode(consoleEncoding))












"""
#Usage examples, assuming this library is in a subfolder named 'resources':
defaultEncoding='utf-8'
try:
    import resources.dealWithEncoding as dealWithEncoding   #deal text files having various encoding methods
    dealWithEncodingLibraryIsAvailable=True
except:
    dealWithEncodingLibraryIsAvailable=False
    sys.exit(1)

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
