from bottle import abort, get, post, redirect, request, route
from sqlalchemy import Table, Column, Integer, Numeric, String, MetaData
from sqlalchemy import ForeignKey, DateTime, PickleType, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from mako.template import Template
from mako.lookup import TemplateLookup
from bbqcrm import get_menus, template_index

import datetime
import json
import os, os.path

_config = None
_path = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
try:
	f = open(os.path.join(_path, 'config.json'))
	_config = json.load(f)
	f.close()
except:
	raise

_appdir    = _config.get("appdir", os.path.dirname(__file__))
_private   = _config.get("privdir",
				os.path.join(os.path.dirname(__file__), "private"))
_templates = [_config.get("templates", _appdir + '/templates')]
_lookup    = TemplateLookup(directories=_templates)
_root      = _config.get("root", "")
_enabled_modules = _config.get("modules", [])
_static    = _config.get("static", _private+"/static")
_site      = _config.get("sitename", "Untitled")

_modconf = _config.get("Membership", {})
_modname = _modconf.get("modname", "membership")
_ = _root + "/" + _modname

_engine = None
try:
	_db_engine   = _config.get("db_type")
	_db_database = _config.get("db_database", "bbqcrm")
	_db_username = _config.get("db_username", None)
	_db_password = _config.get("db_password", None)
	_db_host     = _config.get("db_host", "localhost")
	_db_port     = _config.get("db_port", None)
	_db_table    = _modname
	if _db_engine == "sqlite":
		_engine = create_engine("sqlite:///%s" % (_private+_db_database+".db"))
	else:
		pref = (_db_username+":"+_db_password+"@") if _db_username and _db_password else "" 
		suff = _db_host + (_db_port if _db_port else "") + "/" + _db_database
		_engine = create_engine("%s://%s%s" % (_db_engine, pref, suff))
except:
	raise

_Session = sessionmaker(bind=_engine, autoflush=True, autocommit=True)
_SqlBase = declarative_base()
_SqlBase.metadata.bind = _engine
_SqlBase.metadata.create_all()
#_session = Session()

#-----------------#
# Public Methods  #
#-----------------#
def get_menu():
	return ("Membership", _), (
		('Member list', _),
		('Add member', _ + '/add'),
		('Remove member', _ + '/remove'),
		('Get member', _ + '/get')
	)

#-----------------#
#     Classes     #
#-----------------#
class _Membership_Type(_SqlBase):
	__tablename__ = "membership_types"

	id = Column(Integer, primary_key=True)
	type = Column(String, nullable=False)
	length = Column(Integer, nullable=False) # in Months, 0 = forever

#class _Permissions(_SqlBase):
#	__tablename__ = "permissions"

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
	joined     = Column(DateTime)
	paid       = Column(DateTime)
	begin      = Column(DateTime)
	end        = Column(DateTime)

	def __init__(self, sid=None, f=None, l=None, u=None, p=None, a1=None, 
			a2=None, sub=None, st=None, post=None, hp=None, m=None, e=None,
			paid=None, begin=None, end=None):
		
		self.username = u
		self.password = p
		
		self.student_id = sid
		self.firstname = f
		self.lastname = l
		self.address1 = a1
		self.address2 = a2
		self.suburb = suburb
		self.state = st
		self.postcode = post
		self.homephone = hp
		self.mobile = m
		self.email = e
		
		self.joined = datetime.datetime.now()
		self.paid = paid
		self.begin = begin
		self.end = end

#-----------------#
# Private Methods #
#-----------------#

@route(_)
def _membership():
	page = "Membership"
	content = "<p>Not here yet.</p>"
	return template_index(_root, page, content)

@route(_+"/add")
def _add():
	form = """
	<form id="new_user" action="%s" method="POST">
	<table>
		<tr>
			<td>Username:</td>
			<td><input name="username" type="text" /></td>
		</tr>
		<tr>
			<td>Password:</td>
			<td><input name="password" type="password" /></td>
		</tr>
		<tr><td><br/></td></tr>
		<tr>
			<td>Given name:</td>
			<td><input name="firstname" type="text" /></td>
		</tr>
		<tr>
			<td>Surname:</td>
			<td><input name="lastname" type="text" /></td>
		</tr>
		<tr>
			<td>Address:</td>
			<td><input name="address1" type="text" /></td>
		</tr>
		<tr>
			<td></td>
			<td><input name="address2" type="text" /></td>
		</tr>
		<tr>
			<td>Suburb:</td>
			<td><input name="suburb" type="text" /></td>
		</tr>
		<tr>
			<td>State:</td>
			<td><input name="state" type="text" /></td>
		</tr>
		<tr>
			<td>Postcode:</td>
			<td><input name="postcode" type="text" /></td>
		</tr>
		<tr><td><br/></td></tr>
		<tr>
			<td>Home phone (optional):</td>
			<td><input name="homephone" type="text" /></td>
		</tr>
		<tr>
			<td>Mobile phone:</td>
			<td><input name="mobile" type="text" /><br/></td>
		</tr>
		<tr>
			<td>Email:</td>
			<td><input name="email" type="text" /><br/></td>
		</tr>
		<tr><td><br/></td></tr>
		<tr>
			<td><input name="submit" type="submit" value="Submit" /></td>
		</tr>
	</table>
	</form>
	""" % (_+"add")
	page = "Membership / Add Member"
	return template_index(_root, page, form)

@post(_+"/add")
def _add_post():
	#TODO add checks
	
	pass

@route(_+"/remove")
def _remove():
	return

@route(_+"/get/:number")
def _get():
	return
