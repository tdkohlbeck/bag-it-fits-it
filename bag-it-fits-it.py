#!/usr/bin/env python

import shutil, os, sys, subprocess
import bagit
import json, csv, xmltodict, jsonstocsv

dirToBag = sys.argv[1]
archiveBagDir = sys.argv[2] + '/master-bag'
examineBagDir = sys.argv[2] + '/working-bag'
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

fitsDicts = []
for filename in os.listdir(fitsXmlDir):
    fitsXmlReport = open(fitsXmlDir + filename)
    fitsDict = xmltodict.parse(fitsXmlReport.read())
    fitsXmlReport.close()

    flatFitsDict = flattenJson(fitsDict, '/')

    fitsDicts.append(flatFitsDict)
    allFitsReports = open(sys.argv[2] + 'reports.json', 'a+')
    allFitsReports.write(json.dumps(flatJson, indent=2))
    allFitsReports.write(',\n')
    allFitsReports.close()

#csvFitsReport = jsons-to-csv(flatJsonFitsReports)

headers = []
for fitsDict in fitsDicts:
    for key in fitsDict.keys():
        if key not in headers: headers.append(key)

csvFile = open(sys.argv[2]+'report.csv', 'w')
pen = csv.writer(csvFile)
pen.writerow(headers)

for fitsDict in fitsDicts:
    print('fitsDicts len: ' + str(len(fitsDicts)))
    row = []
    currentColumn = 0
    for key in fitsDict.keys():
        print('fitsDict len: ' + str(len(fitsDict.keys())))
        #print(json.dumps(fitsDict, indent=2))
        if key == headers[currentColumn]:
            print('currentColumn: ' + str(currentColumn))
            print('row length: ' + str(len(row)))
            row.append(fitsDict[key])
        else:
            row.append('')
        currentColumn += 1
    pen.writerow(row)

csvFile.close()

print(json.dumps(open(sys.argv[2]+'reports.json').read(), indent=2))
