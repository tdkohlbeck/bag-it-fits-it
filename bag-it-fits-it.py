#!/usr/bin/env python

# TODO: download/unzip fits if not present
# TODO: command line for location of fits.xml, csv, bags, etc.?
# TODO: convert spaghetti to list comprehensions
# TODO: lint(dirpath) to replace ' ' with '_', remove double slashes and flip if windows
# TODO: check for spaces in all options

from subprocess import call
import argparse, csv, filecmp, json, os, platform, re, shutil, sys
import bagit, xmltodict


parser = argparse.ArgumentParser(
    description=(
        '1. Creates two archive directories (working and master) using the BagIt specification, '
        '2. Runs FITS to generate xml reports on all working bag files, '
        '3. Compiles all xml reports into a single csv file'
    ),
    epilog=(
        'If master, working, xml, or csv are omitted, their location will default to output. '
        'If output is omitted, its location will default to input'
    )
)
parser.add_argument('input',
    help='the directory to bag \'n fits'
)
parser.add_argument('-o', '--output',
    help='the location to place bags and reports'
)
parser.add_argument('-m', '--master',
    help='the location to place the master bag'
)
parser.add_argument('-w', '--working',
    help='the location to place the working bag'
)
parser.add_argument('-x', '--xml',
    help='the location to place the fits.xml reports'
)
parser.add_argument('-c', '--csv',
    help='the location to place the csv report'
)
parser.add_argument('-f', '--fits',
    help='the location of the fits directory (if not in script directory)'
)
args = parser.parse_args()


errors = {
    'arg_length': (
        "|| bag-it-fits-it: ERROR\n"
        "| please provide:\n"
        "|  1. a directory to bag-n-fits\n"
        "|  2. optionally a directory to place output\n"
        "| if no second directory is provided, original location will be bagged\n"
        "| example: $ bag-it-fits-it.py /dir/to/bag /dir/to/output"
    ),
    'fits': (
        '|| bag-it-fits-it: ERROR\n'
        '| please place fits in same directory as script\n'
        '| and ensure the directory is named \'fits\''
    ),
    'spaces': (
        '|| bag-it-fits-it: ERROR\n'
        '| please remove all spaces from the output directory name'
        '| note: not sure if this is true for full Windows paths...'
    )
}

# util functions
def create_bags(in_dir, master_dir, working_dir):
    shutil.copytree(in_dir, master_dir)
    bag = bagit.make_bag(master_dir)
    bag.save()
    shutil.copytree(master_dir, working_dir)
def validate_bag(bag_dir):
    bag = bagit.Bag(bag_dir)
    good = bag_dir + ' validated!'
    bad = bag_dir + ' corrupted!'
    result = good if bag.is_valid() else bad
    print('| ' + result)
# structured dict to serial (flat) dict
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


if args.output and re.search(r'(\s)', args.output):
    print(errors['spaces'])
    quit()


to_bag = args.input
output = args.output + '/bags-and-reports/' if args.output else args.input + '/bags-and-reports/'
master = args.master + '/master/' if args.master else output + '/master/'
working = args.working + '/working/' if args.working else output + '/working/'
fits_xml = args.xml + '/fits-xml/' if args.xml else output + '/fits-xml/'
fits_dir = args.fits if args.fits else ''


# create bags, directories, validate master
create_bags(to_bag, master, working)
validate_bag(master)


# run FITS on working bag
is_win = platform.system() == 'Windows' # special child
fits_script = r'\fits.bat' if is_win else '/fits.sh'
if not fits_dir:
    print('| no fits location given, searching script directory...')
    for item in os.listdir('.'):
        is_fits = re.search(r'(fits)', item)
        is_dir = os.path.isdir(item)
        if is_fits and is_dir:
            print('| fits directory found!')
            fits_dir = item
    if not fits_dir:
        print('| unable to find a fits directory!')
        print('| please specify a location using the --fits option')
        print('| or place the fits directory in your script folder')
        quit()

os.mkdir(fits_xml)
print('| running FITS on working directory:')
call([
    fits_dir + fits_script,
    '-r',
    '-i',
    working + 'data/',
    '-o',
    fits_xml,
    '-x'
])
print('| working directory successfully FITSed! :)')


# convert xmls to dicts and squash 'em
flatFitsDicts = []
fitsReportFiles = os.listdir(fits_xml)
for filename in fitsReportFiles:
    fitsXmlReport = open(fits_xml + filename)
    fitsDict = xmltodict.parse(fitsXmlReport.read())
    fitsXmlReport.close()
    flatFitsDict = flattenDict(fitsDict, '__')
    flatFitsDicts.append(flatFitsDict)


# place all dict keys in a list for csv headers
headers = ['filepath']
for fitsDict in flatFitsDicts:
    for key in sorted(fitsDict):
        if key not in headers:
            headers.append(str(key))


# grab filepaths from bag manifest
manifest = working + '/manifest-sha256.txt'
file_locations = []
with open(manifest, 'r') as f:
    for line in f:
        match = re.search(r'(data.+)', line)
        if match:
            file_locations.append(match.group())
        else:
            file_locations.append('Not Found')


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
validate_bag(working)


# write headers and rows to csv
clean_header_row = []
for header in headers:
    match = re.search(r'(\w+)$', header)
    clean_header_row.append(match.group())
with open(output +'/report.csv', 'w') as f:
    pen = csv.writer(f)
    pen.writerow(clean_header_row)
    pen.writerows(rows)


# that's all folks!
success_message = (
    '| bags and report successfully created at: ' +
    os.path.abspath(output)
)
print(success_message)
