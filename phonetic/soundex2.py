
import json

invertedDict={}

def inverted_soundex(json_data):
	for element in json_data:
		
		if element[0] not in invertedDict:
			invertedDict[element[0]]=[element[1]]

	return invertedDict
	
if __name__=='__main__':
	import sys
	filename=sys.argv[1]
	with open(filename) as fp:
		json_data=json.load(fp)
		d=inverted_soundex(json_data)
		with open('soundexDict2.json', 'w') as out:
			json.dump(d, out)
