# -*- coding: utf-8 -*-
#!/usr/bin/env python
import sys
import logging
import webapp2


class MainController(webapp2.RequestHandler):
    def get(self):
        url = u"http://www.topevents24.de/shop/default.asp?id=2806&start=4&mode=search&place=München".encode('utf-8').strip()
        
        logging.info(url)
        


        url = url.replace('ä','%E4')
        url = url.replace('Ä','%C4')
        url = url.replace('ö','%F6')
        url = url.replace('Ö','%D6')
        url = url.replace('ü','%FC')
        url = url.replace('Ü','%DC')

        #url_object = dict(urlparse.parse_qs(url))



        logging.info( url )
        
        #url = url.encode('utf-8')
        #print url
        
        #url_enc = urllib2.quote(url)
        


# Define available routes
ROUTES = [
	webapp2.Route(r'/test', handler=MainController, name='admin'),
]

app = webapp2.WSGIApplication(ROUTES, debug=True)