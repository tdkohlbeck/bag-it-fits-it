#!/usr/bin/env python

import shutil, os, sys, subprocess
import bagit
import filecmp
import json, csv, xmltodict, jsonstocsv

# TODO create something like '"xml report" means "xmlFits"'?

# directory locations
dirToBag = sys.argv[1]
outputDir = sys.argv[2]
masterBagDir = outputDir + '/master-bag'
workingBagDir = outputDir + '/working-bag'
fitsXmlDir = outputDir + '/fits-xml/'

# create bags, directories
shutil.copytree(dirToBag, masterBagDir)
os.mkdir(fitsXmlDir)
bag = bagit.make_bag(masterBagDir)
bag.save()
shutil.copytree(masterBagDir, workingBagDir)

# run FITS on working bag
cmd = './fits/fits.sh -r -i ' + workingBagDir + '/data/ -o ' + fitsXmlDir + ' -x'
subprocess.call(cmd, shell=True)

def flattenDict(obj, delim):
    val = {}
    for i in obj:
        if isinstance(obj[i], dict):
            get = flattenDict(obj[i], delim)
            for j in get:
                val[ i + delim + j ] = get[j]
        else:
            val[i] = obj[i]
    return val

# convert xml reports to dicts, compile in list
flatFitsDicts = []
fitsReportFiles = sorted(os.listdir(fitsXmlDir))
for filename in fitsReportFiles:
    fitsXmlReport = open(fitsXmlDir + filename)
    fitsDict = xmltodict.parse(fitsXmlReport.read())
    fitsXmlReport.close()
    flatFitsDict = flattenDict(fitsDict, ' / ')
    flatFitsDicts.append(flatFitsDict)

# place all dict keys in a list
headers = ['filepath']
for fitsDict in flatFitsDicts:
    for key in sorted(fitsDict):
        if key not in headers: headers.append(str(key))

# TODO * make sure same number of headers every time
#      * write list to file, diff files every run
#      * overwrite file for every run?
# write dict keys as csv column names
csvFile = open(outputDir + 'report.csv', 'w')
pen = csv.writer(csvFile)
pen.writerow(headers)

# TODO compare dict to row and header
# write values to relevant columns
currentRow = 0
for fitsDict in flatFitsDicts:
    row = [ fitsReportFiles[currentRow] ]
    print(currentRow)
    for key in sorted(fitsDict):
        for header in headers:
            if key == header: row.append(fitsDict[key])
            else: row.append('')
            #if len(row) > 8: print(headers[len(row) % 8])

    pen.writerow(row)
    currentRow += 1

csvFile.close()
