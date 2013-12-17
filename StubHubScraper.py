# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
from urllib2 import urlopen
import simplejson as json
#import results
from urllib import quote
import datetime
import time

cOut = None
jOut = None

#outputs data in json and csv format
def output(eventName, day, date, venue, city, tickets):
	jData = json.dumps({'Event Name': eventName, 'Day' : day, 'Date' : date, 'Venue' : venue, 'City' : city, 'Price' : tickets[0], 'Tickets Left' : tickets[1]})
	jOut.write(jData + '\n')
	cOut.write(eventName + "," + day + "," + date + "," + venue + "," + city + "," + tickets[0] + "," + tickets[1] + "\n")



#organize all event information
def findEventDetails(html):
	allText = html.findAll(text=True)
	eventName = allText[0].strip()
	date = allText[1].strip().split(',')
	venue = allText[3].strip()
	city = allText[4].strip()

	#check if the date is announced, if it is not, we will skip this event
	if date[0] != "TBD":
		
		#now we have to find the tickets sale information, which is a little trickier
		tix = html.findAll('td')
		length = len(tix)
		#is there a valid "tickets" field? if so, extract info
		#note: every now and then the structure is incorrect and we can't parse a event's info
		if length > 4:
			try:
				tickets = tix[4].text.encode('ascii','ignore').split("&nbsp;")
				tickets[0] = tickets[0].replace('Priced from:',"")
				tickets[1] = tickets[1].replace('USD',"")
				tickets[1] = tickets[1].replace("tickets left","")
				output(eventName, date[0].strip(), date[1].strip(), venue, city, tickets)
			except IndexError: 
				pass #an error is thrown when we come across text that is not for an event				


def execute(BASEURL, BASEURL1, BASEURL2):
	#how many pages of search results are there?
	soup = BeautifulSoup(urlopen(BASEURL).read())
	results = int(soup.find(attrs={'class':'resultRed'}).text)
	pages = results/100
	print str(results) + ' results found in ' + str(pages) + ' pages'

	#let's visit all the pages and extract information
	csvText = ""
	jsonText = ""
	for x in range (0,pages+1):
		tempURL = BASEURL1 + str(x) + BASEURL2
		soup = BeautifulSoup(urlopen(tempURL).read())
		for tr in soup.findAll('tr'):
			findEventDetails(tr)
	return results

# function that manages scraping in a list of different cities
cities = { ('Austin','TX'),
			('New York','NY'),
			('San Francicso','CA'),
			('Los Angeles','CA'),
			('Chicago','IL'),
			('Houston','TX'),
			('Phoenix','AZ'),
			('Philadelphia','PA'),
			('San Diego','CA'),
			('Dallas','TX'),
			('San Jose','CA'),
			('Detroit','MI'),
			('Jacksonville','FL'),
			('Indianapolis','IN'),
			('Columbus','OH'),
			('Baltimore','MD'),
			('Charlotte','NC'),
			('Nashville', 'TN'),
			('New Orleans, LA'),
			('Portland','WA'),
			('Minneapolis','MN'),
			('Boston','MA'),
			('Seattle','WA'),
			('Miami','FL'),
			('Cleveland','OH')
			}

totalResults = 0
version = 1

#fucntion that constructs each city's URL 
def constructURL(city, state):
	BASEURL1 = "http://www.stubhub.com/search/doSearch?searchStr=" + city.replace(" ","%20") + ",%20" + str(state) + "&searchMode=event&rows=100&start=" 
	BASEURL2 = "&pageNumber=1&resultsPerPage=50&searchMode=event&start=0&rows=50&geo_exp=1"
	startURL = BASEURL1 + '0' + BASEURL2
	startURL = quote(startURL, safe="%/:=&?~#+!$,;'@()*[]")
	return startURL, BASEURL1, BASEURL2


#call scraper on each city
while True:
	date = "CollectedData/"
	date += datetime.date.today().strftime("%B %d, %Y")
	jOut = open(date+'_'+str(version)+'_json','w')
	cOut = open(date+'_'+str(version)+'_csv.txt','w')

	#add all the cities to a stack, only pop stack after complete scrape of city
	toScrape = []
	for city in cities:
		toScrape.append(city)

	while len(toScrape) > 0:
		city = toScrape.pop()
		print
		print "Searching for events in " + city[0] + ', ' + city[1]
		startURL, BASEURL1, BASEURL2 = constructURL(city[0],city[1])
		try:
			totalResults += execute(startURL,BASEURL1,BASEURL2)
		except Exception as e:
			print e
			print "Error occured scraping events in " + city[0] + ', ' + city[1] + " - we will try again"
			toScrape.append(city)

	print str(totalResults) + ' total events recorded found'
	print
	jOut.close()
	cOut.close()
	if (version == 3):
		version = 1
	else:
		version+=1
	print
	print "Completed search, will resume in 8 hours"
	print
	time.sleep(3600*24) #scrape every 8 hours





