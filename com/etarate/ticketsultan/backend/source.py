#!/usr/bin/env python
from google.appengine.api import memcache
from google.appengine.ext import ndb


# Contains the sources where to download the content
class Source(ndb.Model):
    name = ndb.StringProperty(required=True)
    display_name = ndb.StringProperty(required=True)
    tec_name = ndb.StringProperty(required=True)
    url = ndb.StringProperty(required=True)
    status = ndb.StringProperty(required=True, choices=['new', 'collected', 'parse', 'success', 'failed'])
    parser_file = ndb.StringProperty(required=True)
    parser_file_detail = ndb.StringProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)

    @staticmethod
    def get_source_status():

        count_failed = memcache.get('sources_result_failed')

        if count_failed is None:
            sources_result_success = Source.query(Source.status == 'success').count_async()
            sources_result_failed = Source.query(Source.status == 'failed').count_async()
            sources_result_total = Source.query().count_async()

            count_success = sources_result_success.get_result()
            count_failed = sources_result_failed.get_result()
            count_total = sources_result_total.get_result()

            memcache.add('sources_result_success', count_success, 320)
            memcache.add('sources_result_failed', count_failed, 320)
            memcache.add('sources_result_total', count_total, 320)
        else:
            count_success = memcache.get('sources_result_success')
            count_total = memcache.get('sources_result_total')

        return [('success', count_success), ('failed', count_failed), ('total', count_total)]
