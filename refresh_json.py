import json

def make_dict(f, output):
	abbrev = open(f, "r")
	d = {}

	for line in abbrev:
		line = line.split("\t")
		a = line[0]
		w = line[1].strip()
		if not a in d:
			d[a] = [w]
		else:
			d[a].append(w)

	with open(output, 'w') as out:
		json.dump(d, out)

def make_json(f, output):
	input = open(f, "r")
	d = {}
	for line in input:
		for word in line.split():
			word = word.lower()
			if not word in d:
				d[word] = 1
	with open(output, 'w') as out:
		json.dump(d, out)

make_dict('abbrev_word.txt','abbrev_word.json')
make_dict('abbrev_phrase.txt','abbrev_phrase.json')
make_dict('abbrev_sem.txt','abbrev_sem.json')
make_dict('correct.txt','correct.json')
make_json('ispell_dict.txt', 'dict.json')