import flask
import os
import requests
from bs4 import BeautifulSoup
import random

app = flask.Flask(__name__)

def shutterstock_search(query):
	"""
	Search shutterstock for images, provided a query.
	Returns information on one random image from the
	first page.
	"""
	# get response from shutterstock
	response = requests.get(
		'https://www.shutterstock.com/search', 
		params = {'searchterm': query}
	)

	# interpret response
	soup = BeautifulSoup(response.content, 'lxml')
	images = soup.select('div .search-content li')

	# Return if there were no images
	if not images: 
		return(dict(
			success = False,
			description = 'There were no results for your search.'
		))

	# choose a random result from the first page
	my_image = random.choice(images)

	# build results
	result = dict(
		success = True,
		description =  my_image.find('div',{'class':'description'}).text.strip(),
		image_url = 'http://' + my_image.find('img')['src'][2:],
		search_url = response.url
	)
	return(result)

@app.route('/shutterstock-slack', methods=['POST'])
def handler():

	# query shutterstock
    query = flask.request.form['text']
    results = shutterstock_search(query)

    # construct payload
    if not results['success']:
    	payload = dict(
    		response_type = 'ephemeral',
    		text = results['description']
    	)
    else:
	    payload = dict(
	    	response_type = 'in_channel',
	    	attachments = [dict(
	    		author_link = results['search_url'],
	    		author_name = 'Shutterstock',
	    		fallback = 'Your search failed. Sorry :slightly_frowning_face:',
	    		image_url = results['image_url'],
	    		title = results['description'],
	    	)]
	    )

    # jsonify, return
    return flask.jsonify(**payload)

@app.route('/', methods=['GET'])
def mainpage():
	return('Working...')

if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)
