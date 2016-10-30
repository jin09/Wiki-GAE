#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json
import logging
import random
import string
import urllib2
from xml.dom import minidom
from datetime import datetime, timedelta
from google.appengine.api import memcache
import webapp2
import jinja2
import os
import re
import hmac
from google.appengine.ext import db
import hashlib

jinja_env = jinja2.Environment(autoescape=True,
                               loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


class Wiki(db.Model):
    path = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    time = db.DateTimeProperty(auto_now_add=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class WikiPage(Handler):
    def get(self, path):
        search = db.GqlQuery("select * from Wiki where path=:1", path)
        content = ""
        if search:
            for i in search:
                content = i.content
                break
            if content != "":
                self.render("index.html", content=content)
            else:
                self.redirect('/_edit' + path)
        else:
            self.redirect('/_edit' + path)

    def post(self):
        self.response.write("Wiki edit")


class EditPage(Handler):
    def get(self, path):
        query = db.GqlQuery("select * from Wiki where path=:1", path)
        content = ""
        for i in query:
            content = i.content
            break
        self.render("editor.html", savedata=content)

    def post(self, path):
        content = self.request.get("textarea")
        if content!="":
            wiki = Wiki(path=path, content=content)
            wiki.put()
            logging.error(path)
            self.redirect(path)
        else:
            self.render("editor.html", error="Text Field cannot be empty!!!")

class Logout(Handler):
    def get(self):
        self.response.write("Logout PAGE")

    def post(self):
        self.response.write("logout edit")


class Login(Handler):
    def get(self):
        self.response.write("login PAGE")

    def post(self):
        self.response.write("login edit")


class Signup(Handler):
    def get(self):
        self.response.write("Signup PAGE")

    def post(self):
        self.response.write("Signup edit")


PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'

app = webapp2.WSGIApplication([('/signup', Signup),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/_edit' + PAGE_RE, EditPage),
                               (PAGE_RE, WikiPage),
                               ],
                              debug=True)
