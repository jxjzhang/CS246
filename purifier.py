# 1) squeeze(word) -> list of candidate words
# 2) edit_candidates(word, d) -> list of (word, d) within distance d
# 3) phonetic_candidates(word) -> list of (word, 1/2)
# compress(list of (word, d)) -> only keep any duplicate word tuple with the biggest distance
# iterate over list:
# abbrev_word(word) -> return list of words to replace the word abbreviation (if applicable)
# word_freq(word) -> return frequency and multiply with d
# -> list of tuples (candidate, p) where p is relative probability


import re, json, collections, numpy, math, string
from operator import itemgetter
import unicodedata
from soundex import *
from metaphone import *

class Mysqueezer:
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
    def find_duplicates(self,word):
        start=-1
        end = -1
        for i in range(len(word)-2):
            if word[i]==word[i+1] and word[i+1] == word[i+2]:
                start = i
                k = i+1
                while k<len(word) and word[k]==word[i]:
                    k+=1
                end = k-1
                break
        return (start,end)
    
    def squeeze(self,word):
        lists = []
        (start,end) = self.find_duplicates(word)
        lists += self.gen(word,start,end)     
        return lists
    def gen(self,word,start,end):
        ret = []
        if start==-1:
            ret.append(word)
            return ret
        list1 = word[0:start]+word[end:]
        list2 = word[0:start+1]+word[end:]
        (s,e) = self.find_duplicates(list1)
        ret += self.gen(list1, s, e) 
        (s,e) = self.find_duplicates(list2)
        ret += self.gen(list2, s, e)
        return ret

def norm(s):
	if isinstance(s, unicode):
		return unicodedata.normalize('NFKD', s).encode('ascii','ignore')
	else:
		return s


# removes the metadata on a raw tweet file (including retweet indicators)
# replaces @username with [username], and any links with [url]
def cleanse(line):
	line = norm(line)
	metadata = re.compile('^@\w+ \[\d+\]$')
	rtprefix = re.compile('^RT @\w+: ')
	user = re.compile('@\w+')
	url = re.compile('http(s)?://[^\s]+')

	if not metadata.match(line):
		m = rtprefix.search(line)
		if (m):
			line = line[m.end():]
		
		line = user.sub("[username]", line)
		line = url.sub("[url]", line)
		return line
	return ""

def cleanse_file(f, o):
	tweets = open(f, "r")
	output = open(o, "w")
	for line in tweets:
		output.write(cleanse(line))

# Returns a list of possible squeezed words
def squeeze(word):
	squeezer = Mysqueezer()
	return squeezer.squeeze(word)

def words(text): return re.findall('[a-z]+', text.lower()) 

def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model

def edits1(word):
   splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
   deletes    = [a + b[1:] for a, b in splits if b]
   transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
   replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
   inserts    = [a + c + b     for a, b in splits for c in alphabet]
   return set(deletes + transposes + replaces + inserts)

def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words): return set(w for w in words if w in NWORDS)

def correct(word):
    candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
#    if(known[word]) return (word,0)
#    if(edits1(word)) return (word,
    return max(candidates, key=NWORDS.get)
def correct_new(word):
    set0 = known([word])
    set1 = known(known(edits1(word)))
    set2 = known_edits2(word)

    lst = []
    tmp = list(set0)
    for i in tmp:
	lst.append((i,1.0))
    tmp = list(set1)
    for i in tmp:
	lst.append((i,1.0/(1+1)))
    tmp = list(set2)
    for i in tmp:
	lst.append((i,1.0/(1+2)))
    return lst	

def edit_candidates(word, d):
		
	return correct_new(word)

# Returns phonetic candidates (list of tuples)
# TODO(?): Check whether 0.5 is realistic
def phonetic_candidates_soundex(word, d):
	word=word.lower()
	phonetic_representation=soundex(word)[1]
	# print(phonetic_representation)
	soundex_candidates=[]
	if phonetic_representation in dict_inverted_soundex:
		word_list = dict_inverted_soundex[phonetic_representation]
		for w in word_list:
			soundex_candidates.append((w, 0.5*d))
		
	return soundex_candidates

def phonetic_candidates_metaphone(word, d):
	word=word.lower()
	metaphone_representation=doublemetaphone(word)
	metaphone_candidates=[]
	for element in metaphone_representation: 
		if element in dict_inverted_metaphone:
			word_list=dict_inverted_metaphone[element]
			for w in word_list:
				metaphone_candidates.append((w, 0.5*d))
	
	return metaphone_candidates
	

# Returns a compressed list of tuples that only include the maximum distance value per word
def compress(tuples):
	tuples = sorted(tuples, key=itemgetter(1), reverse=True)
	tuples = sorted(tuples, key=itemgetter(0))
	w = ""
	compressed = []
	for t in tuples:
		tuple = (norm(t[0]), t[1])
		if w != tuple[0]:
			w = tuple[0]
			compressed.append(tuple)
	return compressed

# Normalized dictionary lookup on single word abbreviations
def abbrev_word(word):
	if not word in dict_abbrword:
		return [word]
	else:
		return dict_abbrword[word]

# Normalized dictionary lookup on phrase abbreviations
def abbrev_phrase(word):
	if not word in dict_abbrphrase:
		return word
	else:
		return norm(dict_abbrphrase[word][0])

# Normalized dictionary lookup on semantic replacements
def sem(word):
	if not word in dict_sem:
		return word
	else:
		return norm(dict_sem[word][0])

# Normalized dictionary lookup on word frequency
def word_freq(word):
	if not word in dict_freq:
		return 0
	else:
		return dict_freq[word]

# Ranking the phonetic candidates by letter commonality
# Consonants worth more than vowels
# Returns the tracking value and the best viterbi value for global alignment
def read_scoring(scorefile):
    state = 0
    header = []
    sm = {}
    for line in open(scorefile, 'r'):
        line = line.rstrip('\n')
        line = line.rstrip('\r')
        if None == re.search('^#', line):
            a = line.split(' ')
            if 0 == state:
                header = a
                state = state + 1
            else:
                if len(a) != 1 + len(header):
                    print('error: the number of entries did not match the header')
                    sys.exit(2)
                for i in range(len(header)):
                    sm[a[0] + header[i]] = float(a[i+1])
    
    return sm

def bestglobal(m, sm, r, c, s1, s2, rpen, cpen):
	if (s1 not in alphabet):
		s1 = '*'
	if (s2 not in alphabet):
		s2 = '*'

	diag = m[r-1, c-1] + sm[s1 + s2]
	across = m[r, c-1] + cpen
	down = m[r-1, c] + rpen
	best = max(diag, across, down)

	if (best == down):
		t = -1
	elif (best == across):
		t = 1
	elif (best == diag):
		t = 0

	return (t, best)

def align(a, b, sm):
	n = len(a) + 1 # rows
	m = len(b) + 1 # cols
	rpenalty = -1
	cpenalty = -0.1

	gv = numpy.zeros(n * m).reshape(n, m) # global viterbi matrix
	gvtrack = numpy.zeros(n * m).reshape(n, m) # tracking for gv

	gvtrack[0,0] = '-999' # represents a start point in string alignment

	# initialize the gv matrix
	for i in range(0, m):
		gv[0, i] = i * cpenalty
		if (i != 0):
			gvtrack[0, i] = 1
	for i in range (0, n):
		gv[i, 0] = i * rpenalty
		if (i != 0):
			gvtrack[i, 0] = -1

	for r in range(1, n):
		for c in range (1, m):
			(t, v) = bestglobal(gv, sm, r, c, b[c-1], a[r-1], rpenalty, cpenalty)
			gv[r, c] = v
			gvtrack[r, c] = t
	return gv[n-1, m-1]

def tokenize(word):
	return list(word)

def letter_sim(word, candidate):
	score = align(word, word, dict_letters)
	sim = align(word, candidate, dict_letters)
	return sim/score

def viterbi_trim(candidates, word):
	c = []
	for tuple in candidates:
		sim = (letter_sim(word, tuple[0]) - phonetic_threshold)*(1/phonetic_threshold)
		if (sim >= 0):
			if (tuple[0] in NWORDS or tuple[0] in dict_sem or tuple[0] in dict_abbrphrase):
				sim *= 1.2 # TODO: arbitrary weight towards stuff in dict?
			c.append((tuple[0], tuple[1]*sim))
	return c


# TODO(?): Generate bigram frequency dictionary

# Returns a list of candidate word tuples in descending probability order
def word_correct(word):
	wordre = re.compile('[a-z][\w\-\']*')
	candidates = []
	
	a = abbrev_word(word)
	words = []
	for w in a:
		words += squeeze(w)
	
	c = []
	for w in words:
		candidates += edit_candidates(w, 1)
		candidates += phonetic_candidates_soundex(w, 1)
		candidates += phonetic_candidates_metaphone(w, 1)
		c += viterbi_trim(candidates, w)
		

	candidates = compress(c)
	c = []
	for t in candidates:
		if (t[1] * word_freq(t[0])) > 0:
			c.append((t[0], t[1] * math.log(word_freq(t[0]) + 1)))
	candidates = sorted(c, key=itemgetter(1), reverse=True)

	if not candidates:
		candidates = [(word, 1)]
	else:
		top = candidates[0][1]
		c = []
		# print candidates
		for t in candidates:
			if (t[1]/top >= word_threshold):
				c.append(t)
		if (word in NWORDS or not wordre.match(word)): # Add word back into candidates with highest score if in dict
			c.insert(0, (word,top))
		candidates = compress(c)
			
	candidates = sorted(candidates, key=itemgetter(1), reverse=True)
	return candidates

def text_correct(input, output):
	text = open(input, 'r')
	output = open(output, 'w')
	wordre = re.compile('[a-z][\w\-\']*')
	whitespace = re.compile('\s+')
	wordsplit = re.compile(r'([^a-zA-Z0-9-\'#\[\]]+)')
	
	for line in text:
		output.write(line)
		print line
		text_candidates = []
		clean_line = cleanse(line).lower()
		for word in (wordsplit).split(clean_line):
			if (wordre.match(word) and word != "2"):
				text_candidates.append(word_correct(word))
			elif (whitespace.match(word)):
				text_candidates.append([(word,0)])
			else:
				text_candidates.append([(word,-1)])

		for c in text_candidates:
			output.write(abbrev_phrase(sem(c[0][0]))) # Replace with semantic equiv, if applicable


def test_word():
	total = 0
	errors = 0
	for key in dict_correct:
		total += 1
		output = key + '\t'
		output += ','.join(dict_correct[key])

		c = []
		for t in word_correct(key):
			c.append(t[0])
		output += '\n\t' + ','.join(c)
		
		if not set(dict_correct[key]).intersection(set(c)):
			print output
			errors += 1
	print str(errors) + '/' + str(total) + ' errors'


# temporary globals: loading dictionaries
alphabet = 'abcdefghijklmnopqrstuvwxyz'
vowels = 'aeiou'

NWORDS = open("dict.json")
NWORDS = json.load(NWORDS)
dict_freq = open("wordFreqDict.json")
dict_freq = json.load(dict_freq)
dict_abbrword = open("abbrev_word.json")
dict_abbrword = json.load(dict_abbrword)
dict_abbrphrase = open("abbrev_phrase.json")
dict_abbrphrase = json.load(dict_abbrphrase)
dict_sem = open("abbrev_sem.json")
dict_sem = json.load(dict_sem)
dict_inverted_soundex=open("inverted_soundexDict.json")
dict_inverted_soundex=json.load(dict_inverted_soundex)
dict_inverted_metaphone=open("inverted_metaphoneDict.json")
dict_inverted_metaphone=json.load(dict_inverted_metaphone)
dict_letters = read_scoring("letter_scoring.txt")
dict_correct = open("correct.json")
dict_correct = json.load(dict_correct)
phonetic_threshold = 0.4 # used to trim the phonetic candidates
word_threshold = 0.7 # used to trim the word candidates

