
import requests,os
import urllib

from bs4 import BeautifulSoup as BS

main = 'https://en.wikipedia.org'

link = main + '/wiki/UEFA_Euro_2016_squads'

r = requests.get(link)

s = BS(r.text,'lxml')


tables = s.findAll(attrs={"class":"sortable"})

teams_name = [t.text  for t in s.findAll(attrs={"class":"mw-headline"}) if 'Group' not in t.text and 'By ' not in t.text and 'References' not in t.text and 'Player' not in t.text] 


teams = dict()



for i,team_table in enumerate(tables):

	path = os.path.join('images','teams',teams_name[i])

	if not os.path.exists(path):
		os.mkdir(path)

	teams[teams_name[i]] = []

	for player in team_table.findAll('th'):
			if player.attrs['scope'] == 'row':

				new_player = dict()
				new_player['link'] = player.a.attrs['href']
				new_player['name'] = player.a.text
				teams[teams_name[i]].append(new_player)

				print new_player['name']
				r1 = requests.get(main + new_player['link'])
				s1 = BS(r1.text,'lxml')

				image = s1.find_all('a',{'class':'image'})

				if len(image) > 0:

					new_player['image'] = 'http:' + image[0].img['src']

					print new_player['image']

					urllib.urlretrieve(new_player['image'], os.path.join('images','teams',teams_name[i],new_player['name']+'.jpg'))


 	#teams[teams_name[i]] = [player for j,player in  enumerate(teams[teams_name[i]]) if j%2==0] 	
