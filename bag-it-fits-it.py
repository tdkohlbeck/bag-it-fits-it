#!/usr/bin/env python

# TODO: download/unzip fits if not present
# TODO: convert spaghetti to list comprehensions
# TODO: lint(dirpath) to replace ' ' with '_', remove double slashes and flip if windows
# TODO: check for spaces in all options

from subprocess import call
import argparse, csv, filecmp, json, os, re, shutil, sys
import bagit, xmltodict
import utils


parser = argparse.ArgumentParser(
    description=(
        '1. Creates two archive directories (working and master) using the BagIt specification, '
        '2. Runs FITS to generate xml reports on all working bag files, '
        '3. Compiles all xml reports into a single csv file'
    ),
    epilog=(
        'If master, working, xml, or csv are omitted, their location will default to output. '
        'If output is omitted, its location will default to input. '
        'If fits is omitted, script will look for fits folder in the script folder. '
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


if args.output and re.search(r'(\s)', args.output):
    print(utils.errors['spaces'])
    quit()


output = utils.overload_path(args.output, args.input, '') # args.output + 'output/' if args.output else to_bag + 'output/'
master = utils.overload_path(args.master, output, 'master/') # args.master + 'master/' if args.master else output + 'master/'
working = utils.overload_path(args.working, output, 'working/') # args.working + '/working-bag/' if args.working else output + '/working/'
xml_dir = utils.overload_path(args.xml, output, 'fits_xml/') # args.xml + '/fits-xml/' if args.xml else output + '/fits-xml/'
report_dir = utils.overload_path(args.csv, output) # args.csv if args.csv else output
fits_dir = utils.overload_path(args.fits, '') # args.fits if args.fits else ''


utils.create_bags(args.input, master, working)
utils.validate_bag(master)
utils.run_fits(working, xml_dir, fits_dir)


# convert xmls to dicts and squash 'em
xml_files = [ xml for xml in os.listdir(xml_dir) ]
flat_reports = [
    utils.xml_to_flat_dict(xml_dir + xml)
    for xml in xml_files
]


# place every key in revery report in a list for csv headers
headers = ['filepath']
for report in flat_reports:
    for key in sorted(report):
        if key not in headers:
            headers.append(key)



# write values to relevant columns
filepaths = utils.bag_filepaths(working)
rows = []
current_row = 0
for report in flat_reports:
    for filepath in filepaths:
        report = xml_files[current_row]
        match = re.search(r'(.+)(?=.fits.xml)', report)
        filename = match.group()
        if filename == filepath[-len(filename):]:
            row = [ os.path.abspath(working + filepath) ]
    for header in headers:
        if header != 'filepath' and header in report:
            row.append(report[header])
        elif header != 'filepath':
            row.append('n/a')
    rows.append(row)
    current_row += 1


# validate working bag after scrape
utils.validate_bag(working)


# write headers and rows to csv
clean_header_row = []
for header in headers:
    match = re.search(r'(\w+)$', header)
    clean_header_row.append(
        utils.camel_case_to_spaces(match.group())
    )


with open(report_dir +'/report.csv', 'w+') as f:
    pen = csv.writer(f)
    pen.writerow(clean_header_row)
    pen.writerows(rows)


# that's all folks!
success_message = (
    '| SUCCESS! bags and report successfully created at: ' +
    os.path.abspath(output)
)
print(success_message)
