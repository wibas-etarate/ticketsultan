import sys
#import jinja2
import webapp2
from com.etarate.ticketsultan.backend.source import *
from com.etarate.ticketsultan.backend.ticket import *
from com.etarate.ticketsultan.backend.location import *

class DebugController(webapp2.RequestHandler):
    def get(self):
        template_values = {
            'tickets':'A',
        }
        print "Infos for TicketSultan"
        print "registered sys.path"
        print sys.path
        
        #template = JINJA_ENVIRONMENT.get_template('template_engine/search-result.html')
        self.response.write("Hello")


# Define available routes
ROUTES = [
	   webapp2.Route(r'/debug', handler=DebugController, name='debug'),
]

app = webapp2.WSGIApplication(ROUTES, debug=True)
