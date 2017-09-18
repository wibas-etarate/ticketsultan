# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import re
import sys
import urllib
import logging
import traceback
import webapp2

from lxml import html, etree
from lxml.html.clean import Cleaner

from com.etarate.ticketsultan.backend.source import *
from com.etarate.ticketsultan.backend.ticket import *
from com.etarate.ticketsultan.backend.location import *

from google.appengine.api import urlfetch
from google.appengine.api import taskqueue

from source import *

class MainController(webapp2.RequestHandler):
	def post(self):
	
		ticket_id = str(self.request.get('ticket_id'))
		source_id = str(self.request.get('source_id'))
		print ""
		print ""
		print ""
		print "Loading TICKET_ID: " + str(ticket_id) + " FROM SOURCE_ID " + str(source_id)
		print ""
		
		ticket = Ticket.get_by_id( int( ticket_id ) )
		source = Source.get_by_id( int( source_id ) )
		
		if (ticket.status == 'new' or ticket.status == 'failed'):
			#print "File"
			#print source.parser_file_detail
			
			cleaner = Cleaner(style=True, links=True, add_nofollow=True, page_structure=False, safe_attrs_only=False)	
			urlfetch.set_default_fetch_deadline(90)
			
			try:
				http_headers={'Accept-Charset': 'utf-8;q=0.7,*;q=0.7',}
				website = urlfetch.fetch(url=ticket.url, headers=http_headers )
			except:
				print "ERROR: URLFETCH of detail page failed"
			
			try:
				website.content = website.content.encode('utf-8').decode('iso-8559-1')
			except:
				print "encoding went wrong"
			
			# Saves our content as a string
			page = str(website.content)
			content = cleaner.clean_html(page)
			# Parses the HTML
			tree = html.fromstring(content)
			
			try:
				print "=== >> TICKET SAVE"
				execfile('./backend_service/parsers/'+ source.parser_file_detail)
				ticket.status = 'success'
				ticket.put()
			except:
				ticket.status = 'failed'
				ticket.put()
				print "=== >> ERROR Counld not Save Ticket"
				print("Unexpected error:", sys.exc_info()[0])

ROUTES = [
	webapp2.Route(r'/admin/', handler=MainController, name='admin'),
	webapp2.Route(r'/admin/parse_ticket', handler=MainController, name='parse_ticket'),
]

app = webapp2.WSGIApplication(ROUTES, debug=True)