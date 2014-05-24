import json

inverted_metaphoneDict={}

def make_inverted_dict(json_data):
		for key in json_data.keys():
			represent=json_data[key]
			for element in represent:

				if not element=="" and element not in inverted_metaphoneDict:
						inverted_metaphoneDict[element]=[key]
				elif not element=="" and key not in inverted_metaphoneDict[element]:
						inverted_metaphoneDict[element].append(key)
		return inverted_metaphoneDict

if __name__=='__main__':
	 	import sys
		filename=sys.argv[1]
		with open(filename) as fp:
				json_data=json.load(fp)
				d=make_inverted_dict(json_data)
				with open("inverted_metaphoneDict.json","w") as out:
						json.dump(d, out)

