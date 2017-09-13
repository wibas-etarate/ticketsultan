#!/usr/bin/python
# -*- coding: utf-8 -*-

# The Content is within (tree) a XML representation of the HTML Page
# Add the end, start a task to get the detailed content
# PARAMS Available
# source = current Source
# tree = current XML (cleaned)

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

			