"""Mime type handling for web requests"""
import os.path
import json

from . import webio
from . import errors as E

# ########################################################################## #

def stripCppComments(sPath):
	lLines = []
	
	fIn = open(sPath, encoding='UTF-8')
	for sLine in fIn:
		sLine = sLine.strip()
		# Walk the line, if we are not in quotes and see '//' ignore everything
		# from there to the end
		iQuote = 0
		iComment = -1
		n = len(sLine)
		for i in range(n):
			if sLine[i] == '"': 
				iQuote += 1
				continue
			if sLine[i] == '/' and (i < n-1) and (sLine[i+1] == '/') \
				and (iQuote % 2 == 0):
				iComment = i
				break;
					
		if iComment > -1:
			sLine = sLine[:iComment]
			sLine = sLine.strip()
			
		lLines.append(sLine)

	sData = '\n'.join(lLines)
	
	fIn.close()

	return sData

def loadCommentedJson(sPath):
	"""Read a commented Json file

	Pre-parse a *.json file removing all C++ style commets, '//', and then
	build a dictionary using the standard json.loads function.

	Returns (dict): A dictionary object if the file exists and could be read
		otherwise a ServerError is raised if basic parsing failed.
	"""
	sData = stripCppComments(sPath)
	return json.loads(sData)

# ######################################################################### #
def load(dConf):
	"""Load the local mime-types dictionary
	"""
	
	if 'MIME_FILE' not in dConf:
		raise E.ServerError("MIME_FILE is not defined in your das2server.conf file.")

	if not os.path.isfile(dConf['MIME_FILE']):
		raise E.ServerError("Move %s.example to %s to finish server configuration"%(
			dConf['MIME_FILE'],dConf['MIME_FILE']
		))

	dMime = loadCommentedJson(dConf['MIME_FILE'])

	return dMime

# ######################################################################### #
def get(dMimes, sType, sVersion, sSerial):
	"""Given info on an output type, define the mime string

	Args:
		sType - The basic type, one of 'das', 'csv', 'png', 'qstream', etc.
		sVersion - A type version some of the early das versions are just
		   octet-streams
		sSerial - Sometimes the same information can be represented multiple
		   ways (binary, text, xml)

	Returns a (mime type, extension, title) tuple
	"""

	sMime = None
	sExt = None
	sTitle = None

	if sType not in dMimes:
		return ("application/binary", "bin", "Unknown Data Type")

	dType = dMimes[sType]

	# The defaults
	sMime = dType['mime']
	sExt  = dType['extension']
	sTitle = dType['title']

	# Override for version
	dVer = {}
	if 'version' in dType:
		if sVersion in dType['version']:
			dVer = dType['version'][sVersion]

			sMime = dVer['mime']
			sExt  = dVer['extension']
			sTitle = dVer['title']
	
	# Override for variant
	if 'variant' in dVer:
		if sSerial in dVer['variant']:
			dVariant = dVer['variant'][sSerial]

			sMime = dVariant['mime']
			sExt  = dVariant['extension']
			sTitle = dVariant['title']

	# Override text types so that data display in a browser if desired
	if webio.isBrowser():
		sFront = sMime.split()[0]
		if sFront.startswith('text/'):
			for sSubMime in ('/csv', '/xml'):
				if not sMime.endswith(sSubMime):
					sMime = 'text/plain; charset=utf-8'

	return (sMime, sExt, sTitle)


# ########################################################################## #
# OLD MIME STUFF -- To be deleted #

MIME = 0
INLINE = 1
EXTENSION = 2

g_dDasClientMime = { 
	'text': 
		{'d2s': ('text/vnd.das2.das2stream; charset=utf-8', 'inline', 'd2t'),
		 'qds': ('text/vnd.das2.qstream; charset=utf-8', 'inline', 'qdt'),
		 'vap': ('application/x-autoplot-vap+xml', 'attachment', 'vap'),
		 'csv': ('text/csv','attachment','csv')
		 },
				 
	'bin':
		{'d2s': ('application/vnd.das2.das2stream', 'attachment', 'd2s'),
		 'qds': ('application/vnd.das2.qstream', 'attachment', 'qds'),
       'vap': ('application/vnd.autoplot.vap+xml', 'attachment', 'vap'),
		},
		 
	'image':
		{'d2s': ('image/png', 'inline', 'png'),
		 'qds': ('image/png', 'inline', 'png')}
}

g_dBrowserMime = {
	'text': 
		{'d2s': ('text/plain; charset=utf-8', 'inline', 'd2t'),
		 'qds': ('text/plain; charset=utf-8', 'inline', 'qdst'),
       'vap': ('application/x-autoplot-vap+xml', 'attachment', 'vap'), 
		 'csv': ('text/csv','attachment','csv')
		},
				 
	'bin':g_dDasClientMime['bin'],

	'image':g_dDasClientMime['image']
}

# Top level mime switch toggled off of 'isBrowser' function

g_dMime = {True:g_dBrowserMime, False:g_dDasClientMime}


##############################################################################
def getOutputMime(sOutCat, sOutFmt='d2s'):
	"""Getting a mime-type for a return object based on it output category and
	optionally the type of data generated by the reader
	
	sOutCat - The category of output, one of 'text','bin','image'
	sOutFmt - When the output is text or bin, also specify if you are sending
	          a das2stream or a Qstream, should be one of 'd2s' or 'qds'
				 
	Returns the following 3-strings in a tuple:
	  
	     ( mime-type, content disposition, filename extension)
	
	For the text types charset=utf-8 is added
	"""
	
	return g_dMime[webio.isBrowser()][sOutCat][sOutFmt]
	
##############################################################################
def getMimeByExt(sPath):
	"""Returns a mime-type string for one of our files types, or None if
	the file-type isn't recognized"""
	
	i = sPath.rfind('.')
	if i == -1:
		return None
		
	sExt = sPath[i+1:].lower()
	
	if sExt == 'qdt': 
		return g_dMime[webio.isBrowser()]['text']['qds']
		
	if sExt == 'd2t':
		return g_dMime[webio.isBrowser()]['text']['d2s']
	
	if sExt == 'qds': 
		return g_dMime[webio.isBrowser()]['bin']['qds']
		
	if sExt == 'd2s':
		return g_dMime[webio.isBrowser()]['bin']['d2s']
		
	if sExt == 'vap':
		return g_dMime[webio.isBrowser()]['text']['vap']
		
	if sExt == 'csv':
		return g_dMime[webio.isBrowser()]['text']['csv']

	return None