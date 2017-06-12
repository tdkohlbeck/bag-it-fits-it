#!/usr/bin/env python

import shutil, os, sys, subprocess
import bagit
import xmltodict, json

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
jsonStr = json.dumps(xmltodict.parse(xml.read()), indent=3)
xml.close()

def flattenJson(obj, delim):
    val = {}
    for i in obj.keys():
        if isinstance(obj[i], dict):
            get = flattenJson(obj[i], delim)
            for j in get.keys():
                val[ i + delim + j ] = get[j]
        else:
            val[i] = obj[i]
    return val

flatJson = flattenJson(json.loads(jsonStr), '__')

jsonFile = open(fitsXmlDir + 'report.json', 'w+')
jsonFile.write(json.dumps(flatJson, indent=2))
jsonFile.close()

"""
subprocess.call(
    './json_to_csv.py ' +
    'textMD:textMD ' +
    fitsXmlDir + 'report.json ' +
    fitsXmlDir + 'report.csv',
    shell=True
)


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
