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
from bottle import abort, get, post, redirect, request, route, static_file
from mako.template import Template
from mako.lookup import TemplateLookup

import bottle
import json
import os, os.path

#-----------------#
# Private globals #
#-----------------#
_config = None
_path = os.path.dirname(os.path.abspath(__file__))
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

@route(_root + '/')
def index():
	t = _lookup.get_template('index.txt')
	content = """<h1>It works!</h1>"""
	out = t.render(pref=_root, site=_config.get("sitename", "Untitled"), 
				   page="Dashboard", menus=get_menus(), content=content)
	return out

#-----------------#
# Private Methods #
#-----------------#
def _get_menus():	
	menus = []
	for m in _modules:
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
		_modules.append(__import__(m))
except:
	raise
#-----------------#
#  Main function  #
#-----------------#
if __name__ == "__main__":
	import sys
	print __doc__
	if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
		print help
	else:
		bottle.debug(2)	
		application = bottle.app()
		bottle.Response.content_type = "application/xhtml+xml; charset=UTF-8"
		bottle.run(host='0.0.0.0', port=8080, app=application)

