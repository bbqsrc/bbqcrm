from bottle import abort, get, post, redirect, request, route
from sqlalchemy import Table, Column, Integer, Numeric, String, MetaData
from sqlalchemy import ForeignKey, DateTime, PickleType, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from mako.template import Template
from mako.lookup import TemplateLookup

from bbqcrm import get_menus
import datetime
import json
import os, os.path

_config = None
try:
	f = open(os.path.join(os.path.dirname(__file__), 'config.json'))
	_config = json.load(f)
	f.close()
except:
	raise

_appdir    = _config.get("appdir", os.path.dirname(__file__))
_templates = [_config.get("templates", _appdir + '/templates')]
_lookup    = TemplateLookup(directories=_templates)
_root      = _config.get("root", "")
_enabled_modules = _config.get("modules", [])
_static    = _config.get("static", _appdir+"/static")
_site      = _config.get("sitename", "Untitled")

_modconf = _config.get("Membership", {})
_ = _root + "/" + _modconf.get("modname", "membership")

_engine = create_engine("sqlite:///%s" % _appdir + "/test.db")# TODO SRSLY, this
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

class _Member(_SqlBase):
	__tablename__ = "members"

	id        = Column(Integer, primary_key=True)
	firstname = Column(String)
	lastname  = Column(String)
	username  = Column(String)
	password  = Column(String)
	address1  = Column(String)
	address2  = Column(String)
	suburb    = Column(String)
	state     = Column(String)
	postcode  = Column(String)
	homephone = Column(String)
	mobile    = Column(String)
	email     = Column(String)
	joined    = Column(DateTime)
	member_expires = Column(DateTime)

	def __init__(self, f, l, u, p, a1, a2, sub, st, post, hp, m, e):
		self.firstname = f
		self.lastname = l
		self.username = u
		self.password = p
		self.address1 = a1
		self.address2 = a2
		self.suburb = suburb
		self.state = st
		self.postcode = post
		self.homephone = hp
		self.mobile = m
		self.email = e
		self.joined = datetime.datetime.now()

#-----------------#
# Private Methods #
#-----------------#

@route(_)
def _membership():
	t = _lookup.get_template('index.txt')
	page = "Membership"
	content = "<p>Not here yet.</p>"
	out = t.render(pref=_root, site=_site, page=page, 
		menus=get_menus(), content=content)
	return out

@route(_+"/add")
def _add():
	form = """
	<form id="new_user" action="%s" method="POST">
		Username: <input name="username" type="text" /> 
		Password: <input name="password" type="password" />
		<br/>
		Given name: <input name="firstname" type="text" />
		Surname: <input name="lastname" type="text" />
		<br/>
		Address: <input name="firstname" type="text" />
		<br/>
		<input name="firstname" type="text" />
		<br/>
		Suburb: <input name="suburb" type="text" />
		State: <input name="state" type="text" />
		Postcode: <input name="postcode" type="text" />
		<br/>
		Home phone (optional): <input name="homephone" type="text" />
		Mobile phone: <input name="mobile" type="text" /><br/>
		Email: <input name="email" type="text" /><br/>
		<input name="submit" type="submit" value="Submit" />
	</form>
	""" % (_+"add")
	t = _lookup.get_template('index.txt')
	page = "Membership / Add Member"
	out = t.render(pref=_root, site=_site, page=page, 
		menus=get_menus(), content=form)
	return out

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
