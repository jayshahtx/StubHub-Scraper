# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
from urllib2 import urlopen
import simplejson as json
#import results
from urllib import quote
import datetime
import time

#initialize writers
cOut = None
jOut = None

#set result counter to 0
totalResults = 0

# List of cities to scrape
cities = { ('Austin+San+Antonio','TX'),
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
			('Portland','OR'),
			('Minneapolis','MN'),
			('Boston','MA'),
			('Seattle','WA'),
			('Miami','FL'),
			('Cleveland','OH')
			}


#outputs data in json and csv format
def output(eventName, time, day, date, month, venue, city, price, ticketsLeft):
	jData = json.dumps({'Event Name': eventName, 'Time' : time, 'Day' : day, 'Date' : date, 'Month' : month, 'Venue' : venue, 'City' : city, 'Price' : price, 'Tickets Left' : ticketsLeft})
	jOut.write(jData + '\n')
	cOut.write(eventName + "," + time + "," + day + "," + date + "," + month + "," + venue + "," + city + "," + price + "," + ticketsLeft + "\n")

#function which finds the data from the first two columns of a page result
def soupify(tr, tag, attr1, attr2): 
	data = tr.find(tag, attrs = {attr1:attr2})
	soup = BeautifulSoup(str(data))
	output = soup.find(text=True)
	return output.encode("ascii","ignore").strip()

#function which finds data from third column
def soupify2(tr,tag,attr1,attr2):
	data = tr.find(tag, attrs = {attr1:attr2})
	soup = BeautifulSoup(str(data))
	eventDeets = soup.findAll("a",text=True)
	venue = eventDeets[1].strip()
	city = eventDeets[2].strip()
	time = eventDeets[3].strip()
	return venue,city,time

#Method to parse each page's results
def parseResultsPage(soup):
	
	#Find table in page, visit each row
	table = soup.find('table')
	rows = table.findAll('tr')
	for tr in rows:

		#first two columns of information (day, numerical day, month, and event name)
		day = soupify(tr,"div",'class','ticketDetails day')
		numDay = soupify(tr,"span",'id','ticketEventDate')
		month = soupify(tr,"span",'id','ticketEventMonth')
		eventName = soupify(tr,"td",'class','eventName')
		price = soupify(tr,"span","class","currency-price")

		#check if this is a valid row
		if (day != "None"):
			venue, city, time = soupify2(tr,'td','class','blackFont eventLocation')
			
			#check if there are actually tickets for sale
			if (price != "None"):
				data = tr.findAll("td",text=True)
				tik = len(data)-1
				tikLeft = (data[tik]).strip()
				#decode tickets left to ascii, perform string manipulation to get only the number of tickets left
				ticketsLeft  = tikLeft.encode('ascii','ignore').strip("tickets left")
			else:
				price = "NA"
				ticketsLeft = "0"

			output(eventName,time,day,numDay,month,venue,city,price,ticketsLeft)

		

#Calculates total number of events in a city, visits each results page, and returns event count
def pageNavigation(BASEURL, BASEURL1, BASEURL2):
	#how many pages of search results are there?
	soup = BeautifulSoup(urlopen(BASEURL).read())
	results = int(soup.find(attrs={'class':'resultRed'}).text)
	pages = results/100
	print str(results) + ' results found in ' + str(pages) + ' pages'

	#let's visit all the pages and extract information
	for x in range (0,pages+1):
		tempURL = BASEURL1 + str(x) + BASEURL2
		#create beautifulsoup representation of each page of results
		soup = BeautifulSoup(urlopen(tempURL).read())
		#Extract all events in a city
		parseResultsPage(soup)
	return results

#fucntion that constructs each city's URL 
def constructURL(city, state):
	BASEURL1 = "http://www.stubhub.com/search/doSearch?searchStr=" + city.replace(" ","%20") + ",%20" + str(state) + "&searchMode=event&rows=100&start=" 
	BASEURL2 = "&pageNumber=1&resultsPerPage=50&searchMode=event&start=0&rows=50&geo_exp=1"
	startURL = BASEURL1 + '0' + BASEURL2
	startURL = quote(startURL, safe="%/:=&?~#+!$,;'@()*[]")
	return startURL, BASEURL1, BASEURL2


#call scraper on each city every 24 hours
while True:
	date = "CollectedData/"
	date += datetime.date.today().strftime("%B %d, %Y")
	jOut = open(date+'_json','wb')
	cOut = open(date+'_csv.txt','wb')

	#add all the cities to a stack, only pop stack after complete scrape of city
	toScrape = []
	for city in cities:
		toScrape.append(city)

	#scrape each city, if error occurs, add city back onto stack
	while len(toScrape) > 0:
		city = toScrape.pop()
		print
		print "Searching for events in " + city[0] + ', ' + city[1]
		startURL, BASEURL1, BASEURL2 = constructURL(city[0],city[1])
		try:
			totalResults += pageNavigation(startURL,BASEURL1,BASEURL2)
		except Exception as e:
			print e
			print "Error occured scraping events in " + city[0] + ', ' + city[1] + " - we will try again"
			toScrape.append(city)

	#summarize all activity, cloes writers
	print
	print str(totalResults) + ' total events recorded'
	print "Completed search, will resume in 24 hours"
	jOut.close()
	cOut.close()
	print
	time.sleep(3600*24) #scrape every 24 hours





