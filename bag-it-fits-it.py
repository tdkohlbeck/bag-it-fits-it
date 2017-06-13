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

cmd = './fits/fits.sh -r -i '+examineBagDir+' -o '+fitsXmlDir+' -x'
subprocess.call(cmd, shell=True)

xml = open(fitsXmlDir + 'bagit.txt.fits.xml')
jsonStr = json.dumps(xmltodict.parse(xml.read()))
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

#jsonFile = open(fitsXmlDir + 'report.json', 'w+')
#jsonFile.write(json.dumps(flatJson, indent=2))
#jsonFile.close()

for filename in os.listdir(fitsXmlDir):
    print(fitsXmlDir + filename)
    report = open(fitsXmlDir + filename)
    obj = xmltodict.parse(report.read())
    report.close()
    reports = open(sys.argv[2] + 'reports.json', 'a+')
    flatJson = flattenJson(obj, '__')
    reports.write(json.dumps(flatJson, indent=2))
    reports.close()
