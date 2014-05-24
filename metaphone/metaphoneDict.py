from metaphone import doublemetaphone
from itertools import ifilter, imap
import json
def create_metaphone_dict(fp):
		words=(word for line in fp for word in line.split())
		words=imap(lambda w: w.lower(), words)
		words=imap(lambda w: purifyWord(w), words)
		metaphoneDict={}
		for word in words:
				if word not in metaphoneDict:
						metaphoneDict[word]=doublemetaphone(word)
		return metaphoneDict
def purifyWord(word):
		for letter in word:
			if not letter.isalpha():
				return ""	
		return word

if __name__=='__main__':
	import sys
	filename=sys.argv[1]
	with open(filename) as fp:
		d=create_metaphone_dict(fp)
		with open('metaphoneDict.json', 'w') as out:
				json.dump(d, out)
