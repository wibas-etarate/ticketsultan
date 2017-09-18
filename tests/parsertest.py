# encoding: utf-8
#!/usr/bin/env python

import jinja2
import webapp2

from com.etarate.ticketsultan.backend.source import *
from com.etarate.ticketsultan.backend.ticket import *
from com.etarate.ticketsultan.backend.location import *
from com.etarate.ticketsultan.backend import *
from com.etarate.ticketsultan.backend.parsers import *





JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


# Welcome Screen
class TestController(webapp2.RequestHandler):
    def get(self):
        print "test started"
        topevent24 = topevent24.TopEvent24()

# Define available routes
ROUTES = [
	webapp2.Route(r'/tests/parser/', handler=TestController, name='tedting'),
]

app = webapp2.WSGIApplication(ROUTES, debug=True)
