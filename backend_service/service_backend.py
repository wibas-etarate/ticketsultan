# -*- coding: utf-8 -*-
# !/usr/bin/env python

import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

from com.etarate.ticketsultan.backend.source import *
from com.etarate.ticketsultan.backend.ticket import *
from com.etarate.ticketsultan.backend.location import *

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


# Welcome Screen
class MainController(webapp2.RequestHandler):
    def get(self):

        source_info = dict(Source().get_source_status())

        ticket_count = memcache.get('ticket_count')
        if ticket_count is None:
            tickets_result = Ticket.query().count_async()
            prices_result = TicketPrice.query().count_async()
            ticket_count = tickets_result.get_result()
            prices_count = prices_result.get_result()

            memcache.add('ticket_count', ticket_count, 300)
            memcache.add('prices_count', prices_count, 300)
        else:
            prices_count = memcache.get('prices_count')

        template_values = {
            'title': 'Welcome to TicketSultan Admin UI',
            'count_success': source_info['success'],
            'count_failed': source_info['failed'],
            'count_total': source_info['total'],
            'count_sources': source_info['total'],
            'count_tickets': ticket_count,
            'count_prices': prices_count,
        }

        template = JINJA_ENVIRONMENT.get_template('views/dashboard.html')
        self.response.write(template.render(template_values))


# Sources Management
class SourceController(webapp2.RequestHandler):
    def get(self):
        if self.request.get('delete'):
            id = int(self.request.get('delete'))
            print "DELETING SOURCE id:" + str(id)

            source = Source.get_by_id(id)
            source.key.delete()

        # Load all sources
        sources = Source.query().fetch(limit=100)
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
            'title': 'Source Saved',
        }
        template = JINJA_ENVIRONMENT.get_template('views/main.html')
        self.response.write(template.render(template_values))


class TicketController(webapp2.RequestHandler):
    def get(self):

        q = self.request.get('q')

        if q is not '':
            #search_options = search.QueryOptions()
            search_query = search.Query(query_string=q)
            search_results = search.Index(name='ticketsearchindex').search(query=search_query)

            id_list = []
            for id in search_results.results:
                key = ndb.Key('Ticket',int(id.doc_id))
                id_list.append(key)

            print id_list
            tickets = ndb.get_multi(id_list)
        else:
            tickets = Ticket.query().fetch(limit=100)

        source_info = dict(Source().get_source_status())
        logging.info(source_info)

        ticket_count = 'max 100'

        template_values = {
            'title': 'Tickets',
            'count_success': source_info['success'],
            'count_failed': source_info['failed'],
            'count_total': source_info['total'],
            'tickets': tickets,
            'ticket_count': ticket_count,
        }

        template = JINJA_ENVIRONMENT.get_template('views/tickets.html')
        self.response.write(template.render(template_values))


ROUTES = [
    webapp2.Route(r'/admin/', handler=MainController, name='admin'),
    webapp2.Route(r'/admin/sources', handler=SourceController, name='sources'),
    webapp2.Route(r'/admin/tickets', handler=TicketController, name='tickets'),
]

app = webapp2.WSGIApplication(ROUTES, debug=True)
