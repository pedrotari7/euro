import os
import json

def load_json(filename):
	if os.path.exists(filename):
		with open(filename, 'r') as fp:
			return json.load(fp, encoding='utf8')
	else:
		return {}


if __name__ == '__main__':
	
	users = load_json('users/info.json')

	for u in users:
		count = 0
		#print u,users[u]['email'],' MVP:',
		users[u]['games'] = load_json('users/'+u+'/games.json')

		# print count

		for g in users[u]['games']:
			if users[u]['games'][g]['stage'] == 'Round of 16':
				if users[u]['games'][g]['score']:
					count += 1

		#print  count,'/36 ', round(count/36.,2),*
		
		if count/8. != 1:
			# print count
			print u,round(count/8.,2)
			#print '\n'



