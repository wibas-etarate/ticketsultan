# -*- coding: utf-8 -*-
#!/usr/bin/env python
from com.etarate.ticketsultan.backend.parser import *


class MainController(webapp2.RequestHandler):
    def get(self):
		parser = Parser()
		
		source_task = taskqueue.add( target='sources', url='/admin/parse_source_task', params={'source_id': source.key.id(), 'ticket_id': ticket.key.id()} )


ROUTES = [
	webapp2.Route(r'/admin/parse_source', handler=MainController, name='parse'),
]

app = webapp2.WSGIApplication(ROUTES, debug=True)