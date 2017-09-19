#!/usr/bin/env python
from google.appengine.ext import ndb

# Contains the sources where to download the content
class Source(ndb.Model):
	name = ndb.StringProperty(required=True)
	display_name = ndb.StringProperty(required=True)
	tec_name = ndb.StringProperty(required=True)
	url = ndb.StringProperty(required=True)
	status = ndb.StringProperty(required=True, choices=['new','collected','parse','success','failed'])
	parser_file = ndb.StringProperty(required=True)
	parser_file_detail = ndb.StringProperty(required=True)
	created = ndb.DateTimeProperty(auto_now_add=True)
	updated = ndb.DateTimeProperty(auto_now=True)

	def get_source_status(self):
		sources_success = Source.query(Source.status=='success').fetch(keys_only=True) 
		sources_failed = Source.query(Source.status=='failed').fetch(keys_only=True)
		sources_total = Source.query().fetch(keys_only=True)

		count_success = len(sources_success)
		count_failed = len(sources_failed)
		count_total = len(sources_total)

		return [('success',count_success),('failed',count_failed),('total',count_total)]

	