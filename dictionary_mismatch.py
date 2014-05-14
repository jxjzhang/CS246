import re

tweets = open("tweets.txt", "r")
dictionary1 = open("/usr/share/dict/words", "r")
dictionary2 = open("google_dict.txt", "r")
dictionary3 = open("tv_dict.txt", "r")
dictionary4 = open("manual_dict.txt", "r")

abbrev = open("abbrev.txt", "r")
metadata = re.compile('^[@.* \[\d+\]|\-\-.*\-\-]$')
dictword = re.compile("^[\w|'|-]+$")
rtprefix = re.compile('^RT @\w+: ')
num = re.compile('^\d+$')

def populate_dict(dictionary, d, i):
	for line in dictionary:
		line = line.strip().lower()
		if dictword.match(line) and not line in d:
			d[line] = i
			i += 1

en_dict = {}
twitter_dict = {}
abbrev_dict = {}

i = 0
populate_dict(dictionary1, en_dict, i)
populate_dict(dictionary2, en_dict, i)
populate_dict(dictionary3, en_dict, i)
populate_dict(dictionary4, en_dict, i)

for line in abbrev:
	line = line.split()[0]
	if not line in abbrev_dict:
		abbrev_dict[line] = i
		i += 1


for line in tweets:
	if not metadata.match(line):
		m = rtprefix.search(line)
		if m:
			line = line[m.end():]
		for word in line.split():
			word = word.lower()
			if dictword.match(word):
				if not word in en_dict and not word in abbrev_dict and not num.match(word):
					if not word in twitter_dict:
						twitter_dict[word] = 1
					else:
						f = twitter_dict[word]
						twitter_dict[word] = f + 1

for w in sorted(twitter_dict, key=twitter_dict.get, reverse=False):
	print w, twitter_dict[w]