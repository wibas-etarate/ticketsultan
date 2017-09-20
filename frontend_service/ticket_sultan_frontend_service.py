# encoding: utf-8
# !/usr/bin/env python

import os
import urllib
import sys
import datetime
import logging
from datetime import timedelta
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.api import memcache
import jinja2
import webapp2
from com.etarate.ticketsultan.backend.source import *
from com.etarate.ticketsultan.backend.ticket import *
from com.etarate.ticketsultan.backend.location import *

logging.debug(sys.path)

sys.path.append('../ticket_sultan/backend_service')

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

        # Cache the Ticket count (so only first access is slow)
        ticket_count = memcache.get('ticket_count')
        if ticket_count is None:
            logging.info("writing ticket count to memcache")
            ticket_option = ndb.QueryOptions(keys_only=True)
            tickets = Ticket.query().fetch(options=ticket_option)
            ticket_count = len(tickets)

            memcache.add('ticket_count', ticket_count, 3600)

        today = datetime.datetime.now()

        yesterday = datetime.timedelta(days=-1)
        # tickets from today
        # blow into cache to speed up
        tickets_today = memcache.get('tickets_today')
        if tickets_today is None:
            logging.info("writing todays tickets to memcache")
            tickets_today = Ticket.query(Ticket.start >= today - yesterday).filter(Ticket.start <= today)
            memcache.add('tickets_today', tickets_today, 360)

        # the next 4 tickets from today on
        tickets_next = memcache.get('tickets-net')
        if tickets_next is None:
            logging.info("writing next tickets to memcache")
            tickets_next = Ticket.query(Ticket.start >= today).order(Ticket.start).fetch(limit=4)
            memcache.add('tickets_next', tickets_next, 120)

        # tickets_next = tickets_next_query.fetch(limit=4)

        logging.info("Loaded Tickets from database " + str(ticket_count))

        template_values = {
            'ticket_count': str(ticket_count),
            'tickets_today': tickets_today,
            'tickets_next': tickets_next,
        }

        template = JINJA_ENVIRONMENT.get_template('template_engine/homepage-1.html')
        self.response.write(template.render(template_values))


# Helper class for Paging
class PageController(object):
    page_current = 1
    page_next = 0
    page_list = ['1', '2']
    page_prev = 0
    page_count = 0
    ticket_count = 0  # Tickets found
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

        # calculate the pages
        self.page_current = self.get_current_page()
        self.page_count = int((self.ticket_found % _PAGING_LIMIT_PER_PAGE) + 1)
        self.page_next = self.page_current + 1
        self.page_prev = self.page_current - 1

        render_page_start = self.page_current - (_PAGING_LIMIT_PAGES / 2)
        render_page_end = render_page_start + _PAGING_LIMIT_PAGES

        if render_page_start < 1:
            render_page_start = 1
            render_page_end = render_page_start + _PAGING_LIMIT_PAGES

        for p in range(render_page_start, render_page_end):
            self.page_list.append(int(p))

    def get_current_page(self):
        current_page_number = self._request.get('page', 1)
        return int(current_page_number)

    def get_page_offset(self):
        page_offset = int(self.get_current_page() * _PAGING_LIMIT_PER_PAGE) + 1
        return page_offset


# Search detail page
class SearchController(webapp2.RequestHandler):
    def get(self):
        """Search Request on page /search/"""
        q = self.request.get('q')
        search_string = q
        location = self.request.get('location')

        # Cache cities
        locations = memcache.get('locations')
        if locations is None:
            logging.info("writing Cities to memcache")
            locations = City.query()
            memcache.add('locations', locations, 3600)

        page_controller = PageController(self.request)

        if location is not '' and len(location) > 5:
            print "location :" + str(location)
            if len(q) > 2:
                search_string = search_string + ' AND'
            search_string = search_string + " city=" + location

        # clean searchstring
        search_string = search_string.strip()

        search_options = search.QueryOptions(limit=_PAGING_LIMIT_PER_PAGE, offset=page_controller.get_page_offset())
        search_query = search.Query(query_string=search_string, options=search_options)
        search_results = search.Index(name='ticketsearchindex').search(query=search_query)

        logging.info('generated search string: ' + str(search_string))

        page_infos = page_controller.calculate(search_results)

        template_values = {
            'tickets': search_results,
            'ticket_count': search_results.number_found,
            'ticket_show': len(search_results.results),
            'paging': page_controller,
            'q': q,
            'locations': locations,
            'location': location,
        }

        template = JINJA_ENVIRONMENT.get_template('template_engine/search-result.html')
        self.response.write(template.render(template_values))


# Define available routes
ROUTES = [
    webapp2.Route(r'/', handler=MainController, name='welcome'),
    webapp2.Route(r'/search/', handler=SearchController, name='search'),
]

app = webapp2.WSGIApplication(ROUTES, debug=True)
