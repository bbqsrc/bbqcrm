from bottle import abort, get, post, redirect, request, route
from sqlalchemy import Table, Column, Integer, Numeric, String, MetaData
from sqlalchemy import ForeignKey, DateTime, PickleType, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from mako.template import Template
from mako.lookup import TemplateLookup
from bbqcrm.core import get_menus, template_index

import datetime
import json
import os, os.path


#-----------------#
# Private globals #
#-----------------#
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

_modconf = _config.get("Logging", {})
_modname = _modconf.get("modname", "logging")

_smtp_host = _modconf.get("smtp_host") 
_smtp_port = _modconf.get("smtp_port", 25)
_smtp_user = _modconf.get("smtp_username", None)
_smtp_pass = _modconf.get("smtp_password", None)

_ = _root + "/" + _modname

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
_SqlBase.metadata.create_all()

def get_menu():
	return ("Logging", _), (
		('Logs', _),
		('Settings', _ + '/settings')
	)

@route(_)
def _logging():
	pass

@route(_+'/settings')
	pass
