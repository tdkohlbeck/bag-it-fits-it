#!/usr/bin/env python

import csv, filecmp, json, os, platform, re, shutil, subprocess, sys
import bagit, xmltodict

# TODO: fits flag so they don't have to move/download it
# TODO download/unzip fits if not present
# TODO command line option to point to already installed fits?

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
    ),
    'spaces': (
        '|| bag-it-fits-it.py\n'
        '| please remove all spaces from the output directory name'
        '| note: not sure if this is true for full Windows paths...'
    )
}


# structured dict to serial (flat) dict
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

# master:  the bag to archive (and not touch)
# output:  the directory to place the master and working
#          bags, xml reports, and csv report. (TODO: specify
#          these as optional flags?)
# to_bag:  the directory to archive and scrape for metadata
# wokring: the bag to scrape (and later examine)

# do some pre-flight checks
if len(sys.argv) <= 2:
    print(errors['arg_length'])
    quit()

output = sys.argv[2]
if re.search(r'(\s)', output):
    print(errors['spaces'])
    quit()


# directory locations
to_bag = os.path.abspath(sys.argv[1])
master = output + '/master-bag/'
working = output + '/working-bag/'
fits_xml = output + '/fits-xml/'


# create bags, directories
shutil.copytree(to_bag, master)
bag = bagit.make_bag(master)
bag.save()
shutil.copytree(master, working)
os.mkdir(fits_xml)
bag = bagit.Bag(master)

if not bag.is_valid():
    print('| WARNING: master bag is corrupted!')
else:
    print('| master bag is validated! :)')


# run FITS on working bag
fits_dir = ''
fits_script = ''

if platform.system() == 'Windows': # (special child)
    fits_script = r'\fits.bat'
else:
    fits_script = '/fits.sh'

for item in os.listdir('.'):
    is_fits = re.search(r'(fits)', item)
    is_dir = os.path.isdir(item)
    if is_fits and is_dir:
        fits_dir = item
cmd = (
    fits_dir + fits_script + ' -r' +
    ' -i ' + working + 'data/' +
    ' -o' + fits_xml +
    ' -x'
)
print('| running FITS on working directory:')
subprocess.call(cmd, shell=True)
print('| working directory successfully FITSed! :)')


# convert xml reports to dicts, compile in list
# TODO: remove unneeded sorted?
flatFitsDicts = []
fitsReportFiles = sorted(os.listdir(fits_xml))

# convert xmls to dicts and squash 'em
for filename in fitsReportFiles:
    fitsXmlReport = open(fits_xml + filename)
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
csvFile = open(output + '/report.csv', 'w')

manifest = working + '/manifest-sha256.txt'
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
            row = [ os.path.abspath(working + location) ]
    # TODO: bag location, not fits xml location
    for header in headers:
        if header != 'filepath' and header in fitsDict:
            row.append(fitsDict[header])
        elif header != 'filepath':
            row.append('?')
    rows.append(row)
    currentRow += 1


# validate working bag after scrape
bag = bagit.Bag(working)
if not bag.is_valid():
    print('| working bag is corrupted!')
else:
    print('| working bag is validated! :D')

clean_header_row = []
for header in headers:
    match = re.search(r'(\w+)$', header)
    clean_header_row.append(match.group())

pen = csv.writer(csvFile)
pen.writerow(clean_header_row)
pen.writerows(rows)

csvFile.close()
success_message = '| bags and report successfully created at: ' + os.path.abspath(output)
print(success_message)
