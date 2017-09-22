#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys
import urllib
import urllib2
import logging
import traceback
import webapp2
import jinja2
import time
import datetime
from lxml import html, etree
from lxml.html.clean import Cleaner
from com.etarate.ticketsultan.backend.source import *
from com.etarate.ticketsultan.backend.ticket import *
from com.etarate.ticketsultan.backend.location import *
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch_errors import DeadlineExceededError
from google.appengine.api import taskqueue

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.autoescape'], autoescape=True)


class Parser(object):
    # The current source we are working in
    source = None
    ticket = None
    cleaner = None

    website_content = None
    html_tree = None

    def parse(self, source_id):
        if source_id is not None:
            _source_id = int(source_id)

            logging.info('Parsing with ID ' + str(_source_id))
            self.source = Source().get_by_id(_source_id)

            if self.source is None:
                logging.error('Source is none, nothing loaded... aborting parsing')
            else:
                logging.info('parser setup and loaded ' + str(_source_id))
                self.request_external_page(self.source.url)
        else:
            logging.warning('Source id does not exist')

    def success(self):
        if self.source is not None:
            self.source.status = 'success'
            self.put()

    def failed(self):
        if self.source is not None:
            self.source.status = 'failed'
            self.put()

    def get_source(self):
        return self.source_current

    # This method need to stay explicit to be capable to update the current price at any time
    def parse_price(self, ticket_id):
        if ticket_id is not None:
            _ticket_id = int(ticket_id)

            logging.info('Parsing ticket with ID ' + str(_ticket_id))
            self.ticket = Ticket().get_by_id(_ticket_id)

            if self.ticket is None:
                logging.error('Ticket is none, nothing loaded... aborting parsing')
            else:
                logging.info('parser setup and loaded ' + str(_ticket_id))
                self.request_external_page(self.ticket.url, False, True)
        else:
            logging.warning('Ticket id does not exist')

    def clean_html(self, clean_string):
        result = clean_string.replace('<div>', '').replace('</div>', '')
        try:
            result = result.encode('utf-8').decode('iso-8859-1')
        except:
            print "failed to encode"
        result = result.strip()
        return result

    def __clean_url(self, url):
        logging.info(u'cleaning url ' + url)

        try:
            url = url.replace(u'ä', '%E4')
            url = url.replace(u'Ä', '%C4')
            url = url.replace(u'ö', '%F6')
            url = url.replace(u'Ö', '%D6')
            url = url.replace(u'ü', '%FC')
            url = url.replace(u'Ü', '%DC')
        except Exception as e:
            logging.warning('Unable to clean url.. returning uncleaned')
            logging.warning(e)

        return url

    def request_external_page(self, parse_url, clean=True, replace_special=True):
        # logging.info('Requesting external site ' + str(parse_url.encode('utf-8').decode(encoding)) )
        self.cleaner = Cleaner(style=True, links=True, add_nofollow=True, page_structure=False, safe_attrs_only=False)
        urlfetch.set_default_fetch_deadline(60)  # 60 is the max allowed for tasks in google cloud.

        website = None
        timer = datetime.datetime.now()

        try:
            if replace_special == True:
                parse_url = self.__clean_url(parse_url)
            try:
                website = urlfetch.fetch(url=parse_url)
                timer_end = datetime.datetime.now()
                time_delta = timer_end - timer
                time_delta = int(time_delta.total_seconds() * 1000)
                logging.info('page request took :' + str(time_delta) + ' miliseconds')


                if time_delta >= 35000: # If pressure is to high, slow down
                    pass
                    # TODO return an error and handle a slow down with page requests
                    logging.warning('Fetch took > 35 seconds. We will slow down in the future the page requests.')


            except DeadlineExceededError as e:
                logging.warning('The website took to long to respond. try again')
                raise e
            except Exception as e:
                logging.error('Could not fetch external website')
                logging.error(e)

            self.website_content = website.content

            logging.info("content length : " + str(len(self.website_content)))

            # cleaning the html code before parsing
            if clean:
                logging.info("returning page cleaned from scrap")
                try:
                    self.website_content = self.cleaner.clean_html(self.website_content)
                except Exception as e:
                    logging.error('cleaning website content failed')
                    logging.error(e)

            try:
                self.html_tree = html.fromstring(self.website_content)
            except Exception as e:
                logging.error('Could not parse html to tree')
                logging.error(e)

            logging.debug(website.content)

        except Exception as e:
            logging.error("Loading of external page failed")
            logging.error(e)
