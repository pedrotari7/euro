#!/usr/bin/python
# -*- coding: utf-8 -*-


import threading
import json
import urllib
import ast
import copy
import os
import sys
import random
import string
from operator import itemgetter
from datetime import datetime, date
from socket import *

reload(sys)
sys.setdefaultencoding('utf8')

class euro(object):
	"""docstring for euro"""

	def __init__(self, port):
		super(euro, self).__init__()

		# sys.stdout = open('logs/output.log', 'a+')
		# print 'test'
		self.folder = "/home/pedrotari7/Desktop/euro"
		self.final_stages = ['Round of 16',
							 'Quarter-finals', 'Semi-finals', 'Final']
		self.group_colors = ['#BBF3BB', '#BBF3BB', '#BBF3FF', 'transparent']
		self.points_colors = ['transparent',
							  '#F7DCDC', '#F2EEC2', '#C5E5E8', '#CAF2BF']
		self.colors = self.get_colors()
		self.PORT = port
		self.buffersize = 250000
		self.teams = self.read_teams()
		self.footer = self.read_template('templates/footer_template.html')
		self.games = self.load_json('resources/games_current.json')
		# self.games = self.read_games_info()
		self.thirdplace = self.load_json('resources/3place.json')
		self.third_group = []
		self.users = self.load_json('users/info.json')
		self.load_users()
		self.players = self.load_json('resources/players.json')

		# user = unicode('João Pedro Alvito', encoding='utf-8')

		# self.create_new_user(user)
		# print 'localhost/scripts/agenda?id=' + self.users[user]['id'] + '&user=' + user.replace(' ', '%20')

		# self.create_new_user('pedro')
		# self.games = self.read_games_info()

		self.update_users_pontuations()

		self.start_server()

	# Internal functions

	def get_colors(self):
		colors = dict()

		colors['HEADER'] = '\033[95m'
		colors['OKBLUE'] = '\033[94m'
		colors['OKGREEN'] = '\033[92m'
		colors['WARNING'] = '\033[93m'
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

	def timed_print(self, message, user,color=None, parent=None):

		try:
			color = self.colors[color]
		except:
			color = ''
		try:
			parent = self.colors[parent]
		except:
			parent = ''

		temp = ' ' + self.colors['OKGREEN'] + ' [' + user + '] ' + self.colors['ENDC']

		user = temp if user else ' '

		out = parent + self.get_current_time() + self.colors['ENDC'] + user + color + message + self.colors['ENDC']

		print out

		if not os.path.exists('logs'):
			os.mkdir('logs')
		with open('logs/output.log', 'a+') as f:
			f.write(out.encode('utf-8') + '\n')

	def get_current_time(self):

		return datetime.now().strftime("%Y-%m-%d %H:%M:%S ")

	def get_timeobject_now(self):

		return datetime.now()

		# return datetime(2016, 6, 10, 23, 0, 1)

	def start_thread(self, handler, args=()):
		t = threading.Thread(target=handler, args=args)
		t.daemon = True
		t.start()

	# Storing and Restoring

	def dump_json(self, data, filename):
		with open(os.path.join(self.folder, filename), 'w') as fp:
			json.dump(data, fp, sort_keys=True, indent=4, encoding="utf-8")

	def load_json(self, filename):
		filename = os.path.join(self.folder, filename)
		if os.path.exists(filename):
			with open(filename, 'r') as fp:
				return json.load(fp, encoding='utf8')
		else:
			return {}

	def read_teams(self):
		teams = dict()
		groups = dict()
		with open(os.path.join(self.folder, 'resources/teams.txt'), 'r') as f:
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

	def read_template(self, filename):

		with open(os.path.join(self.folder, filename), 'r') as f:
			return unicode(f.read(), encoding='utf-8')

	def read_games_info(self):
		games = dict()
		with open(os.path.join(self.folder, 'resources/data.txt'), 'r') as f:
			data = f.read().split('\n')
			i = 0
			current_stage = ''

			while i < len(data):
				if len(data[i]) < 15:
					current_stage = data[i]
					i += 1
				new_game = self.create_game(data[i], current_stage)
				games[new_game['number']] = new_game
				i += 1

		return games

	def create_game(self, info, stage):
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
		new_game['t1_original'] = info[2]
		new_game['t2_original'] = info[3]
		new_game['location'] = info[4]
		new_game['score'] = ''
		new_game['winner'] = ''
		if info[2] in self.teams:
			new_game['t1_flag'] = self.teams[info[2]]['flag_url']
		if info[3] in self.teams:
			new_game['t2_flag'] = self.teams[info[3]]['flag_url']

		return new_game

	def clean_teams(self, teams):
		for team in teams:
			teams[team]['G'] = 0
			teams[team]['GF'] = 0
			teams[team]['GA'] = 0
			teams[team]['GD'] = 0
			teams[team]['W'] = 0
			teams[team]['D'] = 0
			teams[team]['L'] = 0
			teams[team]['PTS'] = 0
			teams[team]['name'] = team
		return teams

	# Users

	def is_admin(self, user):
	
		return user == u'João Pedro Alvito'

	def id_generator(self, size=10, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):

		return ''.join(random.choice(chars) for _ in range(size))

	def create_new_user(self, user):

		if user not in self.users:
			self.users[user] = dict()

		self.users[user]['username'] = user

		if not os.path.exists(os.path.join(self.folder, 'users', user)):
			os.mkdir(os.path.join(self.folder, 'users', user))

		p = os.path.join(self.folder, 'users', user, 'games.json')
		if os.path.exists(p):
			self.users[user]['games'] = self.load_json(
				os.path.join('users', user, 'games.json'))
		else:
			self.users[user]['games'] = self.load_json(
				'resources/games_clean.json')
			self.dump_json(self.games, os.path.join(
				'users', user, 'games.json'))

		self.users[user]['teams'] = self.clean_teams(self.read_teams())

		self.users[user]['points'] = dict()

		if 'mvp' not in self.users[user]:
			self.users[user]['mvp'] = dict()
			self.users[user]['mvp']['country'] = ''
			self.users[user]['mvp']['name'] = ''

		if 'scorer' not in self.users[user]:
			self.users[user]['scorer'] = dict()
			self.users[user]['scorer']['country'] = ''
			self.users[user]['scorer']['name'] = ''


		if 'country' not in self.users[user]:
			self.users[user]['country'] = ''

		self.clean_user_points(user)

		self.users[user]['id'] = self.id_generator()

	def load_users(self):
		for user in self.users:
			self.create_new_user(user)

	def clean_user_points(self, user):
		self.users[user]['points']['exact'] = 0
		self.users[user]['points']['right'] = 0
		self.users[user]['points']['one'] = 0
		self.users[user]['points']['none'] = 0
		self.users[user]['points']['groups'] = 0
		self.users[user]['points']['awards'] = 0
		self.users[user]['points']['PTS'] = 0
		self.users[user]['points']['penalties'] = 0

	def find_user_by_id(self, user_id):

		for user in self.users:
			if self.users[user]['id'] == user_id:
				return user
		return ''

	def sort_users_scoreboard(self):

		scores = sorted([(self.users[u]['points']['PTS'], u) for u in self.users], reverse=True)

		return [self.users[user] for score, user in scores]

	def update_users_pontuations(self):

		self.teams = self.clean_teams(self.teams)

		for game in self.games:
			scoring = self.games[game]['stage'] == 'Groups'
			self.games[game], self.teams = self.parse_score(
				self.games[game], self.teams, scoring)

		self.third_group = []
		self.real_ordered_group = dict()
		for group in sorted(self.groups):
			self.real_ordered_group[group] = self.sort_teams(
				self.groups[group], self.teams, self.games)
			self.third_group.append(self.real_ordered_group[group][2])

		third_group_finished = all([team['G']>=3 for team in self.third_group]) 	

		self.sort_third_group()

		for user in self.users:
			self.clean_user_points(user)
			self.users[user]['teams'] = self.clean_teams(
				self.users[user]['teams'])

			for game in self.games:
				scoring = self.users[user]['games'][game]['stage'] == 'Groups'
				self.users[user]['games'][game], self.users[user]['teams'] = self.parse_score(
					self.users[user]['games'][game], self.users[user]['teams'], scoring)
				self.prediction_result(user, self.games[game], self.users[user]['games'][str(game)])

			self.users[user]['predicted_groups'] = dict()


			for group in sorted(self.groups):

				self.users[user]['predicted_groups'][group] = self.sort_teams(
					self.groups[group], self.users[user]['teams'], self.users[user]['games'])


				if all([team['G']>=3 for team in self.real_ordered_group[group]]):

					for i, T in enumerate(self.real_ordered_group[group]):
						if self.users[user]['predicted_groups'][group][i]['name'] == T['name']:
							self.users[user]['points']['groups'] += 1
							self.users[user]['points']['PTS'] += 1

		for game in self.games:
			game = self.games[game]
			if game['stage'] == 'Round of 16':

				if '1' in game['t1_original']:
					group = game['t1_original'].split('1')[1]
					team = self.real_ordered_group[group][0]['name']
					if self.teams[team]['G'] == 3:
						game['t1'] = team
				if '1' in game['t2_original']:
					group = game['t2_original'].split('1')[1]
					team = self.real_ordered_group[group][0]['name']
					if self.teams[team]['G'] == 3:
						game['t2'] = team
				if '2' in game['t1_original']:
					group = game['t1_original'].split('2')[1]
					team = self.real_ordered_group[group][1]['name']
					if self.teams[team]['G'] == 3:
						game['t1'] = team
				if '2' in game['t2_original']:
					group = game['t2_original'].split('2')[1]
					team = self.real_ordered_group[group][1]['name']
					if self.teams[team]['G'] == 3:
						game['t2'] = team

				if '3' in game['t2_original'] and third_group_finished:
					group = game['t1_original'].split('1')[1]
					a = ''.join([t['groups']for t in self.third_group][:4])
					a = ''.join(sorted(a))
					group = self.thirdplace[a][group]
					team = self.real_ordered_group[group][2]['name']
					if self.teams[team]['G'] == 3:
						game['t2'] = team

			if game['stage'] in ['Quarter-finals', 'Semi-finals', 'Final']:
				if self.games[game['t1_original']]['winner']:
					game['t1'] = self.games[game['t1_original']]['winner']
				if self.games[game['t2_original']]['winner']:
					game['t2'] = self.games[game['t2_original']]['winner']

			if game['t1'] in self.teams:
				game['t1_flag'] = self.teams[game['t1']]['flag_url']
			if game['t2'] in self.teams:
				game['t2_flag'] = self.teams[game['t2']]['flag_url']

	# HTML creation

	def create_nav(self, user):

		nav = self.read_template('templates/nav_template.html')

		if self.users[user]['country'] in self.teams:
			flag = self.teams[self.users[user]['country']]['flag_url']
		else:
			flag = ''

		if self.is_admin(user):
			admin = '<li><a href="../scripts/admin?&id='+self.users[user]['id']+'">Admin</a></li>'
			admin += '<li><a href="../logs/output.log">Logs</a></li>'

		else:
			admin = ''

		nav = nav.format(name=user, id=self.users[user]['id'], flag=flag, admin = admin)

		return nav

	def calculate_time_diference(self, g):

		readonly = ''
		remain = ''
		date_object = datetime.strptime(g['date'], '%d %B %Y %H:%M')

		diff = date_object - self.get_timeobject_now()
		if g['score']:
			remain = g['score']
		elif diff.days > 0:
			remain = 'in ' + str(diff.days) + ' days'
		elif diff.days == 0:
			remain = str(diff).split(".")[0]
		elif diff.days < 0:
			remain = 'Live'

		if g['stage'] == 'Groups' and (datetime(2016, 6, 10, 21, 0, 0) - self.get_timeobject_now()).days < 0:
			readonly = 'readonly'
		elif g['stage'] != 'Groups' and ((g['t1'] not in self.teams.keys()) or (g['t2'] not in self.teams.keys())):
			readonly = 'readonly'

		return readonly, diff, remain

	def fill_real_game(self, user, g):

		game_template = self.read_template('templates/admin_game_template.html')

		readonly, diff, remain = self.calculate_time_diference(g)

		if g['t1'] in self.teams:
			t1_link = 'team?&country='+g['t1']+'&id='+self.users[user]['id']
		else:
			t1_link = ''
		if g['t2'] in self.teams:	
			t2_link = 'team?&country='+g['t2']+'&id='+self.users[user]['id']
		else:
			t2_link = ''

		t1_flag = g['t1_flag'] if 't1_flag' in g else ''
		t2_flag = g['t2_flag'] if 't2_flag' in g else ''

		result = 0

		t1_score = self.games[str(g['number'])]['t1_score']
		t2_score = self.games[str(g['number'])]['t2_score']

		checked = 'checked' if g['finished'] else ''

		return game_template.format(is_finished = checked ,id=self.users[user]['id'], color='', date=g['date'].replace('2016', ''), location=g['location'], t1=g['t1'], t2=g['t2'], t1_flag=t1_flag, t2_flag=t2_flag, number=g['number'], remain=remain, t1_score=t1_score, t2_score=t2_score, t1_link=t1_link, t2_link=t2_link, read='')

	def fill_game_template(self, desired_user, user, g, read_only=False):

		game_template = self.read_template('templates/game_template.html')

		readonly, diff, remain = self.calculate_time_diference(g)

		if g['t1'] in self.teams:
			t1_link = 'team?&country='+g['t1']+'&id='+self.users[user]['id']
		else:
			t1_link = ''
		if g['t2'] in self.teams:	
			t2_link = 'team?&country='+g['t2']+'&id='+self.users[user]['id']
		else:
			t2_link = ''

		t1_flag = g['t1_flag'] if 't1_flag' in g else ''
		t2_flag = g['t2_flag'] if 't2_flag' in g else ''

		result = 0

		t1_score = self.users[desired_user]['games'][str(g['number'])]['t1_score']
		t2_score = self.users[desired_user]['games'][str(g['number'])]['t2_score']

		if t1_score!='' or diff.days < 0:
			if diff.days >= 0 and desired_user!=user:
				t1_score = 'X'
				t2_score = 'X'
			elif diff.days < 0:
				readonly = 'readonly'

		result = self.prediction_result(desired_user, self.games[str(
			g['number'])], self.users[desired_user]['games'][str(g['number'])])

		if read_only:
			readonly = 'readonly'

		return game_template.format(id=self.users[user]['id'], color=self.points_colors[result], date=g['date'].replace('2016', ''), location=g['location'], t1=g['t1'], t2=g['t2'], t1_flag=t1_flag, t2_flag=t2_flag, number=g['number'], remain=remain, t1_score=t1_score, t2_score=t2_score, t1_link=t1_link, t2_link=t2_link, read=readonly)

	def create_group_table_html(self, user, ordered_group, compare_group=[]):

		group_html = self.read_template('templates/group_template.html')
		positions_htmls = ''

		for i, T in enumerate(ordered_group):

			group_postion_html = self.read_template(
				'templates/group_position_template.html')

			if compare_group:
				if compare_group[i]['name'] == T['name']:
					self.users[user]['points']['groups'] += 1
					self.users[user]['points']['PTS'] += 1
					color = self.points_colors[4]
				else:
					color = self.points_colors[1]

			else:
				color = self.group_colors[i]

			group_postion_html = group_postion_html.format(team=T['name'], team_flag=T['flag_url'], color=color, G=T['G'], GF=T['GF'], GA=T['GA'], GD=T['GF'] - T['GA'], W=T['W'], L=T['L'], D=T['D'], PTS=T['PTS'])

			positions_htmls += group_postion_html

		return positions_htmls, group_html

	def create_scheduele_with_groups(self, user, desired_user, stage):

		if desired_user == user:
			main = self.read_template('templates/scheduele_template.html')
		else:
			main = self.read_template(
				'templates/scheduele_read_only_template.html')

		if user == desired_user and (datetime(2016, 6, 11, 14, 0, 0) - self.get_timeobject_now()).days > 0:
			mvp_link = 'mvp?&id='+self.users[user]['id']+'&mvp=mvp'
		else:
			if 'name' in self.users[desired_user]['mvp'] and self.users[desired_user]['mvp']['name']:
				mvp_link = self.players[self.users[desired_user]['mvp']['country']][self.users[desired_user]['mvp']['name']]['link']
			else:
				mvp_link = ''

		if self.users[desired_user]['mvp']['country']:			
			mvp_img = '../images/teams/'+self.users[desired_user]['mvp']['country']+'/'+ self.users[desired_user]['mvp']['name']
			mvp_img = mvp_img.replace(' ','%20').encode('utf-8')
			if desired_user != user and (datetime(2016, 6, 11, 14, 0, 0) - self.get_timeobject_now()).days >= 0:
				mvp_img = '../images/avatar.png'
		else:
			mvp_img = '../images/avatar.png'

		if user == desired_user  and (datetime(2016, 6, 11, 14, 0, 0) - self.get_timeobject_now()).days >= 0:
			scorer_link = 'mvp?&id='+self.users[user]['id']+'&mvp=scorer'
		else:
			if 'name' in self.users[desired_user]['scorer'] and self.users[desired_user]['scorer']['name']:
				scorer_link = self.players[self.users[desired_user]['scorer']['country']][self.users[desired_user]['scorer']['name']]['link']
			else:
				scorer_link = ''

		if self.users[desired_user]['scorer']['country']:			
			scorer_img = '../images/teams/'+self.users[desired_user]['scorer']['country']+'/'+ self.users[desired_user]['scorer']['name']
			scorer_img = scorer_img.replace(' ','%20').encode('utf-8')
			if desired_user != user and (datetime(2016, 6, 11, 14, 0, 0) - self.get_timeobject_now()).days >= 0:
				scorer_img = '../images/avatar.png'
		else:
			scorer_img = '../images/avatar.png'

		header = self.read_template('templates/header_template.html')

		header = header.format(title='My Predictions')

		self.update_users_pontuations()

		nav = self.create_nav(user)

		games_html = ''

		games_html += '<br><h2 id="Knockout">Knockout Stage</h2>'

		for phase in self.final_stages:
			games_html += '<h3 id="' + phase + '">' + phase + '</h3>'
			for game in [self.games[g] for g in sorted(self.games.keys()) if self.games[g]['stage'] == phase]:
				games_html += self.fill_game_template(
					desired_user, user, game, user != desired_user)



		for group in sorted(self.groups):

			table_html = self.read_template('templates/table_template.html')

			# Real
			positions_htmls, group_html = self.create_group_table_html(
				desired_user, self.real_ordered_group[group])
			table_left = group_html.format(
				side='float:left', title='Real', positions=positions_htmls)

			# Predicted
			if user==desired_user or (datetime(2016, 6, 10, 21, 0, 0) - self.get_timeobject_now()).days < 0:
				positions_htmls, group_html = self.create_group_table_html(desired_user, self.users[desired_user]['predicted_groups'][group], compare_group=self.real_ordered_group[group])
				table_right = group_html.format(
					side='float:right', title='Predicted', positions=positions_htmls)

			else:
				positions_htmls = ''
				table_right = group_html.format(
					side='float:right', title='Revealed on the 10th of June', positions=positions_htmls)

			games_html += table_html.format(group=group, left=table_left, right=table_right)

			games_html += '<br>'

			group_games = []
			for G in self.games:
				if 'group' in self.games[G] and self.games[G]['group'] == group:
					group_games.append(self.games[G])

			group_games = sorted(group_games, key=itemgetter('number'))

			for G in group_games:
				games_html += self.fill_game_template(desired_user, user, self.games[str(G['number'])], user != desired_user)

		# third group
		games_html += '<br>'

		games_html += self.create_third_group_table()

		main = main.format(id=self.users[desired_user]['id'], header=header, nav=nav,user=desired_user , data=games_html, footer=self.footer, anchor=stage, mvp_img=mvp_img, mvp_link=mvp_link, scorer_img=scorer_img, scorer_link=scorer_link)

		return main.encode('utf-8')

	def create_rules(self, user):

		main = self.read_template('templates/rules_template.html')

		header = self.read_template('templates/header_template.html')
		header = header.format(title='Rules')

		nav = self.create_nav(user)

		main = main.format(nav=nav, header=header, footer=self.footer)

		return main.encode('utf-8')

	def update_predictions(self, user, data):

		self.users[user]['games'] = self.load_json(
			'resources/games_clean.json')

		group = ''

		for pred in ast.literal_eval(data):
			if 'None' not in pred[1]:
				self.users[user]['games'][
					pred[0]] = copy.copy(self.games[pred[0]])
				self.users[user]['games'][pred[0]]['score'] = pred[1]
				if self.users[user]['games'][pred[0]]['stage'] != 'Groups':
					group = 'Knockout'
				elif self.users[user]['games'][pred[0]]['stage'] == 'Groups' and len(group) < 2:
					if self.users[user]['games'][pred[0]]['stage'] > group:
						group = self.users[user]['games'][pred[0]]['group']

		self.dump_json(self.users[user]['games'], os.path.join('users', user, 'games.json'))

		return group

	def update_real_scores(self, data):

		for pred in ast.literal_eval(data):

			if 'None' not in pred[1] and ' ' not in self.games[pred[0]]['score']:
				self.games[pred[0]]['score'] = pred[1]
				self.games[pred[0]]['finished'] = pred[2] == 'on'

		self.dump_json(self.games, 'resources/games_current.json')

	def create_scoreboard(self, user):

		main_html = self.read_template('templates/scoreboard_template.html')

		header = self.read_template('templates/header_template.html')
		header = header.format(title='Scoreboard')

		self.teams = self.clean_teams(self.teams)
		self.update_users_pontuations()

		nav = self.create_nav(user)

		lines, ordered_users = self.create_scoreboard_user(user)

		main_html = main_html.format(
			id=user, header=header, nav=nav, lines=lines, footer=self.footer)

		return main_html.encode('utf-8')

	def create_scoreboard_user(self, user):

		positions = ''

		users = self.sort_users_scoreboard()

		for i, U in enumerate(users):

			position_html = self.read_template(
				'templates/scoreboard_position_template.html')

			S = U['points']

			if user == U['username']:
				color = '#CAF2BF'
			else:
				color = ''

			if U['country'] in self.teams:
				flag = self.teams[U['country']]['flag_url']
			else:
				flag = ''

			positions += position_html.format(pos=i + 1, color=color, id=self.users[user]['id'], flag=flag, name=U['username'], exact=S['exact'], right=S['right'], one=S['one'], none=S['none'], points=S['PTS'], groups=S['groups'], penalties=S['penalties'], awards=S['awards'])

		return positions,[u['username'] for u in users]

	def create_settings(self, user, new_user):

		main_html = self.read_template('templates/settings_template.html')

		title = 'Pick your Favourite Country'	

		nav = self.create_nav(user)

		header = self.read_template('templates/header_template.html')
		header = header.format(title='Settings')

		teams = [self.teams[t] for t in self.teams.keys()]

		teams = sorted(teams, key=itemgetter('name'))

		countries = ''

		for team in teams:
			countries += '<a style="background-image:url(' + team['flag_url'].replace(
				'23', '200') + ');" class="settings_flag_link" href="../scripts/home?&country=' + team['name'] + '&id=' + self.users[user]['id'] + '">'
			# countries += '<p>'+team['name']+'</p>'
			# countries += '<img class="settings_flag" src="'+ team['flag_url'].replace('23','150') +'"></img>'
			countries += '</a>'

		main_html = main_html.format(
			title=title, id=user, header=header, nav=nav, countries=countries, footer=self.footer)

		return main_html.encode('utf-8')

	def create_game_page(self, user, game):

		main_html = self.read_template('templates/game_page_template.html')

		header = self.read_template('templates/header_template.html')
		header = header.format(title='Game ' + game)

		nav = self.create_nav(user)
		
		g = self.games[game]

		if g['t1'] in self.teams:
			t1_link = 'team?&country='+g['t1']+'&id='+self.users[user]['id']
		else:
			t1_link = ''
		if g['t2'] in self.teams:
			t2_link = 'team?&country='+g['t2']+'&id='+self.users[user]['id']
		else:
			t2_link = ''
		
		t1_flag = g['t1_flag'] if 't1_flag' in g else ''
		t2_flag = g['t2_flag'] if 't2_flag' in g else ''

		readonly, diff, remain = self.calculate_time_diference(g)

		t1_score = g['t1_score']
		t2_score = g['t2_score']

		users_predictions = ''

		for U in self.users:

			position_html = self.read_template(
				'templates/game_page_position_template.html')

			g = self.users[U]['games'][game]

			result = self.prediction_result(
				user, self.games[game], g, points=False)

			if diff.days < 0:
				score = g['score'] if g['score'] else '-'
			else:
				score = 'x-x' if g['score'] else '-'

			flag = ''
			if self.users[U]['country'] in self.teams:
				if 'flag_url' in self.teams[self.users[U]['country']]:
					flag = self.teams[self.users[U]['country']]['flag_url']

			users_predictions += position_html.format(id=self.users[user]['id'], name=self.users[U]['username'], flag=flag, score=score, color=self.points_colors[result])

		main_html = main_html.format(id=user, header=header, predictions=users_predictions, number=game, nav=nav, date=g['date'].replace('2016', ''), location=g['location'], t1=g['t1'], t2=g['t2'], t1_flag=t1_flag, t2_flag=t2_flag, remain=remain, t1_score=t1_score, t2_score=t2_score, t1_link=t1_link, t2_link=t2_link ,footer=self.footer)

		return main_html.encode('utf-8')

	def create_home_page(self, user):

		main_html = self.read_template('templates/home_page_template.html')

		header = self.read_template('templates/header_template.html')
		header = header.format(title='Home')

		self.teams = self.clean_teams(self.teams)

		self.update_users_pontuations()

		nav = self.create_nav(user)

		lines, ordered_users = self.create_scoreboard_user(user)

		game = str(sorted([int(n) for n in self.games.keys() if not self.games[n]['finished']])[0])

		g = self.games[game]

		t1_link = 'team?&country='+g['t1']+'&id='+self.users[user]['id']
		t2_link = 'team?&country='+g['t2']+'&id='+self.users[user]['id']

		t1_flag = g['t1_flag'] if 't1_flag' in g else ''
		t2_flag = g['t2_flag'] if 't2_flag' in g else ''

		t1_score = g['t1_score']
		t2_score = g['t2_score']

		users_predictions = ''

		readonly, diff, remain = self.calculate_time_diference(g)

		for U in ordered_users:

			position_html = self.read_template(
				'templates/game_page_position_template.html')

			G = self.users[U]['games'][game]

			result = self.prediction_result(
				user, self.games[game], G, points=False)

			if diff.days < 0:
				score = G['score'] if G['score'] else '-'
			else:
				score = 'x-x' if G['score'] else '-'

			if self.users[U]['country'] in self.teams:
				flag = self.teams[self.users[U]['country']]['flag_url']
			else:
				flag = ''

			users_predictions += position_html.format(id=self.users[user]['id'], name=self.users[U]['username'], flag=flag, score=score, color=self.points_colors[result])

		main_html = main_html.format(id=user, header=header, lines=lines, predictions=users_predictions, number=game, nav=nav, date=g['date'].replace('2016', ''), location=g['location'], t1=g['t1'], t2=g['t2'], t1_flag=t1_flag, t2_flag=t2_flag, t1_link=t1_link,t2_link=t2_link, remain=remain, t1_score=t1_score, t2_score=t2_score, footer=self.footer)

		return main_html.encode('utf-8')

	def create_third_group_table(self):

		group_html = self.read_template(
			'templates/group_thrid_place_template.html')
		positions_htmls = ''

		for i, T in enumerate(self.third_group):

			group_postion_html = self.read_template(
				'templates/group_third_place_position_template.html')

			if i < 4:
				color = self.points_colors[4]
			else:
				color = self.points_colors[1]

			if i < 4:
				group = T['groups']
				a = ''.join([t['groups'] for t in self.third_group][:4])
				a = ''.join(sorted(a))
				new_group = [g for g in self.thirdplace[a].keys() if self.thirdplace[
					a][g] == group][0]
				team = self.real_ordered_group[new_group][0]
				next_team_flag = team['flag_url']
			else:
				next_team_flag = ''

			group_postion_html = group_postion_html.format(team=T['name'], team_flag=T['flag_url'], next_team_flag=next_team_flag, color=color, G=T['G'], GF=T['GF'], GA=T['GA'], GD=T['GF'] - T['GA'], W=T['W'], L=T['L'], D=T['D'], PTS=T['PTS'])

			positions_htmls += group_postion_html

		return group_html.format(side='margin:0px auto;', title='Third Place Tie Break', positions=positions_htmls)

	def create_team(self,user,country):

		main = self.read_template('templates/team_template.html')

		header = self.read_template('templates/header_template.html')

		header = header.format(title=country)

		nav = self.create_nav(user)

		G = '<div class="players" style="text-align:center;">'
		D = '<div class="players" style="text-align:center;">'
		M = '<div class="players" style="text-align:center;">'
		F = '<div class="players" style="text-align:center;">'
		for player in self.players[country].keys():
			data = '<a style="background-image:url(../images/teams/'+country+'/'+player.replace(' ','%20')+'.'+self.players[country][player]['term']+');" class="player_link" href="'+self.players[country][player]['link']+'"></a>'
			pos = self.players[country][player]['pos']

			if pos == 'GK':
				G+=data
			if pos == 'DEF':
				D+=data
			if pos == 'MID':
				M+=data
			if pos == 'FRW':
				F+=data

		G += '</div>'
		D += '</div>'
		M += '</div>'
		F += '</div>'			


		main = main.format(header=header, nav=nav, team=country, G=G, D=D, M=M, F=F, footer=self.footer)


		return main.encode('utf-8')
	
	def create_mvp(self,user,mvp,country,player):

		if country == 'None' and player =='None':
			main_html = self.read_template('templates/settings_template.html')

			title = 'From which country...'

			nav = self.create_nav(user)

			header = self.read_template('templates/header_template.html')
			header = header.format(title=mvp)

			teams = [self.teams[t] for t in self.teams.keys()]

			teams = sorted(teams, key=itemgetter('name'))

			countries = ''

			for team in teams:
				countries += '<a style="background-image:url(' + team['flag_url'].replace(
					'23', '200') + ');" class="settings_flag_link" href="../scripts/mvp?&country=' + team['name'] + '&id=' + self.users[user]['id'] + '&mvp='+mvp +'">'
				# countries += '<p>'+team['name']+'</p>'
				# countries += '<img class="settings_flag" src="'+ team['flag_url'].replace('23','150') +'"></img>'
				countries += '</a>'

			main_html = main_html.format(
				title=title, id=user, header=header, nav=nav, countries=countries, footer=self.footer)

			return main_html.encode('utf-8')
		elif player == 'None':
			main = self.read_template('templates/team_template.html')

			header = self.read_template('templates/header_template.html')

			header = header.format(title=country)

			nav = self.create_nav(user)

			G = '<div class="players" style="text-align:center;">'
			D = '<div class="players" style="text-align:center;">'
			M = '<div class="players" style="text-align:center;">'
			F = '<div class="players" style="text-align:center;">'
			for player in self.players[country].keys():
				data = '<a style="background-image:url(../images/teams/'+country+'/'+player.replace(' ','%20')+'.'+self.players[country][player]['term']+');" class="player_link" href="mvp?&id='+self.users[user]['id']+'&country='+country+'&player='+player+'&mvp='+mvp+'"></a>'
				pos = self.players[country][player]['pos']

				if pos == 'GK':
					G+=data
				if pos == 'DEF':
					D+=data
				if pos == 'MID':
					M+=data
				if pos == 'FRW':
					F+=data

			G += '</div>'
			D += '</div>'
			M += '</div>'
			F += '</div>'			


			main = main.format(header=header, nav=nav, team=country, G=G, D=D, M=M, F=F, footer=self.footer)


			return main.encode('utf-8')

	def create_admin(self, user):

		main = self.read_template('templates/admin_template.html')

		header = self.read_template('templates/header_template.html')

		header = header.format(title='Admin')

		self.update_users_pontuations()

		nav = self.create_nav(user)

		games_html = ''

		for g in sorted([int(n) for n in self.games.keys()]):
			g = str(g)

			games_html += self.fill_real_game(user, self.games[g])

		main = main.format(id=self.users[user]['id'], header=header, nav=nav, data=games_html, footer=self.footer)

		return main.encode('utf-8')

	# Football Functions
	def parse_score(self, game, teams, scoring=True):

		if game['score'] and ' ' not in game['score']:
			game['penalties'] = False
			game['t1_score'], game['t2_score'] = [int(a) for a in game['score'].split('-')]
			if scoring:
				teams[game['t1']]['G'] += 1
				teams[game['t1']]['GF'] += game['t1_score']
				teams[game['t1']]['GA'] += game['t2_score']
				teams[game['t1']]['GD'] = teams[game['t1']]['GF'] - teams[game['t1']]['GA']

				teams[game['t2']]['G'] += 1
				teams[game['t2']]['GF'] += game['t2_score']
				teams[game['t2']]['GA'] += game['t1_score']
				teams[game['t2']]['GD'] = teams[game['t2']]['GF'] - teams[game['t2']]['GA']

			if game['t1_score'] == game['t2_score']:
				game['winner'] = 'tie'

				if scoring and game['stage'] == 'Groups':
					teams[game['t1']]['D'] += 1
					teams[game['t1']]['PTS'] += 1
					teams[game['t2']]['D'] += 1
					teams[game['t2']]['PTS'] += 1
			elif game['t1_score'] > game['t2_score']:
				game['winner'] = game['t1']
				if scoring:
					teams[game['t1']]['W'] += 1
					teams[game['t1']]['PTS'] += 3
					teams[game['t2']]['L'] += 1
			elif game['t1_score'] < game['t2_score']:
				game['winner'] = game['t2']
				if scoring:
					teams[game['t1']]['L'] += 1
					teams[game['t2']]['PTS'] += 3
					teams[game['t2']]['W'] += 1

		elif ' ' in game['score']:
			scores = game['score'].replace('(', '').replace(')', '').split(' ')
		
			temp_score = scores[0]

			game['t1_score'], game['t2_score'] = [int(a) for a in temp_score.split('-')]

			if game['t1_score'] == game['t2_score']:
				t1, t2 = [int(a) for a in scores[1].split('-')]
				if t1 > t2:
					game['winner'] = game['t1']
				elif t1 < t2:
					game['winner'] = game['t2']


			elif game['t1_score'] > game['t2_score']:
				game['winner'] = game['t1']

			elif game['t1_score'] < game['t2_score']:
				game['winner'] = game['t2']

			game['penalties'] = True

			temp_score = game['score'].replace('(', '').replace(')', '').split(' ')[0]
			game['t1_score'], game['t2_score'] = [int(a) for a in temp_score.split('-')]

		else:
			game['t1_score'] = ''
			game['t2_score'] = ''
			game['winner'] = ''
			game['t1'] = game['t1_original']
			game['t2'] = game['t2_original']
			game['t1_flag'] = ''
			game['t2_flag'] = ''

		return game, teams

	def sort_teams(self, group, teams, games):

		final_order = []

		group_teams = dict()

		for t in group:
			if teams[t]['PTS'] in group_teams:
				group_teams[teams[t]['PTS']].append(t)
			else:
				group_teams[teams[t]['PTS']] = [t]

		for points in sorted(group_teams.keys(), reverse=True):
			if len(group_teams[points]) == 1:
				final_order += [group_teams[points][0]]
			else:
				# First Tie break points in the games between each other
				final_order += self.sort_teams_common_games(
					group_teams[points], teams, games)

		return [teams[t] for t in final_order]

	def sort_teams_common_games(self, tied_teams, teams, games):

		common_games = [games[g] for g in games if (games[g]['t1'] in tied_teams and games[g]['t2'] in tied_teams) and games[g]['score']]

		if not common_games:
			teams = sorted([teams[t] for t in tied_teams], key=itemgetter('GD'), reverse=True)
			return [t['name'] for t in teams]

		new_teams = dict()
		for t in tied_teams:
			new_teams[t] = dict()
		new_teams = self.clean_teams(new_teams)

		for game in common_games:
			games[str(game['number'])], new_teams = self.parse_score(
				games[str(game['number'])], new_teams, True)

		group_teams = dict()
		for t in new_teams:
			if new_teams[t]['PTS'] in group_teams:
				group_teams[new_teams[t]['PTS']].append(t)
			else:
				group_teams[new_teams[t]['PTS']] = [t]

		final_order = []

		for points in sorted(group_teams.keys(), reverse=True):

			if len(group_teams[points]) == 1:
				# Tie break points in the games between each other
				final_order += [group_teams[points][0]]
			else:
				# First Tie break goal diference in the games between each
				# other
				sorted_teams = self.sort_teams_parameter(
					group_teams[points], new_teams, 'GD')

				if sorted_teams:
					final_order += sorted_teams
				else:
					sorted_teams = self.sort_teams_parameter(
						group_teams[points], new_teams, 'GF')
					if sorted_teams:
						final_order += sorted_teams
					else:
						sorted_teams = self.sort_teams_parameter(
							group_teams[points], teams, 'GD')
						if sorted_teams:
							final_order += sorted_teams
						else:
							sorted_teams = self.sort_teams_parameter(
								group_teams[points], teams, 'GF')
							if sorted_teams:
								final_order += sorted_teams
							else:
								final_order += group_teams[points]

		return final_order

	def sort_teams_parameter(self, tied_teams, teams, tiebreaker):

		group_teams = dict()
		for t in tied_teams:
			if teams[t][tiebreaker] in group_teams:
				group_teams[teams[t][tiebreaker]].append(t)
			else:
				group_teams[teams[t][tiebreaker]] = [t]

		final_order = []

		for goals in sorted(group_teams.keys(), reverse=True):

			if len(group_teams[goals]) == 1:
				# Tie break goals in the games between each other

				final_order += [group_teams[goals][0]]
			else:
				# First Tie break goal diference in the games between each
				# other

				return None

		return final_order

	def prediction_result(self, user, real, predicted, points=True):

		if 'penalties' in real and real['penalties']:
			if points and real['winner'] == predicted['winner']:
				self.users[user]['points']['penalties'] += 1
				self.users[user]['points']['PTS'] += 1		


		if not predicted['score'] or '-' not in real['score']:
			return 0
		elif real['score'].split(' ')[0] == predicted['score'].split(' ')[0]:
			if points:
				self.users[user]['points']['exact'] += 1
				self.users[user]['points']['PTS'] += 5
			return 4
		elif real['winner'] == predicted['winner'] and not real['penalties']:
			if points:
				self.users[user]['points']['right'] += 1
				self.users[user]['points']['PTS'] += 3
			return 3
		elif real['t1_score'] == predicted['t1_score']:
			if points:
				self.users[user]['points']['one'] += 1
				self.users[user]['points']['PTS'] += 1
			return 2
		elif real['t2_score'] == predicted['t2_score']:
			if points:
				self.users[user]['points']['one'] += 1
				self.users[user]['points']['PTS'] += 1
			return 2
		else:
			if points:
				self.users[user]['points']['none'] += 1
			return 1

	def sort_third_group(self):

		tiebreaker = 'PTS'

		final_order = []

		tied_teams = [t['name'] for t in self.third_group]

		teams = self.teams

		group_teams = dict()
		for t in tied_teams:
			if teams[t][tiebreaker] in group_teams:
				group_teams[teams[t][tiebreaker]].append(t)
			else:
				group_teams[teams[t][tiebreaker]] = [t]

		for goals_pts in sorted(group_teams.keys(), reverse=True):

			if len(group_teams[goals_pts]) == 1:
				final_order += [group_teams[goals_pts][0]]
			else:

				tiebreaker = 'GD'
				group_teams_gf = dict()
				tied_teams = group_teams[goals_pts]
				for t in tied_teams:
					if teams[t][tiebreaker] in group_teams_gf:
						group_teams_gf[teams[t][tiebreaker]].append(t)
					else:
						group_teams_gf[teams[t][tiebreaker]] = [t]

				for goals_gf in sorted(group_teams_gf.keys(), reverse=True):

					if len(group_teams_gf[goals_gf]) == 1:
						final_order += [group_teams_gf[goals_gf][0]]
					else:
						tiebreaker = 'GF'
						group_teams_gd = dict()
						tied_teams = group_teams_gf[goals_gf]
						for t in tied_teams:
							if teams[t][tiebreaker] in group_teams_gd:
								group_teams_gd[teams[t][tiebreaker]].append(t)
							else:
								group_teams_gd[teams[t][tiebreaker]] = [t]

						for goals_gd in sorted(group_teams_gd.keys(), reverse=True):

							if len(group_teams_gd[goals_gd]) == 1:
								final_order += [group_teams_gd[goals_gd][0]]
							else:
								final_order += group_teams_gd[goals_gd]

		self.third_group = [teams[t] for t in final_order]

	# Server
	def save_games(self):

		self.dump_json(self.games, 'resources/games_current.json')

		for user in self.users:
			if 'games' in self.users[user]:
				self.dump_json(self.users[user]['games'], os.path.join(
					'users', user, 'games.json'))
				del self.users[user]['games']
			if 'teams' in self.users[user]:
				del self.users[user]['teams']

		self.dump_json(self.users, 'users/info.json')

	def handle_request(self, conn, addr, data):

		new_link = '../html/missing.html'

		if data == 'login':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')

			if len(data) == 1:
				token = data[0]

				url = "https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=" + token
				response = urllib.urlopen(url)
				data = json.loads(response.read())

				user = data['name']

				is_new_user = user in self.users

				self.create_new_user(user)
				self.users[user]['email'] = data['email']

				if not is_new_user:
					self.timed_print('New user: ' + user, user, color=self.colors['OKBLUE'])
					new_link = 'settings?&id=' + \
						self.users[user]['id'] + '&new=Y'
				else:
					self.timed_print('User logged in: ' + user, user, color=self.colors['OKBLUE'])
					new_link = 'home?&id=' + self.users[user]['id']

			conn.send(new_link.encode('utf-8'))

		elif data == 'settings':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')
			user = self.find_user_by_id(data[0])
			new = data[1] == 'Y'

			if user:
				self.timed_print('Settings', user)
				new_page = self.create_settings(user, new)

			else:
				self.timed_print('Error in getting user', '', self.colors['FAIL'])
				new_page = self.read_template('templates/start_template.html')

			conn.send(new_page)

		elif data == 'admin':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')
			user = self.find_user_by_id(data[0])
			if user in self.users:
				self.timed_print('Admin', user)
				new_page = self.create_admin(user)
			else:
				self.timed_print('Error in getting user', '', self.colors['FAIL'])
				new_page = self.read_template('templates/start_template.html')

			conn.send(new_page)

		elif data == 'agenda':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')
			user = self.find_user_by_id(data[0])
			desired_user = unicode(data[1], encoding='utf-8')
			stage = data[2]
			if user and (desired_user in self.users):
				self.timed_print('Requested ' + desired_user + ' predictions', user)
				new_page = self.create_scheduele_with_groups(
					user, desired_user, stage)
			else:
				self.timed_print('Error in getting user', '', self.colors['FAIL'])
				new_page = self.read_template('templates/start_template.html')

			conn.send(new_page)

		elif data == 'rules':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')
			user = self.find_user_by_id(data[0])

			if user:
				self.timed_print('Rules', user)
				new_page = self.create_rules(user)
			else:
				self.timed_print('Error in getting user', '', self.colors['FAIL'])
				new_page = self.read_template('templates/start_template.html')

			conn.send(new_page)

		elif data == 'predict':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')

			user = self.find_user_by_id(data[0])

			if user:
				self.timed_print('New predictions', user)
				stage = self.update_predictions(user, data[1])
				new_page = 'agenda?&id=' + \
					data[0] + '&user=' + user + '&stage=' + stage
			else:
				self.timed_print('Error in getting user', '',self.colors['FAIL'])
				new_page = '../index.html'

			conn.send(new_page.encode('utf-8'))

		elif data == 'updatescore':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')

			user = self.find_user_by_id(data[0])

			if user:
				self.timed_print('Update real score', user)
				self.update_real_scores(data[1])
				new_page = 'admin?&id=' + data[0]  
			else:
				self.timed_print('Error in getting user', '', self.colors['FAIL'])
				new_page = '../index.html'

			conn.send(new_page.encode('utf-8'))

		elif data == 'scoreboard':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')
			user = self.find_user_by_id(data[0])

			if user:
				self.timed_print('Scoreboard', user)
				new_page = self.create_scoreboard(user)
			else:
				self.timed_print('Error in getting user', '', self.colors['FAIL'])
				new_page = self.read_template('templates/start_template.html')

			conn.send(new_page)

		elif data == 'team':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')

			user = self.find_user_by_id(data[0])
			team = data[1]

			if user:
				self.timed_print('Team: ' + team, user)
				new_page = self.create_team(user,team)
			else:
				self.timed_print('Error in getting user', '', self.colors['FAIL'])
				new_page = self.read_template('templates/start_template.html')

			conn.send(new_page)

		elif data == 'mvp':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')

			user = self.find_user_by_id(data[0])
			mvp = data[1]
			country = data[2]
			player = data[3]

			if user:
				if country!='None' and player!='None':
					self.users[user][mvp]['country'] = country
					self.users[user][mvp]['name'] = player
					new_page = self.create_scheduele_with_groups(
					user, user, 'None')
				else:
					self.timed_print('Mvp('+mvp+')', user)
					new_page = self.create_mvp(user,mvp,country,player)
					
			else:
				self.timed_print('Error in getting user', '', self.colors['FAIL'])
				new_page = self.read_template('templates/start_template.html')

			conn.send(new_page)

		elif data == 'game':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')
			user = self.find_user_by_id(data[0])
			game = data[1]

			if user:
				self.timed_print('Game ' + game, user)
				new_page = self.create_game_page(user, game)
			else:
				self.timed_print('Error in getting user', '', self.colors['FAIL'])
				new_page = self.read_template('templates/start_template.html')

			conn.send(new_page)

		elif data == 'home':

			conn.send('ok')

			data = conn.recv(self.buffersize).split('\n')
			user = self.find_user_by_id(data[0])

			if user:
				self.timed_print('Home', user)
				country = data[1]
				if country != 'None':
					self.users[user]['country'] = country
				new_page = self.create_home_page(user)

			else:
				self.timed_print('Error in getting user', '', self.colors['FAIL'])
				new_page = self.read_template('templates/start_template.html')

			conn.send(new_page)

	def start_server(self):

		HOST = ''
		ADDR = (HOST, self.PORT)

		self.serv = socket(AF_INET, SOCK_STREAM)

		self.serv.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

		try:
			self.serv.bind((ADDR))
			self.serv.listen(5)
			self.serv.settimeout(0.2)
		except:
			self.timed_print('euro server is already ON ', '', 'FAIL')
			return

		self.timed_print('euro server is now started', '', 'OKGREEN')

		while 1:
			try:
				try:
					conn, addr = self.serv.accept()
					conn.setblocking(1)
				except timeout:
					continue

				# self.timed_print(
					# 'IP: ' + str(addr[0]) + ' Port: ' + str(addr[1]) + ' ...connected!', 'OKBLUE')

				conn.send('ok')

				data = conn.recv(self.buffersize).lower().strip(
					'\n').strip('\r')

				self.start_thread(self.handle_request, args=(conn, addr, data))

			except KeyboardInterrupt:
				# self.save_session()
				break

		self.save_games()

		self.serv.close()
		self.timed_print('euro server stopped', '','WARNING')


if __name__ == '__main__':

	PORT = 50000
	new_server = euro(PORT)
