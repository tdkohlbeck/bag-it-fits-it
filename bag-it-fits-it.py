#!/usr/bin/env python

import shutil, os, sys, subprocess, platform, re
import bagit
import filecmp
import json, csv, xmltodict

# TODO create something like '"xml report" means "xmlFits"'?

# do some pre-flight checks
if len(sys.argv) <= 2:
    print("""|| bag-it-fits-it.py:
|please provide:
|  1. a directory to bag-n-fits
|  2. optionally a directory to place output
|if no second directory is provided, original location will be bagged
|example: \> bag_it_fits_it.py /dir/to/bag /dir/to/output""")
    quit()

fits_script = ''
if platform.system() == 'Windows':
    fits_script = 'fits\\fits.bat'
else: fits_script = 'fits/fits.sh'

if not os.path.isdir('./fits'):
    print("""|| bag-it-fits-it.py:
|please place fits in same directory as script
|and ensure the directory is named \'fits\'""")
    quit()

# TODO: error for space in output dir name

# directory locations
dirToBag = os.path.abspath(sys.argv[1])
outputDir = os.path.abspath(sys.argv[2])
masterBagDir = outputDir + '/master-bag/'
workingBagDir = outputDir + '/working-bag/'
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
cmd = fits_script + ' -r -i ' + workingBagDir + 'data/ -o ' + fitsXmlDir + ' -x'
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

manifest = workingBagDir + '/manifest-sha256.txt'
file_locations = []
with open(manifest, 'r') as f:
    for line in f:
        match = re.search(r'(data.+)', line)
        if match:
            file_locations.append(match.group())
        else:
            file_locations.append('Not Found')

#for fits_file in fitsReportFiles:


# write values to relevant columns
rows = []
currentRow = 0
for fitsDict in flatFitsDicts:
    for location in file_locations:
        report = fitsReportFiles[currentRow]
        match = re.search(r'(.+)(?=.fits.xml)', report)
        filename = match.group()
        if filename == location[-len(filename):]:
            row = [ os.path.abspath(workingBagDir + location) ]
    # TODO: bag location, not fits xml location
    for header in headers:
        if header != 'filepath' and header in fitsDict:
            row.append(fitsDict[header])
        elif header != 'filepath':
            row.append('?')
    rows.append(row)
    currentRow += 1

bag = bagit.Bag(workingBagDir)
print('|has our working bag emerged unscathed? ' + str(bag.is_valid()))
if not bag.is_valid():
    print('|working bag got fucked')
    quit()

clean_header_row = []
for header in headers:
    match = re.search(r'(\w+)$', header)
    clean_header_row.append(match.group())

pen = csv.writer(csvFile)
pen.writerow(clean_header_row)
pen.writerows(rows)

csvFile.close()
success_message = '|bags and report successfully created at: ' + os.path.abspath(outputDir)
print(success_message)
