import lxml.etree as ET
import codecs
import os
import re
from resource_path import resource_path

def validate(xml_filename):

	# called on each error that is found and reports the error
	def error_check(issueCount, issueTriplet, message, element):
		issueCount = issueCount + 1
		issueTriplet.append([message + ".", str(element.getroottree().getpath(element))[1:], str(element.sourceline) + ":"])
		return issueCount, issueTriplet
	
################ Validation rules for @normal dates ###############################################################################################	
	def check_normal(issueCount, issueTriplet, xml_root, element):
		if not 'normal' in element.attrib:
			issueCount = issueCount + 1
			issueTriplet.append(["<" + element.tag + ">" + " element has no @normal.", str(element.getroottree().getpath(element))[1:], str(element.sourceline) + ":"])
		else:
			if re.search('[a-zA-Z]', element.attrib['normal']):
				issueCount = issueCount + 1
				issueTriplet.append(["<" + element.tag + ">" + " @normal is incorrect, contains alphabetical characters.", str(element.getroottree().getpath(element)), str(element.sourceline) + ":"])
			normalLength = (4, 7, 9, 10, 12, 15, 18, 21)
			if not len(element.attrib['normal']) in normalLength:
				issueCount = issueCount + 1
				issueTriplet.append(["<" + element.tag + ">" + " @normal is invalid, does not contain a correct number of characters", str(element.getroottree().getpath(element)), str(element.sourceline) + ":"])
			else:
				if len(element.attrib['normal']) > 4:
					if "/" in element.attrib['normal'] or "-" in element.attrib['normal']:
						if element.attrib['normal'].count('/') > 1:
							issueCount = issueCount + 1
							issueTriplet.append(["<" + element.tag + ">" + " @normal is invalid", str(element.getroottree().getpath(element)), str(element.sourceline) + ":"])
					else:
						issueCount = issueCount + 1
						issueTriplet.append(["<" + element.tag + ">" + " @normal is invalid, must use '-' or '/' to encode complex dates", str(element.getroottree().getpath(element)), str(element.sourceline) + ":"])
				if len(element.attrib['normal']) == 9:
					if "-" in element.attrib['normal']:
						if element.attrib['normal'].count('-') == 1:
							if len(element.attrib['normal'].split('-')[0]) != 4 or len(element.attrib['normal'].split('-')[1]) != 4:
								issueCount = issueCount + 1
								issueTriplet.append(["<" + element.tag + ">" + " @normal is invalid", str(element.getroottree().getpath(element)), str(element.sourceline) + ":"])
						elif element.attrib['normal'].count('-') == 2:
							if len(element.attrib['normal'].split('-')[0]) != 4 or len(element.attrib['normal'].split('-')[1]) != 2 or len(element.attrib['normal'].split('-')[3]) != 2:
								issueCount = issueCount + 1
								issueTriplet.append(["<" + element.tag + ">" + " @normal is invalid", str(element.getroottree().getpath(element)), str(element.sourceline) + ":"])
						else:
							issueCount = issueCount + 1
							issueTriplet.append(["<" + element.tag + ">" + " @normal is invalid", str(element.getroottree().getpath(element)), str(element.sourceline) + ":"])
					elif "/" in element.attrib['normal']:
						if len(element.attrib['normal'].split('/')[0]) != 4 or len(element.attrib['normal'].split('/')[1]) != 4:
							issueCount = issueCount + 1
							issueTriplet.append(["<" + element.tag + ">" + " @normal is invalid", str(element.getroottree().getpath(element)), str(element.sourceline) + ":"])
					else:
						issueCount = issueCount + 1
						issueTriplet.append(["<" + element.tag + ">" + " @normal is invalid", str(element.getroottree().getpath(element)), str(element.sourceline) + ":"])
				elif len(element.attrib['normal']) == 7:
					if "-" in element.attrib['normal']:
						if len(element.attrib['normal'].split('-')[0]) != 4 or len(element.attrib['normal'].split('-')[1]) != 2:
							issueCount = issueCount + 1
							issueTriplet.append(["<" + element.tag + ">" + " @normal is invalid", str(element.getroottree().getpath(element)), str(element.sourceline) + ":"])
					else:
						issueCount = issueCount + 1
						issueTriplet.append(["<" + element.tag + ">" + " @normal is invalid", str(element.getroottree().getpath(element)), str(element.sourceline) + ":"])
		return issueCount, issueTriplet

############### Validation rules for series and subseries #############################################################################################		
	def check_series(issueCount, issueTriplet, parent, series, collId):
		#id check
		if not "id" in series.attrib:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Component <" + series.tag + "> missing @id", series)
		else:
			if not series.attrib['id'].startswith('nam_' + collId):
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Component <" + series.tag + "> @id is incorrect", series)
		
		if series.find('did') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <did> in <" + series.tag + "> element", series)
		else:
			if series.find('did/unittitle') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <unittitle> in <" + series.tag + "> element", series.find('did'))
			else:
				if not series.find('did/unittitle').text:
					if series.find('did/unittitle/emph') is None and series.find('did/unittitle/title') is None:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<unittitle> element is empty.", series.find('did/unittitle'))
			if series.find('did/unitid') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <unitid> in <" + series.tag + "> element", series.find('did'))
			if series.find('did/unitdate') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <unitdate> in <" + series.tag + "> element", series.find('did'))
			for emptyDate in series.find('did'):
				if emptyDate.tag == "unitdate":
					if emptyDate.text.endswith(','):
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid comma (,) at the end of <unitdate> element", emptyDate)
					elif emptyDate.text.endswith(', '):
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid comma (, ) at the end of <unitdate> element", emptyDate)
					elif emptyDate.text.endswith(' '):
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid space ( ) at the end of <unitdate> element", emptyDate)
			seriesDate = 0
			for seriesChild in series.find('did'):
				if not seriesChild.text:
					if not seriesChild.tag == "physdesc":
						if childElement.find('emph') is None:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<" + seriesChild.tag + "> element is empty", seriesChild)
				elif seriesChild.tag == "unittitle":
					if not "label" in seriesChild.attrib:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing @label in <unittitle>", seriesChild)
					else:
						if seriesChild.attrib['label'] == "Series" or seriesChild.attrib['label'] == "Subseries":
							pass
						else:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid @label in <unittitle>, should be 'Series' or 'Subseries'", seriesChild)
				elif seriesChild.tag == "unitdate":
					seriesDate = seriesDate + 1
					issueCount, issueTriplet = check_normal(issueCount, issueTriplet, series.find('did'), seriesChild)
					if "circa" in seriesChild.text.lower():
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid 'circa' in <unitdate>, must use 'ca.'", seriesChild)
					if "Ca." in seriesChild.text.lower():
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid 'Ca.' in <unitdate>, must use 'ca.'", seriesChild)
					if "undated" in seriesChild.text:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid 'undated' in <unitdate>, should be 'Undated'", seriesChild)
					if seriesDate > 5:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Too many <unitdate> elements in <" + series.tag + "> element, limit is 5", seriesChild)
					if seriesChild.text[:1].isalpha():
						if seriesChild.text.startswith('ca.') or seriesChild.text.lower() == "undated":
							pass
						else:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<unitdate> does not conform to DACS, begins with letter", seriesChild)
				elif seriesChild.tag == "unitid":
					if not float(seriesChild.text):
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<unitdate> is invalid, examples include '3' or '1.2'", seriesChild)
				elif seriesChild.tag == "physdesc":
					if seriesChild.find('extent') is None:
						if seriesChild.find('physfacet') is None:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <extent> or <physfacet> element", seriesChild)
						else:
							if seriesChild.find('physfacet').text:
								pass
							else:
								issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<physfacet> element has no description", seriesChild.find('physfacet'))
					else:
						if not "unit" in seriesChild.find('extent').attrib:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No @unit in <extent> element", seriesChild.find('extent'))
						elif not seriesChild.find('extent').attrib['unit'] == "cubic ft.":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid @unit in <extent>, should be 'cubic ft.'", seriesChild.find('extent'))
						try:
							int(seriesChild.find('extent').text)
						except ValueError:
							try:
								float(seriesChild.find('extent').text)
								if seriesChild.find('extent').text.startswith('.'):
									issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid <extent>, decimals must start with '0'",seriesChild.find('extent'))
							except ValueError:
								issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid <extent>, should only be number or decimal", seriesChild.find('extent'))
				else:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + seriesChild.tag + "> in <" + series.tag + ">", seriesChild)
		for seriesDesc in series:
			if seriesDesc.tag == "did":
				pass
			elif seriesDesc.tag == "scopecontent":
				if seriesDesc.find('p') is None:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <p> element in <scopecontent>", seriesDesc)
				else:
					for para in seriesDesc:
						if not para.text:
							if para.find('emph') is None:
								issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<p> element is empty", para)
							elif not para.find('emph').text:
								issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<p> element is empty", para)
			elif seriesDesc.tag == "arrangement":
				if seriesDesc.find('p') is None:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <p> element in <arrangement>", seriesDesc)
				else:
					for para in seriesDesc:
						if not para.text:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<p> element is empty", para)
			elif seriesDesc.tag == "accessrestrict":
				if seriesDesc.find('p') is None:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing element <p> in <accessrestrict>", seriesDesc)
				else:
					for para in seriesDesc:
						if para.tag == "p":
							if not seriesDesc.find('p').text:
								issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Empty element <p> in <accessrestrict>", seriesDesc)
						else:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element " + para.tag + " in <accessrestrict>", seriesDesc)
			elif seriesDesc.tag == "altformavail":
				if seriesDesc.find('p') is None:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing element <p> in <altformavail>", seriesDesc)
				else:
					for para in seriesDesc:
						if para.tag == "p":
							if not seriesDesc.find('p').text:
								issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Empty element <p> in <altformavail>", seriesDesc)
						else:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element " + para.tag + " in <altformavail>", seriesDesc)
			elif seriesDesc.tag.startswith('c0'):
				pass
			else:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + seriesDesc.tag + "> in <" + series.tag + ">", seriesDesc)
		
		return issueCount, issueTriplet

################### Validation rules for file-level ##################################################################################################		
	def check_file(issueCount, issueTriplet, parent, file, collId, collNormal):
		#define series normal
		serNormal = parent.find('did/unitdate').attrib['normal']
		#id check
		if not "id" in file.attrib:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Component <" + file.tag + "> missing @id", file)
		else:
			if not file.attrib['id'].startswith('nam_' + collId):
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Component <" + file.tag + "> @id is incorrect", file)
			if not "_" in file.attrib['id']:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "File-level Component <" + file.tag + "> @id is incorrect, missing underscore (_)", file)
		if file.find('did') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <did> in file-level <" + file.tag + "> element", file)
		else:
			containerTypes = ('Oversized', 'Video-Tape', 'Mini-DV', 'Reel', 'DVD', 'Cassette', 'Card-File', 'Artifact-box', 'Flat-File', 'VHS', 'Umatic', 'Phonograph-Record', '3.5in-Floppy', '5.25in-Floppy', 'Film', 'Map-Tube', 'CD', 'CD-R', 'Zip-Disk', 'Floppy-Disk', 'Record', 'Microfilm', 'Drawer', 'Inventory')
			for childElement in file.find('did'):
				if not childElement.text:
					if not childElement.tag == "physdesc":
						if not childElement.tag == "dao":
							if childElement.find('emph') is None:
								if childElement.find('title') is None:
									issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<" + childElement.tag + "> element is empty", childElement)
			if file.find('did/container') is None:
				if file.find('did/dao') is None:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <container> in file-level <" + file.tag + "> element", file.find('did'))
			else:
				if not 'type' in file.find('did/container').attrib:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <container> @type in file-level <" + file.tag + "> element", file.find('did/container'))
				else:
					if file.find('did')[0].tag == "container":
						if not 'type' in file.find('did')[0].attrib:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <container> @type in file-level <" + file.tag + "> element", file.find('did')[0])
						else:
							if file.find('did')[1].tag == "container":
								if not 'type' in file.find('did')[1].attrib:
									issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <container> @type in file-level <" + file.tag + "> element", file.find('did')[1])
								else:
									if file.find('did')[0].attrib['type'] != 'Box' and file.find('did')[0].attrib['type'] != 'Oversized' and file.find('did')[0].attrib['type'] != 'Flat-File' and file.find('did')[0].attrib['type'] != 'Roll' and file.find('did')[0].attrib['type'] != 'Artifact-box' and file.find('did')[0].attrib['type'] != 'Drawer':
										issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<container> @type is invalid or out of order", file.find('did')[0])
									if file.find('did')[1].attrib['type'] != 'Folder' and file.find('did')[1].attrib['type'] != 'Item':
										if not file.find('did')[1].attrib['type'] in containerTypes:
											issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<container> @type is invalid or out of order", file.find('did')[1])
							else:
								if file.find('did')[0].attrib['type'] == "Box":
									issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <container> @type='Folder' in file-level <" + file.tag + "> element", file.find('did')[0])
								elif file.find('did')[0].attrib['type'] == "Folder":
									issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <container> @type='Box' in file-level <" + file.tag + "> element", file.find('did')[0])
								elif not file.find('did')[0].attrib['type'] in containerTypes:
									issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<container> @type is invalid", file.find('did')[0])
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <container> in file-level <" + file.tag + "> element", file.find('did'))
			if file.find('did/unittitle') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <unittitle> in file-level <" + file.tag + "> element", file.find('did'))
			else:
				if not file.find('did/unittitle').text:
					if file.find('did/unittitle/emph') is None and file.find('did/unittitle/title') is None:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "File-level <unittitle> element is empty.", file.find('did/unittitle'))
			if file.find('did/unitdate') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <unitdate> in file-level <" + file.tag + "> element", file.find('did'))
			for emptyDate in file.find('did'):
				if emptyDate.tag == "unitdate":
					if not emptyDate.text:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "File-level <unitdate> element is empty.", emptyDate)
			dateCount = 0
			for childTag in file.find('did'):
				if childTag.tag =="unitdate":
					dateCount = dateCount + 1
					issueCount, issueTriplet = check_normal(issueCount, issueTriplet, file.find('did'), childTag)
					if "," in childTag.text:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid comma (,) in <unitdate>", childTag)
					if "circa" in childTag.text.lower():
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid 'circa' in <unitdate>, must use 'ca.'", childTag)
					if "Ca." in childTag.text.lower():
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid 'Ca.' in <unitdate>, must use 'ca.'", childTag)
					if "undated" in childTag.text:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid 'undated' in <unitdate>, should be 'Undated'", childTag)
					if childTag.text == "Undated":
						if 'normal' in childTag.attrib:
							if childTag.attrib['normal'] != collNormal and childTag.attrib['normal'] != serNormal:
								issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@normal for Undated file does not match collection or series @normal date", childTag)
					if dateCount > 5:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Too many <unitdate> elements in <" + file.tag + "> element, limit is 5", childTag)
					if childTag.text[:1].isalpha():
						if childTag.text.startswith('ca.') or childTag.text.lower() == "undated" or childTag.text.lower().startswith('late') or childTag.text.lower().startswith('early'):
							pass
						else:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<unitdate> does not conform to DACS, begins with letter", childTag)
				invalidList = ("abstract", "daogrp", "head", "langmaterial", "materialspec", "origination", "physloc", "repository")
				if childTag.tag in invalidList:
					if childTag.tag == "langmaterial" and collId.startswith('ger'):
						#allow for file-level <langmaterial> in German Emigre collections
						pass
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + childTag.tag + "> in <unitdate>", childTag)
				if childTag.tag == "dao":
					if "actuate" in childTag.attrib:
						if not childTag.attrib['actuate'] == "onrequest":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @actuate must be 'onrequest'", childTag)
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @actuate missing", childTag)
					if "linktype" in childTag.attrib:
						if not childTag.attrib['linktype'] == "simple":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @linktype must be 'simple'", childTag)
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @linktype missing", childTag)
					if "show" in childTag.attrib:
						if not childTag.attrib['show'] == "new":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @show must be 'new'", childTag)
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @show missing", childTag)
					if "href" in childTag.attrib:
						if not childTag.attrib['href'].startswith('http://library.albany.edu/speccoll/findaids/eresources/digital_objects/'):
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @href is incorrect", childTag)
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @href missing", childTag)
				if childTag == "physdesc":
					if childTag.find('extent') is None:
						if childTag.find('physfacet') is None:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <extent> or <physfacet> element", childTag)
						else:
							if childTag.find('physfacet').text:
								pass
							else:
								issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<physfacet> element has no description", childTag.find('physfacet'))
					else:
						if not "unit" in childTag.find('extent').attrib:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No @unit in <extent> element", childTag.find('extent'))
						elif not childTag.find('extent').attrib['unit'] == "cubic ft.":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid @unit in <extent>, should be 'cubic ft.'", childTag.find('extent'))
						try:
							int(childTag.find('extent').text)
						except ValueError:
							try:
								float(childTag.find('extent').text)
								if childTag.find('extent').text.startswith('.'):
									issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid <extent>, decimals must start with '0'",childTag.find('extent'))
							except ValueError:
								issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid <extent>, should only be number or decimal", childTag.find('extent'))
					
		for childElement in file:
			if childElement.tag == "did":
				pass
			elif childElement.tag == "scopecontent":
				if not childElement.text:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<scopecontent> is missing", childElement)
			elif childElement.tag == "note":
				if not childElement.text:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<note> is missing", childElement)
			elif childElement.tag == "accessrestrict":
				if childElement.find('p') is None:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing element <p> in <accessrestrict>", childElement)
				else:
					if not childElement.find('p').text:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<accessrestrict> paragraph is empty", childElement)
			elif childElement.tag == "langmaterial":
				if collId.startswith('gre'):
					pass
				else:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + childElement.tag + "> in <" + file.tag + ">", childElement)
			elif childElement.tag.startswith('c0'):
				if 'level' not in childElement.attrib:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + childElement.tag + "> in <" + file.tag + ">", childElement)
				elif childElement.attrib['level'] == "item":
					pass
				else:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + childElement.tag + "> in <" + file.tag + ">, only item-level allowed below file-level", childElement)
			else:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + childElement.tag + "> in <" + file.tag + ">", childElement)
						
		return issueCount, issueTriplet
		
		
################### Validation rules for file-level ##################################################################################################		
	def check_item(issueCount, issueTriplet, parent, item, collId, collNormal):
		#define series normal
		serNormal = parent.find('did/unitdate').attrib['normal']
		#id check
		if not "id" in item.attrib:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Component <" + item.tag + "> missing @id", item)
		else:
			if not item.attrib['id'].startswith('nam_' + collId):
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Component <" + item.tag + "> @id is incorrect", item)
		if item.find('did') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <did> in item-level <" + item.tag + "> element", item)
		else:
			if item.find('did/unittitle') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <unittitle> in item-level <" + item.tag + "> element", item.find('did'))
			else:
				if not item.find('did/unittitle').text:
					if item.find('did/unittitle/emph') is None and item.find('did/unittitle/title') is None:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Item-level <unittitle> element is empty.", item.find('did/unittitle'))
			for childElement in item.find('did'):
				if not childElement.text:
					if not childElement.tag == "physdesc":
						if not childElement.tag == "dao":
							if childElement.find('emph') is None:
								if childElement.find('title') is None:
									issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<" + childElement.tag + "> element is empty", childElement)
				invalidList = ("abstract", "daogrp", "head", "langmaterial", "materialspec", "origination", "physloc", "repository")
				if childElement.tag in invalidList:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + childElement.tag + "> in <unitdate>", childElement)
				if childElement.tag == "dao":
					if "actuate" in childTag.attrib:
						if not childElement.attrib['actuate'] == "onrequest":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @actuate must be 'onrequest'", childElement)
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @actuate missing", childElement)
					if "linktype" in childElement.attrib:
						if not childElement.attrib['linktype'] == "simple":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @linktype must be 'simple'", childElement)
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @linktype missing", childElement)
					if "show" in childElement.attrib:
						if not childElement.attrib['show'] == "new":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @show must be 'new'", childElement)
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @show missing", childElement)
					if "href" in childElement.attrib:
						if not childElement.attrib['href'].startswith('http://library.albany.edu/speccoll/findaids/eresources/digital_objects/'):
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @href is incorrect", childElement)
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<dao> @href missing", childElement)
				if childElement == "physdesc":
					if childElement.find('extent') is None:
						if childElement.find('physfacet') is None:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <extent> or <physfacet> element", childElement)
						else:
							if childElement.find('physfacet').text:
								pass
							else:
								issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<physfacet> element has no description", childElement.find('physfacet'))
					else:
						if not "unit" in childElement.find('extent').attrib:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No @unit in <extent> element", childElement.find('extent'))
						elif not childElement.find('extent').attrib['unit'] == "cubic ft.":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid @unit in <extent>, should be 'cubic ft.'", childElement.find('extent'))
						try:
							int(childElement.find('extent').text)
						except ValueError:
							try:
								float(childElement.find('extent').text)
								if childElement.find('extent').text.startswith('.'):
									issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid <extent>, decimals must start with '0'",childElement.find('extent'))
							except ValueError:
								issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid <extent>, should only be number or decimal", childElement.find('extent'))
		for childTag in item:
			if childTag.tag == "did":
				pass
			elif childTag.tag == "scopecontent":
				if not childTag.text:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<scopecontent> is missing", childTag)
			elif childTag.tag == "note":
				if not childTag.text:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<note> is missing", childTag)
			elif childTag.tag == "accessrestrict":
				if childTag.find('p') is None:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing element <p> in <accessrestrict>", childTag)
				else:
					if not childTag.find('p').text:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<accessrestrict> paragraph is empty", childTag)
			elif childTag.tag == "langmaterial":
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + childTag.tag + "> in <" + item.tag + ">", childTag)
			else:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + childTag.tag + "> in <" + item.tag + ">", childTag)
						
		return issueCount, issueTriplet
		
######## Start of Validation Rules ########################################################################################################################	
	issueCount = 0
	issueTriplet = []
	
	#parse XML
	try:
		xml_doc = ET.parse(xml_filename)
		xml_root = xml_doc.getroot()
	except Exception, e:
		for xmlError in e.error_log:
			issueCount = issueCount + 1
			issueTriplet.append([str(xmlError.message), "", str(xmlError.line) + ":" + str(xmlError.column)])
	else:
		#Validate with DTD
		dtd_file = codecs.open(resource_path("ead.dtd"))
		dtd = ET.DTD(dtd_file)
		if dtd.validate(xml_root) == True:
			pass
		else:
			for dtd_error in dtd.error_log.filter_from_errors():
				issueCount = issueCount + 1
				issueTriplet.append([str(dtd_error.message), "", str(dtd_error.line) + ":" + str(dtd_error.column)])
		
		#check processing instructions
		piNoSeries = "<?xml version='1.0' encoding='utf-8'?><?xml-stylesheet type='text/xsl' href='collection-level_no_series.xsl'?> <!DOCTYPE ead SYSTEM 'ead.dtd'>"
		piSeries = "<?xml version='1.0' encoding='utf-8'?><?xml-stylesheet type='text/xsl' href='collection-level.xsl'?> <!DOCTYPE ead SYSTEM 'ead.dtd'>"
		
		with open (xml_filename, "r") as fileInput:
			fileString=fileInput.read().replace('\n', '')
			if fileString.startswith(piSeries) or fileString.startswith(piNoSeries):
				pass
			else:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Processing instructions (Doctype, stylesheet) do not match", xml_root)
		
		"""
		#Validate with Schema
		schema = ET.XMLSchema(ET.parse(resource_path("ead.xsd"))
		if schema.validate(xml_root) == True:
			pass
		else:
			for schema_error in schema.error_log:
				issueCount, issueRow = issue(issueCount, "Schema error: " + str(schema_error.message), str(schema_error.line), str(schema_error.column))
				issueTable.append(issueRow)
		"""
		
		#check collection name
		if xml_root.find('archdesc/did/unittitle') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Cannot find <unittitle> element.", xml_root.find('archdesc/did'))
		else:
			if xml_root.find('archdesc/did/unittitle').text is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet,"<unittitle> element has no collection name.", xml_root.find('archdesc/did/unittitle'))
			if xml_root.find('archdesc/did/unittitle').text.isupper() or xml_root.find('archdesc/did/unittitle').text.islower():
				issueCount, issueTriplet = error_check(issueCount, issueTriplet,"Case issue in collection-level <unittitle>", xml_root.find('archdesc/did/unittitle'))
		
		#check unique ids
		filename =  os.path.basename(xml_filename)
		collId = os.path.splitext(filename)[0]
		if xml_root.attrib['id'] is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<ead> has no @id", xml_root)
		elif len(xml_root.attrib['id']) <= 0:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<ead> @id does not contain identifier", xml_root)
		elif xml_root.find('eadheader/eadid') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<eadid> element is missing", xml_root.find('eadheader/eadid'))
		elif xml_root.find('eadheader/eadid').text is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<eadid> does not contain identifier", xml_root.find('eadheader/eadid'))
		else:	
			if not xml_root.attrib['id'].startswith("nam_"):
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<ead> @id does not begin with nam_", xml_root)
				if not xml_root.attrib['id'] == collId:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<ead> @id does not match filename", xml_root)
			else:
				if not xml_root.attrib['id'] == "nam_" + collId:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<ead> @id does not match filename", xml_root)
			if not xml_root.attrib['id'] == xml_root.find('eadheader/eadid').text:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<ead> @id does not match <eadid>", xml_root.find('eadheader/eadid'))
			if xml_root.attrib['id'].isupper():
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<ead> @id contains upper-case text", xml_root)
			if xml_root.find('eadheader/eadid').text.isupper():
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<eadid> contains upper-case text", xml_root.find('eadheader/eadid'))
		
		#check filename
		if "_" in collId:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid underscore (_) in filename", xml_root)
		if collId.startswith('ua') and "." in collId:
			if not len(str(collId.split(".")[1])) == 3:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid filename, record group number must have 3 digits in each set, not " + str(len(str(collId.split(".")[1]))), xml_root)
		
		#check collection <titlestmt>
		if not xml_root.find('eadheader/filedesc/titlestmt/titleproper').text.isupper():
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<titleproper> contains lower-case text", xml_root.find('eadheader/filedesc/titlestmt/titleproper'))
		if xml_root.find('eadheader/filedesc/titlestmt/titleproper').text.endswith(',') or xml_root.find('eadheader/filedesc/titlestmt/titleproper').text.endswith(', '):
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Unnecessary comma (,) in <titleproper>", xml_root.find('eadheader/filedesc/titlestmt/titleproper'))
		if "(" in xml_root.find('eadheader/filedesc/titlestmt/titleproper').text and ")" in xml_root.find('eadheader/filedesc/titlestmt/titleproper').text:
			if "-" in xml_root.find('eadheader/filedesc/titlestmt/titleproper').text.rsplit('(', 1)[1]:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid hyphen in <titleproper> collection identifier", xml_root.find('eadheader/filedesc/titlestmt/titleproper'))
		else:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid <titleproper>, must have collection identifier in parenthesis", xml_root.find('eadheader/filedesc/titlestmt/titleproper'))
		if xml_root.find('eadheader/filedesc/titlestmt/titleproper').text.startswith(' ') or xml_root.find('eadheader/filedesc/titlestmt/titleproper').text.endswith(' '):
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<titleproper> has leading or trailing spaces", xml_root.find('eadheader/filedesc/titlestmt/titleproper'))
		if xml_root.find('eadheader/filedesc/titlestmt/titleproper/date') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <date> element in <titleproper>", xml_root.find('eadheader/filedesc/titlestmt/titleproper'))
		issueCount, issueTriplet = check_normal(issueCount, issueTriplet, xml_root, xml_root.find('eadheader/filedesc/titlestmt/titleproper/date'))
		if xml_root.find('eadheader/filedesc/titlestmt/author') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <author> element in <titlestmt>", xml_root.find('eadheader/filedesc/titlestmt'))
		if not xml_root.find('eadheader/filedesc/titlestmt/author').text:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <author> listed", xml_root.find('eadheader/filedesc/titlestmt/author'))
		#check collection <publicationstmt>
		if xml_root.find('eadheader/filedesc/publicationstmt') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <publicationstmt> element in <filedesc>", xml_root.find('eadheader/filedesc'))
		if xml_root.find('eadheader/filedesc/publicationstmt/publisher') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <publisher> element in <publicationstmt>", xml_root.find('eadheader/filedesc/publicationstmt'))
		if not xml_root.find('eadheader/filedesc/publicationstmt/publisher').text == "M. E. Grenander Department of Special Collections and Archives":
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<publisher> statement is incorrect", xml_root.find('eadheader/filedesc/publicationstmt/publisher'))
		if xml_root.find('eadheader/filedesc/publicationstmt/address') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <address> element in <publicationstmt>", xml_root.find('eadheader/filedesc/publicationstmt'))
		if xml_root.find('eadheader/filedesc/publicationstmt/address/addressline') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <addressline> element in <address>", xml_root.find('eadheader/filedesc/publicationstmt/address'))
		if not xml_root.find('eadheader/filedesc/publicationstmt/address/addressline').text == "1400 Washington Avenue / Albany, New York 12222":
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<address> statement is incorrect", xml_root.find('eadheader/filedesc/publicationstmt/address/addressline'))
		if xml_root.find('eadheader/filedesc/publicationstmt/date') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <date> element in <publicationstmt>", xml_root.find('eadheader/filedesc/publicationstmt'))
		if not xml_root.find('eadheader/filedesc/publicationstmt/date').text:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "no <date> listed", xml_root.find('eadheader/filedesc/publicationstmt/date'))
		if re.search('&copy;', xml_root.find('eadheader/filedesc/publicationstmt/date').text):
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Special character in <date>", xml_root.find('eadheader/filedesc/publicationstmt/date'))
		issueCount, issueTriplet = check_normal(issueCount, issueTriplet, xml_root, xml_root.find('eadheader/filedesc/publicationstmt/date'))
		
		#check <profiledesc>
		if xml_root.find('eadheader/profiledesc') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <profiledesc> element in <eadheader>", xml_root.find('eadheader'))
		if xml_root.find('eadheader/profiledesc/creation') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <creation> element in <profiledesc>", xml_root.find('eadheader/profiledesc'))
		if not xml_root.find('eadheader/profiledesc/creation').text:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No EAD creator in <creation> element", xml_root.find('eadheader/profiledesc/creation'))
		if xml_root.find('eadheader/profiledesc/creation/date') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <date> in <creation> element", xml_root.find('eadheader/profiledesc/creation'))
		if not xml_root.find('eadheader/profiledesc/creation/date').text:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <date> listed", xml_root.find('eadheader/profiledesc/creation/date'))
		issueCount, issueTriplet = check_normal(issueCount, issueTriplet, xml_root, xml_root.find('eadheader/profiledesc/creation/date'))
		if xml_root.find('eadheader/profiledesc/langusage') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <langusage> element in <profiledesc>", xml_root.find('eadheader/profiledesc'))
		if xml_root.find('eadheader/profiledesc/langusage/language') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <language> element in <langusage>", xml_root.find('eadheader/profiledesc/langusage'))
		if not xml_root.find('eadheader/profiledesc/langusage/language').text:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No EAD language in <language> element", xml_root.find('eadheader/profiledesc/langusage/language'))
		if  not 'langcode' in  xml_root.find('eadheader/profiledesc/langusage/language').attrib:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No language code in <language> element", xml_root.find('eadheader/profiledesc/langusage/language'))
		if  not xml_root.find('eadheader/profiledesc/langusage/language').attrib['langcode'] == "eng":
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<language> @langcode is incorrect", xml_root.find('eadheader/profiledesc/langusage/language'))
			
		
		#check <revisiondesc>
		if xml_root.find('eadheader/revisiondesc') is None:
			pass
		else:
			if xml_root.find('eadheader/revisiondesc/change') is None:
				for oddChild in xml_root.find('eadheader/revisiondesc'):
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + oddChild.tag + "> in <revisiondesc>", oddChild)
			else:
				if xml_root.find('eadheader/revisiondesc/change').text.strip():
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<change> element requires <date> and <item> elements", xml_root.find('eadheader/revisiondesc/change'))
				else:
					for change in xml_root.find('eadheader/revisiondesc'):
						if xml_root.find('eadheader/revisiondesc/change/date') is None and xml_root.find('eadheader/revisiondesc/change/item') is None:
							pass
						else:
							if change.find('date') is None:
								issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Revisions require complete <date> and <item> elements", change)
							else:
								if change.find('date').text or change.find('item').text:
									issueCount, issueTriplet = check_normal(issueCount, issueTriplet, xml_root, change.find('date'))
									if xml_root.find('eadheader/revisiondesc/change/item') is None:
										issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Revisions require complete <date> and <item> elements", change)
									else:
										if not xml_root.find('eadheader/revisiondesc/change/date').text:
											issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<date> element is incomplete", xml_root.find('eadheader/revisiondesc/change/date'))
										if not xml_root.find('eadheader/revisiondesc/change/item').text:
											issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<item> element is incomplete", xml_root.find('eadheader/revisiondesc/change/item'))
					
		archdesc = xml_root.find('archdesc')
		#check <archdesc>
		if not xml_root.find('archdesc').attrib['level'] == 'collection':
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<archdesc> @level is incorrect", xml_root.find('archdesc'))
		
		#head
		if archdesc.find('did/head') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> is missing from <archdesc>/<did>", archdesc.find('did'))
		else:
			if not archdesc.find('did/head').text == "Descriptive Summary":
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> is incorrect, should read 'Descriptive Summary'", archdesc.find('did/head'))
		
		#unitid
		if archdesc.find('did/unitid') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Collection-level <unitid> is missing", archdesc.find('did'))
		else:
			if not archdesc.find('did/unitid').text == xml_root.attrib['id']:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<unitid> is incorrect", archdesc.find('did/unitid'))
		
		#unitdate
		if archdesc.find('did/unittitle/unitdate') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <unitdate>", archdesc.find('did/unittitle'))
		else:
			issueCount, issueTriplet = check_normal(issueCount, issueTriplet, xml_root, xml_root.find('archdesc/did/unittitle/unitdate'))
			if "type" in archdesc.find('did/unittitle/unitdate').attrib:
				if archdesc.find('did/unittitle/unitdate').attrib['type'] == "inclusive":
					pass
				else:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <unitdate> listed as 'inclusive'", archdesc.find('did/unittitle/unitdate'))
			else:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <unitdate> @type'", archdesc.find('did/unittitle/unitdate'))
				
		#abstract
		if archdesc.find('did/abstract') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <abstract> listed", archdesc.find('did'))
		else:
			if not len(archdesc.find('did/abstract').text) > 20:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Collection-level <abstract> is not listed or is too small", archdesc.find('did/abstract'))
		
		#language material
		if archdesc.find('did/langmaterial') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <langmaterial> listed", archdesc.find('did'))
		else:
			if archdesc.find('did/langmaterial/language') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <language> listed", archdesc.find('did/langmaterial'))
			else:
				mixCount = 0
				for langTag in archdesc.find('did/langmaterial'):
					if langTag.attrib['langcode'] is None:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing @langcode in <language>", langTag)
					if not langTag.tail is None:
						if len(langTag.tail.strip()) > 0:
							mixCount = mixCount + 1
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Collection-level <langmaterial> contains mixed-content", langTag)
				if mixCount == 0:
					if archdesc.find('did/langmaterial').text:
						if len(archdesc.find('did/langmaterial').text.strip()) > 0:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Collection-level <langmaterial> contains mixed-content", archdesc.find('did/langmaterial'))
		
		#origination (creator)
		if archdesc.find('did/origination') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <origination> element", archdesc.find('did'))
		else:
			if archdesc.find('did/origination/corpname') is None and archdesc.find('did/origination/persname') is None and archdesc.find('did/origination/famname') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No creator element listed", archdesc.find('did/origination'))
			else:
				if archdesc.find('did/origination').xpath('count(*)') > 1:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Multiple creators listed", archdesc.find('did/origination'))
				if not archdesc.find('did/origination/corpname') is None:
					if not archdesc.find('did/origination/corpname').text:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Creator <corpname> is empty", archdesc.find('did/origination/corpname'))
					if archdesc.find('did/origination/corpname').attrib['encodinganalog'] is None:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing @encodinganalog for creator <corpname>", archdesc.find('did/origination/corpname'))
					elif not archdesc.find('did/origination/corpname').attrib['encodinganalog'] == "110":
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@encodinganalog for creator <corpname> is incorrect, should be '110'", archdesc.find('did/origination/corpname'))
					if archdesc.find('did/origination/corpname').attrib['source'] is None:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing @source for creator <corpname>", archdesc.find('did/origination/corpname'))
					elif not archdesc.find('did/origination/corpname').attrib['source'] == "lcsh" and not archdesc.find('did/origination/corpname').attrib['source'] == "local":
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@source for creator <corpname> is incorrect, should be 'lcsh' or 'local'", archdesc.find('did/origination/corpname'))
				if not archdesc.find('did/origination/persname') is None:
					if not archdesc.find('did/origination/persname').text:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Creator <persname> is empty", archdesc.find('did/origination/persname'))
					if archdesc.find('did/origination/persname').attrib['encodinganalog'] is None:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing @encodinganalog for creator <persname>", archdesc.find('did/origination/persname'))
					elif not archdesc.find('did/origination/persname').attrib['encodinganalog'] == "100":
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@encodinganalog for creator <persname> is incorrect, should be '100'", archdesc.find('did/origination/persname'))
					if archdesc.find('did/origination/persname').attrib['source'] is None:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing @source for creator <persname>", archdesc.find('did/origination/persname'))
					elif not archdesc.find('did/origination/persname').attrib['source'] == "lcsh" and not archdesc.find('did/origination/persname').attrib['source'] == "local":
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@source for creator <persname> is incorrect, should be 'lcsh' or 'local'", archdesc.find('did/origination/persname'))
				if not archdesc.find('did/origination/famname') is None:
					if not archdesc.find('did/origination/famname').text:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Creator <famname> is empty", archdesc.find('did/origination/famname'))
					if archdesc.find('did/origination/famname').attrib['encodinganalog'] is None:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing @encodinganalog for creator <famname>", archdesc.find('did/origination/famname'))
					elif not archdesc.find('did/origination/famname').attrib['encodinganalog'] == "100":
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@encodinganalog for creator <famname> is incorrect, should be '100'", archdesc.find('did/origination/famname'))
					if archdesc.find('did/origination/famname').attrib['source'] is None:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing @source for creator <famname>", archdesc.find('did/origination/famname'))
					elif not archdesc.find('did/origination/famname').attrib['source'] == "lcsh" and not archdesc.find('did/origination/famname').attrib['source'] == "local":
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@source for creator <famname> is incorrect, should be 'lcsh' or 'local'", archdesc.find('did/origination/famname'))
		
		#physdesc
		if archdesc.find('did/physdesc') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <physdesc> element", archdesc.find('did'))
		else:
			if archdesc.find('did/physdesc/extent') is None:
				if archdesc.find('did/physdesc/physfacet') is None:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <extent> or <physfacet> element", archdesc.find('did/physdesc'))
				else:
					if archdesc.find('did/physdesc/physfacet').text:
						pass
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Collection-level <physfacet> element has no description", archdesc.find('did/physdesc/physfacet'))
			else:
				if not "unit" in archdesc.find('did/physdesc/extent').attrib:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No @unit in collection-level <extent> element", archdesc.find('did/physdesc/extent'))
				elif not archdesc.find('did/physdesc/extent').attrib['unit'] == "cubic ft.":
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid @unit in collection-level <extent>, should be 'cubic ft.'", archdesc.find('did/physdesc/extent'))
				try:
					int(archdesc.find('did/physdesc/extent').text)
				except ValueError:
					try:
						float(archdesc.find('did/physdesc/extent').text)
						if archdesc.find('did/physdesc/extent').text.startswith('.'):
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid collection-level <extent>, decimals must start with '0'", archdesc.find('did/physdesc/extent'))
					except ValueError:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid collection-level <extent>, should only be number or decimal", archdesc.find('did/physdesc/extent'))
				
		#physloc
		if archdesc.find('did/physloc') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <physloc> element", archdesc.find('did'))
		else:
			if not archdesc.find('did/physloc').text:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Collection-level <physloc> is empty", archdesc.find('did/physloc'))
		#repository
		if archdesc.find('did/repository') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <repository> element", archdesc.find('did'))
		else:
			if archdesc.find('did/repository/corpname') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <corpname> element in collection-level <repository> element", archdesc.find('did/repository'))
			else:
				if not archdesc.find('did/repository/corpname').text == "M. E. Grenander Department of Special Collections and Archives, University at Albany, SUNY":
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Collection-level <repository> is incorrect", archdesc.find('did/repository/corpname'))
				if archdesc.find('did/repository/corpname').attrib['encodinganalog'] is None:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<repository> @encodinganalog is missing", archdesc.find('did/repository/corpname'))
				elif not archdesc.find('did/repository/corpname').attrib['encodinganalog'] == "610":
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<repository> @encodinganalog is incorrect", archdesc.find('did/repository/corpname'))
				if archdesc.find('did/repository/corpname').attrib['source'] is None:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<repository> @source is missing", archdesc.find('did/repository/corpname'))
				elif not archdesc.find('did/repository/corpname').attrib['source'] == "local":
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<repository> @source is incorrect", archdesc.find('did/repository/corpname'))
		
		#Collection-level archdesc elements

		#accessrestrict
		if archdesc.find('accessrestrict') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <accessrestrict> element", archdesc)
		else:
			if archdesc.find('accessrestrict/head') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <head> in collection-level <accessrestrict>", archdesc.find('accessrestrict'))
			else:
				if archdesc.find('accessrestrict/head').text.startswith(' ') or archdesc.find('accessrestrict/head').text.endswith(' '):
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> has leading or trailing spaces", archdesc.find('accessrestrict/head'))
				else:
					if not archdesc.find('accessrestrict/head').text == "Access":
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> is incorrect, should be 'Access'", archdesc.find('accessrestrict/head'))
			for accessRestr in archdesc.find('accessrestrict'):
				if accessRestr.tag.lower() == "head":
					pass
				else:
					if accessRestr.tag == "p" or accessRestr.tag == "list":
						pass
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + accessRestr.tag + ">in <accessrestrict>", accessRestr)#accessrestrict
		
		#userestrict
		if archdesc.find('userestrict') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <userestrict> element", archdesc)
		else:
			if archdesc.find('userestrict/head') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <head> in collection-level <userestrict>", archdesc.find('userestrict'))
			else:
				if archdesc.find('userestrict/head').text.startswith(' ') or archdesc.find('userestrict/head').text.endswith(' '):
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> has leading or trailing spaces", archdesc.find('userestrict/head'))
				else:
					if not archdesc.find('userestrict/head').text == "Copyright":
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> is incorrect, should be 'Copyright'", archdesc.find('userestrict/head'))
			for useRestr in archdesc.find('userestrict'):
				if useRestr.tag.lower() == "head":
					pass
				else:
					if useRestr.tag == "p" or useRestr.tag == "list":
						pass
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + useRestr.tag + "> in <userestrict>", useRestr)
						
		#acqinfo
		if archdesc.find('acqinfo') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <acqinfo> element", archdesc)
		else:
			if archdesc.find('acqinfo/head') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <head> in collection-level <acqinfo>", archdesc.find('acqinfo'))
			else:
				if archdesc.find('acqinfo/head').text.startswith(' ') or archdesc.find('acqinfo/head').text.endswith(' '):
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> has leading or trailing spaces", archdesc.find('acqinfo/head'))
				else:
					if not archdesc.find('acqinfo/head').text == "Acquisition Information":
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> is incorrect, should be 'Acquisition Information'", archdesc.find('acqinfo/head'))
			for acqInfo in archdesc.find('acqinfo'):
				if acqInfo.tag.lower() == "head":
					pass
				else:
					if acqInfo.tag == "p":
						pass
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + acqInfo.tag + "> in <acqinfo>", acqInfo)
						
		#prefercite
		if archdesc.find('prefercite') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <prefercite> element", archdesc)
		else:
			if archdesc.find('prefercite/head') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <head> in collection-level <prefercite>", archdesc.find('prefercite'))
			else:
				if archdesc.find('prefercite/head').text.startswith(' ') or archdesc.find('prefercite/head').text.endswith(' '):
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> has leading or trailing spaces", archdesc.find('prefercite/head'))
				else:
					if not archdesc.find('prefercite/head').text == "Preferred Citation":
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> is incorrect, should be 'Preferred Citation'", archdesc.find('prefercite/head'))
			for prefCite in archdesc.find('prefercite'):
				if prefCite.tag.lower() == "head":
					pass
				else:
					if prefCite.tag == "p":
						pass
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + prefCite.tag + "> in <prefercite>", prefCite)
						
		#scopecontent
		if archdesc.find('scopecontent') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <scopecontent> element", archdesc)
		else:
			if archdesc.find('scopecontent/head') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <head> in collection-level <scopecontent>", archdesc.find('scopecontent'))
			else:
				if archdesc.find('scopecontent/head').text.startswith(' ') or archdesc.find('scopecontent/head').text.endswith(' '):
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> has leading or trailing spaces", archdesc.find('scopecontent/head'))
				else:
					if not archdesc.find('scopecontent/head').text == "Scope and Content Information":
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> is incorrect, should be 'Scope and Content Information'", archdesc.find('scopecontent/head'))
			for scope in archdesc.find('scopecontent'):
				if scope.tag.lower() == "head":
					pass
				else:
					if scope.tag == "p":
						pass
					else:
						if scope.tag == "dao" and collId == "apap337":
							#allow for <dao> in <scopecontent> for Henry Schwarzschild Memorial Collection
							pass
						else:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + scope.tag + "> in <scopecontent>", scope)
						
		#bioghist
		if archdesc.find('bioghist') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <bioghist> element", archdesc)
		else:
			if archdesc.find('bioghist/head') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <head> in collection-level <bioghist>", archdesc.find('bioghist'))
			else:
				if archdesc.find('bioghist/head').text.startswith(' ') or archdesc.find('bioghist/head').text.endswith(' '):
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> has leading or trailing spaces", archdesc.find('bioghist/head'))
				else:
					if archdesc.find('bioghist/head').text == "Biographical Sketch" or archdesc.find('bioghist/head').text == "Biographical History" or archdesc.find('bioghist/head').text == "Administrative History" or archdesc.find('bioghist/head').text == "Historical Note" or archdesc.find('bioghist/head').text == "Organizational Sketch":
						pass
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> is incorrect, use a correct heading for <bioghist>", archdesc.find('bioghist/head'))
			for biogNote in archdesc.find('bioghist'):
				if biogNote.tag.lower() == "head":
					pass
				else:
					if biogNote.tag == "p":
						pass
					elif biogNote.tag == "chronlist":
						pass
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + biogNote.tag + "> in <bioghist>", biogNote)
		
		#arrangement
		if archdesc.find('arrangement') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <arrangement> element", archdesc)
		else:
			if archdesc.find('arrangement/head') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <head> in collection-level <arrangement>", archdesc.find('arrangement'))
			else:
				if archdesc.find('arrangement/head').text.startswith(' ') or archdesc.find('arrangement/head').text.endswith(' '):
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> has leading or trailing spaces", archdesc.find('arrangement/head'))
				else:
					if not archdesc.find('arrangement/head').text == "Arrangement of the Collection":
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> is incorrect, should be 'Arrangement of the Collection'", archdesc.find('arrangement/head'))
			for arrEle in archdesc.find('arrangement'):
				if arrEle.tag.lower() == "head":
					pass
				else:
					if arrEle.tag == "p":
						pass
					elif arrEle.tag == "list":
						if "simple" in arrEle.attrib['type']:
							pass
						else:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid <list> @type in <arrangement>", arrEle)
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + arrEle.tag + "> in <arrangement>", arrEle)
						
		#controlaccess
		if archdesc.find('controlaccess') is None:
			issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No collection-level <controlaccess> element", archdesc)
		else:
			if archdesc.find('controlaccess/head') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <head> in collection-level <controlaccess>", archdesc.find('controlaccess'))
			else:
				if archdesc.find('controlaccess/head').text.startswith(' ') or archdesc.find('controlaccess/head').text.endswith(' '):
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> has leading or trailing spaces", archdesc.find('controlaccess/head'))
				else:
					if not archdesc.find('controlaccess/head').text == "Subject and Genre Headings":
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> is incorrect, should be 'Subject and Genre Headings'", archdesc.find('controlaccess/head'))
			for heading in archdesc.find('controlaccess'):
				if heading.tag == "head":
					pass
				else:
					if not heading.text:
						if heading.find('emph') is None:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Controlled access heading is empty", heading)
						else:
							if not heading.find('emph').text:
								issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Controlled access heading is empty", heading)
					if "source" not in heading.attrib:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@source missing for controlled access heading", heading)
					else:
						if heading.attrib['source'] == "lcsh" or heading.attrib['source'] == "aat" or heading.attrib['source'] == "local" or heading.attrib['source'] == "tgm" or heading.attrib['source'] == "tgn":
							pass
						else:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@source is incorrect, should be 'lcsh,' 'aat, 'tgm,' 'tgn,' or 'local'", heading)
					if "encodinganalog" not in heading.attrib:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@encodinganalog missing for controlled access heading", heading)
					if heading.tag == "persname":
						if not heading.attrib['encodinganalog'] == "600":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@encodinganalog incorrect", heading)
					elif heading.tag == "corpname":
						if heading.attrib['encodinganalog'] == "610" or heading.attrib['encodinganalog'] == "611":
							pass
						else:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@encodinganalog incorrect", heading)
					elif heading.tag == "famname":
						if not heading.attrib['encodinganalog'] == "600":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@encodinganalog incorrect", heading)
					elif heading.tag == "function":
						if not heading.attrib['encodinganalog'] == "657":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@encodinganalog incorrect", heading)
					elif heading.tag == "subject":
						if not heading.attrib['encodinganalog'] == "650":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@encodinganalog incorrect", heading)
					elif heading.tag == "name":
						if not heading.attrib['encodinganalog'] == "720":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@encodinganalog incorrect", heading)
					elif heading.tag == "occupation":
						if not heading.attrib['encodinganalog'] == "656":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@encodinganalog incorrect", heading)
					elif heading.tag == "title":
						if not heading.attrib['encodinganalog'] == "630":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@encodinganalog incorrect", heading)
					elif heading.tag == "geogname":
						if not heading.attrib['encodinganalog'] == "651":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@encodinganalog incorrect", heading)
					elif heading.tag == "genreform":
						if not heading.attrib['encodinganalog'] == "655":
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "@encodinganalog incorrect", heading)
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element in <controlaccess>", heading)
						
		#bibliography
		if archdesc.find('bibliography') is None:
			pass
		else:
			if archdesc.find('bibliography/head') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Missing <head> in collection-level <bibliography>", archdesc.find('bibliography'))
			else:
				if archdesc.find('bibliography/head').text.startswith(' ') or archdesc.find('bibliography/head').text.endswith(' '):
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> has leading or trailing spaces", archdesc.find('bibliography/head'))
				else:
					if archdesc.find('bibliography/head').text == "Bibliography" or archdesc.find('bibliography/head').text == "Selected Bibliography":
						pass
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> is incorrect, should be 'Bibliography' or 'Selected Bibliography'", archdesc.find('bibliography/head'))
			for bibRef in archdesc.find('bibliography'):
				if bibRef.tag == "head":
					pass
				elif bibRef.tag == "bibliography":
					for subBib in bibRef:
						if subBib.tag == "head":
							pass
						else:
							if not subBib.text:
								if subBib.find('emph') is None:
									if subBib.find('title') is None:
										issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Element <" + subBib.tag + "> is empty", subBib)
									elif not subBib.find('title').text:
										if subBib.find('title/emph') is None:
											issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Element <" + subBib.tag + "> is empty", subBib)
										elif not subBib.find('title/emph').text:
											issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Element <" + subBib.tag + "> is empty", subBib)
								elif not subBib.find('emph').text:
									issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Element <" + subBib.tag + "> is empty", subBib)
							if subBib.tag == "p":
								pass
							elif subBib.tag == "bibref" or subBib.tag == "archref":
								pass
							else:
								issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + subBib.tag + "> in <bibliography>", subBib)
				else:
					if not bibRef.text:
						if bibRef.find('emph') is None:
							if bibRef.find('title') is None:
								issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Element <" + bibRef.tag + "> is empty", bibRef)
							elif not bibRef.find('title').text:
								if bibRef.find('title/emph') is None:
									issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Element <" + bibRef.tag + "> is empty", bibRef)
								elif not bibRef.find('title/emph').text:
									issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Element <" + bibRef.tag + "> is empty", bibRef)
						elif not bibRef.find('emph').text:
							issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Element <" + bibRef.tag + "> is empty", bibRef)
					if bibRef.tag == "p":
						pass
					elif bibRef.tag == "bibref" or bibRef.tag == "archref":
						pass
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + bibRef.tag + "> in <bibliography>", bibRef)
						
		#relatedmaterial
		if archdesc.find('relatedmaterial') is None:
			pass
		else:
			for related in archdesc.find('relatedmaterial'):
				if related.tag.lower() == "head":
					pass
				else:
					if not related.text:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Element <" + related.tag + "> is empty", related)
					if related.tag == "p":
						pass
					elif related.tag == "bibref" or related.tag == "archref":
						pass
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + related.tag + "> in <relatedmaterial>", related)
						
		#separatedmaterial
		if archdesc.find('separatedmaterial') is None:
			pass
		else:
			for separated in archdesc.find('separatedmaterial'):
				if separated.tag.lower() == "head":
					pass
				else:
					if not separated.text:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Element <" + separated.tag + "> is empty", separated)
					if separated.tag == "p":
						pass
					elif separated.tag == "bibref" or separated.tag == "archref":
						pass
					else:
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + separated.tag + "> in <relatedmaterial>", separated)
		
		#invalid elements
		acceptElements = ("did", "accessrestrict", "userestrict", "acqinfo", "prefercite", "scopecontent", "bioghist", "arrangement", "controlaccess", "bibliography", "relatedmaterial", "separatedmaterial", "altformavail", "processinfo", "dsc")
		for archdescChild in archdesc:
			if not archdescChild.tag in acceptElements:
				if not archdescChild.tag is ET.Comment:
					issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + archdescChild.tag + "> in <archdesc>", archdescChild)

		
		#dsc (Container List)
		if archdesc.find('dsc') is None:
			pass
		else:
			if archdesc.find('dsc/head') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> missing in <dsc>", archdesc.find('dsc'))
			elif archdesc.find('dsc/head').text.startswith(' ') or archdesc.find('dsc/head').text.endswith(' '):
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> contains leading or trailing spaces", archdesc.find('dsc/head'))
			elif not archdesc.find('dsc/head').text == "Container List":
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "<head> is incorrect, should be 'Container List'", archdesc.find('dsc/head'))
			if archdesc.find('dsc/c') is None:
				pass
			else:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <c> in container list, use <c01>, <c02>, etc", archdesc.find('dsc/c'))
			if archdesc.find('dsc/c01') is None:
				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "No <c01> in <dsc>, if only collection-level then remove <dsc>", archdesc.find('dsc'))
			else:
				
				if archdesc.find('did/unittitle/unitdate') is None:
					collNormal = ""
				else:
					if 'normal' in archdesc.find('did/unittitle/unitdate').attrib:
						collNormal = archdesc.find('did/unittitle/unitdate').attrib['normal']
					else:
						collNormal = ""
				
				#c01
				for cmpnt in archdesc.find('dsc'):	
					if cmpnt.tag == "head" or cmpnt.tag is ET.Comment:
						pass
					elif not cmpnt.tag == "c01":
						issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Invalid element <" + cmpnt.tag + ">", cmpnt)
					else:
						#########################################################################Test This
						if cmpnt.find('c02') is None and not cmpnt.attrib['level'] == "series":
							if cmpnt.attrib['level'] == "item":
								#item level
								issueCount, issueTriplet = check_item(issueCount, issueTriplet, archdesc.find('dsc'), cmpnt, collId, collNormal)
							else:
								#file level
								issueCount, issueTriplet = check_file(issueCount, issueTriplet, archdesc.find('dsc'), cmpnt, collId, collNormal)
						else:
							#series level
							issueCount, issueTriplet = check_series(issueCount, issueTriplet, archdesc.find('dsc'), cmpnt, collId)
							
							#c02
							for cmpnt2 in cmpnt:
								if cmpnt2.tag is ET.Comment:
									pass
								elif not cmpnt2.tag == "c02":
									pass
								else:
									if cmpnt2.find('c03') is None and 'level' not in cmpnt2.attrib:
										#file level
										issueCount, issueTriplet = check_file(issueCount, issueTriplet, cmpnt, cmpnt2, collId, collNormal)
									else:
										if cmpnt2.attrib['level'] == "subseries" or cmpnt2.attrib['level'] == "series":
											#subseries level
											issueCount, issueTriplet = check_series(issueCount, issueTriplet, cmpnt, cmpnt2, collId)
										elif cmpnt2.attrib['level'] == "item":
											#item level
											issueCount, issueTriplet = check_item(issueCount, issueTriplet, cmpnt, cmpnt2, collId, collNormal)									
										else:
											#file level
											issueCount, issueTriplet = check_file(issueCount, issueTriplet, cmpnt, cmpnt2, collId, collNormal)
											
										
										#c03
										for cmpnt3 in cmpnt2:
											if cmpnt3.tag is ET.Comment:
												pass
											elif not cmpnt3.tag == "c03":
												pass
											else:
												if cmpnt3.find('c04') is None and 'level' not in cmpnt3.attrib:
													#file level
													issueCount, issueTriplet = check_file(issueCount, issueTriplet, cmpnt2, cmpnt3, collId, collNormal)
												else:
													if cmpnt3.attrib['level'] == "subseries" or cmpnt3.attrib['level'] == "series":
														#subsubseries level
														issueCount, issueTriplet = check_series(issueCount, issueTriplet, cmpnt2, cmpnt3, collId)
													elif cmpnt3.attrib['level'] == "item":
														#item level
														issueCount, issueTriplet = check_item(issueCount, issueTriplet, cmpnt2, cmpnt3, collId, collNormal)
													else:
														#file level
														issueCount, issueTriplet = check_file(issueCount, issueTriplet, cmpnt2, cmpnt3, collId, collNormal)
														
													
													#c04
													for cmpnt4 in cmpnt3:
														if cmpnt4.tag is ET.Comment:
															pass
														elif not cmpnt4.tag == "c04":
															pass
														else:
															if cmpnt4.find('c05') is None and 'level' not in cmpnt4.attrib:
																#file level
																issueCount, issueTriplet = check_file(issueCount, issueTriplet, cmpnt3, cmpnt4, collId, collNormal)
															else:
																if cmpnt4.attrib['level'] == "subseries" or cmpnt4.attrib['level'] == "series":
																	#subsubseries level
																	issueCount, issueTriplet = check_series(issueCount, issueTriplet, cmpnt3, cmpnt4, collId)
																elif cmpnt4.attrib['level'] == "item":
																	#item level
																	issueCount, issueTriplet = check_item(issueCount, issueTriplet, cmpnt3, cmpnt4, collId, collNormal)
																else:
																	#file level
																	issueCount, issueTriplet = check_file(issueCount, issueTriplet, cmpnt3, cmpnt4, collId, collNormal)
																
																
																#c05
																for cmpnt5 in cmpnt4:
																	if cmpnt5.tag is ET.Comment:
																		pass
																	elif not cmpnt5.tag == "c05":
																		pass
																	else:
																		if cmpnt5.find('c06') is None and 'level' not in cmpnt5.attrib:
																			#file level
																			issueCount, issueTriplet = check_file(issueCount, issueTriplet, cmpnt4, cmpnt5, collId, collNormal)
																		else:
																			if cmpnt5.attrib['level'] == "subseries" or cmpnt5.attrib['level'] == "series":
																				#subsubseries level
																				issueCount, issueTriplet = check_series(issueCount, issueTriplet, cmpnt4, cmpnt5, collId)
																			elif cmpnt5.attrib['level'] == "item":
																				#item level
																				issueCount, issueTriplet = check_item(issueCount, issueTriplet, cmpnt4, cmpnt5, collId, collNormal)
																			else:
																				#file level
																				issueCount, issueTriplet = check_file(issueCount, issueTriplet, cmpnt4, cmpnt5, collId, collNormal)
																				
																			
																			#c06
																			for cmpnt6 in cmpnt5:
																				issueCount, issueTriplet = error_check(issueCount, issueTriplet, "Must have permission to use <c06> or below", cmpnt6)
																				
	finally:
		return issueCount, issueTriplet