#!/usr/bin/env python

import shutil, os, sys, subprocess
import bagit
import json, csv, xmltodict, jsonstocsv

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
cmd = './fits/fits.sh -r -i ' + workingBagDir + ' -o ' + fitsXmlDir + ' -x'
subprocess.call(cmd, shell=True)

def flattenDict(obj, delim):
    val = {}
    for i in obj.keys():
        if isinstance(obj[i], dict):
            get = flattenDict(obj[i], delim)
            for j in get.keys():
                val[ i + delim + j ] = get[j]
        else:
            val[i] = obj[i]
    return val

# convert xml reports to dicts, compile in list
flatFitsDicts = []
for filename in os.listdir(fitsXmlDir):
    fitsXmlReport = open(fitsXmlDir + filename)
    fitsDict = xmltodict.parse(fitsXmlReport.read())
    fitsXmlReport.close()
    flatFitsDict = flattenDict(fitsDict, ' / ')
    flatFitsDicts.append(flatFitsDict)

# place all dict keys in a list
headers = []
for fitsDict in flatFitsDicts:
    for key in fitsDict.keys():
        if key not in headers: headers.append(key)

# write dict keys as csv column names
csvFile = open(sys.argv[2]+'report.csv', 'w')
pen = csv.writer(csvFile)
pen.writerow(headers)

# write values to relevant columns
for fitsDict in flatFitsDicts:
    row = []
    currentColumn = 0
    for key in fitsDict.keys():
        if key == headers[currentColumn]:
            row.append(fitsDict[key])
        else:
            row.append('')
        currentColumn += 1
    pen.writerow(row)

csvFile.close()
