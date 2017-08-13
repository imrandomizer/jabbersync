import sqlite3
import re
import time as tm
import os
import codecs
import sys
import re

global currentUser
global databaseLoc
databaseLoc = ""
htmlData = ""
#cmd will stay up even after search
persistent= 0

def locateDB():
	if os.path.isfile('./database/app.config'):
		file = open("./database/app.config","r" )
		strs = file.read().split("\n")
		if(len(strs)<1):
			print("app.config file is empty, please delete this file from present directory. Jabber sync search cannot work")
			input()
			sys.exit()
		currentUser   = strs[0]
		DBLocation    = strs[1]
		if(len(strs)>2):
			addressAppend = strs[2]+"/"
		else:
			addressAppend = os.getcwd()+"/"
		file.close()
		return addressAppend+"database/"
	print("./database/app.config file not found")
	input()
	sys.exit()
	return ""

def start():
	global databaseLoc
	if(os.path.isdir(locateDB())):
		databaseLoc = locateDB()
		#print(databaseLoc)
	else:
		print("Database location not found, application not started from jabber Sync local directory")
		input()
		sys.exit()
	#print("Using jabber sync database location as ",databaseLoc)


#returns the list of files in the database directory as list 
def generateFileList(DIR):
	lis = [name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]
	#print("Found ",len(lis)," files in the database directory.")
	return lis

#location of text "<br>" in an html
def locsOfdiv(data):
	brtags =[]
	for m in re.finditer("<br>",data):
		brtags.append(m.start())
	brtags.append(len(data))
	return brtags

def locOfPat(data, pat):
	locpat =[]
	#print("searching ",pat," in ",data)
	for m in re.finditer(pat,data):
		if(len(locpat)>=1):
			if(m.start()-locpat[len(locpat)-1]>10):
				locpat.append(m.start())
		else:
			locpat.append(m.start())
	return locpat

def putLink(string,tag,location):
	return "<a href=\"" + location+"#"+tag+string+"</a>"

def defaultListing(databaseLoc,fileList):
	htmlData1 = """<h2><p style="color:red;">Default Listing</p></h2>"""
	for files in fileList:
		htmlData1 += "<br><a href=\"" + databaseLoc+"/"+files+"\">"+files+"</a>"
	return htmlData1

def search(term,databaseLoc,fileList):
	global htmlData
	
	matches = 0
	for files in fileList:
		if("html" not in files ):
			continue
		#for each file 
		#codecs.open("database/"+x[7]+".html", "a", "utf-8")
		fileHandler = codecs.open(databaseLoc+"/"+files,"r","utf-8")
		#print(databaseLoc+"/"+files)
		data = fileHandler.read()
		data = data.lower()
		term = term.lower()
		fileHandler.close()
		loc_br = locsOfdiv(data)
		len_loc_br = len(loc_br)
		loc_pat = locOfPat(data,term)
		#print("loc _pat ",loc_pat)
		start = 0 
		end = 0
		tagQ = []
		if(len(loc_pat)>=1):
			#htmlData += databaseLoc+"/"+files+"<br>"
			htmlData += "<a href=\"" + databaseLoc+"/"+files+"\">"+files+"</a>"
			for location in loc_pat:

				for x in range(0,len_loc_br):
					if(location<loc_br[x]):
						end = x
						break
				start = loc_br[x-1]
				end   = loc_br[x]
				#print(start,end)
				messageQ = data[start+12:end+4]
				#print(messageQ)
				tagLocation = messageQ[7:25]
				
				linkText = putLink(messageQ[29:27+24],tagLocation,databaseLoc+"/"+files)
				#print("link text ",linkText)
				#htmlData += "<pre>"+"&#9;"+linkText+messageQ[27:]+"</pre>"
				if(tagLocation not in tagQ):
					#print("tag Q == ",tagQ)
					tagQ.append(tagLocation)
					relevantStr = messageQ[24+27:]
					relevantStr = relevantStr.replace(term,"<b>"+term+"</b>")
					matches += 1
					htmlData += "<pre>"+"&#9;"+linkText+relevantStr+"</pre>"
					
			htmlData += "<br><hr><br>"
	htmlData  = "<h1><center>Jabber Chat Archive</center></h1><br>"+"<h2>Search term :<b>"+term+"</b></h2>"+str(matches)+" Matches found.<br><br>"+htmlData
	if(matches==0):
		htmlData += "<br>"+defaultListing(databaseLoc,fileList)+"<br>"
	htmlData += """<br><br><br><p>Report bugs and suggest features <a href="mailto:nasinha@informatica.com?Subject=Jabber%20Chat%20Archiver" target="_top">here</a></p>"""
	return htmlData

def __main__():
	global databaseLoc
	global persistent
	global htmlData

	searchTerm = ""
	if(len(sys.argv)==1):
		print("No search term provided in argument \nSearch Term :")
		searchTerm = input()
	else:
		starting = 1
		if("-P" in sys.argv[1] or "-p" in sys.argv[1]):
			persistent = 1
			starting =2
		if("-H" in sys.argv[1] or "-h" in sys.argv[1]):
			print("Usage :\n<exe> <search term>\n<exe> -P <search term> to enable persistent search\n")
			sys.exit()

		for x in range(starting,len(sys.argv)):
			searchTerm += sys.argv[x]+" "
		searchTerm = searchTerm.strip()
	for x in range(1,100):
		start()
		result = ""
		files = generateFileList(databaseLoc)
		if(len(searchTerm)>2):
			print(searchTerm,len(searchTerm))
			#for debug
			#databaseLoc = "./database/db/"
			result = search(searchTerm,databaseLoc,files)
		else:
			result = "<h1><center>Jabber Chat Archive</center></h1><br>"
			result += """<h2><p style="color:red;">Serach term should contain atleast 3 characters : </p></h2>"""
			result += defaultListing(databaseLoc,files)
			result += """<br><br><br><p>Report bugs and suggest features <a href="mailto:nasinha@informatica.com?Subject=Jabber%20Chat%20Archiver" target="_top">here</a></p>"""
		res = open("result.html","wb")
		res.write(result.encode('utf-8'))
		res.close()
		os.system(r"cmd /c start  result.html")
		if(persistent==0):
			break
		else:
			print("Persistent searching (term):")
			htmlData = ""
			searchTerm = input()
			searchTerm = searchTerm.strip().lower()

__main__()
#print(databaseLoc)