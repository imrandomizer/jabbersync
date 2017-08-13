import sqlite3
import re
import time as tm
import os
import codecs

global currentUser
global DBLocation
global addressAppend


def convFromEpoch(time):
	a =   tm.strftime("%a %d %b %Y %H:%M:%S", tm.localtime((int(time)/1000) / 1000.0))
	return str(a)

def addDivTagtoWrite(message, stamp):
	return "<div id=\""+stamp+"\">"+message+"</div>"

#This is to push the "self" users message to proper queue
#This is done by getting the "item" number from the history_message table
#and matching this with "item" number in history_participants table
def writeUserMessageToRespectiveQueue(currentUser, message,time,itemnumber,connectionObject,stamp):
	global addressAppend
	result = connectionObject.execute('''SELECT * FROM history_participant where item='''+str(itemnumber)+''';''');
	for x in result:
		if(currentUser not in x[7]):
			#file = open("database/"+x[7]+".html","a")
			file = codecs.open(addressAppend+"database/"+x[7]+".html", "a", "utf-8")
			toWrite = '{}  :  {}  : '.format(time.ljust(30), currentUser.ljust(15)) + message + "<br>"
			file.write(addDivTagtoWrite(toWrite,stamp))
			file.close()

def writeToRespectiveFile(message,time,sendee,stamp):
	global addressAppend
	file = codecs.open(addressAppend+"database/"+sendee+".html","a","utf-8")
	try:
		sendee = sendee.replace("@informatica.com","")
		toWrite = '{}  :  {}  : '.format(time.ljust(30), sendee.ljust(15)) + message + "<br>"
		file.write(addDivTagtoWrite(toWrite,stamp))
	except:
		print(message)


def extractMessageFromHTML(obj):
	tryToFindText = re.search('<div>(.+?)</div>',str(obj))
	if tryToFindText:
		return tryToFindText.group(1)
	return ""

def getLastUpdateStamp():
	try:
		file = open("./database/data.app","r")
		data = file.read()
		file.close()
		if(len(data)<1):
			return 0
		return int(data)
	except:
		return 0

def updateLastStamp(stamp):
	file = open("./database/data.app","w")
	file.write(str(stamp))
	file.close()

def tryTofindDB(username):
	if(os.path.isdir("C:\\\\Users\\\\"+username+"\\\\AppData\\\\Local\\\\Cisco\\\\Unified Communications\\\\Jabber\\\\CSF\\\\History")):
		dataBasePath = "C:\\\\Users\\\\"+username+"\\\\AppData\\\\Local\\\\Cisco\\\\Unified Communications\\\\Jabber\\\\CSF\\\\History\\\\"+username+"@informatica.com.db"
		if(os.path.exists(dataBasePath)):
			print("Found jabber database "+dataBasePath+" \n Use this DB (y/n) ?")
			userinp = input()
			if(userinp.lower()=='y'):
				return True,dataBasePath
	return False,""

def pathExistWithWritePermission(path):
	if(os.path.isdir(path)):
		if not os.path.exists(path+"/database"):
			os.makedirs(path+'/database')
		return True
	else:
		print("Folder "+path+" Does not exists.")
		return False

def readConfig():
	global addressAppend
	if os.path.isfile('./database/app.config'):
		file = open("./database/app.config","r")
		strs = file.read().split("\n")
		if(len(strs)<1):
			print("app.config file is empty, please delete this file from present directory.")
		currentUser   = strs[0]
		DBLocation    = strs[1]
		if(len(strs)>2):
			addressAppend = strs[2]+"/"
			if(pathExistWithWritePermission(addressAppend)):
				pass
			else:
				print(addressAppend+ " path does not exits, please check the app.config file. Reverting to PWD." )
				addressAppend = ""
		else:
			addressAppend = ""
		file.close()
	else:
		print("not able to locate app.config in present working directory.")
		currentUser = input("your username eg 'nasinha' :")
		use,location = tryTofindDB(currentUser)
		if(use):
			DBLocation = location
		else:
			for x in range(0,500):
				DBLocation  = input('''Provide absolute database location for cisco jabber.\n eg (C:\\\\Users\\\\<username>\\\\AppData\\\\Local\\\\Cisco\\\\Unified Communications\\\\Jabber\\\\CSF\\\\History\\\\<username>@informatica.com.db) :''')
				if os.path.isfile(DBLocation):
					break
				print(DBLocation + "not a valid path.")
			pathToAppend = ""
		for x in range(0,500):
			pathToAppend = input("""Complete path to where you want the application to save chats ? (blank for present working directory):""")
			if(len(pathToAppend)<=1):
				addressAppend=os.getcwd()+"/"
				print("Writing the database files to "+str(addressAppend))
				break
			if(pathExistWithWritePermission(pathToAppend)):
				addressAppend = pathToAppend+"/"
				print("Writing the database files to "+str(addressAppend))
				break
			print("Enter a valid option.")

		file = open("./database/app.config","w")
		file.write(currentUser+"\n")
		file.write(DBLocation+"\n")
		file.write(addressAppend)
		file.close()
	return DBLocation, currentUser

def main():
	global addressAppend
	
	addressAppend = ""
	highest = getLastUpdateStamp()
	print("Last timestamp recorded was "+convFromEpoch(highest)+".")
	if not os.path.exists("database"):
		os.makedirs('database')
	DBLocation, currentUser = readConfig()

	#"C:\\Users\\nasinha\\AppData\\Local\\Cisco\\Unified Communications\\Jabber\\CSF\\History\\nasinha@informatica.com.db"
	print("Reading Database from :"+DBLocation)
	conn = sqlite3.connect(DBLocation)
	cursor = conn.execute("SELECT * FROM history_message where date > "+str(highest)+" ORDER BY date;")
	returned = 0
	for x in cursor:
		returned += 1
		message = extractMessageFromHTML(x[2])
		sendee  = x[4]
		time    = convFromEpoch(str(x[3]))
		if(highest < int(x[3])):
			highest = int(x[3])
		if(currentUser in sendee ):
			writeUserMessageToRespectiveQueue(currentUser, message,time,x[5],conn,str(x[3]))
		else:
			writeToRespectiveFile(message,time,sendee,str(x[3]))
	print(returned," new entries found in jabber databse.")
	conn.close()
	updateLastStamp(highest)

main()