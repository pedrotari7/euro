#!/usr/bin/python

import cgi ,cgitb, os, math
from socket import *


cgitb.enable()
form = cgi.FieldStorage()

values = []
#for k in form.keys():
#	values.append((k,str(form.getvalue(k))))

id = str(form.getvalue('id'))

for i in xrange(1,52):
	t1 = str(form.getvalue(str(i)+'t1'))
	t2 = str(form.getvalue(str(i)+'t2'))
	values.append((str(i),t1+'-'+t2))

# print "Content-type: text/html\n\n"

try:
	HOST = 'localhost'
	PORT = 50000

	ADDR = (HOST,PORT)

	cli = socket( AF_INET,SOCK_STREAM)
	cli.connect((ADDR))

	data = cli.recv(1024)

	if data.lower().strip('\n').strip('\r') == 'ok':
		cli.send('predict')
		data = cli.recv(1024)

		if data.lower().strip('\n').strip('\r') == 'ok':
			cli.send(id+ '\n' + str(values))
			data = cli.recv(1024)

except:
	raise
	login = False

print "Location:"+ data +"\n\n";
