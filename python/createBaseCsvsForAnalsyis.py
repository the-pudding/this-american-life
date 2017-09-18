#meema spadola

import json
import csv

dialogueDict = []
episodesDict = []
actsDict = []

startEpisodeNum = 1
endEpisodeNum = 624

with open('../important/finalGender.json', 'rb') as genderfile:
    genderdata = json.load(genderfile)
    genderdata = dict((k.lower(), v) for k, v in genderdata.iteritems())
    
    for episodeNum in range(startEpisodeNum, endEpisodeNum):
        if (episodeNum != 374):
            print "Parsing episode " + str(episodeNum)
            filename = "../transcripts/" + str(episodeNum) + ".json"
            epfilename = "../transcripts/ep" + str(episodeNum) + ".json"
            with open(filename) as infile:
                data = json.load(infile)
                with open(epfilename) as infile2:
                    data2 = json.load(infile2)

                    episodesDict.append([episodeNum,
                                         data['radio_date'].split('.')[0],
                                         data['radio_date'].split('.')[1],
                                         data['radio_date'].split('.')[2],
                                         data2['episode_title'].encode('utf-8'),
                                         data2['episode_description'].encode('utf-8'),
                                         data2['image_url'],
                                         data2['transcript_url']
                                       ])

                    for act in data['acts']:
                        contributorList = ""
                        for contributor in act["contributors"]:
                            if contributorList == "":
                                contributorList += contributor["name"]
                            else:
                                contributorList += ", " + contributor["name"]

                        actsDict.append([episodeNum,
                                        act["id"],
                                        act["title"].encode('utf-8'),
                                        contributorList,
                                        act["description"].encode('utf-8')])
                        lineCount = 0
                        for line in act["script"]:
                            genderArr = genderdata[line["name"].strip().lower()]
                            gender = ""
                            if len(genderArr) == 1:
                                gender = genderArr[0].split()[0]
                            else:
                                for genderVal in genderArr:
                                    if int(genderVal.split()[1]) == episodeNum:
                                        gender = genderVal.split()[0]

                            dialogueDict.append([episodeNum,
                                                act["id"],
                                                lineCount,
                                                line["name"].encode('utf-8'),
                                                gender,
                                                line["role"],
                                                line["dialogue"].encode('utf-8'),
                                                line["start_timestamp"]])
                            lineCount += 1

    f = csv.writer(open("../important/gender.csv", "wb"))
    f.writerow(["name","gender","episode","timestamp"])
    for key, value in genderdata.iteritems():
        for x in value:
            f.writerow([key, x.split()[0], x.split()[1], x.split()[2]])

with open("../important/dialogue.tsv", 'wb') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    header = ["episode","act","dialogueId","name","gender","role","dialogue","timestamp"]
    writer.writerow(header)
    for item in dialogueDict:
        writer.writerow(item)

with open("../important/episodes.tsv", 'wb') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    episodeHeader = ["episode","month", "day", "year","title","description", "imageurl", "url"]
    writer.writerow(episodeHeader)
    for item in episodesDict:
        writer.writerow(item)

with open("../important/acts.tsv", 'wb') as outfile:
    writer = csv.writer(outfile, delimiter='\t')
    actsHeader = ["episode","act","title", "contributors", "description"]
    writer.writerow(actsHeader)
    for item in actsDict:
        writer.writerow(item)
    