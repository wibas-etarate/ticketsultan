# -*- coding: utf-8 -*-

# The Content is within (tree) a XML representation of the HTML Page
# Add the end, start a task to get the detailed content
# PARAMS Available
# source = current Source
# tree = current XML (cleaned)

# Here we just parse the pages with tickets and extract the detail link.
import urlparse
import urllib
from datetime import datetime
from datetime import time

content_part = tree.find(".//div[@id='content']")
content_part_tables = content_part.findall(".//table")

print '-- Starting parsing parser_topevent24.py'

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
				ticket_note = parsed_url_params['descr'] if 'descr' in parsed_url_params else ''
				
				# If we find the time in the document, we add id :-)
				if len(ticket_note) > 5:
					print "Ticket_Note :" + ticket_note
					ticket_time = re.search(r"\_(.*?)\_", ticket_note) #regex check when there is a time in format _20:00_ and extracts the part
					ticket_time = str( ticket_time.group(0) )
					ticket_time = ticket_time.replace('_','') #remove the _
					ticket_times = ticket_time.split(":") # Split the string to get hour and minute separate
					
					#TODO add the time to datetime (there is some conflict with time and datetime class)
					#ticket_time = datetime.time(int(ticket_times[0]), int(ticket_times[1]),0)
					print str(ticket_time)
					print type(ticket_time)
					#ticket_date = datetime.combine(ticket_date, ticket_time)
				
				ticket = Ticket()
				ticket.url = "http://www.topevents24.de/shop/" + str(clean_url)
				ticket.status = 'success'
				ticket.name = ticket_name
				ticket.start = ticket_date
				ticket.note = ticket_note.replace('_',' ')
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
