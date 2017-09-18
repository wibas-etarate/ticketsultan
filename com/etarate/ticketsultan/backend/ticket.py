# encoding: utf-8
#!/usr/bin/env python
from google.appengine.ext import ndb
from google.appengine.api import search
from source import *
import logging
from location import *
import pprint

# the ticket	
class Ticket(ndb.Model):
	name = ndb.StringProperty(required=False)
	start = ndb.DateTimeProperty()
	city = ndb.KeyProperty(kind='City',repeated=False)
	country = ndb.KeyProperty(kind='Country',repeated=False)
	note = ndb.StringProperty(required=False)
	price = ndb.FloatProperty()
	url = ndb.StringProperty(required=False) # Where is the detail page to get
	shop_url = ndb.StringProperty(required=False) # The final link for buying the ticket
	status = ndb.StringProperty(required=True, choices=['new','success','failed'])
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
					search.NumberField(name='price', value=self.price)
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


# the ticket	
class Ticket_Category(ndb.Model):
	name = ndb.StringProperty(required=True)
	