#!/usr/bin/env python2

__notice__	 = """
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
__license__  = "MPL"	# Mozilla Public License 2.0
__author__   = "notuxic"
__version__  = "0.1"
__release__  = "0"
__revision__ = "1"
__credits__  = """"
socks/SocksiPy coded by Dan Haim <negativeiq@users.sourceforge.net>
	socks/PySocks forked by Anorov <anorov.vorona@gmail.com>
imaplib2 coded by Piers Lauder <piers@janeelix.com>
"""
__depends__  = """
socks
imaplib2
"""


import json
import socket
import socks
import smtplib
import poplib
import imaplib2
import email.utils
import email.parser
from email.mime.text import MIMEText
try:
	import ssl
	SSL_AVAIL = True
except ImportError:
	SSL_AVAIL = False




class SMTP_(smtplib.SMTP):
	"""
	This class manages a connection to an SMTP or ESMTP server.
	It is a subclass of smtplib.SMTP with additional commands.
		- starttls(self)
	"""
	SMTP_PORT = 25
	TLS_USED = False
	
	def __init__(self, host = "", port = SMTP_PORT, local_hostname = None, timeout = socket._GLOBAL_DEFAULT_TIMEOUT):
		smtplib.SMTP.__init__(self, host, port, local_hostname, timeout)

## Supported by python's smtplib
#	
#	def starttls(self):
#		self.ehlo_or_helo_if_needed()
#		if not SSL_AVAIL:
#			raise Exception("SSL not supported")
#		if not self.has_extn("starttls"):
#			raise smtplib.smtplib.SMTPException("STARTTLS not supported by server")
#		if self.TLS_USED:
#			raise smtplib.smtplib.SMTPException("TLS session already established")
#			
#		resp,reply = self.docmd("STARTTLS")
#		if resp == 220:
#			self.sock = ssl.wrap_socket(self.sock, keyfile = None, certfile = None)
#			self.file = smtplib.SSLFakeFile(self.sock)
#			self.TLS_USED = True
#			# Delete all information and request it again
#			self.helo_resp = None
#			self.ehlo_resp = None
#			self.esmtp_features = {}
#			self.does_esmtp = 0
#			self.ehlo_or_helo_if_needed()
#		else:
#			raise smtplib.smtplib.SMTPException(reply)
#		return (resp,reply)
		
	


class SMTPSOCKS(SMTP_):
	"""
	This class manages a connection to an SMTP or ESMTP server through a HTTP or SOCKS proxy
	It is a subclass of SMTP with additional commands
		- starttls(()
		proxytype:
			_HTTP
			SOCKS4
			_SOCKS5
		A user and password for the proxy are optional
	"""
	SMTP_PORT = 25
	SOCKS_PORT = 1080
	TLS_USED = False
	
	def __init__(self, host = "", port = SMTP_PORT, local_hostname = None, sockshost = "", socksport = SOCKS_PORT, proxytype = socks.PROXY_TYPE_SOCKS4, socksuser = None, sockspwd = None, timeout = socket._GLOBAL_DEFAULT_TIMEOUT):
		self.sockshost = sockshost
		self.socksport = socksport
		self.proxytype = proxytype
		self.socksuser = socksuser
		self.sockspwd = sockspwd
		smtplib.SMTP.__init__(self, host, port, local_hostname, timeout)
	
	def _get_socket(self, host, port, timeout):
		if self.debuglevel > 0:
			print>>stderr, "connect:", (host, port)
		self.sock = socks.socksocket()
		if self.socksuser and self.sockspwd:
			self.sock.setproxy(self.proxytype, self.sockshost, self.socksport, True, self.socksuser, self.sockspwd)
		else:
			self.sock.setproxy(self.proxytype, self.sockshost, self.socksport)
		self.sock.connect((host,port))
		return self.sock




class SMTPS(smtplib.SMTP_SSL):
	"""
	This class manages a SSL/TLS encrypted connection to an SMTP or ESMTP server through a HTTP or SOCKS proxy
	It is a subclass of smtplib.SMTP_SSL
	"""
	if not SSL_AVAIL:
		raise Exception("SSL not supported")
	
	SMTP_SSL_PORT = 465
	
	def __init__(self, host = "", port = SMTP_SSL_PORT, local_hostname = None, keyfile = None, certfile = None, timeout = socket._GLOBAL_DEFAULT_TIMEOUT):
		smtplib.SMTP_SSL.__init__(self, host, port, local_hostname, keyfile, certfile, timeout)




class SMTPSSOCKS(SMTPS):
	"""
	This class manages a SSL/TLS encrypted connection to an SMTP or ESMTP server through a HTTP or SOCKS proxy
	It is a subclass of SMTP_SSL
		proxytype:
			_HTTP
			SOCKS4
			_SOCKS5
		A user and password for the proxy are optional
	"""
	if not SSL_AVAIL:
		raise Exception("SSL not supported")
	
	SMTP_SSL_PORT = 465
	SOCKS_PORT = 1080
	
	def __init__(self, host = "", port = SMTP_SSL_PORT, local_hostname = None, sockshost = "", socksport = SOCKS_PORT, proxytype = socks.PROXY_TYPE_SOCKS4, socksuser = None, sockspwd = None, keyfile=None, certfile=None, timeout = socket._GLOBAL_DEFAULT_TIMEOUT):
		self.sockshost = sockshost
		self.socksport = socksport
		self.proxytype = proxytype
		self.socksuser = socksuser
		self.sockspwd = sockspwd
		self.keyfile = keyfile
		self.certfile = certfile
		SMTPS.__init__(self, host, port, local_hostname, keyfile, certfile, timeout)
	
	def _get_socket(self, host, port, timeout):
		if self.debuglevel > 0:
			print>>stderr, "connect:", (host, port)
		self.sock = socks.socksocket()
		if self.socksuser and self.sockspwd:
			self.sock.setproxy(self.proxytype, self.sockshost, self.socksport, True, self.socksuser, self.sockspwd)
		else:
			self.sock.setproxy(self.proxytype, self.sockshost, self.socksport)
		self.sock.connect((host,port))
		self.sock = ssl.wrap_socket(self.sock, self.keyfile, self.certfile)
		self.file = smtplib.SSLFakeFile(self.sock)
		return self.sock




class POPException(Exception): pass

class POP3(poplib.POP3):
	"""
	This class manages a connection to a POP server
	It is a subclass of popblib.POP3 with additional commands
		- starttls(self)
	"""
	POP3_PORT = 110
	TLS_USED = False
	
	def __init__(self, host = "", port = POP3_PORT, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
		self.host = host
		self.port = port
		self.sock = socket.create_connection((host, port), timeout)
		self.file = self.sock.makefile("rb")
		self._debugging = 0
		self.welcome = self._getresp()
		self.capability()
		
	def capability(self):
		"""
		Generates an array contaning all supported server commands
		"""
		self.capabilities = []
		resp,reply,num = self._longcmd("CAPA")
		if "OK" in resp:
			for i in range(len(reply)):
				self.capabilities.append(reply[i])
		else:
			raise POPException("CAPA not supported by server")
		

	def starttls(self, keyfile = None, certfile = None):
		"""
		Puts the connection in TLS mode
		"""
		if not SSL_AVAIL:
			raise Exception("SSL not supported")
		if "STLS" not in self.capabilities:
			raise POPException("STLS not supported by server")
		if self.TLS_USED:
			raise POPException("TLS session already established")
			
		reply = self._shortcmd("STLS")
		if "+OK" in reply:
			self.sock = ssl.wrap_socket(self.sock, keyfile, certfile)
			self.file = smtplib.SSLFakeFile(self.sock)
			self.TLS_USED = True
			# Delete old information, and request it again
			self.capability()
		else:
			raise POPException(reply)
		return reply




class POP3SOCKS(POP3):
	"""
	This class manages a connection to a POP server through a HTTP or SOCKS proxy
	It is a subclass of POP3 with additional commands
		- starttls(self)email date format
		proxytype:
			_HTTP
			SOCKS4
			_SOCKS5
		A user and password for the proxy are optional
	"""
	POP3_PORT = 110
	SOCKS_PORT = 1080
	TLS_USED = False
	
	def __init__(self, host = "", port = POP3_PORT, sockshost = "", socksport = SOCKS_PORT, proxytype = socks.PROXY_TYPE_SOCKS4, socksuser = None, sockspwd = None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
		self.host = host
		self.port = port
		self.sockshost = sockshost
		self.socksport = socksport
		self.proxytype = proxytype
		self.socksuser = socksuser
		self.sockspwd = sockspwd
		self.sock = socks.socksocket()
		if self.socksuser and self.sockspwd:
			self.sock.setproxy(self.proxytype, self.sockshost, self.socksport, True, self.socksuser, self.sockspwd)
		else:
			self.sock.setproxy(self.proxytype, self.sockshost, self.socksport)
		self.sock.connect((host,port))
		self.file = self.sock.makefile("rb")
		self._debugging = 0
		self.welcome = self._getresp()
		self.capability()




class POPS3(poplib.POP3_SSL):
	"""
	This class manages a SSL/TLS encrypted connection to a POP server
	It is a subclass of poplib.POP3_SSL with additional commands
	"""
	if not SSL_AVAIL:
		raise POPException("SSL not supported")
	
	POP3_SSL_PORT = 995
	SOCKS_PORT = 1080
	
	def __init__(self, host = "", port = POP3_SSL_PORT, keyfile = None, certfile = None, timeout = socket._GLOBAL_DEFAULT_TIMEOUT):
		self.host = host
		self.port = port
		self.keyfile = keyfile
		self.certfile = certfile
		self.buffer = ""
		self.sock = socket.create_connection((host, port), timeout)
		self.sslobj = ssl.wrap_socket(self.sock, self.keyfile, self.certfile)
		self.file = self.sslobj.makefile("rb")
		self._debugging = 0
		self.welcome = self._getresp()
		self.capability()
	
	def capability(self):
		"""
		Generates an array contaning all supported server commands
		"""
		self.capabilities = []
		resp,reply,num = self._longcmd("CAPA")
		if "OK" in resp:
			for i in range(len(reply)):
				self.capabilities.append(reply[i])
		else:
			raise POPException("CAPA not supported by server")




class POPS3SOCKS(POPS3):
	"""
	This class manages a SSL/TLS encrypted connection to a POP server through a HTTP or SOCKS proxy
	It is a subclass of POP3_SSL
		proxytype:
			_HTTP
			SOCKS4
			_SOCKS5
		A user and password for the proxy are optional
	"""
	if not SSL_AVAIL:
		raise POPException("SSL not supported")
	
	POP3_SSL_PORT = 995
	SOCKS_PORT = 1080
	
	def __init__(self, host = "", port = POP3_SSL_PORT, sockshost = "", socksport = SOCKS_PORT, proxytype = socks.PROXY_TYPE_SOCKS4, socksuser = None, sockspwd = None, keyfile = None, certfile = None):
		self.host = host
		self.port = port
		self.sockshost = sockshost
		self.socksport = socksport
		self.proxytype = proxytype
		self.socksuser = socksuser
		self.sockspwd = sockspwd
		self.keyfile = keyfile
		self.certfile = certfile
		self.buffer = ""
		self.sock = socks.socksocket()
		if self.socksuser and self.sockspwd:
			self.sock.setproxy(self.proxytype, self.sockshost, self.socksport, True, self.socksuser, self.sockspwd)
		else:
			self.sock.setproxy(self.proxytype, self.sockshost, self.socksport)
		self.sock.connect((host,port))
		self.file = self.sock.makefile("rb")
		self.sslobj = ssl.wrap_socket(self.sock, self.keyfile, self.certfile)
		self._debugging = 0
		self.welcome = self._getresp()




class IMAPException(imaplib2.IMAP4.error): pass

class IMAP4(imaplib2.IMAP4):
	"""
	This class manages a connection to an IMAP server
	It is a subclass of imaplib2.IMAP4 with additional commands
		- 
	"""
	IMAP4_PORT = 143
	TLS_USED = False
	
	def __init__(self,host = "", port = IMAP4_PORT):
		imaplib2.IMAP4.__init__(self, host, port)




class IMAP4SOCKS(IMAP4):
	"""
	This class manages a connection to an IMAP server through a HTTP or SOCKS proxy7
	It is a subclass of IMAP4 with additional commands
		- 
		proxytype:
			_HTTP
			SOCKS4
			_SOCKS5
		A user and password for the proxy are optional
	"""
	IMAP4_PORT = 143
	SOCKS_PORT = 1080
	TLS_USED = False
	
	def __init__(self,host = "", port = IMAP4_PORT, sockshost = "", socksport = SOCKS_PORT, proxytype = socks.PROXY_TYPE_SOCKS4, socksuser = None, sockspwd = None):
		self.sockshost = sockshost
		self.socksport = socksport
		self.proxytype = proxytype
		self.socksuser = socksuser
		self.sockspwd = sockspwd
		IMAP4.__init__(self, host, port)
	
	def open(self, host = "", port = IMAP4_PORT,):
		self.host = host
		self.port = port
		self.sock = socks.socksocket()
		if self.socksuser and self.sockspwd:
			self.sock.setproxy(self.proxytype, self.sockshost, self.socksport, True, self.socksuser, self.sockspwd)
		else:
			self.sock.setproxy(self.proxytype, self.sockshost, self.socksport)
		self.sock.connect((host,port))
		self.file = self.sock.makefile("rb")
		self.read_fd = self.sock.fileno()




class IMAPS4(imaplib2.IMAP4_SSL):
	"""
	This class manages a SSL/TLS encrypted connection to an IMAP server
	It is a subclass of imaplib2.IMAP4_SSL with additional commands
	"""
	if not SSL_AVAIL:
		IMAPException("SSL not supported")
	
	IMAP4_SSL_PORT = 993
	SOCKS_PORT = 1080
	
	def __init__(self, host = "", port = IMAP4_SSL_PORT, keyfile = None, certfile = None):
		self.host = host
		self.port = port
		self.keyfile = keyfile
		self.certfile = certfile
		imaplib2.IMAP4_SSL.__init__(self, self.host, self.port)
		self.read_fd = self.sock.fileno()




class IMAPS4SOCKS(IMAPS4):
	"""
	This class manages a SSL/TLS encrypted connection to an IMAP server through a HTTP or SOCKS proxy
	It is a subclass of IMAP4_SSL with additional commands
		proxytype:
			_HTTP
			SOCKS4
			_SOCKS5
		A user and password for the proxy are optional
	"""
	if not SSL_AVAIL:
		IMAPException("SSL not supported")
	
	IMAP4_SSL_PORT = 993
	SOCKS_PORT = 1080
	
	def __init__(self, host = "", port = IMAP4_SSL_PORT, sockshost = "", socksport = SOCKS_PORT, proxytype = socks.PROXY_TYPE_SOCKS4, socksuser = None, sockspwd = None, keyfile = None, certfile = None):
		self.keyfile = keyfile
		self.certfile = certfile
		self.sockshost = sockshost
		self.socksport = socksport
		self.proxytype = proxytype
		self.socksuser = socksuser
		self.sockspwd = sockspwd
		IMAPS4.__init__(self, host, port)


	def open(self, host = "", port = IMAP4_SSL_PORT):
		self.host = host
		self.port = port
		self.sock = socks.socksocket()
		if self.socksuser and self.sockspwd:
			self.sock.setproxy(self.proxytype, self.sockshost, self.socksport, True, self.socksuser, self.sockspwd)
		else:
			self.sock.setproxy(self.proxytype, self.sockshost, self.socksport)
		self.sock.connect((host,port))
		self.ssl_wrap_socket()
		self.file = self.sock.makefile("rb")



class SMTP():
	"""
	This class is a wrapper around the various SMTP classes, wich provides high-level functionality
	All commands use UIDs instead of sequential IDs
	"""
	
	def __init__(self,userpass,host,port=None,encrypt=None,proxy=None):
		self.host = host
		if not port:
			self.port = self.getDefaultPort(encrypt)
		else:
			self.port = port
		
		if proxy:
			sockshost,socksport,socksuser,sockspwd,proxytype = proxy
		if encrypt:
			encryption,keyfile,certfile = encrypt
			
			if encryption.upper() == "SSL":
				if proxy:
					self.smtp = SMTPSSOCKS(self.host,self.port,sockshost,socksport,proxytype,socksuser,sockspwd,keyfile,certfile)
				else:
					self.smtp = SMTPS(self.host,self.port,keyfile,certfile)
					
			elif encryption.upper() == "STARTTLS":
				if proxy:
					self.smtp = SMTPSOCKS(self.host,self.port,sockshost,socksport,proxytype,socksuser,sockspwd)
				else:
					self.smtp = SMTP_(self.host,self.port)
				self.smtp.starttls(keyfile,certfile)
				
			else:
				raise smtplib.SMTPException("<" + encryption + "> is not a valid encryption type!")
		
		else:
			
			if proxy:
				self.smtp = SMTPSOCKS(self.host,self.port,sockshost,socksport,proxytype,socksuser,sockspwd)
				
			else:
				self.smtp = SMTP_(self.host,self.port)
			
		user = userpass[0]
		passwd = userpass[1]
		self.smtp.login(user,passwd)
		
	def getDefaultPort(self,encrypt):
		if not encrypt or encrypt[0] == "STARTTLS":
			port = 25
		else:
			port = 465
		return port




class POP():
	"""
	This class is a wrapper around the various POP classes, wich provides high-level functionality
	All commands use UIDs instead of sequential IDs
	"""
	
	def __init__(self,userpass,host,port=None,encrypt=None,proxy=None):
		self.host = host
		if not port:
			self.port = self.getDefaultPort(encrypt)
		else:
			self.port = port
		
		if proxy:
			sockshost,socksport,socksuser,sockspwd,proxytype = proxy
		if encrypt:
			encryption,keyfile,certfile = encrypt
			
			if encryption.upper() == "SSL":
				if proxy:
					self.pop = POPS3SOCKS(self.host,self.port,sockshost,socksport,proxytype,socksuser,sockspwd,keyfile,certfile)
				else:
					self.pop = POPS3(self.host,self.port,keyfile,certfile)
					
			elif encryption.upper() == "STARTTLS":
				if proxy:
					self.pop = POP3SOCKS(self.host,self.port,sockshost,socksport,proxytype,socksuser,sockspwd)
				else:
					self.pop = POP3(self.host,self.port)
				self.pop.starttls(keyfile,certfile)
				
			else:
				raise POPException("<" + encryption + "> is not a valid encryption type!")
		
		else:
			
			if proxy:
				self.pop = POP3SOCKS(self.host,self.port,sockshost,socksport,proxytype,socksuser,sockspwd)
				
			else:
				self.pop = POP3(self.host,self.port)
		
		self.pop.user(userpass[0])
		self.pop.pass_(userpass[1])
		self.genSeqIDTable()
		
	def getDefaultPort(self,encrypt):
		if not encrypt or encrypt[0] == "STARTTLS":
			port = 110
		else:
			port = 995
		return port
	
	
	def genSeqIDTable(self):
		self.seqid = {}
		ids = self.pop.list()[1]
		for id in ids:
			id = id.split(' ')[0]
			self.seqid[self.getUID(id)] = id
	
	
	def getUID(self,seqid):
		uid = self.pop.uidl(seqid)
		uid = uid.split(' ')[2]
		return uid
	
	
	def getSeqID(self,uid):
		id = self.seqid[uid]
		return id
	
	
	def parseHeader(self,rawheader):
		rawheader = '\r\n'.join(rawheader[1])
		rawheader = email.parser.HeaderParser().parsestr(rawheader)
		header = {}
		for tag in rawheader.items():
			if tag[0] in header:
				try:
					header[tag[0]].append(tag[1])
				except AttributeError:
					tmp = header[tag[0]]
					header[tag[0]] = []
					header[tag[0]].append(tmp)
					header[tag[0]].append(tag[1])
			else:
				header[tag[0]] = tag[1]
		return header
	
	
	def getMail(self,uid):
		id = self.getSeqID(uid)
		rawmail = self.pop.retr(id)
		mail = email.parser.Parser().parsestr('\r\n'.join(rawmail))
		return mail
	
	
	def peekHeader(self,uid):
		id = self.getSeqID(uid)
		rawheader = self.pop.top(id,0)
		header = self.parseHeader(rawheader)
		return header
	
	
	def peekText(self,uid,lines=70):
		id = self.getSeqID(uid)
		rawtext = self.pop.top(id,lines)
		rawtext = email.parser.Parser().parsestr('\r\n'.join(rawtext[1]))
		if rawtext.is_multipart():
			for part in rawtext.walk():
				if part.get_content_type() == 'text/plain':
					text = part.get_payload()
					break
		return text
	
	
	def peekMail(self,uid,lines=300):
		id = self.getSeqID(uid)
		rawmail = self.pop.top(id,lines)
		mail = email.parser.Parser().parsestr('\r\n'.join(rawmail[1]))
		return mail




class IMAP():
	"""
	This class is a wrapper around the various IMAP classes, wich provides high-level functionality
	All commands use UIDs instead of sequential IDs
	"""
	
	def __init__(self,userpass,host,port=None,encrypt=None,proxy=None):
		self.host = host
		if not port:
			self.port = self.getDefaultPort(encrypt)
		else:
			self.port = port
		
		if proxy:
			sockshost,socksport,socksuser,sockspwd,proxytype = proxy
		if encrypt:
			encryption,keyfile,certfile = encrypt
			
			if encryption.upper() == "SSL":
				if proxy:
					self.imap = IMAPS4SOCKS(self.host,self.port,sockshost,socksport,proxytype,socksuser,sockspwd,keyfile,certfile)
				else:
					self.imap = IMAPS4(self.host,self.port,keyfile,certfile)
					
			elif encryption.upper() == "STARTTLS":
				if proxy:
					self.imap = IMAP4SOCKS(self.host,self.port,sockshost,socksport,proxytype,socksuser,sockspwd)
				else:
					self.imap = IMAP4(self.host,self.port)
				self.imap.starttls(keyfile,certfile)
				
			else:
				raise IMAPException("<" + encryption + "> is not a valid encryption type!")
		
		else:
			
			if proxy:
				self.imap = IMAP4SOCKS(self.host,self.port,sockshost,socksport,proxytype,socksuser,sockspwd)
				
			else:
				self.imap = IMAP4(self.host,self.port)
		
		user = userpass[0]
		passwd = userpass[1]
		self.imap.login(user,passwd)
	
	def getDefaultPort(self,encrypt):
		if not encrypt or encrypt[0] == "STARTTLS":
			port = 143
		else:
			port = 993
		return port
	
	
	def parseHeader(self,rawheader):
		if not rawheader[1][0]:
			raise IMAPException('EMail does not exist!')
		rawheader = rawheader[1][0][1]
		rawheader = email.parser.HeaderParser().parsestr(rawheader)
		header = {}
		for tag in rawheader.items():
			if tag[0] in header:
				try:
					header[tag[0]].append(tag[1])
				except AttributeError:
					tmp = header[tag[0]]
					header[tag[0]] = []
					header[tag[0]].append(tmp)
					header[tag[0]].append(tag[1])
			else:
				header[tag[0]] = tag[1]
		return header
	
	def parseBodyStruct(self,rawstruct):
		rawstruct = rawstruct[1][0]
		if not rawstruct:
			raise IMAPException('Email does not exist!')
		rawstruct = rawstruct.replace(' ',',').replace(')(','),(').replace('NIL','None').replace('BODYSTRUCTURE','"BODYSTRUCTURE"')
		rawstruct = eval(rawstruct)[1][1]
		structs = []
		for part in rawstruct:
			if not isinstance(part,tuple):
				structs.append(part)
				break
			struct = {}
			struct['Content-Type'] = part[0].lower() + '/' + part[1].lower()
			struct['Type'] = part[0]
			struct['Subtype'] = part[1]
			struct['Parameters'] = {}
			key = None
			for i in range(len(part[2])):
				if i%2 == 0:
					key = part[2][i]
				else:
					struct['Parameters'][key] = part[2][i]
			struct['ID'] = part[3]
			struct['Description'] = part[4]
			struct['Encoding'] = part[5]
			struct['Size'] = part[6]
			struct['Epilogue'] = None
			if len(part) > 7:
				struct['Epilogue'] = []
				for i in range(7,len(part)):
					struct['Epilogue'].append(part[i])
			structs.append(struct)
		return structs
	
	
	def getHeader(self,uid):
		rawheader = self.imap.uid("fetch",uid,"(BODY[HEADER])")
		header = self.parseHeader(rawheader[1][0][1])
		return header
		
	
	def getHeaderFields(self,uid,fields):
		for i in range(len(fields)):
			fields[i] = fields[i].title()
		rawfields = " ".join(fields)
		rawheader = self.imap.uid("fetch",uid,"(BODY[HEADER.FIELDS (" + rawfields + ")])")
		header = self.parseHeader(rawheader)
		return header
	
	def getBodyStruct(self,uid):
		rawstruct = self.imap.imap.uid('fetch',uid,'(BODYSTRUCTURE)')
		struct = self.parseBodyStruct(rawstruct)
		return struct
	
	def getText(self,uid):
		rawheader = self.imap.uid('fetch',uid,'(BODY[HEADER.FIELDS (MIME-VERSION CONTENT-TYPE)])')
		rawtext = self.imap.uid('fetch',uid,'(BODY[TEXT])')
		rawtext = rawheader[1][0][1] + rawtext[1][0][1]
		text = email.parser.Parser().parsestr(rawtext)
		return text
	
	def getAttachment(self,uid,nznum):
		rawattachm = self.imap.uid('fetch',uid,'(BODY[' + str(nznum) + '])')
		attachm = email.parser.Parser().parsestr(rawattachm[1][0][1])
		return attachm
	
	def getMail(self,uid):
		rawmail = self.imap.uid('fetch',uid,'(BODY[])')
		mail = email.parser.Parser().parsestr(rawmail[1][0][1])
		return mail
	
	
	def peekHeader(self,uid):
		rawheader = self.imap.uid("fetch",uid,"(BODY.PEEK[HEADER])")
		header = self.parseHeader(rawheader)
		return header
	
	
	def peekHeaderFields(self,uid,fields):
		for i in range(len(fields)):
			fields[i] = fields[i].title()
		rawfields = " ".join(fields)
		rawheader = self.imap.uid("fetch",uid,"(BODY.PEEK[HEADER.FIELDS (" + rawfields + ")])")
		header = self.parseHeader(rawheader)
		return header
	
	
	def peekText(self,uid):
		rawheader = self.imap.uid('fetch',uid,'(BODY.PEEK[HEADER.FIELDS (MIME-VERSION CONTENT-TYPE)])')
		rawtext = self.imap.uid('fetch',uid,'(BODY.PEEK[TEXT])')
		rawtext = rawheader[1][0][1] + rawtext[1][0][1]
		rawtext = email.parser.Parser().parsestr(rawtext)
		if rawtext.is_multipart():
			for part in rawtext.walk():
				if part.get_content_type() == 'text/plain':
					text = part.get_payload()
					break
		return text
	
	
	def peekMail(self,uid):
		rawmail = self.imap.uid('fetch',uid,'(BODY.PEEK[])')
		mail = email.parser.Parser().parsestr(rawmail[1][0][1])
		return mail
