# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import re
import sys
import urllib
import logging
import traceback
import webapp2
import jinja2
import time
from lxml import html, etree
from lxml.html.clean import Cleaner
from com.etarate.ticketsultan.backend.source import *
from com.etarate.ticketsultan.backend.ticket import *
from com.etarate.ticketsultan.backend.location import *
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class MainController(webapp2.RequestHandler):
    def get(self):
		sources = Source().query(Source.status=='new')
		logging.info('Service Parse - Start Parsing')
		logging.debug('Loaded : ' + str(sources.count()) + ' sources')
		
		
		for source in sources:
			file = source.parser_file

			logging.debug('fetch URL: ' + source.url )
			
			cleaner = Cleaner(style=True, links=True, add_nofollow=True, page_structure=False, safe_attrs_only=False)	
			urlfetch.set_default_fetch_deadline(90)
			website = urlfetch.fetch(source.url)
			
			# Saves our content as a string
			page = str(website.content)
			page = cleaner.clean_html(page)
			# Parses the HTML
			tree = html.fromstring(page)
			
			try:
				logging.info('Service Parse - Start Parsing executing file '+str(file))
				execfile('./backend_service/parsers/'+file)
				source.status = 'success'
				source.put()
				time.sleep(1) # Not stress the endpoint to much, we wait some time before catching the next page
				logging.debug('Parser executed successfully')
			except Exception as e:
				source.status = 'failed'
				source.put()
				logging.error(e)
		
ROUTES = [
	webapp2.Route(r'/admin/parse_source', handler=MainController, name='parse'),
]

app = webapp2.WSGIApplication(ROUTES, debug=True)