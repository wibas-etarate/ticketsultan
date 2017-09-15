# encoding: utf-8
#!/usr/bin/env python


import os
import urllib
import sys
import datetime
import logging
from datetime import timedelta

logging.debug(sys.path)

sys.path.append('../ticket_sultan/backend_service')

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import search

import jinja2
import webapp2
from backend_service.ticket import *



# Statics to control the paging behavior
_PAGING_LIMIT_PER_PAGE = 5
_PAGING_LIMIT_PAGES = 6


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# Welcome Screen
class MainController(webapp2.RequestHandler):
    def get(self):
		tickets = Ticket.query().order()

		today = datetime.datetime.now()
		
		yesterday = datetime.timedelta(days=-1)
		# tickets from today
		tickets_today = Ticket.query(Ticket.start >= today-yesterday).filter(Ticket.start <= today)
		#tickets_today = tickets_today.filter(Ticket.start <= today)
		# the next 4 tickets from today on
		tickets_next = Ticket.query(Ticket.start >= today).order(Ticket.start).fetch(limit=4)
		#tickets_next = tickets_next_query.fetch(limit=4)
		
		logging.info("Loaded Tickets from database " + str(tickets.count()))
		
		template_values = {
			'ticket_count': str( tickets.count() ),
			'tickets': tickets,
		}
		
		template = JINJA_ENVIRONMENT.get_template('template_engine/homepage-1.html')
		self.response.write(template.render(template_values))

# Helper class for Paging
class PageController(object):
	page_current = 0
	page_next = 0
	page_list = ['1','2']
	page_prev = 0
	page_count = 0
	ticket_count = 0	# Tickets found
	ticket_found = 0
	ticket_show_start = 0
	ticket_show_end = 0
	
	_request = None
	
	def __init__(self, request):
		self._request = request
		
		if self._request == None:
			logging.error("ERROR: You have to provide the request objext here")
			
	def calculate(self, search_result_query):
		print "calculating paging"
		self.page_list = []
		
		self.ticket_count = len(search_result_query.results)
		self.ticket_found = search_result_query.number_found
		self.ticket_show_start = int(self.page_current * _PAGING_LIMIT_PER_PAGE) - _PAGING_LIMIT_PER_PAGE
		self.ticket_show_end = int(self.page_current * _PAGING_LIMIT_PER_PAGE)
		
		#calculate the pages
		self.page_current = self.get_current_page()
		self.page_count = int((self.ticket_found % _PAGING_LIMIT_PER_PAGE) + 1)
		self.page_next = self.page_current +1
		self.page_prev = self.page_current -1
		
		render_page_start = self.page_current - (_PAGING_LIMIT_PAGES/2)
		render_page_end = render_page_start + _PAGING_LIMIT_PAGES
		
		if render_page_start < 1:
			render_page_start = 1
			render_page_end = render_page_start + _PAGING_LIMIT_PAGES
		
		for p in range(render_page_start, render_page_end):
			self.page_list.append(int(p))
		
	def get_current_page(self):
		current_page_number = self._request.get('page',1)
		return int(current_page_number)
	
	def get_page_offset(self):
		page_offset = int(self.get_current_page() * _PAGING_LIMIT_PER_PAGE) +1
		return page_offset
	
#Search detail page    
class SearchController(webapp2.RequestHandler):
    def get(self):
    	"""Search Request on page /search/"""
    	search_string = self.request.get('q')	
    	
    	page_controller = PageController(self.request)
    	
    	search_options = search.QueryOptions(limit = _PAGING_LIMIT_PER_PAGE, offset = page_controller.get_page_offset() )    	
    	search_query = search.Query(query_string=search_string,options=search_options)
    	search_results = search.Index(name='ticketsearchindex').search(query=search_query)
    	
    	page_infos = page_controller.calculate(search_results)
    
    	
    	template_values = {
            'tickets':search_results,
            'ticket_count':search_results.number_found,
            'ticket_show':len(search_results.results),
            'paging':page_controller,
        }
        
        template = JINJA_ENVIRONMENT.get_template('template_engine/search-result.html')
        self.response.write(template.render(template_values))

        
# Define available routes
ROUTES = [
	webapp2.Route(r'/', handler=MainController, name='welcome'),
	webapp2.Route(r'/search/', handler=SearchController, name='search'),
]

app = webapp2.WSGIApplication(ROUTES, debug=True)