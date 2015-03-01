import webapp2
import os
import jinja2
import urllib2
import random
from urllib2 import Request, urlopen
import json
import datetime
import random

import models
import filters

from google.appengine.ext import db
from webapp2_extras import sessions
from google.appengine.api import memcache, images

from main import BaseHandler, config
import comment_helper
import item

class FreshenTop50Handler(BaseHandler):
	def get(self):
		post_number = random.randint(0,50)
		print post_number
		post = db.Query(models.Post).order("-score").get(offset=post_number)
		if post:
			post.score = item.calculate_score(len(post.upvotes)-len(post.downvotes),post.ctime)
			post.put()
		return self.response.out.write("True")

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
)

app = webapp2.WSGIApplication(
    [('/zf/freshenup', FreshenTop50Handler)],
    debug=True,
    config=config
)