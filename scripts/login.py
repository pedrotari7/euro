#!/usr/bin/python

import cgi ,cgitb, os
import urllib,json
from socket import *


cgitb.enable()
form = cgi.FieldStorage()

token = str(form.getvalue('token'))

# print "Content-type: text/html\n\n"

try:
	HOST = 'localhost'
	PORT = 50000

	ADDR = (HOST,PORT)

	cli = socket( AF_INET,SOCK_STREAM)
	cli.connect((ADDR))

	data = cli.recv(1024)

	if data.lower().strip('\n').strip('\r') == 'ok':
		cli.send('login')
		data = cli.recv(1024)
		if data.lower().strip('\n').strip('\r') == 'ok':
			url = "http://www.googleapis.com/oauth2/v3/tokeninfo?id_token="+token
			response = urllib.urlopen(url)
			#data = json.loads(response.read())

			cli.send(response.read() + '\n')
			data = cli.recv(1024)

except:
	raise
	login = False

print "Location:"+ data +"\n\n";
