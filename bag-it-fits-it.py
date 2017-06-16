#!/usr/bin/env python

import shutil, os, sys, subprocess
import bagit
import filecmp
import json, csv, xmltodict

# TODO create something like '"xml report" means "xmlFits"'?

# directory locations

def error():
    lines = [
        'please provide:',
        '1. a directory to bag-n-fits',
        '2. optionally a directory to place output',
        'if no second directory is provided, original location will be bagged',
        'example: \> bag_it_fits_it.py /dir/to/bag /dir/to/output',
    ]
    for line in lines:
        os.system('echo ' + line)


# TODO loop through lines of text, calling echo for each
if len(sys.argv) <= 2:
    error()
    quit()

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
    for i in sorted(obj):
        if isinstance(obj[i], dict):
            get = flattenDict(obj[i], delim)
            for j in sorted(get):
                val[ i + delim + j ] = get[j]
        else:
            val[i] = obj[i]
    return val

# convert xml reports to dicts, compile in list
flatFitsDicts = []
fitsReportFiles = sorted(os.listdir(fitsXmlDir))

def checkReplace(name):
    fh = open('/tmp/'+name+'.txt', 'r')
    old = fh.read()
    fh.close()
    new = globals()[name]
    print(name + ' changed: ' + str(str(old) != str(new)))
    #print(old)
    #print(new)
    fh = open('/tmp/'+name+'.txt', 'w')
    fh.write(str(globals()[name]))
    fh.close()

# convert xmls to dicts and squash 'em
for filename in fitsReportFiles:
    fitsXmlReport = open(fitsXmlDir + filename)
    fitsDict = xmltodict.parse(fitsXmlReport.read())
    fitsXmlReport.close()
    flatFitsDict = flattenDict(fitsDict, '__')
    flatFitsDicts.append(flatFitsDict)

# place all dict keys in a list
headers = ['filepath']
for fitsDict in flatFitsDicts:
    for key in sorted(fitsDict):
        if key not in headers: headers.append(str(key))

# write dict keys as csv column names
csvFile = open(outputDir + 'report.csv', 'w')
pen = csv.writer(csvFile)
pen.writerow(headers)

# write values to relevant columns
currentRow = 0
for fitsDict in flatFitsDicts:
    row = [ fitsReportFiles[currentRow] ]
    for header in headers:
        if header != 'filepath' and header in fitsDict:
            row.append(fitsDict[header])
        elif header != 'filepath':
            row.append('?')
    pen.writerow(row)
    currentRow += 1

csvFile.close()
