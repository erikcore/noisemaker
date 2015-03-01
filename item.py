import webapp2
import os
import jinja2
import urllib2
import random
from urllib2 import Request, urlopen
import json
import datetime

import models
import filters

from google.appengine.ext import db
from webapp2_extras import sessions
from google.appengine.api import memcache, images

from main import BaseHandler, config
import comment_helper

class ItemHandler(BaseHandler):
	def get(self):
		path_parts = self.request.path.split('/')
		item_id = path_parts[2]
		item = memcache.get(item_id)
		if not item:
			item = models.Post().get_by_id(long(item_id))
		comment_dict = comment_helper.get_top_level_comment_dict(item)
		template = jinja_environment.get_template('myapp/templates/item.html')
		self.response.out.write(template.render(dict(
			current_user=self.current_user,
			karma=comment_helper.get_karma_for_user(self.current_user),
			post=item,
			comment_dict=comment_dict,
		)))

class SubmitHandler(BaseHandler):
	def post(self):
		new_title = self.request.get("new_title")
		new_url = self.request.get("new_url")
		new_text = self.request.get("new_text")
		new_post = models.Post()
		new_post.author = db.Key(self.current_user['key'])
		new_post.title = new_title
		new_post.url = new_url
		new_post.upvotes.append(self.current_user['id'])
		new_post.put()
		new_post.score = calculate_score(len(new_post.upvotes),new_post.ctime)
		new_post.put()
		memcache.add(key=str(new_post.key().id()), value=new_post, time=5)
		self.redirect("/item/%d" % new_post.key().id())
	def get(self):
		if self.current_user:
			template = jinja_environment.get_template('myapp/templates/submit.html')
			self.response.out.write(template.render(dict(
				current_user=self.current_user,
				karma=comment_helper.get_karma_for_user(self.current_user),
			)))
		else:
			self.redirect("/login/?whence=/submit/") # append "must be logged in" error

def calculate_score(votes, ctime, gravity=1.8):
	time_since = datetime.datetime.now() - ctime
	time_since_hours = time_since.total_seconds() // 3600
	return (votes - 1) / pow((time_since_hours+2), gravity)

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)

jinja_environment.filters.update({
	'timesince': filters.timesince,
	'pluralize': filters.pluralize,
	'get_base_url': filters.get_base_url,
	'urlencode': filters.urlencode,
	})

app = webapp2.WSGIApplication(
    [('/submit/?', SubmitHandler),('/item.*', ItemHandler)],
    debug=True,
    config=config
)