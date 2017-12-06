import requests
from requests.auth import HTTPDigestAuth
import json
import base64
import csv

def getToken():
	clientId = '6bbdf1b0b07b4c6bba857e2cc937074c'
	clientSecret = 'de1acfa4836449b2afa6a874a441ad49'

	encodeClient = base64.b64encode(bytes(clientId+':'+clientSecret, 'ascii')).decode('ascii')
	encodeClient = 'Basic ' + encodeClient
	tokenUrl = 'https://accounts.spotify.com/api/token'
	tokenHeaders = {'Authorization': encodeClient}
	tokenParams = {'grant_type': 'client_credentials'}
	token = ''
	# tokenResponse = requests.post(tokenUrl, params=tokenParams, headers=tokenHeaders, )

	tokenResponse=requests.post(tokenUrl, data=tokenParams, auth = (clientId, clientSecret))

	if(tokenResponse.ok):
		jData = json.loads(tokenResponse.content)
		token = jData['access_token']
		return token
	else:
		tokenResponse.raise_for_status()


def getCategories(token):
	# token = getToken()
	url = 'https://api.spotify.com/v1/browse/categories'
	headers = {'Accept': 'application/json',
				'Authorization': 'Bearer ' + token}

	categories = []
	offset = 0
	while True:
		params = {'limit': '50', 'offset': offset}
		myResponse = requests.get(url, params=params, headers=headers)
		if(myResponse.ok):
			jData = json.loads(myResponse.content)
			tmpList = jData['categories']

			offset += len(tmpList['items'])
			print("length ", len(tmpList['items']))

			if len(tmpList['items']) == 0:
		   		print('done offset:', offset)
		   		break

			for item in tmpList['items']:
				categories.append(item['id'])
		else:
		  # If response code is not ok (200), print the resulting http error code with description
		    myResponse.raise_for_status()

	return categories

def getPlayListFromCategory(id, token):
	# token = getToken()
	url = 'https://api.spotify.com/v1/browse/categories/'+id+'/playlists'
	headers = {'Accept': 'application/json',
				'Authorization': 'Bearer ' + token}
	offset = 0
	hrefs = []
	while True:
		params = {'limit': '50', 'offset': offset}
		myResponse = requests.get(url, params=params, headers=headers)

		if(myResponse.ok):
		    jData = json.loads(myResponse.content)
		    tmp = jData['playlists']

		    offset += len(tmp['items'])
		    print("length ", len(tmp['items']))
		    if len(tmp['items']) == 0:
		    	print('done offset:', offset)
		    	break

		    for item in tmp['items']:
		    	tmp = item['tracks']
		    	href = tmp['href']
		    	hrefs.append(href)
		    	# print(hrefs)
		else:
		  # If response code is not ok (200), print the resulting http error code with description
		    myResponse.raise_for_status()

	return hrefs

def getTracksFromPlayList(url, token):
	# token = getToken()
	# url = 'https://api.spotify.com/v1/users/11120963440/playlists/'+id+'/tracks'
	# url = 'https://api.spotify.com/v1/users/spotify/playlists/37i9dQZF1DWWwaxRea1LWS/tracks'
	headers = {'Accept': 'application/json',
				'Authorization': 'Bearer ' + token}

	tracks = []
	offset = 0
	while True:
		params = {'limit': '100', 'offset': offset}
		myResponse = requests.get(url, params=params, headers=headers)
		if(myResponse.ok):
		    jData = json.loads(myResponse.content)
		    tmp = jData['items']
		    print('track offset: ', offset)
		    if len(jData['items']) == 0:
		    	print('track done track length: ', len(tracks))
		    	break
		    offset += len(jData['items'])

		    for item in jData['items']:
		    	info = item['track']
		    	tracks.append(info['id'])
		    # writeCsv("123.csv", jData)
		    # return tracks

		else:
		  # If response code is not ok (200), print the resulting http error code with description
		    myResponse.raise_for_status()

	return tracks


def writeCsv(newFileName, items, keys):
	# print("write: "+id)
	print(newFileName)
	with open(newFileName, 'w', encoding='utf-8') as f:
		writer = csv.writer(f)
		writer.writerow(keys)
		for track in items:
			keys = []
			if track is not None:
				for key in track:
					keys.append(key)
				vals = []
				for key in keys:
					vals.append(track[key])
				try:
					writer.writerow(vals)
				except:
					print("out of range")
	f.close()

def getFeature(ids, token, i):
	# token = getToken()

	url = "https://api.spotify.com/v1/audio-features/?ids="
	for id in ids:
		if id is not None:
			url += id + ','

	headers = {'Accept': 'application/json',
				'Authorization': 'Bearer ' + token}

	myResponse = requests.get(url, headers=headers)

	if(myResponse.ok):
	    jData = json.loads(myResponse.content)
	    items = jData['audio_features']
	    keys = []
	    for track in items:
	    	if track is not None:
	    		for key in track:
	    			keys.append(key)
	    		writeCsv('feature/'+id+'.csv', items, keys)
	    		break
	else:
	  # If response code is not ok (200), print the resulting http error code with description
	    myResponse.raise_for_status()



if __name__ == '__main__':
	token = getToken()
	categoryIds = getCategories(token)
	print('category id length', len(categoryIds))
	print(categoryIds)
	#get playlists from catefory id	
	playLists = []
	for id in categoryIds:
		playLists.append(getPlayListFromCategory(id, token))
		print(len(playLists))

	#get tracks from playlists
	tracks = []
	for i in range(len(playLists)):
	# for i in range(15):
		# if i < 12:
		# 	continue
		for url in playLists[i]:
			tracks.append(getTracksFromPlayList(url, token))
			print(len(tracks))
	
	#get audio feature from max 100 tracks in a batch
	for i in range(len(tracks)):
		ids = []

		for id in tracks[i]:
			ids.append(id)
			if len(ids) == 100:
				getFeature(ids, token, i)
				ids = []

		getFeature(ids, token, i)
