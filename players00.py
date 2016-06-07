import urllib
import json
import os
from bs4 import BeautifulSoup as BS


def dump_json(data, filename):
	with open(filename, 'w') as fp:
		json.dump(data, fp, sort_keys=True, indent=4, encoding="utf-8")

main = 'http://www.thefinalball.com/'

alias = {
	"Switzerland": "Switzerland",
	"Albania": "Albania",
	"France": "France",
	"Romania": "Romania",
	"Russia": "Russia",
	"England": "England",
	"Wales": "Wales",
	"Slovakia": "Slovakia",
	"Germany": "Germany",
	"Ukraine": "Ukraine",
	"N. Ireland": "N. Ireland",
	"Poland": "Poland",
	"Croatia": "Croatia",
	"Czech Rep.": "Czech Rep.",
	"Turkey": "Turkey",
	"Spain": "Spain",
	"Ireland": "Ireland",
	"Italy": "Italy",
	"Belgium": "Belgium",
	"Sweden": "Sweden",
	"Hungary": "Hungary",
	# "Austria": "Austria",
	"Iceland": "Iceland",
	"Portugal": "Portugal",
}

teams = alias.keys()

teams_info = dict()

for team in teams:

	teams_info[team] = dict()

	if not os.path.exists(os.path.join('zerozero', team)):
		os.mkdir(os.path.join('zerozero', team))
	if not os.path.exists(os.path.join('images', 'teams', team)):
		os.mkdir(os.path.join('images', 'teams', team))

	with open('zerozero/' + team + '.html', mode='r') as f:

		print team

		s = BS(f.read(), 'lxml')

		print len(s.findAll(attrs={"class": "zztable"}))
		table = s.findAll(attrs={"class": "zztable"})[1]

		players = table.findAll('tr')[1:]

		for player in players:

			data = player.findAll('td')

			teams_info[team][data[1].text] = dict()
			teams_info[team][data[1].text]['num'] = data[0].text
			teams_info[team][data[1].text]['name'] = data[1].text
			teams_info[team][data[1].text]['pos'] = data[2].text
			teams_info[team][data[1].text]['age'] = data[3].text
			teams_info[team][data[1].text]['club'] = data[4].text
			teams_info[team][data[1].text]['link'] = main + data[1].a['href']

			file = 'zerozero/' + team + '/' + data[1].text + '.html'

			if os.path.exists(file):
				print data[1].text

				with open(file, 'r') as f:
					s = BS(f.read(), 'lxml')

					img_link = main + s.findAll('div',attrs={"class": "logo"})[0].a.img['src']
					term = img_link.split('.')[-1]
					teams_info[team][data[1].text]['term'] = term
					if not os.path.exists(os.path.join('images','teams',team,data[1].text+'.'+term)):
						print img_link
						urllib.urlretrieve(img_link, os.path.join('images','teams',team,data[1].text+'.'+term))


			else:
				print 'NOT OK'
				pass


dump_json(teams_info, 'resources/players.json')
