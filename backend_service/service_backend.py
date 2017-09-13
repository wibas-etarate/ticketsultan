# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

from ticket import *
from source import *

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# Welcome Screen
class MainController(webapp2.RequestHandler):
    def get(self):
    	print "BACKEND"
    	template_values = {
            'title': 'Welcome to TicketSultan Admin UI',
        }

        template = JINJA_ENVIRONMENT.get_template('views/main.html')
        self.response.write(template.render(template_values))

# Sources Management    	
class SourceController(webapp2.RequestHandler):
    def get(self):
    	
    	if self.request.get('delete'):
    		
    		id = int(self.request.get('delete'))
    		print "DELETING SOURCE id:" + str(id)
    		
    		source = Source.get_by_id(id)
    		
    		print source
    		
    		source.key.delete()
    	
    	# Load all sources
    	sources = Source.query()
    	source = None
    
    	template_values = {
            'sources': sources,
            'source': source,
        }

        template = JINJA_ENVIRONMENT.get_template('views/sources.html')
        self.response.write(template.render(template_values))
    
    def post(self):
    	print "Saving Source"
    	
    	source = Source()
    	source.name = self.request.get('dbname')
    	source.display_name = self.request.get('dbname')
    	source.url = self.request.get('url')
    	source.status = 'new'
    	source.parser_file = self.request.get('parserfile')
    	source.put()
    	
    	template_values = {
            'title': 'Ticket Saved',
        }
        template = JINJA_ENVIRONMENT.get_template('views/main.html')
        self.response.write(template.render(template_values))

# Define available routes
ROUTES = [
	webapp2.Route(r'/admin/', handler=MainController, name='admin'),
	webapp2.Route(r'/admin/sources', handler=SourceController, name='sources'),
]

app = webapp2.WSGIApplication(ROUTES, debug=True)