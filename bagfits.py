from pprint import pprint as pprnt
import os, pathlib, sys

input_dir = pathlib.Path(sys.argv[1]).absolute()
output_dir = pathlib.Path(sys.argv[2]).absolute()
master_dir = output_dir / 'master'
working_dir = output_dir / 'working'
fits_xml_dir = output_dir / 'fits_xml'


input_files = [
    str(file) for file in input_dir.rglob('*') # recursive search
    if file.is_file() # no directories!
]

pprnt(input_files)
