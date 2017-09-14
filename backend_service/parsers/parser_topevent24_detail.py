# encoding: utf-8
from datetime import datetime
#The Content is within (tree) a XML representation of the HTML Page
# Add the end, start a task to get the detailed content

#content_part = tree.find(".//div[@id='content']")
#content_part_tables = content_part.findall(".//table")

cleaner2 = Cleaner(scripts=True, embedded=True, meta=True, page_structure=True, links=True, style=True, remove_tags = ['tr','td','div', 'p', 'b', 'br','p'])

content_part = tree.find(".//div[@id='content']")
content_part_tables = content_part.findall(".//table")[3].findall(".//table")[0].findall(".//td")
content_part_ticket_prices = content_part.findall(".//table")[4]

#print "***********************"
#
#for td in content_part_tables:
#	print "<<<<<<------>>>>>"
#	print cleaner2.clean_html(etree.tostring(td))
#
#print "*********************************************************"
print "Ticket URL : " + ticket.url

# Clean out all the bullshit
def clean_html(clean_string):
	result = clean_string.replace('<div>','').replace('</div>','')
	try:
		print "Encoded String Type"
		print type(result)
		result = result.encode('utf-8').decode('iso-8859-1')
		print type(result)
	except:
		print "failed to encode 1"
	result = result.strip()
	return str(result)

#select the element within the HTML page containing specific searchwords like "Ort:" and select the next (default +1) td to extract the content
def find_and_get_next_td(content_element, searchtext_list, next=1):
	i = 0
	for td in content_element:	#Loop throught the content Tds:
		cleaner_html = Cleaner(scripts=True, embedded=True, meta=True, page_structure=True, links=True, style=True, remove_tags = ['a','tr','td','div', 'p', 'b', 'br','p'])
		current_td = cleaner_html.clean_html( etree.tostring( td ) )
		#print "CURRENT TD Contains : " +str(current_td)
		is_found = False
		i=i+1
		
		for searchtext in searchtext_list:		
			if current_td.find(searchtext) > 0:
				is_found = True
				break
		
		if is_found: #If the content has been found, select the result next to it
			result = cleaner_html.clean_html( etree.tostring(content_element[i+next] ))# take the right element and send it for cleaning all the HTML bullshit
			#print "FOUND: taking " + str(next) + " element: " + str(result)
			return result
		
			
			

ticket_name_search_strings = ['Veranstaltung']
ticket_location_search_strings = ['Ort']
ticket_date_search_strings = ['Datum']

ticket.name = clean_html( find_and_get_next_td( content_part_tables, ticket_name_search_strings ) )
print "TICKET NAME :" + ticket.name

#ticket.city = clean_html( content_part_tables[6] )

ticket_city = clean_html( find_and_get_next_td( content_part_tables, ticket_location_search_strings ) )
print "TICKET CITY :" + ticket_city

#city = City.get_or_insert( city_name= clean_html( find_and_get_next_td( content_part_tables, ticket_location_search_strings ) ))
#ticket.city = [city.key,'']

#print "TICKET CITY :" + ticket.city.city_name

ticket_date = clean_html( find_and_get_next_td( content_part_tables, ticket_date_search_strings ) )
ticket.start = datetime.strptime(ticket_date, '%d.%m.%y')
print "TICKET DATE :" + str(ticket.start)

country = Country.query(Country.country_name=='Deutschland').get()

ticket.country = country.key



