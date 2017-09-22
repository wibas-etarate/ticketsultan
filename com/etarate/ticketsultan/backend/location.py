#!/usr/bin/env python
from google.appengine.ext import ndb
from google.appengine.api import search
from source import *


# Location for Tickets
class Location(ndb.Model):
    location_name = ndb.StringProperty(required=False)
    street = ndb.StringProperty(required=False)
    city = ndb.KeyProperty(kind='City', repeated=False)
    geo_location = ndb.StringProperty(required=False)


# City for Tickets
class City(ndb.Model):
    city_name = ndb.StringProperty(required=True)
    country = ndb.KeyProperty(kind='Country', repeated=False)


# Country for Tickets
class Country(ndb.Model):
    country_name = ndb.StringProperty(required=False)
