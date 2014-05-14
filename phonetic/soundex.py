
from itertools import ifilter, imap
import json

#import unicodedata


#def _normalize(s):
#    return unicodedata.normalize('NFKD', _unicode(s))

def soundex(s):
    if not s:
        return s

#    s = _normalize(s)

    replacements = (('bfpv', '1'),
                    ('cgjkqsxz', '2'),
                    ('dt', '3'),
                    ('l', '4'),
                    ('mn', '5'),
                    ('r', '6'))
    result = [s[0]]
    count = 1

    # find would-be replacment for first character
    for lset, sub in replacements:
        if s[0].lower() in lset:
            last = sub
            break
    else:
        last = None

    for letter in s[1:]:
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
	words=ifilter(lambda w: w.isalpha(), words)
	words=imap(lambda w: w.lower(), words)
	#words = list(words)
	#d=soundex(words)
	d = imap(soundex, words)
	return list(d)

if __name__=='__main__':
	import sys
	filename=sys.argv[1]
	with open(filename) as fp:
		d=make_dictionary(fp)
		with open ('soundexDict.json', 'w') as out:
			json.dump(d, out)

