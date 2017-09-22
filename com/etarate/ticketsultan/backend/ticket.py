#!/usr/bin/env python
# encoding: utf-8

import logging

from location import *
from source import *


# the ticket
class Ticket(ndb.Model):
    name = ndb.StringProperty(required=False)
    start = ndb.DateTimeProperty(indexed = True)
    city = ndb.KeyProperty(kind='City', repeated=False, indexed = True)
    country = ndb.KeyProperty(kind='Country', repeated=False)
    note = ndb.StringProperty(required=False)
    prices = ndb.KeyProperty(kind='TicketPrice', repeated=True)
    url = ndb.StringProperty(required=False)  # Where is the detail page to get
    status = ndb.StringProperty(required=True, choices=['new', 'success', 'success-priced', 'failed'], indexed = True)
    source = ndb.KeyProperty(kind='Source', repeated=False)
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @property
    def get_best_price_value(self):
        """
        gets the best price for a ticket or 0
        :return: float best price
        """
        price_list = []
        for price in self.prices:
            price_list.append(price.get().price)

        try:
            best_price = min(float(p) for p in price_list)
            return best_price
        except ValueError:
            return float(0.0)

    def drop_prices(self):
        for price in self.prices:
            price.delete()

        self.prices = []
        self.put()


    def add_price(self, category_class_number, amount, status, shop_url='http://', currency='EUR'):
        price = TicketPrice()
        price.category = TicketCategory().query(TicketCategory.class_order == category_class_number).get().key
        price.currency = Currency().query(Currency.short == currency).get().key
        price.status = status
        price.price = amount
        price.shop_url = shop_url
        price.put()

        self.prices.append(price.key)

        try:
            self.put()
        except Exception as e:
            logging.error(e)

    def _post_put_hook(self, future):
        self.build_search_index()

    def build_search_index(self):
        if self.status == 'success-priced':
            logging.debug('Updating search index for ' + str(self.key.id()))

            # check if index already exists: if exist, delete it
            index = search.Index('ticketsearchindex')
            index.delete(str(self.key.id()))

            model_city = self.city.get()
            model_country = self.country.get()

            best_price = self.get_best_price_value

            try:
                document = search.Document(doc_id=str(self.key.id()),
                                           fields=[
                                               search.TextField(name='name', value=self.name, language='de'),
                                               search.TextField(name='description', value=self.note, language='de'),
                                               search.DateField(name='date', value=self.start),
                                               search.TextField(name='city', value=model_city.city_name, language='de'),
                                               search.TextField(name='country', value=model_country.country_name),
                                               search.NumberField(name='best_price', value=best_price)
                                           ])
            except Exception as e:
                logging.error("there is an error in the search document")
                logging.error(e)
            try:
                logging.debug('search index creation success')
                search.Index(name="ticketsearchindex").put(document)
            except Exception as e:
                logging.error('saving of the search document failed')
                logging.error(e)


class TicketCategory(ndb.Model):
    name = ndb.StringProperty(required=True)
    class_order = ndb.FloatProperty()


class TicketPrice(ndb.Model):
    category = ndb.KeyProperty(kind='TicketCategory', repeated=False)
    status = ndb.StringProperty(required=True, choices=['available', 'not available', 'on sale'])
    price = ndb.FloatProperty(default=0)
    currency = ndb.KeyProperty(kind='Currency', repeated=False)
    shop_url = ndb.StringProperty(required=False, default='')


class Currency(ndb.Model):
    name = ndb.StringProperty(required=True)
    short = ndb.StringProperty(required=True)
    symbol = ndb.StringProperty(required=True)
    factor = ndb.FloatProperty(default=1.0000)
