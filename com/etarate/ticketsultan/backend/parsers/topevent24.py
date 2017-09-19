# -*- coding: utf-8 -*-
#!/usr/bin/env python
import re
import urlparse
import urllib
import traceback
from datetime import datetime
from datetime import time
import time
from lxml import html, etree
from lxml.html.clean import Cleaner
from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
import logging

from com.etarate.ticketsultan.backend.parser import Parser

from com.etarate.ticketsultan.backend.source import *
from com.etarate.ticketsultan.backend.ticket import *
from com.etarate.ticketsultan.backend.location import *


class TopEvent24_Main(Parser):

    def parse(self, source_id):
        super(TopEvent24_Main, self).parse(source_id)

        
        #Find the contend Element in the Page (contains the tables with the links to pages)
        content_part = self.html_tree.find(".//div[@id='content']")
        #Parse all tables to be able to loop over (the page looks different all the time )
        content_part_tr = content_part.findall(".//table")
        logging.debug(content_part_tr)

        try:
	        table_content = content_part_tr[0]
        except Exception as e:
            logging.error('ERROR : content_part_tr is not correct, maybe content changed at target?')
            logging.error(e)

        for tr in table_content:
            #IF the 4th tr not exist, continue with the next one
            if len(tr) < 4:
                continue

            try:
                if tr[4] is not None:
                    content_row_with_link = etree.tostring(tr[4], xml_declaration=True)
                    logging.debug(content_row_with_link)
                    match_link = re.search(r'href=[\'"]?([^\'" >]+)', content_row_with_link)			
                    if match_link:
                        logging.debug("Source Key: " +str(self.source.key.id()))
                        
                        clean_url = str(match_link.group(0)[6:9999])
                        clean_url = clean_url.replace('&amp;', '&')
                        clean_url = urllib.unquote(clean_url)
                        
                        logging.debug("clean URL: " +str(clean_url))
                        
                        parsed_url_params = dict(urlparse.parse_qsl(clean_url))	#A bit dirty/lazy, but parsing the URL Params and blow the resulting touples into a dictionary 
                        
                        ticket_name = parsed_url_params['title'].replace('_',' ')
                        ticket_date = datetime.strptime(parsed_url_params['date'], '%d.%m.%y')
                        ticket_venue = parsed_url_params['venue'].replace('_',' ')
                        
                        ticket_city = parsed_url_params['place'].replace('_',' ')
                        
                        ticket_city_db = City.query(City.city_name==ticket_city).get()

                        ticket_shop_id = parsed_url_params['default.asp?shopid']
                        ticket_note = parsed_url_params['descr'] if 'descr' in parsed_url_params else ''
                        
                        # If we find the time in the document, we add id :-)
                        if len(ticket_note) > 5:
                            logging.debug("Ticket_Note :" + str(ticket_note))
                            ticket_time = re.search(r"\_(.*?)\_", ticket_note) #regex check when there is a time in format _20:00_ and extracts the part
                            ticket_time = str( ticket_time.group(0) )
                            ticket_time = ticket_time.replace('_','') #remove the _
                            ticket_times = ticket_time.split(":") # Split the string to get hour and minute separate
                            
                            #TODO add the time to datetime (there is some conflict with time and datetime class)
                            #ticket_time = datetime.time(int(ticket_times[0]), int(ticket_times[1]),0)
                            #print str(ticket_time)
                            #print type(ticket_time)
                            #ticket_date = datetime.combine(ticket_date, ticket_time)
                        
                        logging.debug("creating new ticket")
                        ticket = Ticket()
                        ticket.url = "http://www.topevents24.de/shop/" + str(clean_url)
                        ticket.name = ticket_name
                        ticket.price = int(0)
                        ticket.start = ticket_date
                        ticket.note = ticket_note.replace('_',' ')
                        ticket.city = ticket_city_db.key
                        ticket.country = Country.query(Country.country_name=='Deutschland').get().key
                        ticket.source_id = self.source.key.id()
                        
                        ticket.status = 'success'
                        ticket.put()

                        taskqueue.add( queue_name='priceupdates', url='/admin/parser/parse_price/ ', params={ 'ticket_id': str(ticket.key.id()) } )

            except Exception as e:
                logging.error(e)
                try:
                    #ticket.status = 'failed'
                    ticket.put()
                except:
                    pass

    def parse_price(self, ticket_id):
        super(TopEvent24_Main, self).parse_price(ticket_id)

        #Find the contend Element in the Page (contains the tables with the links to pages)
        
        logging.info('Parsing Price')
        logging.info(self.html_tree)
        content_part = self.html_tree.find(".//form[@name='pricelist']")

        logging.info('Parsing Content')

        logging.info(content_part)

        #Parse all tables to be able to loop over (the page looks different all the time )
        content_part_tr = content_part.findall(".//tr")


        print "-----------------------"
        for tr in content_part_tr:
            print "-------TR---------"
            print tr

        try:
	        table_content = content_part_tr[0]
        except Exception as e:
            logging.error('ERROR : content_part_tr is not correct, maybe content changed at target?')
            logging.error(e)
        

    def get_source(self):
        super(TopEvent24_Main, self).get_source()
        return self.source_current

        
