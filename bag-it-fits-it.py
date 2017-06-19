#!/usr/bin/env python

import shutil, os, sys, subprocess, platform
import bagit
import filecmp
import json, csv, xmltodict

# TODO create something like '"xml report" means "xmlFits"'?

# directory locations

def error():
    lines = [
        'please provide:\n',
        '1. a directory to bag-n-fits',
        '2. optionally a directory to place output',
        'if no second directory is provided, original location will be bagged\n',
        'example: \> bag_it_fits_it.py /dir/to/bag /dir/to/output',
    ]
    for line in lines:
        os.system('echo ' + line)

# do some pre-flight checks
if len(sys.argv) <= 2:
    error()
    quit()
fits_script = ''
if platform.system() == 'Windows':
    fits_script = 'fits\\fits.bat'
else: fits_script = 'fits/fits.sh'
if not os.path.exists('./fits'):
    print('|bag-it-fits-it.py:\n|please place fits in same directory as script\n|and ensure the directory is named \'fits\'')
    quit()

dirToBag = os.path.abspath(sys.argv[1])
outputDir = os.path.abspath(sys.argv[2])
masterBagDir = outputDir + '/master-bag'
workingBagDir = outputDir + '/working-bag'
fitsXmlDir = outputDir + '/fits-xml/'

# create bags, directories
shutil.copytree(dirToBag, masterBagDir)
os.mkdir(fitsXmlDir)
bag = bagit.make_bag(masterBagDir)
bag.save()
shutil.copytree(masterBagDir, workingBagDir)

# TODO download/unzip fits if not present
# TODO command line option to point to already installed fits?
"""
if not os.path.exists('fits'):
    cmd = 'wget https://projects.iq.harvard.edu/files/fits/files/fits-1.1.1.zip'
    subprocess.call(cmd, shell=True)
"""

# run FITS on working bag
cmd = fits_script + ' -r -i ' + workingBagDir + '/data/ -o ' + fitsXmlDir + ' -x'
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
# TODO: remove unneeded sorted?
flatFitsDicts = []
fitsReportFiles = sorted(os.listdir(fitsXmlDir))

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
csvFile = open(outputDir + '/report.csv', 'w')
pen = csv.writer(csvFile)
pen.writerow(headers)

# write values to relevant columns
currentRow = 0
for fitsDict in flatFitsDicts:
    row = [ os.path.abspath( fitsReportFiles[currentRow] ) ]
    for header in headers:
        if header != 'filepath' and header in fitsDict:
            row.append(fitsDict[header])
        elif header != 'filepath':
            row.append('?')
    pen.writerow(row)
    currentRow += 1

csvFile.close()
success_message = 'bags and report successfully created at: ' + os.path.abspath(outputDir)
os.system('echo ' + success_message)
