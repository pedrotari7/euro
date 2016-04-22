#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading, json, urllib, ast, copy, os
import random, string
from operator import itemgetter
from datetime import datetime, date
from socket import *

class euro(object):
	"""docstring for euro"""
	def __init__(self,port):
		super(euro, self).__init__()
		self.final_stages = ['Round of 16','Quarter-finals','Semi-finals','Final']
		self.group_colors = ['#BBF3BB','#BBF3BB','#BBF3FF','transparent']
		self.points_colors = ['transparent','#F7DCDC','#F2EEC2','#C5E5E8','#CAF2BF']
		self.colors = self.get_colors()
		self.PORT = port
		self.buffersize = 250000
		self.teams = self.read_teams()
		self.footer = self.read_template('templates/footer_template.html')
		self.games = self.load_json('resources/games_current.json')
		self.users = self.load_json('users/info.json')

		self.load_users()

		user = unicode('João Pedro Alvito',encoding='utf-8')

		# self.create_new_user(user)
		print 'localhost/scripts/agenda?id='+self.users[user]['id']+'&user='+user.replace(' ','%20')

		

		#self.create_new_user('pedro')
		#self.games = self.read_games_info()

		self.start_server()

	## Internal functions

	def get_colors(self):
		colors = dict()

		colors['HEADER'] = '\033[95m'
		colors['OKBLUE'] = '\033[94m'
		colors['OKGREEN'] = '\033[92m'
		colors['WARNING']= '\033[93m'
		colors['FAIL'] = '\033[91m'
		colors['ENDC'] = '\033[0m'
		colors['BOLD'] = '\033[1m'
		colors['UNDERLINE'] = '\033[4m'
		colors['WORLD'] = '\033[1;97m'
		colors['PROJECTOR'] = '\033[1;32m'
		colors['VEHICLE'] = '\033[1;95m'
		colors['CMD'] = '\033[1;93m'
		colors['QUALISYS'] = '\033[1;96m'

		return colors

	def timed_print(self,message,color = None,parent= None):

		try:
			color = self.colors[color]
		except:
			color = ''
		try:
			parent = self.colors[parent]
		except:
			parent = ''

		print parent + self.get_current_time() + self.colors['ENDC'] + ' ' + color + message + self.colors['ENDC']

	def get_current_time(self):

		return datetime.now().strftime("%Y-%m-%d %H:%M:%S ")

	def start_thread(self,handler,args=()):
		t = threading.Thread(target=handler,args=args)
		t.daemon = True
		t.start()


	## Storing and Restoring

	def dump_json(self,data,filename):
		with open(filename,'w') as fp:
			json.dump(data,fp,sort_keys=True,indent=4, encoding="utf-8")

	def load_json(self,filename):
		if os.path.exists(filename):
			with open(filename, 'r') as fp:
				return json.load(fp, encoding='utf8')
		else:
			return {}

	def read_teams(self):
		teams = dict()
		groups = dict()
		with open('resources/teams.txt','r') as f:
			for team in f.read().split('\n'):
				team = team.split('\t')

				teams[team[0]] = dict()
				teams[team[0]]['name'] = team[0]
				teams[team[0]]['groups'] = team[1]
				teams[team[0]]['flag_url'] = team[2]
				teams[team[0]]['G'] = 0
				teams[team[0]]['GF'] = 0
				teams[team[0]]['GA'] = 0
				teams[team[0]]['W'] = 0
				teams[team[0]]['D'] = 0
				teams[team[0]]['L'] = 0
				teams[team[0]]['PTS'] = 0

				if team[1] not in groups:
					groups[team[1]] = [team[0]]
				else:
					groups[team[1]].append(team[0])

		self.groups = groups
		return teams

	def read_template(self,filename):

		with open(filename,'r') as f:
			return unicode(f.read(),encoding='utf-8')

	def read_games_info(self):
		games = dict()
		with open('resources/data.txt','r') as f:
			data = f.read().split('\n')
			i = 0
			current_stage = ''

			while i<len(data):
				if len(data[i]) < 15:
					current_stage = data[i]
					i+=1
				new_game = self.create_game(data[i],current_stage)		
				games[new_game['number']] = new_game
				i+=1			

		return games

	def create_game(self,info,stage):
		new_game = dict()
		if len(stage) == 1:
			new_game['stage'] = 'Groups'
			new_game['group'] = stage
		else:
			new_game['stage'] = stage

		info = info.split('\t')
		new_game['number'] = int(info[0])
		new_game['date'] = info[1].strip()
		
		new_game['t1'] = info[2]
		new_game['t2'] = info[3]
		new_game['location'] = info[4]
		new_game['score'] = ''
		new_game['winner'] = ''
		if info[2] in self.teams:
			new_game['t1_flag'] = self.teams[info[2]]['flag_url']
		if info[3] in self.teams:
			new_game['t2_flag'] = self.teams[info[3]]['flag_url']

		return new_game

	def clean_teams(self,teams):
		for team in teams:
				teams[team]['G'] = 0
				teams[team]['GF'] = 0
				teams[team]['GA'] = 0
				teams[team]['W'] = 0
				teams[team]['D'] = 0
				teams[team]['L'] = 0
				teams[team]['PTS'] = 0
		return teams


	## Users

	def id_generator(self, size=10, chars=string.ascii_uppercase + string.digits +string.ascii_lowercase):
		
		return ''.join(random.choice(chars) for _ in range(size))
   
	def create_new_user(self,user):

		if user not in self.users:
			self.users[user] = dict()

		self.users[user]['username'] = user

		if not  os.path.exists(os.path.join('users',user)):
			os.mkdir(os.path.join('users',user))

		p = os.path.join('users',user,'games.json')
		if os.path.exists(p):
			self.users[user]['games'] = self.load_json(p)
		else:
			self.users[user]['games'] = self.load_json('resources/games_clean.json')
			self.dump_json(self.games,p)

		self.users[user]['teams'] = self.read_teams()

		self.users[user]['points'] = dict()

		if 'country' not in self.users[user]:
			self.users[user]['country'] = ''

		self.clean_user_points(user)

		self.users[user]['id'] = self.id_generator()

		print user,self.users[user].keys()

	def load_users(self):
		for user in self.users:
			self.create_new_user(user)

	def clean_user_points(self,user):
		self.users[user]['points']['exact'] = 0
		self.users[user]['points']['right'] = 0
		self.users[user]['points']['one'] = 0
		self.users[user]['points']['none'] = 0
		self.users[user]['points']['groups'] = 0
		self.users[user]['points']['awards'] = 0
		self.users[user]['points']['PTS'] = 0

	def find_user_by_id(self,user_id):

		for user in self.users:
			print repr(user),self.users[user]['id'], user_id
			if self.users[user]['id'] == user_id:
				return user
		return ''

	def sort_users_scoreboard(self):

		print self.users.keys()

		scores = sorted([(self.users[u]['points']['PTS'],u) for u in self.users],reverse=True)

	 	return [self.users[user] for score,user in scores]

	def update_users_pontuations(self):

		for user in self.users:
			self.clean_user_points(user)
			self.users[user]['teams'] = self.clean_teams(self.users[user]['teams'])

			for game in self.games:

				self.users[user]['games'][game],self.users[user]['teams'] = self.parse_score(self.users[user]['games'][game],self.users[user]['teams'])
				
				self.prediction_result(user,self.games[game],self.users[user]['games'][str(game)])

			for group in sorted(self.groups):

				predicted_ordered_group = self.order_teams(self.groups[group],self.users[user]['teams'])
				real_ordered_group = self.order_teams(self.groups[group],self.teams)

				for i,T in enumerate(predicted_ordered_group):					
					if real_ordered_group[i]['name'] == T['name']:
						self.users[user]['points']['groups'] += 1
						self.users[user]['points']['PTS'] += 1

	## HTML creation

	def fill_game_template(self,desired_user,user,g,read_only = False):

		game_template = self.read_template('templates/game_template.html')

		date_object = datetime.strptime(g['date'],'%d %B %Y %H:%M')

		remain = date_object - datetime.now()

		if g['score']:
			remain = g['score']
		elif remain.days > 0:
			remain = 'in ' + str(remain.days) + ' days'


		t1_flag = g['t1_flag'] if 't1_flag' in g else ''
		t2_flag = g['t2_flag'] if 't2_flag' in g else ''

		result = 0

		t1_score = self.users[desired_user]['games'][str(g['number'])]['t1_score']
		t2_score = self.users[desired_user]['games'][str(g['number'])]['t2_score']

		result = self.prediction_result(desired_user,self.games[str(g['number'])],self.users[desired_user]['games'][str(g['number'])])

		if read_only:
			readonly = 'readonly'
		else:
			readonly = ''

		return game_template.format(id=self.users[user]['id'],color=self.points_colors[result],date=g['date'].replace('2016',''),location=g['location'],t1=g['t1'],t2=g['t2'],t1_flag=t1_flag,t2_flag=t2_flag,number=g['number'],remain=remain,t1_score=t1_score,t2_score=t2_score,read=readonly)

	def create_group_table_html(self,user,ordered_group,compare_group=[]):

		group_html = self.read_template('templates/group_template.html')
		positions_htmls = []

		for i,T in enumerate(ordered_group):

			group_postion_html = self.read_template('templates/group_position_template.html')
			
			if compare_group:
				if compare_group[i]['name'] == T['name']:
					self.users[user]['points']['groups'] += 1
					self.users[user]['points']['PTS'] += 1
					color = self.points_colors[4] 
				else:
					color = self.points_colors[1] 

			else:
				color = self.group_colors[i] 

			group_postion_html = group_postion_html.format(team=T['name'],team_flag = T['flag_url'],color = color,G=T['G'],GF=T['GF'],GA=T['GA'],GD=T['GF']-T['GA'],W=T['W'],L=T['L'],D=T['D'],PTS=T['PTS'])

			positions_htmls.append(group_postion_html)

		return positions_htmls, group_html

	def create_scheduele_with_groups(self,user,desired_user):

		if desired_user == user:
			main = self.read_template('templates/scheduele_template.html')
		else:
			main = self.read_template('templates/scheduele_read_only_template.html')

		nav = self.read_template('templates/nav_template.html')

		if self.users[user]['country'] in self.teams:
			flag = self.teams[self.users[user]['country']]['flag_url']
		else:
			flag = ''
		nav = nav.format(name=user, id=self.users[user]['id'], flag=flag)

		games_html = ''

		self.clean_user_points(desired_user)
		self.users[desired_user]['teams'] = self.clean_teams(self.users[desired_user]['teams'])
		self.teams = self.clean_teams(self.teams)

		for game in self.games:
			self.games[game],self.teams = self.parse_score(self.games[game],self.teams)
			self.users[desired_user]['games'][game],self.users[desired_user]['teams'] = self.parse_score(self.users[desired_user]['games'][game],self.users[desired_user]['teams'])


		for group in sorted(self.groups):

			table_html = self.read_template('templates/table_template.html')

			# Real
			ordered_group = self.order_teams(self.groups[group],self.teams)
			positions_htmls, group_html = self.create_group_table_html(desired_user,ordered_group)
			table_left = group_html.format(side='left',title='Real', t1=positions_htmls[0],t2=positions_htmls[1],t3=positions_htmls[2],t4=positions_htmls[3])


			# Predicted
			pred_ordered_group = self.order_teams(self.groups[group],self.users[desired_user]['teams'])
			positions_htmls, group_html = self.create_group_table_html(desired_user,pred_ordered_group, compare_group=ordered_group)
			table_right = group_html.format(side='right',title='Predicted', t1=positions_htmls[0],t2=positions_htmls[1],t3=positions_htmls[2],t4=positions_htmls[3])


			games_html += table_html.format(group= group,left=table_left,right=table_right)

			games_html += '<br>'

			group_games = []
			for G in self.games:
				if 'group' in self.games[G] and self.games[G]['group'] == group:
					group_games.append(self.games[G])

			group_games = sorted(group_games, key=itemgetter('number'))

			for G in group_games:
				games_html += self.fill_game_template(desired_user,user,self.games[str(G['number'])],user!=desired_user)

		games_html += '<h2 id="Knockout">Knockout Stage</h2>'

		for phase in self.final_stages:
				games_html += '<h3 id="'+ phase +'">'+phase+'</h3>'
				for game in [self.games[g] for g in self.games if self.games[g]['stage'] == phase]:
					games_html += self.fill_game_template(desired_user,user,game,user!=desired_user)

		main = main.format(id=self.users[desired_user]['id'], nav = nav ,data = games_html, footer = self.footer)

		return main.encode('utf-8')

	def create_rules(self,user):

		main = self.read_template('templates/rules_template.html')
		nav = self.read_template('templates/nav_template.html')	

		if self.users[user]['country'] in self.teams:
			flag = self.teams[self.users[user]['country']]['flag_url']
		else:
			flag = ''
		nav = nav.format(name=user, id=self.users[user]['id'], flag=flag)

		main = main.format(nav = nav, footer = self.footer)

		return main.encode('utf-8')

	def update_predictions(self,user,data):
		
		self.users[user]['games'] = self.load_json('resources/games_clean.json')

		for pred in ast.literal_eval(data):
			if 'None' not in pred[1]:
				self.users[user]['games'][pred[0]] = copy.copy(self.games[pred[0]])
				self.users[user]['games'][pred[0]]['score'] = pred[1]

	def create_scoreboard(self,user):

		main_html = self.read_template('templates/scoreboard_template.html')
		nav = self.read_template('templates/nav_template.html')

		self.update_users_pontuations()

		if self.users[user]['country'] in self.teams:
			flag = self.teams[self.users[user]['country']]['flag_url']
		else:
			flag = ''
		nav = nav.format(name=user, id=self.users[user]['id'], flag=flag)	

		lines = self.create_scoreboard_user(user)

		main_html = main_html.format(id=user, nav = nav, lines = lines, footer = self.footer)

		return main_html.encode('utf-8')

	def create_scoreboard_user(self,user):

		positions = ''

		users = self.sort_users_scoreboard()

		for i,U in enumerate(users):

			position_html = self.read_template('templates/scoreboard_position_template.html')

			S = U['points']

			if user == U['username']:
				color = '#CAF2BF'
			else:
				color = ''

			flag = self.teams[self.users[U['username']]['country']]['flag_url']

			positions += position_html.format(pos=i+1,color=color,id = self.users[user]['id'] ,flag = flag ,name=U['username'],exact=S['exact'],right=S['right'],one=S['one'],none=S['none'], points=S['PTS'] ,groups=S['groups'],awards=S['awards'])

		return positions

	def create_settings(self,user):
		
		main_html = self.read_template('templates/settings_template.html')
		nav = self.read_template('templates/nav_template.html')

		if self.users[user]['country'] in self.teams:
			flag = self.teams[self.users[user]['country']]['flag_url']
		else:
			flag = ''
		nav = nav.format(name=user, id=self.users[user]['id'], flag=flag)	

		teams = [self.teams[t] for t in self.teams.keys()]

		teams = sorted(teams, key=itemgetter('name')) 

		countries = ''

		for team in teams:
			countries += '<a style="background-image:url('+ team['flag_url'].replace('23','200')  +');" class="settings_flag_link" href="../scripts/agenda?&country='+team['name'] +'&id='+ self.users[user]['id']+ '&user='+ user +'">'
			# countries += '<p>'+team['name']+'</p>'
			#countries += '<img class="settings_flag" src="'+ team['flag_url'].replace('23','150') +'"></img>'
			countries += '</a>'

		main_html = main_html.format(id=user, nav = nav, countries = countries, footer = self.footer)

		return main_html.encode('utf-8')		

	def create_game_page(self,user,game):

		main_html = self.read_template('templates/game_page_template.html')
		nav = self.read_template('templates/nav_template.html')

		# self.update_users_pontuations()


		if self.users[user]['country'] in self.teams:
			flag = self.teams[self.users[user]['country']]['flag_url']
		else:
			flag = ''
		nav = nav.format(name=user, id=self.users[user]['id'], flag=flag)

		g = self.games[game]	

		t1_flag = g['t1_flag'] if 't1_flag' in g else ''
		t2_flag = g['t2_flag'] if 't2_flag' in g else ''


		date_object = datetime.strptime(g['date'],'%d %B %Y %H:%M')

		remain = date_object - datetime.now()

		if g['score']:
			remain = g['score']
		elif remain.days > 0:
			remain = str(remain.days) + ' days'

		t1_score = g['t1_score']
		t2_score = g['t2_score']

		users_predictions=''

		for U in self.users:

			position_html = self.read_template('templates/game_page_position_template.html')

			g = self.users[U]['games'][game]

			result = self.prediction_result(user,self.games[game],g,points = False)

			score = g['score'] if g['score'] else '-'

			if 'flag_url' in self.teams[self.users[U]['country']]:
				flag = self.teams[self.users[U]['country']]['flag_url']

			users_predictions += position_html.format(id =self.users[user]['id'] ,name = self.users[U]['username'],flag=flag, score = score, color= self.points_colors[result])



		main_html = main_html.format(id=user,predictions=users_predictions,number=game,nav=nav,date=g['date'].replace('2016',''),location=g['location'],t1=g['t1'],t2=g['t2'],t1_flag=t1_flag,t2_flag=t2_flag,remain=remain,t1_score=t1_score,t2_score=t2_score, footer = self.footer)

		return main_html.encode('utf-8')


	## Football Functions

	def parse_score(self,game,teams):

		if game['score']:
			game['t1_score'],game['t2_score'] = [int(a) for a in game['score'].split('-')]
			teams[game['t1']]['G'] += 1
			teams[game['t1']]['GF'] += game['t1_score']
			teams[game['t1']]['GA'] += game['t2_score']

			teams[game['t2']]['G'] += 1
			teams[game['t2']]['GF'] += game['t2_score']
			teams[game['t2']]['GA'] += game['t1_score']

			if game['t1_score'] == game['t2_score']:
				game['winner'] = 'tie'
				if game['stage'] == 'Groups':
					teams[game['t1']]['D'] += 1
					teams[game['t1']]['PTS'] += 1
					teams[game['t2']]['D'] += 1
					teams[game['t2']]['PTS'] += 1
			elif game['t1_score'] > game['t2_score']:
				game['winner'] = game['t1']
				teams[game['t1']]['W'] += 1
				teams[game['t1']]['PTS'] += 3
				teams[game['t2']]['L'] += 1
			elif game['t1_score'] < game['t2_score']:
				game['winner'] = game['t2']
				teams[game['t1']]['L'] += 1
				teams[game['t2']]['PTS'] += 3
				teams[game['t2']]['W'] += 1
		else:
			game['t1_score'] = ''
			game['t2_score'] = ''

		return game,teams

	def order_teams(self,group,teams):

		group_teams = [teams[t] for t in group]

		ordered_teams = sorted(group_teams, key=itemgetter('PTS'), reverse = True) 

		return ordered_teams

	def prediction_result(self,user,real,predicted,points=True):

		if not predicted['score']:
			return 0
		elif real['score'] == predicted['score']:
			if points:
				self.users[user]['points']['exact'] +=1
				self.users[user]['points']['PTS'] += 5
			return 4
		elif real['winner'] == predicted['winner']:
			if points:
				self.users[user]['points']['right'] +=1
				self.users[user]['points']['PTS'] += 3
			return 3
		elif real['t1_score'] == predicted['t1_score']:
			if points:
				self.users[user]['points']['one'] +=1
				self.users[user]['points']['PTS'] += 1
			return 2
		elif real['t2_score'] == predicted['t2_score']:
			if points:
				self.users[user]['points']['one'] +=1
				self.users[user]['points']['PTS'] += 1
			return 2

		else:
			if points:
				self.users[user]['points']['none'] +=1
			return 1


	## Server

	def save_games(self):

		self.dump_json(self.games,'resources/games_current.json')

		for user in self.users:
			if 'games' in self.users[user]:
				self.dump_json(self.users[user]['games'],os.path.join('users',user,'games.json'))
				del self.users[user]['games']
			if 'teams' in self.users[user]:
				del self.users[user]['teams']


		self.dump_json(self.users,'users/info.json')

	def handle_request(self,conn,addr,data):

		new_link = '../html/missing.html'

		if data == 'login':
			print 'login'

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')

			if len(data) == 1:
				token = data[0]
				
				url = "https://www.googleapis.com/oauth2/v3/tokeninfo?id_token="+token
				response = urllib.urlopen(url)
				data = json.loads(response.read())
				
				print data['name'], repr(data['name'])

				user = data['name']

				print user, repr(user)
				is_new_user = user in self.users 

				print self.users.keys()

				self.create_new_user(user)
				self.users[user]['email'] = data['email']

				if not is_new_user:
					new_link = 'settings?&id=' + self.users[user]['id']
				else:
					new_link = 'agenda?&id=' + self.users[user]['id']+'&user='+user


			conn.send(new_link.encode('utf-8'))

		elif data == 'settings':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')
			user = self.find_user_by_id(data[0])

			print 'settings ' + user

			new_page = self.create_settings(user)

			conn.send(new_page)

		elif data == 'agenda':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')
			user = self.find_user_by_id(data[0])
			desired_user = unicode(data[1],encoding='utf-8')
			country = data[2]

			if country != 'None':
				self.users[user]['country'] = country

			print 'agenda ',data[0],user,country,desired_user


			new_page = self.create_scheduele_with_groups(user,desired_user)

			conn.send(new_page)

		elif data == 'rules':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')
			user = self.find_user_by_id(data[0])

			new_page = self.create_rules(user)

			conn.send(new_page)

		elif data == 'predict':

			print 'predict'

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')

			user = self.find_user_by_id(data[0])

			self.update_predictions(user,data[1])

			new_link = 'agenda?&id='+data[0]+'&user='+user 

			conn.send(new_link.encode('utf-8'))

		elif data == 'scoreboard':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')
			user = self.find_user_by_id(data[0])

			print 'scoreboard ' + user

			new_page = self.create_scoreboard(user)

			conn.send(new_page)

		elif data == 'game':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')
			user = self.find_user_by_id(data[0])
			game = data[1]

			print 'game ',data[0],user,game

			new_page = self.create_game_page(user,game)

			conn.send(new_page)


	def start_server(self):

		HOST = ''
		ADDR = (HOST,self.PORT)

		self.serv = socket( AF_INET,SOCK_STREAM)

		self.serv.setsockopt(SOL_SOCKET,SO_REUSEADDR, 1)

		try:
			self.serv.bind((ADDR))
			self.serv.listen(5)
			self.serv.settimeout(0.2)
		except:
			self.timed_print('euro server is already ON ' ,'FAIL')
			return

		self.timed_print('euro server is now started' ,'OKGREEN')

		while 1:
			try:
				try:
					conn,addr = self.serv.accept()
					conn.setblocking(1)
				except timeout:
					continue

				self.timed_print('IP: '+ str(addr[0]) + ' Port: ' + str(addr[1]) + ' ...connected!','OKBLUE')

				conn.send('ok')

				data = conn.recv(self.buffersize).lower().strip('\n').strip('\r')

				self.start_thread(self.handle_request, args = (conn,addr,data))

			except KeyboardInterrupt:
				# self.save_session()
				break


		self.save_games()

		self.serv.close()
		self.timed_print('euro server stopped','WARNING')


if __name__ == '__main__':

	PORT = 50000
	new_server = euro(PORT)


