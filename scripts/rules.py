#!/usr/bin/python

import cgi ,cgitb, os
from socket import *


cgitb.enable()
form = cgi.FieldStorage()

id = str(form.getvalue('id'))

try:
	HOST = 'localhost'
	PORT = 50000

	ADDR = (HOST,PORT)

	cli = socket( AF_INET,SOCK_STREAM)
	cli.connect((ADDR))

	data = cli.recv(1024)

	if data.lower().strip('\n').strip('\r') == 'ok':
		cli.send('rules')
		data = cli.recv(1024)
		if data.lower().strip('\n').strip('\r') == 'ok':
			cli.send(id + '\n')
			data = cli.recv(1024)

except:
	raise
	login = False

print "Location:"+ data +"\n\n";
