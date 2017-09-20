#!/usr/bin/env python
# encoding: utf-8

import logging

from location import *


# the ticket
class Ticket(ndb.Model):
    name = ndb.StringProperty(required=False)
    start = ndb.DateTimeProperty()
    city = ndb.KeyProperty(kind='City', repeated=False)
    country = ndb.KeyProperty(kind='Country', repeated=False)
    note = ndb.StringProperty(required=False)
    prices = ndb.KeyProperty(kind='TicketPrice', repeated=True)
    url = ndb.StringProperty(required=False)  # Where is the detail page to get
    status = ndb.StringProperty(required=True, choices=['new', 'success', 'failed'])
    source_id = ndb.IntegerProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    def _post_put_hook(self, future):
        self.build_search_index()

    def build_search_index(self):
        if self.status == 'success':
            logging.debug('Updating search index for ' + str(self.key.id()))
            model_city = self.city.get()
            model_country = self.country.get()

            try:
                document = search.Document(
                    fields=[
                        search.TextField(name='name', value=self.name, language='de'),
                        search.DateField(name='date', value=self.start),
                        search.TextField(name='city', value=model_city.city_name, language='de'),
                        search.TextField(name='country', value=model_country.country_name),
                        #search.NumberField(name='price', value=self.price)
                    ])
            except Exception as e:
                logging.error("there is an error in the search document")
                logging.error(e)
            try:
                logging.debug('search index creation success')
                index = search.Index(name="ticketsearchindex").put(document)
            except Exception as e:
                logging.error('saving of the search document failed')
                logging.error(e)


class TicketCategory(ndb.Model):
    name = ndb.StringProperty(required=True)
    class_order = ndb.FloatProperty()


class TicketPrice(ndb.Model):
    category = ndb.KeyProperty(kind='TicketCategory', repeated=False)
    price = ndb.FloatProperty()
    currency = ndb.KeyProperty(kind='Currency', repeated=False)
    shop_url = ndb.StringProperty(required=False)


class Currency(ndb.Model):
    name = ndb.StringProperty(required=True)
    short = ndb.StringProperty(required=True)
    symbol = ndb.StringProperty(required=True)
    factor = ndb.FloatProperty()