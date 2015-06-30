import lxml.etree as ET
import os
import time
from validate import validate
from resource_path import resource_path

def issue(uniqueIssue):
	message, issuePath, lineColumn = uniqueIssue
	tr_element = ET.Element('tr')
	issue_element = ET.Element('td')
	issuePath_element = ET.Element('td')
	lineColumn_element = ET.Element('td')
	tr_element.append(issue_element)
	tr_element.append(issuePath_element)
	tr_element.append(lineColumn_element)
	issue_element.text = message
	issuePath_element.text = issuePath
	lineColumn_element.text = lineColumn
	return tr_element


selfPath = os.path.realpath(__file__)
path = os.path.dirname(selfPath)

htmlTemplate = "<html><head><title>EAD Validation Report</title><link href='https://maxcdn.bootstrapcdn.com/bootstrap/2.3.2/css/bootstrap.min.css' rel='stylesheet'/></head><body style='padding:10px'><div class='jumbotron'><h1 class='h1'>EAD Validation Report</h1></div><div class='row-fluid'><div class='row-fluid'><div class='span4'/><div class='span8'/></div></div></body></html>"
htmlObject = ET.fromstring(htmlTemplate)
collection_table = ET.fromstring("<table class='table'><tr><th>Collection</th><th>Status</th><th>Issues</th></tr></table>")
collectionCount = 0
collectionError = 0
totalError = 0


for filename in os.listdir(path):
	
	if not filename.endswith('.xml'): continue
	xml_filename = os.path.join(path, filename)
	collId = os.path.splitext(filename)[0]
	collectionCount = collectionCount + 1
	try:
		xml_doc = ET.parse(xml_filename)
		xml_root = xml_doc.getroot()
	except Exception:
		colName = "unknown" 
	finally:
		issueCount, issueTriplet = validate(xml_filename)
	
	if xml_root.find('archdesc/did/unittitle') is None:
		colName = "unknown"
	else:
		colName = xml_root.find('archdesc/did/unittitle').text
		
	if '&' in colName:
		colName = colName.replace('&', 'and')
	
	if issueCount > 0:
		issueTable = ET.fromstring("<table id='" + collId + "' class='table table-hover' style='width:100%;border:1px solid #7DA9D4'><tr><th colspan='3' style='background-color:#7DA9D4'>" +  collId.upper() + ": " + colName + " (" + str(issueCount) + " issues)" + "</th></tr><tr><th>Issue</th><th>Path</th><th>Line:Column</th></tr></table>")
	
	for uniqueIssue in issueTriplet:
		issueRow = issue(uniqueIssue)
		issueTable.append(issueRow)
	
	totalError = totalError + issueCount
	
	#update left side collection table
	if issueCount == 0:
		tr_element = ET.Element('tr')
		tr_element.set('class', 'success')
		col_element = ET.Element('td')
		sta_element = ET.Element('td')
		iss_element = ET.Element('td')
		col_element.text = collId
		sta_element.text = "Valid"
		iss_element.text = str(issueCount) + " issues."
		tr_element.append(col_element)
		tr_element.append(sta_element)
		tr_element.append(iss_element)
		collection_table.append(tr_element)
		print filename + " is valid."
	else:
		collectionError = collectionError + 1
		tr_element = ET.Element('tr')
		tr_element.set('class', 'error')
		col_element = ET.Element('td')
		sta_element = ET.Element('td')
		iss_element = ET.Element('td')
		a_element = ET.Element('a')
		col_element.text = collId
		sta_element.append(a_element)
		a_element.set('href', '#' + collId)
		a_element.text = "INVALID"
		iss_element.text = str(issueCount) + " issues."
		tr_element.append(col_element)
		tr_element.append(sta_element)
		tr_element.append(iss_element)
		collection_table.append(tr_element)
		print filename + " is invalid."
		
		#create issue table
		htmlObject.find("body/div/div/div[@class='span8']").append(issueTable)
	
h5_element = ET.Element('h5')
h5_element.set('class', 'h5')
h5_element.text = "Generated " + str(time.strftime("%d/%m/%Y")) + ", " + str(time.strftime("%H:%M:%S"))
count_element = ET.Element('h5')
count_element.set('class', 'h5')
count_element.text = str(collectionError) + " of " + str(collectionCount) + " collections are invalid, with " + str(totalError) + " total errors."
print count_element.text
htmlObject.find("body/div/div/div[@class='span4']").append(h5_element)
htmlObject.find("body/div/div/div[@class='span4']").append(count_element)
htmlObject.find("body/div/div/div[@class='span4']").append(collection_table)
htmlString = ET.tostring(htmlObject, pretty_print=True)


output_path = path + "\\validation_report" + ".html"
file = open(output_path, "w")
file.write(htmlString)

