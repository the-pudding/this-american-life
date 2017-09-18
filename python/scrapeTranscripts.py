from bs4 import BeautifulSoup
import requests
import json
import collections
import re
# using selenium because email addresses are loaded in to the DOM through JS and output a mess of JS if not loaded properly
from selenium import webdriver
browser1 = webdriver.Chrome()
browser2 = webdriver.Chrome()

startEpisodeNum = 1
endEpisodeNum =  624 #619. add # of most recent episode + 1 since range is exclusive
# no transcript for 374, will break if you try to access that episode

# removes brackets around names such as "[? Leisure ?]"
def cleanUpText (s):
	text = re.sub("\[\?\ ", "", s)
	text = re.sub("\ \?\]", "", text)
	return text

# main iterator
for episodeNum in range(startEpisodeNum, endEpisodeNum):
	if (episodeNum != 374):
		print "Parsing episode " + str(episodeNum)
		filename = '../transcripts/' + str(episodeNum) + '.json'
		# url1 is for transcript, url2 is main page for episode info
		url1 = "https://hw2.thisamericanlife.org/radio-archives/episode/" + str(episodeNum) + "/transcript"
		url2 = "https://hw2.thisamericanlife.org/radio-archives/episode/" + str(episodeNum)
		
		with open (filename, 'wb') as outfile:

			browser1.get(url1)
			browser2.get(url2)

			soup1 = BeautifulSoup(browser1.page_source, "html.parser")
			soup2 = BeautifulSoup(browser2.page_source, "html.parser")

			json_data = collections.OrderedDict()

			# get basic episode info
			episode_num = soup1.find('div', class_='radio-episode-num').get_text()
			episode_title = soup1.find('div', class_='radio').find('a').get_text()
			radio_date= soup1.find('div', class_='radio-date').get_text()[17:]
			transcript_url = url1

			json_data['episode_num'] = episode_num
			json_data['episode_title'] = episode_title
			json_data['radio_date'] = radio_date
			json_data['transcript_url'] = transcript_url

			# get scripts of each act
			num_acts = 0
			acts_data = []

			for act in soup1.findAll('div', class_='act'):
				single_act = collections.OrderedDict()
				num_dialogue_lines = 1

				# get basic act info
				single_act['id'] = act['id']
				single_act['title'] = act.find('h3').get_text()			
				contributors = []
				if num_acts < len(soup2.findAll('div', class_='act-body')):
					if single_act['title'] != "Credits.":
						if soup2.findAll('div', class_='act-body')[num_acts].find('p'):
							single_act['description'] = soup2.findAll('div', class_='act-body')[num_acts].find('p').get_text()
						else:
							single_act['description'] = soup2.findAll('div', class_='act-body')[num_acts].get_text()
						if soup2.findAll('div', class_='act-body')[num_acts].find('ul', class_='act-contributors'):
							for c in soup2.findAll('div', class_='act-body')[num_acts].find('ul', class_='act-contributors').findAll('a'):
								contributor = collections.OrderedDict()
								contributor['name'] = c.get_text()
								contributors.append(contributor)
					else:
						single_act['description'] = "Credits"
				else:
					single_act['description'] = "error"
				single_act['contributors'] = contributors
				num_acts += 1
				

				script_data = []
				# get script-level info
				for dialogue_lines in act.find('div', class_='act-inner').findAll('div'):
					dialogue_data = collections.OrderedDict()
					if dialogue_lines.find('h4'):
						# new dialogue line with different speaker from previous
						lastIdentifiedLineIndex = num_dialogue_lines-1
						dialogue_data['name'] = dialogue_lines.find('h4').get_text()
						dialogue_data['role'] = dialogue_lines['class'][0]
						dialogue_data['id'] = num_dialogue_lines
						dialogue_data['dialogue'] = ""
						for p in dialogue_lines.findAll('p'):
							dialogue_data['start_timestamp'] = p['begin']
							text = cleanUpText(p.get_text())
							# appends paragraphs into one long string
							if dialogue_data['dialogue'] == "":
								dialogue_data['dialogue'] += text
							else:
								dialogue_data['dialogue'] += " " + text
						script_data.append(dialogue_data)
						num_dialogue_lines += 1	
					else:
						# previous dialogue line continues with the same speaker. append to previous line
						for p in dialogue_lines.findAll('p'):
							script_data[lastIdentifiedLineIndex]['dialogue'] += " " + cleanUpText(p.get_text())
				single_act['script'] = script_data

				acts_data.append(single_act)

			json_data['acts'] = acts_data
			json.dump(json_data, outfile, indent=2)

browser1.Dispose()
browser2.Dispose()

# {
# 	"episode_num": "1",
# 	"episode_title": "New Begininings",
# 	"radio_data": "11.17.1995",
# 	"transcript_url": "blahblah",
# 	"acts": [
# 		{
# 			"id": "prologue"
# 			"title": "Prologue"
# 			"producers": [
# 				"name": "blah blah"
# 			]
# 			"script": [
# 				{
# 					"id": "1"
# 					"name": "Ira glass"
# 					"role": "host"
# 					"dialogue": "Blah blah blah"
# 				},
# 				{
# 					"id": "2"
# 					"name": "Joe bob"
# 					"role": "subject"
# 					"dialogue": "Blah blah blah"
# 				}
# 			]
# 		},
# 		{
# 			"id": "act 1"
# 			"title": "act 1"
# 			"producers": [
# 				"name": "blah blah"
# 			]
# 			"script": [
# 				{
# 					"id": "1"
# 					"name": "Ira glass"
# 					"role": "host"
# 					"dialogue": "Blah blah blah"
# 				},
# 				{
# 					"id": "2"
# 					"name": "Joe bob"
# 					"role": "subject"
# 					"dialogue": "Blah blah blah"
# 				}
# 			]
# 		}
# 	]
# }