# -*- coding: utf-8 -*-
#!/usr/bin/env python

from com.etarate.ticketsultan.backend.parsers import Parser

class TopEvent24(Parser):
    
    def __init__(self, source_id):	
		urlfetch.set_default_fetch_deadline(60)

    def next_source(self):
        self.__source_i = self.__source_i + 1
        self.source_current = self.sources[__source_i]

        return self.source_current
    
    def pre_parse(self):
        pass

    def parse(self):
        execfile('./backend_service/parsers/'+self.source_current.parser_file)

    def post_parse(self):
        pass

    def get_source(self):
        return self.source_current

    def success(self):
        self.source_current.status = 'success'
        self.source_current.put()

    def failed(self):
        self.source_current.status = 'failed'
        self.source_current.put()
    
    def request_external_page(self):
        website = urlfetch.fetch(self.source_current.source.url)
        self.website_content = str(website.content)

        # Parses the HTML
		self.html_tree = html.fromstring(page)