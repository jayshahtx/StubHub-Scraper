import json
import os

# Script to fix JSON syntax, after downloading all files, place this file in 
# folder with all the data and run once

def fixfile(fileName):
	with open (fileName, 'r') as myfile:
		data = myfile.read().replace('\n','')
		data = str(data)
		#add the prefix to the json
		pre = "{\"data\":["

		#modify the json to close properly
		data = data.replace('}','},')
		data = data[:-1]
		data = data + ']}'

		#combine for new file
		total = pre + data

		#write out new file
		fo = open(fileName,"wb")
		fo.write(total)
		fo.close()

#loop through all the files in the folder
def loopFolders():
	for i in os.listdir(os.getcwd()):
		if i.endswith("json.txt"):
			fixfile(i)

loopFolders()








