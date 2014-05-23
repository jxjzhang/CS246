#! /usr/bin/python
import json

fname = raw_input("file name:")
try:
	fd = open(fname)
except:
	print 'File cannot be opened:', fname
	exit()

counts = dict()
for line in fd:
	words = line.split()
	for i in range(len(words)-1):
		if words[i].isalpha() and words[i+1].isalpha():
			word1 = words[i].lower()
			word2 = words[i+1].lower()
			tmp = word1+'#'+word2
			if tmp not in counts:
				counts[tmp] = 1
			else:
				counts[tmp] +=1
		
for i in counts.keys():
	if counts[i] <= 3:
		del counts[i]

with open('bigramDict.json','wb') as f:
	json.dump(counts,f)
