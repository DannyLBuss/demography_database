from bs4 import BeautifulSoup
from urllib import urlopen
 
optionsUrl = 'https://compadredb.wordpress.com/'
optionsPage = urlopen(optionsUrl)
#soup = BeautifulSoup(optionsPage)
soup = BeautifulSoup(optionsPage, "html5lib")
print(soup)

title = soup.find('h1', attrs={'class': 'entry-title'}).text
title = title.encode('utf-8').strip()
print "Title: " + title