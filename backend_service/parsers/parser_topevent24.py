# -*- coding: iso-8859-1 -*-
#The Content is within (tree) a XML representation of the HTML Page
# Add the end, start a task to get the detailed content
# PARAMS Available
# source = current Source 
# tree = current XML (cleaned)

content_part = tree.find(".//div[@id='content']")
content_part_tables = content_part.findall(".//table")

#print "----------------------"
#print content_part_tables
#print "----------------------"

table_content = content_part_tables[0]

for tr in table_content:
	#print "----------------------"
	print etree.tostring(tr, xml_declaration=True)
	#print "----------------------"
	try:
		if tr[4]:
			match_link = re.search(r'href=[\'"]?([^\'" >]+)', etree.tostring(tr[4], xml_declaration=True))			
			if match_link:
				print source.key.id()
	    		#print "FOUND : "  + str(match_link.group(0))
	    		clean_url = str(match_link.group(0)[6:999])
	    		clean_url = clean_url.replace('&amp;', '&')
	    		#print clean_url
	    		
	    		ticket = Ticket()
	    		
	    		ticket.url = "http://www.topevents24.de/shop/" + str(clean_url)
	    		ticket.status = 'new'
	    		ticket.source_id = source.key.id()
	    		ticket.put()
	    		
	    		task = taskqueue.add( url='/admin/parse_ticket', params={'source_id': source.key.id(), 'ticket_id': ticket.key.id()} )	
	    	else:
	    		print "no match found"
	except:
		print("Unexpected error:", sys.exc_info())
			