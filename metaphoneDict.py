from metaphone import doublemetaphone
from itertools import ifilter, imap
import json

def create_metaphone_dict(fp):
		words=(word for line in fp for word in line.split())
		words=imap(lambda w: w.lower(), words)
		metaphoneDict={}
		for word in words:
				word2=purifyWord_deep(word)
				if word not in metaphoneDict:
						metaphoneDict[word]=doublemetaphone(word2)
		return metaphoneDict

def purifyWord(word):
		for letter in word:
			if not letter.isalpha() and not letter=="'":
				return False
			else:
				continue
		return True

def purifyWord_deep(word):
		toBeReturned=""
		if purifyWord(word):
				for letter in word:
					if letter.isalpha():
							toBeReturned=toBeReturned+letter
		return toBeReturned
				

if __name__=='__main__':
	import sys
	filename=sys.argv[1]
	with open(filename) as fp:
		d=create_metaphone_dict(fp)
		with open('metaphoneDict.json', 'w') as out:
				json.dump(d, out)

