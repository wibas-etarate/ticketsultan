<<<<<<< HEAD
# -*- coding: utf-8 -*-
#The Content is within (tree) a XML representation of the HTML Page
=======
#!/usr/bin/python
# -*- coding: utf-8 -*-

# The Content is within (tree) a XML representation of the HTML Page
>>>>>>> ac3df9114a865ae4b223fc1a5d18f211641309da
# Add the end, start a task to get the detailed content
# PARAMS Available
# source = current Source
# tree = current XML (cleaned)

<<<<<<< HEAD
# Here we just parse the pages with tickets and extract the detail link.
import urlparse
import urllib
from datetime import datetime

content_part = tree.find(".//div[@id='content']")
content_part_tables = content_part.findall(".//table")
=======
print '-- Starting parsing parser_topevent24.py'
>>>>>>> ac3df9114a865ae4b223fc1a5d18f211641309da

content_part = tree.find(".//div[@id='content']")
content_part_tables = content_part.findall('.//table')

# print "----------------------"
# print content_part_tables
# print "----------------------"
try:
	table_content = content_part_tables[0]
except Exception as e:
	print "ERROR : content_part_tables is not correct, maybe content changed at target?"
	print source.url
	print ""
	print(e)

for tr in table_content:
<<<<<<< HEAD
	#print source.name.encode('iso-8859-1')
	#print etree.tostring(tr, xml_declaration=True)
	#print "----------------------"
	#print ""
	
	#IF the 4th tr not exist, continue with the next one
	if len(tr) < 4:
		continue

	try:
		if tr[4]:
			content_row_with_link = etree.tostring(tr[4], xml_declaration=True)
			#print "---"
			#print content_row_with_link
			#print "---"
			#print ""
			match_link = re.search(r'href=[\'"]?([^\'" >]+)', content_row_with_link)			
			if match_link:
				#print source.key.id()
				clean_url = str(match_link.group(0)[6:9999])
				clean_url = clean_url.replace('&amp;', '&')
				clean_url = urllib.unquote(clean_url)
				
				#print clean_url
				
				parsed_url_params = dict(urlparse.parse_qsl(clean_url))	#A bit dirty/lazy, but parsing the URL Params and blow the resulting touples into a dictionary 
				
				ticket_name = parsed_url_params['title'].replace('_',' ')
				ticket_date = datetime.strptime(parsed_url_params['date'], '%d.%m.%y')
				ticket_venue = parsed_url_params['venue'].replace('_',' ')
				
				ticket_city = parsed_url_params['place'].replace('_',' ')
				
				ticket_city_db = City.query(City.city_name==ticket_city).get()
				#print "city : " + str(ticket_city_db)

				ticket_country = Country.query(Country.country_name=='Deutschland').get()
				ticket_shop_id = parsed_url_params['default.asp?shopid']
				ticket_note = parsed_url_params['descr'].replace('_',' ') if 'descr' in parsed_url_params else ''
				
				# If we find the time in the document, we add id :-)
				if ticket_note:
					ticket_time = re.search(r"\_(.*?)\_", ticket_note) #regex check when there is a time in format _20:00_ and extracts the part
					print str(ticket_time)
					ticket_time = str( ticket_time.group(0) )
					print str(ticket_time)
					ticket_time = ticket_time.replace('_','') #remove the _
					print str(ticket_time)
					ticket_times = ticket_time.split(":") # Split the string to get hour and minute separate
					print "TICKET_TIME : " + str(ticket_times)

					ticket_date = datetime.combine(ticket_date, ticket_time)

				print "URL"
				print ticket_date
				print ticket_time
				print "----"
				
				
				ticket = Ticket()
				ticket.url = "http://www.topevents24.de/shop/" + str(clean_url)
				ticket.status = 'new'
				ticket.name = ticket_name
				ticket.start = ticket_date
				ticket.note = ticket_note
				ticket.city = ticket_city_db.key
				ticket.country = ticket_country.key
				ticket.source_id = source.key.id()
				ticket.put()
				
				#task = taskqueue.add( url='/admin/parse_ticket', params={'source_id': source.key.id(), 'ticket_id': ticket.key.id()} )
	except Exception as e:
		print "ERROR : "
		print e
		print("Unexpected error:", sys.exc_info())
		print traceback.print_exc(file=sys.stdout)
		print ""
=======
    #print '----------------------'
    # print etree.tostring(tr, xml_declaration=True)
    # print "----------------------"

    try:
        if tr[4]:
            match_link = re.search(r'href=[\'"]?([^\'" >]+)',
                                   etree.tostring(tr[4],
                                   xml_declaration=True))
			
            if match_link:
                clean_url = str(match_link.group(0)[6:9999])
                clean_url = clean_url.replace('&amp;', '&')
                
            ticket = Ticket()
            ticket.url = 'http://www.topevents24.de/shop/'+ str(clean_url)
            ticket.status = 'new'
            ticket.source_id = source.key.id()
            ticket.put()
			
            print "URL :        " + str(ticket.url)
            print "Source ID  : " + str(source.key.id())
            print "Ticket ID  : " + str(ticket.key.id())
            
			
            print "1. save ticket url ...success"
            try:
                task = taskqueue.add(url='/admin/parse_ticket',
                                     params={'source_id': source.key.id(),
                                     'ticket_id': ticket.key.id()})
            except Exception as e:
                print "error executing task"
                print(e)
                print ""
                
            
            print "2. create ticket parser task ...success"
        else:
            print 'INFO: no match found'
            
    except Exception as e:
        print "---"
        print "ERROR in parser_topevent24.py"
        print ""
        print(e)
        print "---"
        print ""

			
>>>>>>> ac3df9114a865ae4b223fc1a5d18f211641309da
