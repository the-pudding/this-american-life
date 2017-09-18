from bs4 import BeautifulSoup
import requests
import json
import collections
import cmd
import curses
import sys
import time

from selenium import webdriver


def addInfoToPeopleDict(name, gender, episodeNum, start_timestamp, peopleDict):
	if name not in peopleDict:
		info = []
		info.append(gender + " " + str(episodeNum) + " " + start_timestamp)
		peopleDict[name] = info
	else:
		peopleDict[name].append(gender + " " + str(episodeNum) + " " + start_timestamp)


def seek(hours, minutes, seconds, audioBrowser, firstTime):
	# firstTime is true when its the first time the episode is being played. if True, it'll play and then seek
	# convert hours minutes and seconds from string to useful numeric form
	numSeconds = hours * 3600 + minutes * 60 + seconds
	string = "jwplayer().seek(" + str(numSeconds) + ");"
	audioBrowser.execute_script(string)
	if firstTime:
		time.sleep(0.4)
		audioBrowser.execute_script(string)

def writeChar(c, w):
	w.insertln()
	w.erase()

def curses_main(name, episodeNum, start_timestamp, peopleDict, audioBrowser, outfile, w):
	hours = int(start_timestamp.split(':')[0])
	minutes = int(start_timestamp.split(':')[1])
	seconds = float(start_timestamp.split(':')[2])
	while 1:
		w.insertln()
		w.addstr("> " + name + ": ")
		c = w.getch()
		if c == ord('q'):
			curses.endwin()
			print "Quitting"
			audioBrowser.quit()
			json.dump(peopleDict, outfile, indent=2)
			sys.exit()
		elif c == ord('m'):
			# male
			addInfoToPeopleDict(name, "M", episodeNum, start_timestamp, peopleDict)
			writeChar(c, w)
			break
		elif c == ord('f'):
			# female
			addInfoToPeopleDict(name, "F", episodeNum, start_timestamp, peopleDict)
			writeChar(c, w)
			break
		elif c == ord('g'):
			# group
			addInfoToPeopleDict(name, "G", episodeNum, start_timestamp, peopleDict)
			writeChar(c, w)
		 	break
		elif c == ord('r'):
			# R = replay at timestamp
			seek(hours, minutes, seconds, audioBrowser, False)
			writeChar(c, w)
		elif c == ord('b'):
			# B = go back 5 seconds
			if seconds < 5:
				if minutes < 0:
					hours -= 1
					minutes = 59
					seconds = 60 + seconds - 5
				else:
					minutes -= 1
					seconds = 60 + seconds - 5
			else:
				seconds -= 5
			seek(hours, minutes, seconds, audioBrowser, False)
			writeChar(c, w)



def classify(name, gender, episodeNum, start_timestamp, peopleDict, audioBrowser, outfile, w):
	hours = int(start_timestamp.split(':')[0])
	minutes = int(start_timestamp.split(':')[1])
	seconds = float(start_timestamp.split(':')[2])

	url1 = "https://hw2.thisamericanlife.org/radio-archives/episode/" + str(episodeNum)

	# go to URL for jwplayer
	if audioBrowser.current_url != url1:
		audioBrowser.get(url1)
		seek(hours, minutes, seconds, audioBrowser, True)
	else:
		seek(hours, minutes, seconds, audioBrowser, False)

	curses_main(name, episodeNum, start_timestamp, peopleDict, audioBrowser, outfile, w)

######### main

peopleDict = collections.OrderedDict()
audioBrowser = webdriver.Chrome()
w = curses.initscr()
curses.echo()

# people.json comes out of getGender.py
# finalGender.json has all classified genders from getGender.py and the added on manually classified genders
# people2.json is the temp output file to be pasted into finalGender.json

with open ('finalGender.json') as infile1:
	with open ('people2.json', 'wb') as outfile:
		with open('people.json') as infile:
			gendered_people_data = json.load(infile1)
			people_data = json.load(infile, object_pairs_hook=collections.OrderedDict)
			for key, value in people_data.items():
				if key not in gendered_people_data:
					if len(value) == 1:
						# there is only one entity with this name that needs to be classified
						gender = value[0].split()[0]
						episodeNum = value[0].split()[1]
						start_timestamp = value[0].split()[2]
						if gender == "A" or gender == "MM" or gender == "MF":
							# then we need to classify it
							classify(key, gender, episodeNum, start_timestamp, peopleDict, audioBrowser, outfile, w)
					else:
						# there are multiple entities with this name that need to be classified
						for val in value:
							gender = val.split()[0]
							if gender == "A" or gender == "MM" or gender == "MF":
								# then we need to classify it
								episodeNum = val.split()[1]
								start_timestamp = val.split()[2]
								classify(key, gender, episodeNum, start_timestamp, peopleDict, audioBrowser, outfile, w)

		curses.endwin()
		print "FINISHED!!!!!!!!!!!!!!!!!!!"
		audioBrowser.quit()
		json.dump(peopleDict, outfile, indent=2)