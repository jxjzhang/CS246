# 1) squeeze(word) -> list of candidate words
# 2) edit_candidates(word, d) -> list of (word, d) within distance d
# 3) phonetic_candidates(word) -> list of (word, 1/2)
# compress(list of (word, d)) -> only keep any duplicate word tuple with the biggest distance
# iterate over list:
# abbrev_word(word) -> return list of words to replace the word abbreviation (if applicable)
# word_freq(word) -> return frequency and multiply with d
# -> list of tuples (candidate, p) where p is relative probability


import re, json
from operator import itemgetter
import unicodedata

def norm(s):
	return unicodedata.normalize('NFKD', s).encode('ascii','ignore')

# removes the metadata on a raw tweet file (including retweet indicators)
# replaces @username with [username], and any links with [url]
def cleanse(f, o):
	metadata = re.compile('^@\w+ \[\d+\]$')
	rtprefix = re.compile('^RT @\w+: ')
	user = re.compile('@\w+')
	url = re.compile('http(s)?://.+')

	tweets = open(f, "r")
	output = open(o, "w")
	for line in tweets:
		if not metadata.match(line):
			m = rtprefix.search(line)
			if (m):
				line = line[m.end():]
			
			line = user.sub("[username]", line)
			line = url.sub("[url]", line)
			output.write(line)

# TODO: fill me out
def squeeze(word):
	return [word]

# TODO: fill me out with default distance 1/(1+n)
def edit_candidates(word, d):
	return [(word, 1)]

# TODO: fill me out with distance 0.5
def phonetic_candidates(word):
	phonetic_representation=dict_soundex[word]
	phonetic_representation=phonetic_representation[0]
	print(phonetic_representation)
	word_list =dict_inverted_soundex[phonetic_representation]
	phonetic_candidates=[]
	for word in word_list:
		phonetic_candidates.append((word, 0.5))
		
	return phonetic_candidates

# Returns a compressed list of tuples that only include the maximum distance value per word
def compress(tuples):
	tuples = sorted(tuples, key=itemgetter(1), reverse=True)
	tuples = sorted(tuples, key=itemgetter(0))
	w = ""
	for t in tuples:
		if w != t[0]:
			w = t[0]
		else:
			tuples.remove(t)
	return tuples

# Normalized dictionary lookup on single word abbreviations
def abbrev_word(word):
	if not word in dict_abbrword:
		return [word]
	else:
		return dict_abbrword[word]

# Normalized dictionary lookup on word frequency
def word_freq(word):
	if not word in dict_freq:
		return 0
	else:
		return dict_freq[word]

# Returns a list of candidate word tuples in descending probability order
def word_correct(word):
	words = squeeze(word)
	candidates = []
	for w in words:
		candidates += edit_candidates(w, 1)
		candidates += phonetic_candidates(w)

	candidates = compress(candidates)
	c = []
	for t in candidates:
		for expansion in abbrev_word(t[0]):
			c.append((expansion, t[1] * word_freq(expansion)))

	print sorted(c, key=itemgetter(1), reverse=True)

# temporary globals: loading dictionaries
dict_freq = open("wordFreqDict.json")
dict_freq = json.load(dict_freq)
dict_abbrword = open("abbrev_word.json")
dict_abbrword = json.load(dict_abbrword)
dict_soundex=open("soundexDict_hashTable.json")
dict_soundex=json.load(dict_soundex)
dict_inverted_soundex=open("inverted_soundexDict.json")
dict_inverted_soundex=json.load(dict_inverted_soundex)

