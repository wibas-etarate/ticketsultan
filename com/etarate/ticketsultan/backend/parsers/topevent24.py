# -*- coding: utf-8 -*-
# !/usr/bin/env python
import re
import urllib
import urlparse
from datetime import datetime

from lxml import etree

from com.etarate.ticketsultan.backend.location import *
from com.etarate.ticketsultan.backend.parsers.parser import Parser
from com.etarate.ticketsultan.backend.ticket import *


class TopEvent24Main(Parser):
    def parse(self, source_id):
        super(TopEvent24Main, self).parse(source_id)

        # Find the contend Element in the Page (contains the tables with the links to pages)
        try:
            content_part = self.html_tree.find(".//div[@id='content']")
        except AttributeError as e:
            logging.warning('this source had some issues. No content arrived')
            logging.warning(e)
            return

        # Parse all tables to be able to loop over (the page looks different all the time )
        content_part_tr = content_part.findall(".//table")
        logging.debug(content_part_tr)

        try:
            table_content = content_part_tr[0]
        except Exception as e:
            logging.error('ERROR : content_part_tr is not correct, maybe content changed at target?')
            logging.error(e)

        for tr in table_content:
            # IF the 4th tr not exist, continue with the next one
            if len(tr) < 4:
                continue

            try:
                if tr[4] is not None:
                    content_row_with_link = etree.tostring(tr[4], xml_declaration=True)
                    logging.debug(content_row_with_link)
                    match_link = re.search(r'href=[\'"]?([^\'" >]+)', content_row_with_link)
                    if match_link:
                        logging.debug("Source Key: " + str(self.source.key.id()))

                        clean_url = str(match_link.group(0)[6:9999])
                        clean_url = clean_url.replace('&amp;', '&')
                        clean_url = urllib.unquote(clean_url)

                        logging.debug("clean URL: " + str(clean_url))

                        # A bit dirty/lazy, but parsing the URL Params and blow the resulting
                        # touples into a dictionary
                        parsed_url_params = dict(urlparse.parse_qsl(
                            clean_url))

                        ticket_name = parsed_url_params['title'].replace('_', ' ')
                        ticket_date = datetime.strptime(parsed_url_params['date'], '%d.%m.%y')
                        ticket_venue = parsed_url_params['venue'].replace('_', ' ')

                        ticket_city = parsed_url_params['place'].replace('_', ' ')

                        ticket_city_db = City.query(City.city_name == ticket_city).get()

                        ticket_shop_id = parsed_url_params['default.asp?shopid']
                        ticket_note = parsed_url_params['descr'] if 'descr' in parsed_url_params else ''

                        # If we find the time in the document, we add id :-)
                        if len(ticket_note) > 5:
                            logging.debug("Ticket_Note :" + str(ticket_note))
                            ticket_time = re.search(r"\_(.*?)\_",
                                                    ticket_note)  # regex check when there is a time in format _20:00_ and extracts the part
                            ticket_time = str(ticket_time.group(0))
                            ticket_time = ticket_time.replace('_', '')  # remove the _
                            ticket_times = ticket_time.split(":")  # Split the string to get hour and minute separate

                            h = int(ticket_times[0])
                            m = int(ticket_times[1])
                            s = 0

                            ticket_time = datetime(ticket_date.year, ticket_date.month, ticket_date.day, h, m, s)
                            # print str(ticket_time)
                            # print type(ticket_time)
                            #ticket_date = datetime.combine(ticket_date, ticket_time)

                        logging.debug("creating new ticket")
                        ticket = Ticket()
                        ticket.url = "http://www.topevents24.de/shop/" + str(clean_url)
                        ticket.name = ticket_name
                        ticket.start = ticket_time
                        ticket.note = ticket_note.replace('_', ' ')
                        ticket.city = ticket_city_db.key
                        ticket.country = Country.query(Country.country_name == 'Deutschland').get().key
                        ticket.source = self.source.key

                        ticket.status = 'success'
                        ticket.put()

                        # taskqueue.add(queue_name='priceupdates', url='/admin/parser/parse_price/',
                        #              params={'ticket_id': str(ticket.key.id())})

            except Exception as e:
                logging.error(e)
                try:
                    # ticket.status = 'failed'
                    ticket.put()
                except:
                    pass

    def parse_price(self, ticket_id):
        super(TopEvent24Main, self).parse_price(ticket_id)

        # delete prices in current ticket
        self.ticket.drop_prices()

        logging.info('Parsing Price')
        html_form = self.html_tree.find('.//form[@action="hopper.asp"]')

        if html_form is None:
            self.ticket.status = 'failed'
            self.ticket.put()
            return

        html_table = html_form.find('.//table')

        if html_table is None:
            self.ticket.status = 'failed'
            self.ticket.put()
            return

        html_rows = html_table.findall('.//tr')

        if html_rows is None:
            self.ticket.status = 'failed'
            self.ticket.put()
            return

        # TODO if there are multiple prices, extract them
        for tr in html_rows:
            if tr.attrib['class'] == 'thead':  # we ignore the head
                pass
            else:
                html_subtable = tr.find('.//table')  # check if there are some cards to buy available

                if html_subtable is not None:  # Yes we have cards to buy
                    html_subtable_rows = html_subtable.findall('.//tr')

                    rows = len(html_subtable_rows)

                    if rows == 2:  # Not bookable
                        self.ticket.add_price(1, float(0.0), 'not available')
                    elif rows >= 3:
                        # Cards to buy are in a table with 3 trs
                        content_row = html_subtable_rows[1]
                        content_tds = content_row.findall('.//td')

                        ticket_category = content_tds[0].text

                        ticket_id = 5
                        if ticket_category == 'Kat.1':
                            ticket_id = 1
                        elif ticket_category == 'Kat.2':
                            ticket_id = 2
                        elif ticket_category == 'Kat.3':
                            ticket_id = 3
                        elif ticket_category == 'Kat.4':
                            ticket_id = 4

                        ticket_currency = content_tds[4].text
                        ticket_price = float(content_tds[5].text.replace(',', '.'))

                        self.ticket.add_price(ticket_id, ticket_price, 'available')
                    else:
                        logging.warning('Ticket Price cols do not match filter, CHECK IT BABY!')

        self.ticket.status='success-priced'
        self.ticket.put()

    def get_source(self):
        super(TopEvent24Main, self).get_source()
        return self.source_current
