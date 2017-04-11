from bs4 import BeautifulSoup
from urllib2 import urlopen
from urllib2 import HTTPError
from urllib2 import URLError
import numpy as np
import pandas as pd
import datetime
import random
import re

def wordpress():
	optionsUrl = 'https://compadredb.wordpress.com/'
	optionsPage = urlopen(optionsUrl)
	soup = BeautifulSoup(optionsPage, "html5lib")

	titleList = soup.findAll('h1', attrs={'class': 'entry-title'})
	titles = []
	for apples in titleList:
		titles.append(apples.get_text())

	contentList = soup.findAll('div', attrs={'class': 'entry-content'})
	contents = []
	for pears in contentList:
		contents.append(pears.get_text())

	middle_all = soup.findAll("h1", attrs={'class': 'entry-title'})
	result = []
	for middle in middle_all:
		result.extend(middle.find_all('a', href=True))

	print result

	timesList = soup.findAll('time', attrs={'class': 'entry-date'})
	dates = []
	for oranges in timesList:
		dates.append(oranges.get_text())

#	authorList = soup.findAll('a', attrs={'class': 'url fn n'})
#	for plums in authorList:
#		print(plums.get_text())

	authorList = soup.findAll('a', attrs={'class': 'url fn n'})
	authors = []
	for plums in authorList:
		authors.append(plums.get_text())

# coerce lists into df

	wordpress = pd.DataFrame(
    	{'Title': titles,
    	 'Authors': authors,
    	 'Content': contents,
    	 'Link' : result,
    	 'Date' : dates
    	})

return wordpress

