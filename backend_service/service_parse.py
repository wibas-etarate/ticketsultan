# encoding: utf-8
#!/usr/bin/env python
import os

import jinja2
import webapp2
import logging
from google.appengine.api import taskqueue
from com.etarate.ticketsultan.backend.source import *
from com.etarate.ticketsultan.backend.ticket import *
from com.etarate.ticketsultan.backend.location import *
from com.etarate.ticketsultan.backend import *
from com.etarate.ticketsultan.backend.parsers.topevent24 import *


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


# Welcome Screen
class ParseController(webapp2.RequestHandler):
    def get(self):
        print "test started"

        #Load Sources "matching"
        sources = Source.query(Source.tec_name=='topevents24', Source.status=='new')
        logging.debug("loaded sources for topevents 24 - " + str(len(sources)))

        for source in sources:
            logging.debug('TopEvent24 class instance ' )
            source_id = source.key.id()
            print "SOURCE: " + str(source_id)

            taskqueue.add( queue_name='sources', url='/admin/parser/parse_source/', params={'source_id': source_id} )


class SourceController(webapp2.RequestHandler):
    def post(self):        
        source_id = str(self.request.get('source_id'))
        print "PARSE SOURCE START - SOURCE: " + str(source_id)
        
        parser_topevent24 = TopEvent24_Main()
        parser_topevent24.parse(source_id)

    def get(self):
        logging.warning("EXECUTED AS GET This service need to be called as post")

class PriceController(webapp2.RequestHandler):
    def post(self):
        ticket_id = str(self.request.get('ticket_id'))
        print "PRICE CONTROL START - TICKET: " + str(ticket_id)
        
        parser_topevent24 = TopEvent24_Main()
        parser_topevent24.parse_price(ticket_id)

    def get(self):
        logging.warning("EXECUTED AS GET This service need to be called as post")

# Define available routes
ROUTES = [
	webapp2.Route(r'/admin/parser/', handler=ParseController, name='parse'),
    webapp2.Route(r'/admin/parser/parse_source/', handler=SourceController, name='source'),
    webapp2.Route(r'/admin/parser/parse_price/', handler=PriceController, name='price'),
]

app = webapp2.WSGIApplication(ROUTES, debug=True)
