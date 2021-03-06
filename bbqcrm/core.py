#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
bbqCRM alpha
Brendan Molloy <brendan@bbqsrc.net>
Copyright (c) 2011

This software is licensed under the Creative Commons Zero license.
<http://creativecommons.org/publicdomain/zero/1.0/>
"""

help = """
Required modules:
 * SqlAlchemy
 * Mako
 * Bottle

All three can be easy_install'd.
"""

import sys
if sys.version_info < (2,7,0):
	print("You need Python 2.7 or higher (including Python 3).")
	sys.exit()

from sqlalchemy import Table, Column, Integer, Numeric, String, MetaData
from sqlalchemy import ForeignKey, DateTime, PickleType, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from bottle import abort, get, post, redirect, request, route, static_file
from bottle import HTTPResponse, urljoin
from beaker.middleware import SessionMiddleware
from mako.template import Template
from mako.lookup import TemplateLookup
from hashlib import sha1

import logging
import importlib
import bottle
import json
import os, os.path

#-----------------#
# Private globals #
#-----------------#
_ui = None
_config = None
_path = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
try:
	f = open(os.path.join(_path, 'config.json'))
	_config = json.load(f)
	f.close()
except:
	raise

_salt1 = _config.get("salt1")
_salt2 = _config.get("salt2")
_appdir    = _config.get("appdir", _path)
_private   = _config.get("privdir",
				os.path.join(_path, "private"))
_templates = [_config.get("templates", _appdir + '/templates')]
_lookup    = TemplateLookup(directories=_templates)
_root      = _config.get("root", "")
_enabled_modules = _config.get("modules", [])
_static    = _config.get("static", _appdir+"/static")
_ = _root# + '/'

_engine = None
try:
	_db_engine   = _config.get("db_type")
	_db_database = _config.get("db_database", "bbqcrm")
	_db_username = _config.get("db_username", None)
	_db_password = _config.get("db_password", None)
	_db_host     = _config.get("db_host", "localhost")
	_db_port     = _config.get("db_port", None)
	if _db_engine == "sqlite":
		_engine = create_engine("sqlite:///%s" % 
			(os.path.join(_private, _db_database+".db")))
	else:
		pref = (_db_username+":"+_db_password+"@") if _db_username and _db_password else "" 
		suff = _db_host + (_db_port if _db_port else "") + "/" + _db_database
		_engine = create_engine("%s://%s%s" % (_db_engine, pref, suff))
except:
	raise

_Session = sessionmaker(bind=_engine, autoflush=True, autocommit=True)
_SqlBase = declarative_base()
_SqlBase.metadata.bind = _engine

class _Member(_SqlBase):
	__tablename__ = "members"

	id         = Column(Integer, primary_key=True)
	student_id = Column(Integer)
	firstname  = Column(String)
	lastname   = Column(String)
	username   = Column(String)
	password   = Column(String)
	address1   = Column(String)
	address2   = Column(String)
	suburb     = Column(String)
	state      = Column(String)
	postcode   = Column(String)
	homephone  = Column(String)
	mobile     = Column(String)
	email      = Column(String)
	type       = Column(String)
	joined     = Column(DateTime)
	paid       = Column(DateTime)
	begin      = Column(DateTime)
	end        = Column(DateTime)

	def __init__(self, username=None, password=None, student_id=None, 
			firstname=None, lastname=None, address1=None, address2=None, 
			suburb=None, state=None, postcode=None, homephone=None, mobile=None,
			email=None, begin=None, end=None, paid=None):	
		self.username = username
		self.password = password
		
		self.student_id = student_id
		self.firstname = firstname
		self.lastname = lastname
		self.address1 = address1
		self.address2 = address2
		self.suburb = suburb
		self.state = state
		self.postcode = postcode
		self.homephone = homephone
		self.mobile = mobile
		self.email = email
		
		self.joined = datetime.datetime.now()
		self.begin = begin
		self.end = end
		self.paid = paid

_SqlBase.metadata.create_all()
_session = _Session()

#init logging

#-----------------#
# Public Methods  #
#-----------------#
def syslog_msg(msg):
	syslog = logging.FileHandler(os.path.join(_private, 'bbqcrm.log'))
	syslog.setLevel(logging.INFO)
	syslog.setFormatter(logging.Formatter(_fmt_template, _fmt_date))
	logging.getLogger('').addHandler(syslog)
	logging.getLogger('').info(msg)
	logging.getLogger('').removeHandler(syslog)

def get_menus():
	return _get_menus()

def get_session():
	return request.environ.get('beaker.session')

def get_ip():
	return request.get("REMOTE_ADDR")	

def hash(msg):
	return str(sha1((_salt1+msg+_salt2).encode('utf-8')).hexdigest())	

@route(_+"/login")
def login(msg=""):
	content = """
		<p>%s</p>
		<form id="login" action="%s" method="POST">
			<table>
				<tr>
					<td>Username:</td>
					<td><input name="username" type="text" /></td>
				</tr>
				<tr>
					<td>Password:</td>
					<td><input name="password" type="password" /></td>
				</tr>
				<tr>
					<td colspan='2'>
						<input name="submit" type="submit" value="Submit" />
					</td>
				</tr>
			</table>
		</form>
	""" % (msg, (_+'/login'))
	t = _lookup.get_template('login.txt')
	out = t.render(pref=_root, site=_config.get("sitename", "Untitled"),
				   page="Login", content=content)
	return out

def template_index(root, page, content):
	if not auth_check(): redirect(_+"/login")
	if _ui:
		if _ui == "console":
			pass #TODO for CLI
	
	session = request.environ.get('beaker.session')
	username = None
	if session and 'username' in session:
		username = session['username']
	
	q = _session.query(_Member).filter(_Member.username==username).all()[0]
	t = _lookup.get_template('index.txt')
	out = t.render(pref=root, site=_config.get("sitename", "Untitled"), 
				   page=page, menus=get_menus(), content=content,
				   username=q.username, first=q.firstname, last=q.lastname,
				   logout=(_+"/logout"))
	return out

#-----------------#
#   Decorators    #
#-----------------#
def auth_check():
	session = request.environ.get('beaker.session')
	if not (session and 'username' in session):
		return False
	return True

@route(_+"/")
def index():
	content = """
	<h1>It works!</h1>
	<p>So it works, now what? Well:</p>
	<ol>
	<li>Create a <a href="%s">membership type</a>.</li>
	<li><a href="%s">Add some members</a>.</li>
	<li><a href="%s">Add a payment</a>.</li>
	</ol>
	<p>Hurray!</p>
	""" % (_+"/membership/types", _+"/membership/add", _+"/money/payments/add")
	return template_index(_root, "Dashboard", content)

@route(_+'/logout')
def logout():
	session = request.environ.get('beaker.session')
	session.invalidate()
	redirect('/')

#-----------------#
# Private Methods #
#-----------------#
def _get_menus():	
	menus = [(("Home", "/"),())]
	for m in _modules:
		menus.append(m.get_menu())
	return menus

@post(_+"/login")
def _login_post():
	session = request.environ.get('beaker.session')
	user = request.forms.get('username')
	passwd = request.forms.get('password')
	if user and passwd:
		p = _session.query(_Member).filter(_Member.username==user).all()
		if len(p) > 0 and p[0].password == hash(passwd):
			session['username'] = user
			session.save()
			get_logger('core').info("User '%s' successfully logged in." % user)
			redirect(_+"/")
	get_logger('core').warning("Invalid login attempt for user '%s'." % user)
	return login("Invalid input. Try again.")

@get(_root + '/static/:filename')
def _server_static(filename):
	return static_file(filename, root=_static)

#-----------------#
#    Post Init    #
#-----------------#

class _ConnInfo(logging.Filter):
	def __getitem__(self, nom):
		if nom == "ip":
			return get_ip()
		elif nom == "user":	
			session = get_session()
			if not (session and 'username' in session):
				return None
			return session['username']

	def __iter__(self):
		keys = ["ip", "user"]
		#keys.extend(self.__dict__.keys())
		return keys.__iter__()

_fmt_template = '[%(levelname)s] - [%(asctime)s]: (%(name)s) %(message)s'
_fmt_ip_template = _fmt_template.replace('-', '%(ip)s - %(user)s -')
_fmt_date = '%d/%m/%Y %T'
_fmt = logging.Formatter(_fmt_ip_template, _fmt_date)

_filelog = logging.FileHandler(os.path.join(_private, 'bbqcrm.log'))
_filelog.setFormatter(_fmt)
_filelog.addFilter(_ConnInfo())
_filelog.setLevel(logging.INFO)

_console = logging.StreamHandler()
_console.setFormatter(_fmt)
_console.addFilter(_ConnInfo())
_console.setLevel(logging.DEBUG)

logging.getLogger('').addHandler(_filelog)
logging.getLogger('').addHandler(_console)

def get_logger(x=''):
	logger = logging.getLogger(x)
	logger.setLevel(logging.DEBUG)
	return logging.LoggerAdapter(logger, _ConnInfo())

_modules = []
try:
	for m in _enabled_modules:
		_modules.append(importlib.import_module('..'+m, 'bbqcrm.core'))
except:
	raise
#-----------------#
#  Main function  #
#-----------------#
def main():
	import sys
	print(__doc__)
	if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
		print(help)
	else:
		bottle.debug(2)	
		application = bottle.app()
		session_opts = {
			'session.type': 'file',
			'session.cookie_expires': 300,
			'session.data_dir': _private,
			'session.auto': True
		}
		application = SessionMiddleware(application, session_opts)
		bottle.Response.content_type = "application/xhtml+xml; charset=UTF-8"
		get_logger("System").info("bbqcrm started.")
		bottle.run(host='0.0.0.0', port=8080, app=application)
		get_logger("System").info("bbqcrm shut down.")

if __name__ == "__main__":
	main()

def first_run():
	# TODO try to load config.json for prefilling, especally for database
	# save out db settings to json
	content = """
	<p>It appears that this is your first run of bbqCRM!</p>
	<p>In order to make the most of bbqCRM, I have a few questions for you.</p>
	<form action="%s" method="POST">
		<table>
			<tr>
				<td colspan="2">
					<h2>Administration</h2>
				</td>
			<tr>
				<td>Admin username:</td>
				<td><input type="text" name="username" /></td>
			</tr>
			<tr>
				<td>Admin password:</td>
				<td><input type="password" name="password" /></td>
			</tr>
			<tr>
				<td>Website name:</td>
				<td><input type="text" name="webname" /></td>
			</tr>
			<tr>
				<td>Modules:</td>
				<td>None optional (yet)</td>
			</tr>
			<tr>
				<td colspan="2">
					<h2>Email Settings</h2>
				</td>
			</tr>
			<tr>
				<td>SMTP Host:</td>
				<td><input type="text" name="smtp_host" /></td>
			</tr>
			<tr>
				<td>SMTP Port:</td>
				<td><input type="text" name="smtp_port" /></td>
			</tr>
			<tr>
				<td>SMTP SSL:</td>
				<td><input type="checkbox" name="smtp_ssl" value="true" /></td>
			</tr>
			<tr>
				<td>SMTP Username (if required):</td>
				<td><input type="text" name="smtp_user" /></td>
			</tr>
			<tr>
				<td>SMTP Password (if required):</td>
				<td><input type="password" name="smtp_pass" /></td>
			</tr>
		</table>
	</form>
	"""

