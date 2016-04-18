#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading, json, urllib, ast
from operator import itemgetter
from datetime import datetime, date
from socket import *

class euro(object):
	"""docstring for euro"""
	def __init__(self,port):
		super(euro, self).__init__()
		self.final_stages = ['Round of 16','Quarter-finals','Semi-finals','Final']
		self.group_colors = ['#BBF3BB','#BBF3BB','#BBF3FF','transparent']
		self.colors = self.get_colors()
		self.PORT = port
		self.buffersize = 250000
		self.read_teams()
		self.footer = self.read_template('templates/footer_template.html')
		self.games = self.load_json('resources/games.json')
		self.users = {'pedro':{'games':dict(),'teams':self.teams}}

		#self.games = self.read_games_info()
		for G in self.games:
			self.games[G],self.teams = self.parse_score(self.games[G],self.teams)

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
		with open(filename, 'r') as fp:
			return json.load(fp)

	def read_teams(self):
		teams = dict()
		groups = dict()
		with open('resources/teams.txt','r') as f:
			for team in f.read().split('\n'):
				team = team.split('\t')
				teams[team[0]] = dict()
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
		self.teams = teams

	def read_template(self,filename):

		with open(filename,'r') as f:
			return f.read()

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

		# print new_game.number,new_game.stage,new_game.group,new_game.date, new_game.t1, new_game.t2,new_game.location
		return new_game

	## HTML creation

	def fill_game_template(self,user,g):

		game_template = self.read_template('templates/game_template.html')

		date_object = datetime.strptime(g['date'],'%d %B %Y %H:%M')

		remain = date_object - datetime.now()

		if g['score']:
			remain = g['score']
		elif remain.days > 0:
			remain = 'in ' + str(remain.days) + ' days'


		t1_flag = g['t1_flag'] if 't1_flag' in g else ''
		t2_flag = g['t2_flag'] if 't2_flag' in g else ''

		if str(g['number']) in self.users[user]['games']:
			t1_score = self.users[user]['games'][str(g['number'])]['t1_score']
			t2_score = self.users[user]['games'][str(g['number'])]['t2_score']
		else:
			t1_score = ''
			t2_score = ''


		return game_template.format(date=g['date'].replace('2016',''),location=g['location'].encode('utf-8'),t1=g['t1'],t2=g['t2'],t1_flag=t1_flag,t2_flag=t2_flag,number=g['number'],remain=remain,t1_score=t1_score,t2_score=t2_score)

	def create_scheduele_with_groups(self,user):

		main = self.read_template('templates/scheduele_template.html')
		nav = self.read_template('templates/nav_template.html')

		print 'create scheduele'
		print self.users

		games_html = ''

		for group in sorted(self.groups):

			table_html = self.read_template('templates/table_template.html')

			# Real
			group_html = self.read_template('templates/group_template.html')
			positions_htmls = []

			for i,team in enumerate(self.groups[group]):

				group_postion_html = self.read_template('templates/group_position_template.html')

				group_postion_html = group_postion_html.format(team=team,team_flag = self.teams[team]['flag_url'],color = self.group_colors[i],G=self.teams[team]['G'],GF=self.teams[team]['GF'],GA=self.teams[team]['GA'],GD=self.teams[team]['GF']-self.teams[team]['GA'],W=self.teams[team]['W'],L=self.teams[team]['L'],D=self.teams[team]['D'],PTS=self.teams[team]['PTS'])

				positions_htmls.append(group_postion_html)


			table_left = group_html.format(side='left',title='Real', t1=positions_htmls[0],t2=positions_htmls[1],t3=positions_htmls[2],t4=positions_htmls[3])


			# Predicted
			group_html = self.read_template('templates/group_template.html')
			positions_htmls = []
			for i,team in enumerate(self.groups[group]):

				group_postion_html = self.read_template('templates/group_position_template.html')

				group_postion_html = group_postion_html.format(team=team,team_flag = self.users[user]['teams'][team]['flag_url'],color = self.group_colors[i],G=self.users[user]['teams'][team]['G'],GF=self.users[user]['teams'][team]['GF'],GA=self.users[user]['teams'][team]['GA'],GD=self.users[user]['teams'][team]['GF']-self.users[user]['teams'][team]['GA'],W=self.users[user]['teams'][team]['W'],L=self.users[user]['teams'][team]['L'],D=self.users[user]['teams'][team]['D'],PTS=self.users[user]['teams'][team]['PTS'])

				positions_htmls.append(group_postion_html)
			table_right = group_html.format(side='right',title='Predicted', t1=positions_htmls[0],t2=positions_htmls[1],t3=positions_htmls[2],t4=positions_htmls[3])


			games_html += table_html.format(group= group,left=table_left,right=table_right)

			group_games = []
			for G in self.games:
				if 'group' in self.games[G] and self.games[G]['group'] == group:
					group_games.append(self.games[G])

			group_games = sorted(group_games, key=itemgetter('number'))

			for G in group_games:
				self.games[str(G['number'])],self.teams = self.parse_score(self.games[str(G['number'])],self.teams)
				games_html += self.fill_game_template(user,self.games[str(G['number'])])

		games_html += '<h2 id="Knockout">Knockout Stage</h2>'

		for phase in self.final_stages:
				games_html += '<h3 id="'+ phase +'">'+phase+'</h3>'
				for game in [self.games[g] for g in self.games if self.games[g]['stage'] == phase]:
					games_html += self.fill_game_template(user,game)

		main = main.format(nav = nav ,data = games_html, footer = self.footer)

		file_location = 'html/agenda.html'

		with open(file_location,'w') as f:
			f.write(main)

		file_location = '../' + file_location
		return file_location

	def create_rules(self):

		main = self.read_template('templates/rules_template.html')
		nav = self.read_template('templates/nav_template.html')		

		main = main.format(nav = nav, footer = self.footer)

		file_location = 'html/rules.html'

		with open(file_location,'w') as f:
			f.write(main)

		file_location = '../' + file_location
		return file_location

	def update_predictions(self,user,data):
		
		for pred in ast.literal_eval(data[0]):
			if 'None' not in pred[1]:
				self.users[user]['games'][pred[0]] = self.games[pred[0]]
				self.users[user]['games'][pred[0]]['score'] = pred[1]
				self.users[user]['games'][pred[0]],self.users[user]['teams'] = self.parse_score(self.users[user]['games'][pred[0]],self.users[user]['teams'])

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

		return game,teams


	## Server

	def handle_request(self,conn,addr,data):

		new_link = '../html/missing.html'

		if data == 'login':
			print 'login'

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')

			if len(data) == 1:
				token = data[0]
				print token

		elif data == 'agenda':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')

			print 'agenda'
			print self.users

			#if len(data) == 3:

			#username = data[0]
			#s = data[1]
			#search = data[2]

			new_link = self.create_scheduele_with_groups('pedro')

			conn.send(new_link)

		elif data == 'rules':

			new_link = self.create_rules()

			conn.send(new_link)	

		elif data == 'predict':

			print 'predict'

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')

			print data

			self.users['pedro'] = self.update_predictions('pedro',data)

			new_link = 'agenda'

			conn.send(new_link)

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

		self.dump_json(self.games,'resources/games.json')
		self.serv.close()
		self.timed_print('euro server stopped','WARNING')


if __name__ == '__main__':

	PORT = 50000
	new_server = euro(PORT)


