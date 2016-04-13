#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
from game import Game
from datetime import datetime, date
from socket import *

class euro(object):
	"""docstring for euro"""
	def __init__(self,port):
		super(euro, self).__init__()

		self.group_colors = ['#BBF3BB','#BBF3BB','#BBF3FF','transparent']
		self.colors = self.get_colors()
		self.PORT = port
		self.buffersize = 1024
		self.read_teams()
		self.footer = self.read_template('templates/footer_template.html')
		self.games = self.read_games_info()
		self.start_server()

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

	def read_teams(self):
		teams = dict()
		groups = dict()
		with open('resources/teams.txt','r') as f:
			for team in f.read().split('\n'):
				team = team.split('\t')
				teams[team[0]] = dict()
				teams[team[0]]['groups'] = team[1]
				teams[team[0]]['flag_url'] = team[2]

				if team[1] not in groups:
					groups[team[1]] = [team[0]]
				else:
					groups[team[1]].append(team[0])

		self.groups = groups
		self.teams = teams

	def create_game(self,info,stage):

		new_game = Game()
		if len(stage) == 1:
			new_game.stage = 'Groups'
			new_game.group = stage
		else:
			new_game.stage = stage

		info = info.split('\t')
		new_game.number = info[0]
		new_game.date = info[1].strip()
		
		new_game.t1 = info[2]
		new_game.t2 = info[3]
		new_game.location = info[4]
		if info[2] in self.teams:
			new_game.t1_flag = self.teams[info[2]]['flag_url']
		if info[3] in self.teams:
			new_game.t2_flag = self.teams[info[3]]['flag_url']

		# print new_game.number,new_game.stage,new_game.group,new_game.date, new_game.t1, new_game.t2,new_game.location
		return new_game

	def read_template(self,filename):

		with open(filename,'r') as f:
			return f.read()

	def read_games_info(self):
		games = []

		with open('resources/data.txt','r') as f:
			data = f.read().split('\n')
			i = 0
			current_stage = ''

			while i<len(data):
				if len(data[i]) < 15:
					current_stage = data[i]
					i+=1
				games.append(self.create_game(data[i],current_stage))
				i+=1			

		return games

	def fill_game_template(self,g):

		game_template = self.read_template('templates/game_template.html')

		date_object = datetime.strptime(g.date,'%d %B %Y %H:%M')

		remain = date_object - datetime.now()

		if remain.days > 0:
			remain = 'in ' + str(remain.days) + ' days'

		return game_template.format(date=g.date.replace('2016',''),location=g.location,t1=g.t1,t2=g.t2,t1_flag=g.t1_flag,t2_flag=g.t2_flag,number=g.number,remain=remain)

	def create_scheduele_with_groups(self):

		main = self.read_template('templates/scheduele_template.html')
		nav = self.read_template('templates/nav_template.html')

		games_html = ''

		for group in sorted(self.groups):

			games_html += self.read_template('templates/group_template.html')

			positions_htmls = []
			for i,team in enumerate(self.groups[group]):
				group_postion_html = self.read_template('templates/group_position_template.html')
				positions_htmls.append(group_postion_html.format(pos=i,team=team,team_flag = self.teams[team]['flag_url'],color = self.group_colors[i]))

			games_html = games_html.format(group = group, t1=positions_htmls[0],t2=positions_htmls[1],t3=positions_htmls[2],t4=positions_htmls[3])

			for G in self.games:
				if G.group == group:
					games_html += self.fill_game_template(G)

		for phase in ['Round of 16','Quarter-finals','Semi-finals','Final']:

				games_html += '<h3>'+phase+'</h3>'
				for game in [g for g in self.games if g.stage == phase]:
					games_html += self.fill_game_template(game)

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

	def handle_request(self,conn,addr,data):

		new_link = '../html/missing.html'

		if data == 'login':

			self.handle_new_login(conn,addr)

		elif data == 'agenda':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')

			#if len(data) == 3:

			#username = data[0]
			#s = data[1]
			#search = data[2]

			new_link = self.create_scheduele_with_groups()

			conn.send(new_link)

		elif data == 'rules':

			new_link = self.create_rules()

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

		self.serv.close()
		self.timed_print('euro server stopped','WARNING')


if __name__ == '__main__':

	PORT = 10000
	new_server = euro(PORT)


