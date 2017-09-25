#!/usr/bin/env python
# encoding: utf-8

import os
import jinja2
import webapp2
from google.appengine.api import taskqueue
from google.appengine.api import memcache
from com.etarate.ticketsultan.backend.source import *
from com.etarate.ticketsultan.backend.ticket import *
from com.etarate.ticketsultan.backend.location import *
import logging

from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class SearchUpdateController(webapp2.RequestHandler):
    def get(self):
        tickets = Ticket().query(Ticket.status=='success-priced')
        for ticket in tickets:
            ticket.build_search_index()


class InitController(webapp2.RequestHandler):
    def get(self):
        # Purge Task Queue
        taskqueue.Queue('default').purge()
        taskqueue.Queue('sources').purge()
        taskqueue.Queue('tickets').purge()
        taskqueue.Queue('priceupdates').purge()
        logging.info('taksqueues purged')

        memcache.flush_all()
        logging.info('memcache flushed')

        # Delete existing entities:
        ndb.delete_multi(Source.query().fetch(keys_only=True))
        logging.debug('.. deleted Sources')
        ndb.delete_multi(Ticket.query().fetch(keys_only=True))
        logging.debug('.. deleted Tickets')
        ndb.delete_multi(Country.query().fetch(keys_only=True))
        logging.debug('.. deleted Countries')
        ndb.delete_multi(City.query().fetch(keys_only=True))
        logging.debug('.. deleted Cities')
        ndb.delete_multi(TicketPrice.query().fetch(keys_only=True))
        logging.debug('.. deleted Ticket Prices')
        ndb.delete_multi(TicketCategory.query().fetch(keys_only=True))
        logging.debug('.. deleted Ticket Categories')
        ndb.delete_multi(Currency.query().fetch(keys_only=True))
        logging.debug('.. deleted Currencies')

        logging.info('datastore initialized and emptied')
        # Ticket 24

        countries = ['Deutschland', u'Österreich', 'Schweiz']
        ticket_categories = [('Categorie 1',1),('Categorie 2',2),('Categorie 3',3),('Categorie 4',4),('Categorie 5',5)]
        currencies = [('Euro','EUR',"€", 1.00), ('Dollar','$',"$", 1.20), ('Schweizer Franken','CHF',"CHF", 1.24)]
        cities = [
            ('Mainz', 6), ('Berlin', 351), ('Bilefeld', 16), ('Bonn', 42), ('Bremen', 30), ('Dresden', 101),
            (u'Düsseldorf', 97),
            ('Erlangen', 4), ('Freiburg', 6), ('Hamburg', 260), ('Hannover', 66), ('Heidelberg', 9), ('Heilbronn', 21),
            ('Karlsruhe', 15), ('Kiel', 14), ('Leipzig', 112), ('Leverkusen', 15), ('Magdeburg', 26), (u'München', 110)
        ]

        for category,level in ticket_categories:
            tc = TicketCategory()
            tc.name = category
            tc.class_order = level
            tc.put()

        logging.info('ticket categories created')

        for name,short,symbol,factor in currencies:
            cur = Currency()
            cur.name = name
            cur.short = short
            cur.symbol = symbol
            cur.factor = factor
            cur.put()

        logging.info('currencies created')

        # Fill in countries into DB
        for country in countries:
            c = Country()
            c.country_name = country
            c.put()

            if c.country_name == 'Deutschland':
                country_de = c

        logging.info('countries created')

        # Fill in cities into DB
        for city, pages in cities:
            ci = City()
            ci.city_name = city
            ci.country = country_de.key
            ci.put()

        logging.info('cities created')

        # Create sources for
        source_entities = []
        for city, pages in cities:
            for page in range(1, pages):
                source = Source()
                source.name = 'www.topevents24.de ' + city + ' page ' + str(page) + ' of ' + str(pages)
                source.tec_name = 'topevents24'
                source.display_name = 'topevents24 ' + city + ' page ' + str(page) + ' of ' + str(pages)
                source.url = 'http://www.topevents24.de/shop/default.asp?id=2806&start=' + str(
                    page) + '&mode=search&place=' + city
                source.status = 'new'
                source.parser_file = 'parser_topevent24.py'
                source.parser_file_detail = 'parser_topevent24_detail.py'
                source_entities.append(source)
                logging.info('source created ... ' + source.name)
                break
            break
        logging.info('sources save ... ')
        ndb.put_multi(source_entities)
        logging.info('sources save success ')

        source_info = dict(Source().get_source_status())

        template_values = {
            'title': 'Initialization',
            'content': 'Initialization of the database is complete',
            'count_success': source_info['success'],
            'count_failed': source_info['failed'],
            'count_total': source_info['total'],
        }
        template = JINJA_ENVIRONMENT.get_template('views/main.html')
        self.response.write(template.render(template_values))


# Define available routes
ROUTES = [
    webapp2.Route(r'/admin/init', handler=InitController, name='sources'),
    webapp2.Route(r'/admin/init_search', handler=SearchUpdateController, name='search'),
]

app = webapp2.WSGIApplication(ROUTES, debug=True)
