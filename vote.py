import webapp2
import os
import jinja2
import urllib2
import random
from urllib2 import Request, urlopen
import json
import datetime

import models
import item

from google.appengine.ext import db
from webapp2_extras import sessions
from google.appengine.api import memcache, images

from main import BaseHandler, config

class VoteHandler(BaseHandler):
	def post(self):
		if not self.current_user:
			return self.response.out.write("User must be logged in") # Should probably replace this with a more helpful json error
		id = self.request.get("id")
		type = self.request.get("type")
		if type == "post":
			post = models.Post().get_by_id(int(id))
		if type == "comment":
			print "VOTE FOR COMMENT"
			print id
			post = models.Comment().get_by_id(int(id))
		if self.current_user['id'] in post.upvotes:
			return self.response.out.write("Duplicate vote")
		post.upvotes.append(int(self.current_user['id']))
		post.score = item.calculate_score(len(post.upvotes)-len(post.downvotes),post.ctime)
		post.put()
		self.response.out.write("vote received from %s for item %s" % ( self.current_user['id'], id))
	def get(self):
		self.response.out.write("get is working")

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)

app = webapp2.WSGIApplication(
    [('/vote.*', VoteHandler)],
    debug=True,
    config=config
)