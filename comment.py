import webapp2
import os
import jinja2
import urllib
import urllib2
import random
from urllib2 import Request, urlopen
import json

import models
import filters
import item

from google.appengine.ext import db
from webapp2_extras import sessions
from google.appengine.api import memcache, images

from main import BaseHandler, config

import comment_helper

class SingleCommentHandler(BaseHandler):
	def get(self):
		path_parts = self.request.path.split('/')
		comment_id = path_parts[2] #need validation here
		comment = models.Comment().get_by_id(long(comment_id))
		replies = models.Comment().all().filter("parent_id =", int(comment_id)).filter("parent_type =", "comment")
		template = jinja_environment.get_template('myapp/templates/comment.html')
		self.response.out.write(template.render(dict(
			current_user=self.current_user,
			karma=comment_helper.get_karma_for_user(self.current_user),
			comment=comment,
			replies=replies,
		)))

class NewCommentHandler(BaseHandler):
	def post(self):
		whence = self.request.get('whence')
		parent_type = self.request.get('type')
		parent_id = self.request.get('id')
		body = self.request.get('comment_body').strip()
		if not self.current_user:
			if whence:
				self.redirect("/login/?whence=%s" % whence)
			else:
				self.redirect("/login/")
		if not body or body == '':
			self.redirect(whence)
		new_comment = models.Comment()
		new_comment.author = db.Key(self.current_user['key'])
		new_comment.upvotes.append(long(self.current_user['id']))
		new_comment.body = body
		new_comment.parent_id = int(parent_id)
		new_comment.parent_type = parent_type
		new_comment.put()
		new_comment.score = item.calculate_score(len(new_comment.upvotes)-len(new_comment.downvotes), new_comment.ctime)
		new_comment.put()
		self.redirect(whence)

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)
jinja_environment.filters.update({
	'timesince': filters.timesince,
	'pluralize': filters.pluralize,
	'get_base_url': filters.get_base_url,
	})

app = webapp2.WSGIApplication(
    [('/newcomment.*', NewCommentHandler),('/comment.*', SingleCommentHandler)],
    debug=True,
    config=config
)