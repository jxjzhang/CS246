import json

invertedDict={}

def inverted_soundex(json_data):
	for element in json_data:
		
		if element[1] not in invertedDict:
			invertedDict[element[1]]=[element[0]]
		else:
			if element[0] not in invertedDict[element[1]]:
				invertedDict[element[1]].append(element[0])

	return invertedDict
	
if __name__=='__main__':
	import sys
	filename=sys.argv[1]
	with open(filename) as fp:
		json_data=json.load(fp)
		d=inverted_soundex(json_data)
		with open('inverted_soundexDict.json', 'w') as out:
			json.dump(d, out)
