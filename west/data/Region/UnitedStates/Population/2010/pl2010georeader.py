import fnmatch
import os
import re
import StringIO
import sys
import zipfile

rootPath = sys.argv[1]
pattern = '*.zip'
dataout = open('popbytract.csv','wb')
dataout.write('LOGRECNO,GEOID,AREALAND,AREAWATER,POP100,HU100\n')
for root, dirs, files in os.walk(rootPath) :
    for filename in fnmatch.filter(files, pattern):
        datafile =  os.path.join(root, filename)
        filehandle = open(datafile, 'rb')
        zfile = zipfile.ZipFile(filehandle)
        names = zfile.namelist()
        for name in names:
            if re.search('geo2010', name):
                data = StringIO.StringIO(zfile.read(name))
                for row in data: 
                    if row[8:11] == '140': #filter by tract
                        v1 = row[18:25]  #LOGRECNO 
                        v2 = row[27:29]+row[29:32]+row[54:60] #GEOID
                        v3 = row[198:212] #AREALAND
                        v4 = row[212:226] #AREAWATR
                        v5 = row[318:327] #POP100
                        v6 = row[327:336] #HU100
                        dataout.write( ','.join((v1.strip(),v2.strip(),v3.strip(),v4.strip(),v5.strip(),v6.strip()))+'\n')
        filehandle.close()
dataout.close()
