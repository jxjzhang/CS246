# 1) squeeze(word) -> list of candidate words
# 2) edit_candidates(word, d) -> list of (word, d) within distance d
# 3) phonetic_candidates(word) -> list of (word, 1/2)
# compress(list of (word, d)) -> only keep any duplicate word tuple with the biggest distance
# iterate over list:
# abbrev_word(word) -> return list of words to replace the word abbreviation (if applicable)
# word_freq(word) -> return frequency and multiply with d
# -> list of tuples (candidate, p) where p is relative probability


import re, json, collections, numpy, math
from operator import itemgetter
import unicodedata

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
                print( start,k)
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
def phonetic_candidates(word, d):
	phonetic_representation=dict_soundex[word] # TODO (Shiwen): this should calculate the token, not look it up in case the word is new
	phonetic_representation=phonetic_representation[0]
	print(phonetic_representation)
	word_list =dict_inverted_soundex[phonetic_representation]
	phonetic_candidates=[]
	for w in word_list:
		if (letter_sim(word, w) > phonetic_threshold):
			phonetic_candidates.append((w, 0.5*d))
		
	return phonetic_candidates

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

def bestglobal(m, sm, r, c, s1, s2):
	if (s1 not in alphabet):
		s1 = '*'
	if (s2 not in alphabet):
		s2 = '*'

	diag = m[r-1, c-1] + sm[s1 + s2]
	across = m[r, c-1] + gpenalty
	down = m[r-1, c] + gpenalty
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
	
    gv = numpy.zeros(n * m).reshape(n, m) # global viterbi matrix
    gvtrack = numpy.zeros(n * m).reshape(n, m) # tracking for gv
    
    gvtrack[0,0] = '-999' # represents a start point in string alignment
    
    # initialize the gv matrix
    for i in range(0, m):
        gv[0, i] = i * gpenalty
        if (i != 0):
            gvtrack[0, i] = 1
    for i in range (0, n):
        gv[i, 0] = i * gpenalty
        if (i != 0):
            gvtrack[i, 0] = -1
	
    for r in range(1, n):
        for c in range (1, m):
            (t, v) = bestglobal(gv, sm, r, c, b[c-1], a[r-1])
            gv[r, c] = v
            gvtrack[r, c] = t
    return gv[n-1, m-1]

def letter_sim(word, candidate):
	score = align(word, word, dict_letters)
	sim = align(word, candidate, dict_letters)
	return sim/score

# Returns a list of candidate word tuples in descending probability order
def word_correct(word):
	words = squeeze(word)
	candidates = []
	for w in words:
		# TODO (Zijun): uncomment the line below when edit_candidates is fixed
		#candidates += edit_candidates(w, 1)
		candidates += phonetic_candidates(w, 1)

	candidates = compress(candidates)
	c = []
	for t in candidates:
		for expansion in abbrev_word(t[0]):
			if (t[1] * word_freq(expansion)) > 0:
				c.append((expansion, t[1] * word_freq(expansion)))

	print sorted(c, key=itemgetter(1), reverse=True)

# temporary globals: loading dictionaries
NWORDS = train(words(file('big.txt').read()))
alphabet = 'abcdefghijklmnopqrstuvwxyz'
vowels = 'aeiou'

dict_freq = open("wordFreqDict.json")
dict_freq = json.load(dict_freq)
dict_abbrword = open("abbrev_word.json")
dict_abbrword = json.load(dict_abbrword)
dict_soundex=open("soundexDict_hashTable.json")
dict_soundex=json.load(dict_soundex)
dict_inverted_soundex=open("inverted_soundexDict.json")
dict_inverted_soundex=json.load(dict_inverted_soundex)
dict_letters = read_scoring("letter_scoring.txt")
gpenalty = 0
phonetic_threshold = 0.5 # used to trim the phonetic candidates

