#!/usr/bin/env python

import shutil, os, sys, subprocess
import bagit
import xmltodict, json
#from xmlutils.xml2json import xml2json


dirToBag = sys.argv[1]
archiveBagDir = sys.argv[2] + '/archive-bag'
examineBagDir = sys.argv[2] + '/examine-bag'
fitsXmlDir = sys.argv[2] + '/fits-xml/'

shutil.copytree(dirToBag, archiveBagDir)
os.mkdir(fitsXmlDir)

bag = bagit.make_bag(archiveBagDir)
bag.save()

shutil.copytree(archiveBagDir, examineBagDir)

subprocess.call(
    './fits/fits.sh -r -i ' +
    examineBagDir  +
    ' -o ' +
    fitsXmlDir +
    ' -x',
    shell=True
)

xml = open(fitsXmlDir + 'bagit.txt.fits.xml')
json = json.dumps(xmltodict.parse(xml.read()), indent=3)
xml.close()
jsonFile = open(fitsXmlDir + 'report.json', 'w+')
jsonFile.write(json)
jsonFile.close()

"""
subprocess.call(
    './json_to_csv.py ' +
    json


converter = xml2json(
    dirToBag + 'test.xml',
    fitsXmlDir + 'test.json',
    encoding='utf-8'
)
converter.convert()

converter = xml2json(
    fitsXmlDir + 'bagit.txt.fits.xml',
    fitsXmlDir + 'bagit.txt.fits.json',
    encoding='utf-8'
)
converter.convert()
"""
