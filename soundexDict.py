#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import os

#fname = raw_input('Enter the file name: ')
#try:
#	fhand = open(fname)
#except:
#	print 'File cannot be opened:', fname
#	exit()
#
#counts=dict()

# b, f, p, v → 1
# c, g, j, k, q, s, x, z → 2
# d, t → 3
# l → 4
# m, n → 5
# r → 6
options = { 'b': 1,
		    'f': 1,
		    'p': 1,
			'v': 1,
		    'c': 2,
		    'g': 2,
			'j': 2,
		    'k': 2,
		    'q': 2,
		    's': 2,
			'x': 2,
		    'z': 2,
			'd': 3,
		    't': 3,
		    'm': 5,
		    'n': 5,
			'r': 6,
			'l': 4,
}

def checkLetter(character):
	return character not in "aeiouhwy"

from itertools import ifilter, imap
import json

def to_code(s):
    s = filter(checkLetter, s)
    return ''.join(map(lambda c: str(options[c]), s))

def make_dictionary(fp):
    words = (word for line in fp for word in line.split())
    words = ifilter(lambda w: w.isalpha(), words)
    words = imap(lambda w: w.lower(), words)
    words = imap(lambda w: (w, w[0] + to_code(w[1:])), words)
    d = dict(words)
    return d

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    with open(filename) as fp:
        d = make_dictionary(fp)
        with open('output.json', 'w') as out:
            json.dump(d, out)



