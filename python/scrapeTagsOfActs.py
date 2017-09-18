from bs4 import BeautifulSoup
import requests
import json
import collections
import re
import csv
import urllib2

startEpisodeNum = 1
endEpisodeNum =  624 #619. add # of most recent episode + 1 since range is exclusive
# no transcript for 374, will break

def replaceActIds(newid):
	if newid == "Prologue": return 0.0
	if newid == "Act One": return 0.01
	if newid == "Act Two": return 0.02
	if newid == "Act Three": return 0.03
	if newid == "Act Four": return 0.04
	if newid == "Act Five": return 0.05
	if newid == "Act Six": return 0.06
	if newid == "Act Seven": return 0.07
	if newid == "Act Eight": return 0.08
	if newid == "Act Nine": return 0.09
	if newid == "Act Ten": return 0.10
	if newid == "Act Eleven": return 0.11
	if newid == "Act Twelve": return 0.12
	if newid == "Act Thirteen": return 0.13
	if newid == "Act Fourteen": return 0.14
	if newid == "Act Fifteen": return 0.15
	if newid == "Act Sixteen": return 0.16
	if newid == "Act Seventeen": return 0.17
	if newid == "Act Eighteen": return 0.18
	if newid == "Act Nineteen": return 0.19
	if newid == "Act Twenty": return 0.20
	if newid == "credits": return 0.21
	return 0.99


actdata = {}
# main iterator
for episodeNum in range(startEpisodeNum, endEpisodeNum):
	if (episodeNum != 374):
		print "Parsing episode " + str(episodeNum)
		# url1 is for transcript, url2 is main page for episode info
		url2 = "https://hw2.thisamericanlife.org/radio-archives/episode/" + str(episodeNum)
		r2 = requests.get(url2)

		data2 = r2.text

		soup2 = BeautifulSoup(data2, "html.parser")

		num_acts = 0
		for act in soup2.findAll('div', class_='act'):
			if (act.find("h3")):
				actid = episodeNum + replaceActIds(act.find("h3").get_text())
				neighbor = act.findNext('div', class_="act-body")
				tags = []
				if neighbor.find('span', class_='tags'):
					for tag in neighbor.find('span', class_='tags').findAll('a'):
						tags.append(tag.get_text())
				else:
					tags.append("NONE")
				actdata[str(actid)] = tags
				num_acts += 1

with open('../important/test.csv', "wb") as csv_file:
  writer = csv.writer(csv_file, delimiter=',')
  writer.writerow(["episode-act","tags"])
  for key, value in actdata.iteritems():
		for tag in value:
			writer.writerow([key, tag])