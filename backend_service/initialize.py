# encoding: utf-8
#!/usr/bin/env python
import webapp2
from google.appengine.api import taskqueue
from source import *
from ticket import *
from location import *

from google.appengine.ext import ndb


class InitController(webapp2.RequestHandler):
	def get(self):
		# Purge Task Queue
		q = taskqueue.Queue('default')
		q.purge()
		print "initializing... queue purged"
		
		# Delete existing entities:
		ndb.delete_multi(Source.query().fetch(keys_only=True))
		ndb.delete_multi(Ticket.query().fetch(keys_only=True))
		ndb.delete_multi(Country.query().fetch(keys_only=True))
		ndb.delete_multi(City.query().fetch(keys_only=True))
		
		print "initializing... tickets, sources, cities, countries ... dropped"
		# Ticket 24 
		
		#cities = ['Mainz','Berlin','Bilefeld','Bonn','Bremen','Dresden',u'Düsseldorf','Erlangen','Freiburg','Hamburg','Hannover','Heidelberg','Heilbronn','Karlsruhe','Kiel','Leipzig','Leverkusen','Magdeburg']
		#pages = [6,351,16,42,30,101,97,4,6,260,66,9,21,15,14,112,15,26]
		pages = [10,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
		
		#populating cities an Countries
		countries = [u'München','Deutschland', u'Österreich', 'Schweiz']
		cities = ['Mainz','Berlin','Bilefeld','Bonn','Bremen','Dresden',u'Düsseldorf','Erlangen','Freiburg','Hamburg','Hannover','Heidelberg','Heilbronn','Karlsruhe','Kiel','Leipzig','Leverkusen','Magdeburg']
		
		for country in countries:
			c = Country()
			c.country_name = country
			c.put()
			
			if c.country_name == 'Deutschland':
				country_de = c
		
		country_de_list = []
		country_de_list.append(c.key)
		
		for city in cities:
			ci = City()
			ci.city_name = city
			ci.country = country_de.key
			ci.put()
		
		
		cities = [u'München','Mainz','Berlin']
		pages = [10,1,1]
		
		p_i = 0
		for city in cities:
			pages_count = pages[p_i]
			for page in range(1,pages_count+1):
				source = Source()
				source.name = 'www.topevents24.de ' + city + ' page ' + str(page) + ' of ' + str(pages_count)
				source.display_name = 'topevents24 ' + city + ' page ' + str(page) + ' of ' + str(pages_count)
				source.url = 'http://www.topevents24.de/shop/default.asp?id=2806&start='+str(page)+'&mode=search&place='+ city
				source.status = 'new'
				source.parser_file = 'parser_topevent24.py'
				source.parser_file_detail = 'parser_topevent24_detail.py'
				source.put()
			p_i = p_i +1

# Define available routes
ROUTES = [
	webapp2.Route(r'/admin/init', handler=InitController, name='sources'),
]

app = webapp2.WSGIApplication(ROUTES, debug=True)