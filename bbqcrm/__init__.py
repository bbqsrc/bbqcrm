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
	print "You need Python 2.7 or higher (including Python 3)."
	sys.exit()

from bottle import abort, get, post, redirect, request, route, static_file
from mako.template import Template
from mako.lookup import TemplateLookup

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

_appdir    = _config.get("appdir", _path)
_templates = [_config.get("templates", _appdir + '/templates')]
_lookup    = TemplateLookup(directories=_templates)
_root      = _config.get("root", "")
_enabled_modules = _config.get("modules", [])
_static    = _config.get("static", _appdir+"/static")

#-----------------#
# Public Methods  #
#-----------------#
def get_menus():
	return _get_menus()

def get_menu():
	return ("What?", "/"),()

@route(_root + '/')
def index():
	#t = _lookup.get_template('index.txt')
	content = """<h1>It works!</h1>"""
	#out = t.render(pref=_root, site=_config.get("sitename", "Untitled"), 
	#			   page="Dashboard", menus=get_menus(), content=content)
	#return out
	return template_index(_root, "Dashboard", content)

def template_index(root, page, content):
	if _ui:
		if _ui == "console":
			pass #TODO for CLI
	
	t = _lookup.get_template('index.txt')
	out = t.render(pref=root, site=_config.get("sitename", "Untitled"), 
				   page=page, menus=get_menus(), content=content)
	return out

#-----------------#
# Private Methods #
#-----------------#
def _get_menus():	
	menus = []
	for m in _modules:
		print m
		menus.append(m.get_menu())
	return menus

@get(_root + '/static/:filename')
def _server_static(filename):
	return static_file(filename, root=_static)

#-----------------#
#    Post Init    #
#-----------------#
_modules = []
try:
	for m in _enabled_modules:
		_modules.append(importlib.import_module(m, 'bbqcrm'))
except:
	raise
#-----------------#
#  Main function  #
#-----------------#
def main():
	import sys
	print __doc__
	if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
		print help
	else:
		bottle.debug(2)	
		application = bottle.app()
		bottle.Response.content_type = "application/xhtml+xml; charset=UTF-8"
		bottle.run(host='0.0.0.0', port=8080, app=application)

if __name__ == "__main__":
	main()

