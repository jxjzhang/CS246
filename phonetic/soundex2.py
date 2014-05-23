
from itertools import ifilter, imap
import json

#import unicodedata


#def _normalize(s):
#    return unicodedata.normalize('NFKD', _unicode(s))
def purifyWord(word):

		for letter in word:
				if letter.isalpha() or letter=="'":
						continue
				else:
						return False
		return True

def purifyWord_deep(word):
		toBeReturned=""
		if purifyWord(word):
				for letter in word:
						if letter.isalpha():
								toBeReturned=toBeReturned+letter

		return toBeReturned

def soundex(s):
		if not s:
				return s
		s2=purifyWord_deep(s)

		replacements = (('bfpv', '1'),
						('cgjkqsxz', '2'),
						('dt', '3'),
						('l', '4'),
						('mn', '5'),
						('r', '6'))
		count=0
		result=""
		if len(s2)>0:
				result = [s2[0]]
				count = 1

	# find would-be replacment for first character
		for lset, sub in replacements:
				if len(s2)>0 and s2[0].lower() in lset:
						last = sub
						break
		else:
				last = None
		if len(s2) > 1:
				for letter in s2[1:]:
						for lset, sub in replacements:
								if letter.lower() in lset:
										if sub != last:
												result.append(sub)
												count += 1
										last = sub
										break
						else:
								last = None
						if count == 4:
								break

		result += '0'*(4-count)
		return (s, ''.join(result))


def make_dictionary(fp):
	words=(word for line in fp for word in line.split())
	#iwords=ifilter(lambda w: w.isalpha(), words)
	words=imap(lambda w: w.lower(), words)
	#words = list(words)
	#d=soundex(words)
	d = imap(soundex, words)
	return list(d)


invertedDict={}

def inverted_soundex(json_data):
		for element in json_data:
				#print(element)
				if purifyWord(element[0]):	
						#print(element)
						if element[0] not in invertedDict:
								
								invertedDict[element[0]]=element[1]

		return invertedDict
	
if __name__=='__main__':
	import sys
	filename=sys.argv[1]
	with open(filename) as fp:
		d=make_dictionary(fp)
		print(d)
		result=inverted_soundex(d)
		print(result)
		with open ('soundexDict2.json', 'w') as out:
			json.dump(result, out)

