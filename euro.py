from game import Game


class euro(object):
	"""docstring for euro"""
	def __init__(self):
		super(euro, self).__init__()

		self.colors = ['#BBF3BB','#BBF3BB','#BBF3FF','transparent']

		self.read_teams()

		self.footer = self.read_template('templates/footer_template.html')

		self.games = self.read_games_info()


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
		new_game.date = info[1]
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

		game_template = a.read_template('templates/game_template.html')

		return game_template.format(date=g.date,location=g.location,t1=g.t1,t2=g.t2,t1_flag=g.t1_flag,t2_flag=g.t2_flag,number=g.number)


	def create_scheduele_with_groups(self):

		main = self.read_template('templates/scheduele_template.html')

		games_html = ''

		for group in sorted(self.groups):

			games_html += self.read_template('templates/group_template.html')

			positions_htmls = []
			for i,team in enumerate(self.groups[group]):
				group_postion_html = self.read_template('templates/group_position_template.html')
				positions_htmls.append(group_postion_html.format(pos=i,team=team,team_flag = self.teams[team]['flag_url'],color = self.colors[i]))


			games_html = games_html.format(group = group, t1=positions_htmls[0],t2=positions_htmls[1],t3=positions_htmls[2],t4=positions_htmls[3])

			for G in self.games:
				if G.group == group:
					games_html += self.fill_game_template(G)


		main = main.format(data = games_html, footer = a.footer)

		return main


a = euro()

with open('test.html','w') as f:
	f.write(a.create_scheduele_with_groups())