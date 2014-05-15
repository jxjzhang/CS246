# 1) squeeze(word) -> list of candidate words
# 2) edit_candidates(word, d) -> list of (word, d) within distance d
# 3) phonetic_candidates(word) -> list of (word, 1/2)
# compress(list of (word, d)) -> only keep any duplicate word tuple with the biggest distance
# iterate over list:
# abbrev_word(word) -> return list of words to replace the word abbreviation (if applicable)
# word_freq(word) -> return frequency and multiply with d
# -> list of tuples (candidate, p) where p is relative probability


import re
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



