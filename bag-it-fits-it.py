#!/usr/bin/env python

import csv, filecmp, json, os, platform, re, shutil, subprocess, sys
import bagit, xmltodict

errors = {
    'arg_length': (
        "|| bag-it-fits-it.py:\n"
        "|please provide:\n"
        "| 1. a directory to bag-n-fits\n"
        "| 2. optionally a directory to place output\n"
        "|if no second directory is provided, original location will be bagged\n"
        "|example: $ bag-it-fits-it.py /dir/to/bag /dir/to/output"
    ),
    'fits': (
        '|| bag-it-fits-it.py:\n'
        '|please place fits in same directory as script\n'
        '|and ensure the directory is named \'fits\''
    )
}

# TODO create something like '"xml report" means "xmlFits"'?

# do some pre-flight checks
if len(sys.argv) <= 2:
    print(errors['arg_length'])
    quit()
if not os.path.isdir('./fits'):
    print(errors['fits'])
    quit()

fits_script = ''
if platform.system() == 'Windows':
    fits_script = 'fits\\fits.bat'
else: fits_script = 'fits/fits.sh'


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

bag = bagit.Bag(masterBagDir)
if not bag.is_valid():
    print('|master bag is corrupted!')
    quit()
else:
    print('|master bag is validated!')

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
if not bag.is_valid():
    print('|working bag is corrupted!')
    quit()
else:
    print('|working bag is validated!')

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
