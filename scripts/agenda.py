#!/usr/bin/python

import cgi ,cgitb, os
from socket import *


cgitb.enable()
form = cgi.FieldStorage()

user_name = str(form.getvalue('user'))
s = str(form.getvalue('s')) 

# print "Content-type: text/html\n\n"

try:
	HOST = 'localhost'
	PORT = 10000

	ADDR = (HOST,PORT)

	cli = socket( AF_INET,SOCK_STREAM)
	cli.connect((ADDR))

	data = cli.recv(1024)

	if data.lower().strip('\n').strip('\r') == 'ok':
		cli.send('agenda')
		data = cli.recv(1024)
		if data.lower().strip('\n').strip('\r') == 'ok':
			cli.send(user_name + '\n'+ s)
			data = cli.recv(1024)

except:
	raise
	login = False

print "Location:"+ data +"\n\n";
