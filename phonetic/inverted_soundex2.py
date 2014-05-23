import json

invertedDict={}

def inverted_soundex(json_data):
	for key in json_data.keys():
		
		if json_data[key] not in invertedDict:
			invertedDict[json_data[key]]=[key]
		else:
			if key not in invertedDict[json_data[key]]:
				invertedDict[json_data[key]].append(key)
		if key[0]=='d':
				invertedDict[json_data[key]].append("th"+key[1:])
		if len(key)>1 and key[0]=='t' and key[1]=='h':
				invertedDict[json_data[key]].append("d"+key[2:])

	return invertedDict
	
if __name__=='__main__':
	import sys
	filename=sys.argv[1]
	with open(filename) as fp:
		json_data=json.load(fp)
		d=inverted_soundex(json_data)
		with open('inverted_soundexDict2.json', 'w') as out:
			json.dump(d, out)
