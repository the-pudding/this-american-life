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
endEpisodeNum =  624
#623. add # of most recent episode + 1 since range is exclusive
# no transcript for 374, will break if you try to access that episode

# main iterator
for episodeNum in range(startEpisodeNum, endEpisodeNum):
	if (episodeNum != 374):
		print "Parsing episode " + str(episodeNum)
		filename = '../transcripts/ep' + str(episodeNum) + '.json'
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
			episode_description = soup2.find('div', class_="top").find('div', class_='description').get_text()
			radio_date= soup1.find('div', class_='radio-date').get_text()[17:]
			url = browser2.current_url
			image_url = soup2.find('div',class_="top").find('img')["src"]

			json_data['episode_num'] = episode_num
			json_data['episode_title'] = episode_title
			json_data['episode_description'] = episode_description
			json_data['radio_date'] = radio_date
			json_data['transcript_url'] = url
			json_data['image_url'] = image_url

			json.dump(json_data, outfile, indent=2)

browser1.Dispose()
browser2.Dispose()