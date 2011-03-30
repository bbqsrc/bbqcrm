from bottle import abort, get, post, redirect, request, route
from sqlalchemy import Table, Column, Integer, Numeric, String, MetaData
from sqlalchemy import ForeignKey, DateTime, PickleType, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from mako.template import Template
from mako.lookup import TemplateLookup
from bbqcrm.core import get_menus, template_index

import dateutil.parser
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

#-----------------#
#     Classes     #
#-----------------#
class _Membership_Type(_SqlBase):
	__tablename__ = "membership_types"

	type = Column(String, primary_key=True)
	duration = Column(Integer, nullable=False) # in Months, 0 = forever
	cost = Column(Numeric, nullable=False)

	def __init__(self, type, duration, cost):
		self.type = type
		self.duration = duration
		self.cost = cost

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

#-----------------#
# Public Methods  #
#-----------------#
def get_menu():
	return ("Membership", _), (
		('Member list', _),
		('-', '#'),
		('Add member', _ + '/add'),
		('Remove member', _ + '/remove'),
		('Get member', _ + '/get'),
		('-', '#'),
		('Manage membership types', _ + '/types')
	)

#-----------------#
# Private Methods #
#-----------------#

@route(_)
def _membership():
	page = "Membership"
	content = "<table>"
	content += """
		<tr>
			<td>id</td>
			<td>student_id</td>
			<td>firstname</td>
			<td>lastname</td>
			<td>username</td>
			<td>password</td>
			<td>address1</td>
			<td>address2</td>
			<td>suburb</td>
			<td>state</td>
			<td>postcode</td>
			<td>homephone</td>
			<td>mobile</td>
			<td>email</td>
			<td>type</td>
			<td>joined</td>
			<td>paid</td>
			<td>begin</td>
			<td>end</td>
			<td>Controls</td>
		</tr>
	"""
	q = _session.query(_Member).all()
	for i in q:
		content += "<tr>"
		for j in (i.id, i.student_id, i.firstname, i.lastname, i.username, 
			i.password, i.address1, i.address2, i.suburb, i.state, i.postcode, 
			i.homephone, i.mobile, i.email, i.type, i.joined, i.paid, i.begin, 
			i.end):
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

@route(_+"/add")
def _add():
	opts = ""
	q = _session.query(_Membership_Type).all()
	for i in q:
		opts += "<option value='%s'>%s</option>\n" % (i.type, i.type)

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
			<td>Student ID:</td>
			<td><input name="student_id" type="text" /></td>
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
			<td>Membership Type:</td>
			<td>
				<select name="type">
					%s
				</select>
			</td>
		</tr>
		<tr>
			<td><input name="submit" type="submit" value="Submit" /></td>
		</tr>
	</table>
	</form>
	""" % ((_+"/add"), opts)
	page = "Membership / Add Member"
	return template_index(_root, page, form)

@route(_+"/modify/:num")
def _modify(num):
	pass

@route(_+"/delete/:num")
def _delete_num(num):
	content = ""
	page = "Membership / Delete Member"
	q = _session.query(_Member).filter(_Member.id == num).all()
	if len(q) > 0:
		content = """
		<form action="%s" method="POST">
			Are you sure you want to delete Member %s?<br/>
			<input name="num" type="hidden" value="%s" />
			<input name="submit" type="submit" value="Yes" />
			<input name="bailout" type="button" value="No"
				onclick="javascript:history.go(-1)" />
		</form>
		""" % ((_+"/delete"), num, num)
	else:
		content = """
		<p>Member %s does not exist.</p>
		<p><a href="javascript:history.go(-1)">Back</a></p>
		""" % num
	return template_index(_root, page, content)

@route(_+"/delete")
def _delete():
	pass # STUB, TODO add delete form

@post(_+"/delete")
def _delete_post():
	# TODO: add integrity checks to Payment db :D
	num = int(request.forms.get('num'))
	q = _session.query(_Member).filter(_Member.id == num).all()
	content = ""
	if len(q) > 0:
		_session.delete(q[0])
		content = "Member %s deleted." % num
	else:
		content = "<p>How did you get here?</p>"
	content += "<p><a href='%s'>Membership</a></p>" % (_)
	page = "Membership / Delete Member"
	return template_index(_root, page, content)


@post(_+"/add")
def _add_post():
	m = _Member()
	for key, value in request.forms.items():
		if key != "submit":
			vars(m)[key] = value
	_session.add(m)

	page = "Membership / Add Member"
	content = """
		<p>Member added successfully.</p>
		<br />
		<a href='%s'>Back</a>
		""" % _
	return template_index(_root, page, content)

@route(_+"/types")
def _types():
	current = """
	<h2>Types</h2>
	<table style="border-width: 1px">
		<tr>
			<td>Type</td>
			<td>Duration</td>
			<td>Cost</td>
		</tr>	
	"""
	q = _session.query(_Membership_Type).all()
	for i in q:
		current += "<tr>\n"
		for j in (i.type, i.duration, i.cost):
			current += "\t<td>%s</td>\n" % j
		current += "</tr>\n"
	current += "</table>\n<br /><br />"

	form = """
	<h2>Add Type</h2>
	<form id="new_user" action="%s" method="POST">
	<table>
		<tr>
			<td>Type:</td>
			<td><input name="type" type="text" /></td>
		</tr>
		<tr>
			<td>Duration (in Months):</td>
			<td><input name="duration" type="text" /></td>
		</tr>
		<tr>
			<td>Cost:</td>
			<td><input name="cost" type="text" /></td>
		</tr>
		<tr>
			<td><input name="submit" type="submit" value="Submit" /></td>
		</tr>
	</table>
	</form>
	""" % (_ + "/types/add")
	page = "Membership / Manage Membership Types"
	return template_index(_root, page, (current + form))

@post(_+"/types/add")
def _types_add():
	t = request.forms.get("type")
	d = request.forms.get("duration")
	c = request.forms.get("cost")
	q = _session.query(_Membership_Type).filter(_Membership_Type.type==t).all()
	content = ""
	if len(q) > 0:
		content = "<p>'%s' already in use.</p>\n" % t
	else:
		mt = _Membership_Type(t, d, c)
		_session.add(mt)
		content = "<p>'%s' added successfully.</p>\n" % t
	content += "<p><a href='%s'>Back</a></p>" % (_ + "/types")
	page = "Membership / Manage Membership Types / Add"
	return template_index(_root, page, content)

@route(_+"/remove")
def _remove():
	return

@route(_+"/get/:number")
def _get():
	return
