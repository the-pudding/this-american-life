import json
import sexmachine.detector as gender
import collections

## todo: something with "dr. prefix"

def notSeenInEpisode(s, episodeNum):
	for info in s:
		# info.split()[] is a string and needs conversion to int for comparison
		if episodeNum == int(info.split()[1]):
			return False
	return True

def getGender(s):
	return s[0].split()[0]

def isGeneric(name):
	for i in name.split():
		if i in genericIndicators:
			return True
	return False

startEpisodeNum = 622
endEpisodeNum = 624 #619  #range is exclusive
# no transcript for 374, will break

femaleIndicators = ['Woman', 'Ms.', 'Mrs.', 'Miss', 'Sister', 'Wife', 'Mother', 'Grandmother', 'Daughter', 'Female', "Mom", 'Aunt', 'Auntie', 'Girl', 'Grandma', 'Women', 'Mary', 'Lady', 'Marie', 'Maria', 'Lindsey',  'Lindsay', 'Lynn', 'Ashley', 'Erin', 'Lauren', 'Kim', 'Courtney','Shannon', 'Connie','Carol']
# kim is female except kim jong il

maleIndicators = ['Ira', 'Man', 'Pa', 'Mr.', 'Brother', 'Husband', 'Father', 'Grandfather', 'Male', 'Uncle', "Dad", 'Son', 'Boy', 'President', 'Ryan', 'Chris', 'Sheikh','Kyle','Will','Ray', 'Guy']

groupIndicators = ['Audience', 'and', 'And', 'Chorus', 'Students', 'Choir', 'Class', 'Group', 'All', 'Children','Both', 'Crowd']

genericIndicators = ['Woman', 'Ms.', 'Mrs.', 'Miss', 'Sister', 'Wife', 'Mother', 'Grandmother', 'Daughter', 'Female', "Mom", 'Aunt', 'Auntie', 'Girl', 'Girls' 'Grandma', 'Women', 'Lady', 'Man', 'Pa', 'Mr.', 'Brother', 'Husband', 'Father', 'Grandfather', 'Male', 'Uncle', "Dad", 'Son', 'Boy', 'Audience', 'and', 'And', 'Chorus', 'Students', 'Choir', 'Class', 'Group', 'All', 'Children','Both', 'Crowd']

d = gender.Detector()
peopleDict = collections.OrderedDict()

for episodeNum in range(startEpisodeNum, endEpisodeNum):
	print "Parsing " + str(episodeNum)
	if (episodeNum != 374):
		data = []
		with open("../transcripts/" + str(episodeNum) + '.json') as f:
			data = json.load(f)
		for act in data['acts']:
			for dialogue_line in act['script']:
				dialogue_line['name'] = dialogue_line['name'].strip()
				name = dialogue_line['name']
				gender = d.get_gender(name.split(' ', 1)[0])

				# handle edge cases where people are described rather than named
				for i in femaleIndicators:
					if i in name.split():
						gender = 'F'
				for i in maleIndicators:
					if i in name.split():
						gender = 'M'
				for i in groupIndicators:
					if i in name.split():
						gender = "G"
				# add edge case 
				if gender == "female":
					gender = "F"
				elif gender == "male":
					gender = "M"
				elif gender == "mostly_male":
					gender = "MM"
				elif gender == "mostly_female":
					gender = "MF"
				elif gender == "andy":
					gender = "A"

				# special cases
				if name == "Kim Jong-il":
					gender = "M"

				if name not in peopleDict:
					info = []
					info.append(gender + " " + str(episodeNum) + " " + dialogue_line['start_timestamp'])
					peopleDict[name] = info
				elif (getGender(peopleDict.get(name)) == 'A' or isGeneric(name)) and notSeenInEpisode(peopleDict.get(name), episodeNum):
					peopleDict[name].append(gender + " " + str(episodeNum) + " " + dialogue_line['start_timestamp'])
				elif ((getGender(peopleDict.get(name)) == 'M' or getGender(peopleDict.get(name)) == 'F') and len(name.split()) == 1 and notSeenInEpisode(peopleDict.get(name), episodeNum)):
					peopleDict[name].append(gender + " " + str(episodeNum) + " " + dialogue_line['start_timestamp'])

with open ('../peopleTest.json', 'wb') as outfile:
	json.dump(peopleDict, outfile, indent=2)