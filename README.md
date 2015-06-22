EAD Validator
========

EAD Validator is a strict, rule-based validation tool for Encoded Archival Description. It is written in Python 2.7 and converted to an .exe without any dependencies. Many of the rules were written specifically for the M.E. Grenander Department of Special Collections & Archives at the University at Albany, SUNY. The strictness allows valid EAD files to be used as a consistent data store for archival metadata that will enable the automation of metadata creation, administration, and publication.


Usage
----------

EAD Validator consists of the following files

* validation_report.exe
* validation_report.html
* validation_report.py
* validator.py
* resource_path.py

validation_report.exe is a packaged version of the source and the easiest way to use EAD Validator. It has no dependencies. It reads all .xml files in its own directory and produces a HTML report file that lists the issues and their locations. The validation rules are specific to the M.E. Grenander Department of Special Collections & Archives.

validation_report.html is an example of the HTML report produced by validation_report.exe, it uses Bootstrap 2.3.2.

validator.py is the core set of rules for validation. It contains a function called validate() that accepts a string object and returns two variables: issueCount and issueTriplet. issueCount is an integer count of the number of issues found within the EAD string. issueTriplet is a list object which contains a list of three expressions for each issue: a string error message, a string XPath pointing to the issue, and a string of line:column. validator.py is dependant on the lxml library which is not part of the basic Python install, and also requires the ead.dtd and ead.xsd in the same directory unless those checks are commented out. By default, validation by XML Schema (ead.xsd) is commented out because of namespace incomparability with ead.dtd. validator.py is to be used as a command line tool for validation during automated processes.

validation_report.py is a wrapper script for GUI usage of validator.py. It is dependant on validator.py, resource_path.py, and the lxml add-on library for Python 2.7. validation_report.py reads all .xml files in its directory and uses the rules of validation.py to create an HTML report which lists each error using Bootstrap 2.3.2.

resource_path.py is a function that enables data files (ead.dtd and ead.xsd) to be embeded within validation_report.exe using pyinstaller. Credit belongs to this Stack Overflow answer: http://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile This file will only be of interest to users freezing their modifications to .exe using pyinstaller.

For any questions please contact GWiedeman [at] albany [dot] edu