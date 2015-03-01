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

from google.appengine.api import mail

config = {}
config['webapp2_extras.sessions'] = dict(secret_key='<ENTER A UNIQUE, SUPER SECRET STRING HERE>')

class BaseHandler(webapp2.RequestHandler):
	
	@property
	def current_user(self):
		if self.session.get("user"):
			return self.session.get("user")
		return None

	def dispatch(self):
		self.session_store = sessions.get_store(request=self.request)
		try:
			webapp2.RequestHandler.dispatch(self)
		finally:
			self.session_store.save_sessions(self.response)

	@webapp2.cached_property
	def session(self):
		return self.session_store.get_session()

class HomeHandler(BaseHandler):
	def get(self):
		offset = 0
		limit = 30
		page_no = self.request.get("page")
		if page_no:
			offset = (int(page_no)-1) * limit
		else:
			page_no = 1
		posts = models.Post.all().order("-score").run(offset=offset,limit=limit)
		template = jinja_environment.get_template('myapp/templates/index.html')
		self.response.out.write(template.render(dict(
			current_user=self.current_user,
			karma=comment_helper.get_karma_for_user(self.current_user),
			posts=posts,
			count_begin=offset,
			page_no=int(page_no)
		)))

class RegisterHandler(BaseHandler):
	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		email_address = self.request.get("email")
		whence = self.request.get("whence")
		existing_user = db.Query(models.User).filter('username =', username).get()
		if not existing_user:
			user = models.User(
				username=str(username),
				password=password,
				email=email_address
			)
			user.put()
			user_dict = dict(
				key=str(user.key()),
				id=user.key().id(),
				username=user.username,
				email=user.email,
				ctime=str(user.ctime),
				mtime=str(user.mtime)
			)
			self.session["user"] = user_dict
			if whence:
				self.redirect(str(whence))

			message = mail.EmailMessage(sender="Noisemaker <hello@noisemakerclub.appspotmail.com>", subject="Welcome to Noisemaker")

			message.to = email_address

			message.body = "Welcome to Noisemaker! You're all set! Start posting and discussing at http://noisemaker.co"

			message.send()
			self.redirect("/")
		else:
			self.redirect("/login")

class LoginHandler(BaseHandler):
	def post(self):
		password = self.request.get("password")
		username = self.request.get("username")
		whence = self.request.get("whence")
		user = db.Query(models.User).filter('username =', str(username)).get()
		if not user or user.password != password:
			# TODO: Let user know there was an error logging in.
			self.redirect("/login")
		else:
			user_dict = dict(
				key=str(user.key()),
				id=user.key().id(),
				email=user.email,
				username=user.username,
				ctime=str(user.ctime),
				mtime=str(user.mtime)
			)
			self.session["user"] = user_dict
		if not whence:
			self.redirect("/")
		self.redirect(str(whence))
	def get(self):
		if self.current_user:
			self.redirect("/")
		whence = self.request.get("whence")
		template = jinja_environment.get_template('myapp/templates/login.html')
		self.response.out.write(template.render(dict(
			current_user=self.current_user,
			whence=whence
		)))

class LogoutHandler(BaseHandler):
	def post(self):
		if self.current_user is not None:
			self.session['user'] = None
		self.redirect('/')
	def get(self):
		if self.current_user is not None:
			self.session['user'] = None
		self.redirect('/')

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
	[('/login/?', LoginHandler),('/logout/?', LogoutHandler),('/register/?', RegisterHandler),('/', HomeHandler)],
	debug=True,
	config=config
)
