import httplib
import json

connection = httplib.HTTPConnection('fotmob.com/leagues/euro2016/')
token = ' 589e5bd637f24662a2da3cdef76ab4bb'
headers = { 'X-Auth-Token': token, 'X-Response-Control': 'minified' }
connection.request('GET', '/v1/fixtures', None, headers )
response = json.loads(connection.getresponse().read().decode())

print (response)