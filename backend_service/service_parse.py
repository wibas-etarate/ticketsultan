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
from lxml import html, etree
from lxml.html.clean import Cleaner


from source import *
from ticket import *

from google.appengine.api import urlfetch
from google.appengine.api import taskqueue

from source import *

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class MainController(webapp2.RequestHandler):
    def get(self):
		sources = Source().query()
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
				print "executing file " +str(file)
				execfile('./backend_service/parsers/'+file)
				print "executing file " +str(file) + " success"
			except Exception as e:
				print ""
				print ""
				print e
				print("Unexpected error:", sys.exc_info()[0])
		
ROUTES = [
	webapp2.Route(r'/admin/parse_source', handler=MainController, name='parse'),
]

app = webapp2.WSGIApplication(ROUTES, debug=True)