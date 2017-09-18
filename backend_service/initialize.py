# encoding: utf-8
#!/usr/bin/env python
import webapp2
from google.appengine.api import taskqueue
from com.etarate.ticketsultan.backend.source import *
from com.etarate.ticketsultan.backend.ticket import *
from com.etarate.ticketsultan.backend.location import *
import logging

from google.appengine.ext import ndb

class SearchUpdateController(webapp2.RequestHandler):
	def get(self):
		tickets = Ticket().query()
		for ticket in tickets:
			ticket.build_search_index()


class InitController(webapp2.RequestHandler):
	def get(self):
		# Purge Task Queue
		q = taskqueue.Queue('default')
		q.purge()
		logging.info('initializing... queue purged')
		
		# Delete existing entities:
		ndb.delete_multi(Source.query().fetch(keys_only=True))
		logging.debug('.. deleted Sources')
		ndb.delete_multi(Ticket.query().fetch(keys_only=True))
		logging.debug('.. deleted Tickets')
		ndb.delete_multi(Country.query().fetch(keys_only=True))
		logging.debug('.. deleted Countries')
		ndb.delete_multi(City.query().fetch(keys_only=True))
		logging.debug('.. deleted Cities')
		
		logging.info('datastore initialized and emptied')
		# Ticket 24 
		
		#populating cities an Countries
		countries = ['Deutschland', u'Österreich', 'Schweiz']
		
		cities = [
					('Mainz',6),('Berlin',351),('Bilefeld',16),('Bonn',42),('Bremen',30),('Dresden',101),(u'Düsseldorf',97),
					('Erlangen',4),('Freiburg',6),('Hamburg',260),('Hannover',66),('Heidelberg',9),('Heilbronn',21),
					('Karlsruhe',15),('Kiel',14),('Leipzig',112),('Leverkusen',15),('Magdeburg',26),(u'München',110)
				]

		#Fill in countries into DB
		for country in countries:
			c = Country()
			c.country_name = country
			c.put()
			
			if c.country_name == 'Deutschland':
				country_de = c
		
		#Fill in cities into DB
		for city,pages in cities:
			ci = City()
			ci.city_name = city
			ci.country = country_de.key
			ci.put()
		
		# Create sources for
		for city,pages in cities:
			for page in range(1,pages):
				source = Source()
				source.name = 'www.topevents24.de ' + city + ' page ' + str(page) + ' of ' + str(pages)
				source.tec_name = 'topevents24'
				source.display_name = 'topevents24 ' + city + ' page ' + str(page) + ' of ' + str(pages)
				source.url = 'http://www.topevents24.de/shop/default.asp?id=2806&start='+str(page)+'&mode=search&place='+ city
				source.status = 'new'
				source.parser_file = 'parser_topevent24.py'
				source.parser_file_detail = 'parser_topevent24_detail.py'
				source.put()
				break
		


		logging.info('Initilization complete')
# Define available routes
ROUTES = [
	webapp2.Route(r'/admin/init', handler=InitController, name='sources'),
	webapp2.Route(r'/admin/init_search', handler=SearchUpdateController, name='search'),
]

app = webapp2.WSGIApplication(ROUTES, debug=True)