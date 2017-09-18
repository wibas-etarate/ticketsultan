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

class Parser(Object):
    source = None
    source_current = None
    cleaner = None

    website_content = None
    html_tree = None

    def __init__(self, source_id):
        self.sources = Source().key()
        self.__source_i = 0
        self.cleaner = Cleaner(style=True, links=True, add_nofollow=True, page_structure=False, safe_attrs_only=False)	
		urlfetch.set_default_fetch_deadline(60)

    def next_source(self):
        self.__source_i = self.__source_i + 1
        self.source_current = self.sources[__source_i]

        return self.source_current
    
    def pre_parse(self):
        pass

    def parse(self):
        execfile('./backend_service/parsers/'+self.source_current.parser_file)

    def post_parse(self):
        pass

    def get_source(self):
        return self.source_current

    def success(self):
        self.source_current.status = 'success'
        self.source_current.put()

    def failed(self):
        self.source_current.status = 'failed'
        self.source_current.put()
    
    def request_external_page(self):
        website = urlfetch.fetch(self.source_current.source.url)
        self.website_content = str(website.content)

        # Parses the HTML
		self.html_tree = html.fromstring(page)


    def clean_page(self):

    

