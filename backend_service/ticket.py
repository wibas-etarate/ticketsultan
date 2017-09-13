# encoding: utf-8
#!/usr/bin/env python
from google.appengine.ext import ndb
from google.appengine.api import search
from source import *
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
	shop_url = ndb.StringProperty(required=False) # Where is the detail page to get	
	status = ndb.StringProperty(required=True, choices=['new','success','failed'])
	source_id = ndb.IntegerProperty()
	created = ndb.DateTimeProperty(auto_now_add=True)
	updated = ndb.DateTimeProperty(auto_now=True)
	
	def _post_put_hook(self, future):
		if self.status == 'success':
			print ".....updating ndb model for search"	
			try:
				document = search.Document(
				    doc_id = str(self.key.id()),
				    fields=[
				       search.TextField(name='name', value=self.name),
				       search.DateField(name='date', value=self.start),
				       search.TextField(name='city', value=self.city.city_name),
				       search.TextField(name='country', value=self.country.country_name),
				       ])
			except:
				print "... Error creating the search document."
				raise
			
			try:
			    print "search index ok"
			    index = search.Index(name="ticketsearchindex").put(document)
			except search.Error:
				print "ERROR putting search index"
				logging.exception('Put failed')
	


