import requests
import socket


def getIP():
	from urllib.request import urlopen
	import re as r
	d = str(urlopen('http://checkip.dyndns.com/').read())

	return r.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(d).group(1)


def get_city():
	print(getIP())

	hostname = socket.gethostname()
	ip = getIP()

	# parameters to retrieve from API
	params = ['query', 'status', 'country', 'countryCode', 'city', 'timezone', 'mobile']

	# make the response
	resp = requests.get('http://ip-api.com/json/' + ip, params={'fields': ','.join(params)})

	# read response as JSON (converts to Python dict)
	info = resp.json()

	# display the response
	print(info)
	return info['city']

# get_city()