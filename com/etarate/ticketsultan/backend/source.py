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
	