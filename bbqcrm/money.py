from bottle import abort, get, post, redirect, request, route
from sqlalchemy import Table, Column, Integer, Numeric, String, MetaData
from sqlalchemy import ForeignKey, DateTime, PickleType, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from mako.template import Template
from mako.lookup import TemplateLookup
from bbqcrm.core import get_menus, template_index
from dateutil import parser as dateparser

import bbqcrm.membership
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

_appdir    = _config.get("appdir", _path)
_private   = _config.get("privdir",
				os.path.join(_path, "private"))
_templates = [_config.get("templates", _appdir + '/templates')]
_lookup    = TemplateLookup(directories=_templates)
_root      = _config.get("root", "")
_enabled_modules = _config.get("modules", [])
_static    = _config.get("static", _private+"/static")
_site      = _config.get("sitename", "Untitled")

_modconf = _config.get("Money", {})
_modname = _modconf.get("modname", "money")
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

class _Payment(_SqlBase):
	__tablename__ = "payments"

	id = Column(Integer, primary_key=True)
	member_id = Column(Integer, ForeignKey('members.id'), nullable=False)
	description = Column(String, nullable=False)
	debit = Column(Numeric)
	credit = Column(Numeric)
	date = Column(DateTime, nullable=False)

	def __init__(self, member_id, description, dir, amount, date=None):
		self.member_id = member_id
		self.description = description
		if dir == "credit":
			self.credit = amount
		elif dir == "debit":
			self.debit = amount
		else:
			raise AttributeError("Neither credit nor debit chosen.")
		if not date:
			self.date = datetime.datetime.now()
	
_SqlBase.metadata.create_all()
_session = _Session()

#-----------------#
# Public Methods  #
#-----------------#
def get_menu():
	return ("Money", _), (
		('Finances', _),
		('-', ''),
		('Payments', _ + '/payments'),
		('New payment', _ + '/payments/new')
	)

#-----------------#
# Private Methods #
#-----------------#
@route(_)
def _finances():
	page = "Finance"
	content = "<table>"
	content += """
	<tr>
		<td>ID</td>
		<td>Member ID</td>
		<td>Description</td>
		<td>Date</td>
		<td>Credit</td>
		<td>Debit</td>
	</tr>
	"""
	q = _session.query(_Payment).all()
	for i in q:
		content += "<tr>"
		for j in (i.id, i.member_id, i.description, i.date, i.credit, i.debit):
				content += "<td>%s</td>\n" % j
		content += """
					<td>
						<a href='%s'>Modify</a>&nbsp;
						<a href='%s'>Delete</a>
					</td>\n""" % ((_ + "/modify/%d" % i.id), 
								(_ + "/delete/%d" % i.id))
		content += "</tr>"
	content += "</table>\n"
	return template_index(_root, page, content)

@route(_+"/payments/new")
@route(_+"/payments/new/:num")
def _payments_new(num=""):
	content = """
	<form action="%s" method="POST">
		<table>
			<tr>
				<td>Member ID:</td>
				<td><input type="text" name="member_id" value="%s" /></td>
			</tr>
			<tr>
				<td>Description:</td>
				<td>
					<textarea name="description" rows="8" cols="40"></textarea>
				</td>
			</tr>
			<tr>
				
				<td>Amount:</td>
				<td>
				<table>
				<tr>
				<td>
					<input type="text" name="amount" />
				</td>
				<td>
					<input type="radio" name="dir" value="credit" 
						checked="yes"/> Credit<br />
					<input type="radio" name="dir" value="debit"/> Debit
				</td>
				
				</tr>
				</table>
				</td>
			<tr>
			<tr>
				<td>Date:</td>
				<td><input type="text" name="date" /> (Default: today's date)</td>
			</tr>
			</tr>
				<td><input type="submit" name="submit" value="Submit" /></td>
			</tr>
		</table>
	</form>
	""" % (_ + "/payments/new", num)
	page = "Money / Add Payment"
	return template_index(_root, page, content) 

@post(_+"/payments/new")
def _payments_new_post():
		page = "Money / Add Payment"
		mid = request.forms.get("member_id")
		des = request.forms.get("description")
		d = request.forms.get("dir").strip()
		a = request.forms.get("amount")
		date = request.forms.get("date")
		for k, v in request.forms.items():
			print("%s: %s" % (k, v))
		p = _Payment(mid, des, d, a, date)
		_session.add(p)

		content = "<p>Payment added.</p><p><a href='%s'>Back</a></p>" % (_)
		return template_index(_root, page, content)
