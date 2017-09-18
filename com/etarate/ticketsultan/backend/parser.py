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
import time
from lxml import html, etree
from lxml.html.clean import Cleaner
from com.etarate.ticketsultan.backend.source import *
from com.etarate.ticketsultan.backend.ticket import *
from com.etarate.ticketsultan.backend.location import *
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),extensions=['jinja2.ext.autoescape'],autoescape=True)

class Parser(object):
    #The current source we are working in
    source = None
    ticket = None
    cleaner = None

    website_content = None
    html_tree = None        
    
    def parse(self, source_id):
        logging.info('Parsing with ID ' + str(source_id))
        
        self.source = Source().get_by_id( int(source_id) )

        logging.info('parser setup and loaded ' + str(self.source.key.id()))
        
        self.request_external_page(self.source.url)
        pass

    def get_source(self):
        return self.source_current
    
    #This method need to stay explicit to be capable to update the current price at any time
    def parse_price(self, ticket_id):
        self.ticket = Ticket().get_by_id( int(ticket_id) )
        self.request_external_page( self.ticket.url )

        pass

    def clean_html(self, clean_string):
        result = clean_string.replace('<div>','').replace('</div>','')
        try:
            result = result.encode('utf-8').decode('iso-8859-1')
        except:
            print "failed to encode"
        result = result.strip()
        return str(result)

    def request_external_page(self, parse_url, clean=True, encoding="iso-8859-1"):
        #logging.info('Requesting external site ' + str(parse_url.encode('utf-8').decode(encoding)) )
        self.cleaner = Cleaner(style=True, links=True, add_nofollow=True, page_structure=False, safe_attrs_only=False)
        urlfetch.set_default_fetch_deadline(60) #60 is the max allowed for tasks in google cloud.

        try:
            http_headers={'Accept-Charset': 'utf-8;q=0.7,*;q=0.7',}
            
            print type(parse_url)
            print parse_url
            parse_url_encoded = parse_url.decode('utf-8').encode(encoding)

            logging.info(parse_url_encoded)

            website = urlfetch.fetch(url=parse_url_encoded, headers=http_headers )
            
            self.website_content = str(website.content)
            
            # Parses the HTML

            if clean:
                logging.info("returning page cleanded")
                #html_cleaned = self.clean_html(self.website_content)
                html_cleaned = self.website_content
                self.html_tree = html.fromstring(self.cleaner.clean_html( html_cleaned ))
                logging.debug( str(website.content) )
            else:
                self.html_tree = html.fromstring(self.website_content)
                logging.debug( str(website.content) )

            
        except Exception as e:
            logging.error("Loading of external page failed")
            logging.error(e)

    

