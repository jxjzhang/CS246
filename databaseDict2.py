#!/usr/bin/python
import csv
import os
import json
from collections import OrderedDict
fname = raw_input('Enter the file name: ')
try:
    fhand = open(fname)
except:
    print 'File cannot be opened:', fname
    exit()

counts = dict()
num=0
for line in fhand:
	words = line.split()
	for word in words:
		if word.isalpha():
			word=word.lower()	
			if word not in counts:
				counts[word] = 1
			else:
				counts[word] += 1
		else:
			continue	
	#num+=1
	#if num>100:
		#break
counts=OrderedDict(sorted(counts.items(), key=lambda t: t[0]))	
	#counts=sorted(counts, key=lambda key: counts[key])
	#isorted(counts, key=counts.get)
with open ('outfile2.json','wb') as f:
	json.dump(counts,f)

#outfile.wri:te("\n".join(counts))
#outfile.close()

#print counts
