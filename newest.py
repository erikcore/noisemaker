from main import BaseHandler

import webapp2
import os
import jinja2
import urllib2
import random
from urllib2 import Request, urlopen
import json

import models
import filters
import comment_helper

from google.appengine.ext import db
from webapp2_extras import sessions
from google.appengine.api import memcache, images

config = {}
config['webapp2_extras.sessions'] = dict(secret_key='9e396482-a127-409f-9a88-dd4dba5cde1b')

class NewestHandler(BaseHandler):
	def get(self):
		limit = 30
		page = self.request.get("page")
		offset = 0
		page_no = self.request.get("page")
		if page_no:
			offset = (int(page_no)-1) * limit
		else:
			page_no = 1
		if page and int(page) > 0:
			offset = limit * (int(page) - 1)
		posts = models.Post.all().order("-ctime").run(offset=offset,limit=limit)
		template = jinja_environment.get_template('myapp/templates/index.html')
		self.response.out.write(template.render(dict(
            current_user=self.current_user,
            karma=comment_helper.get_karma_for_user(self.current_user),
            posts=posts,
            count_begin=offset,
            page_no=int(page_no)
        )))

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)
jinja_environment.filters.update({
	'timesince': filters.timesince,
	'pluralize': filters.pluralize,
	'get_base_url': filters.get_base_url,
	'comment_count': filters.comment_count,
	})

app = webapp2.WSGIApplication(
    [('/newest/?', NewestHandler)],
    debug=True,
    config=config
)