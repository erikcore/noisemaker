from google.appengine.ext import db

class User(db.Model):
	username = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	email = db.EmailProperty(required=False)
	ctime = db.DateTimeProperty(auto_now_add=True)
	mtime = db.DateTimeProperty(auto_now=True)

class Post(db.Model):
	author = db.ReferenceProperty(User)
	title = db.StringProperty()
	url = db.TextProperty()
	body = db.TextProperty()
	upvotes = db.ListProperty(long)
	downvotes = db.ListProperty(long)
	score = db.FloatProperty()
	ctime = db.DateTimeProperty(auto_now_add=True)
	mtime = db.DateTimeProperty(auto_now=True)

class KarmaLog(db.Model):
	author = db.ReferenceProperty(User)
	item_id = db.IntegerProperty()
	status = db.IntegerProperty() # up = 1, down = -1
	ctime = db.DateTimeProperty(auto_now_add=True)
	mtime = db.DateTimeProperty(auto_now=True)

class Comment(db.Model):
	parent_id = db.IntegerProperty()
	parent_type = db.StringProperty()
	author = db.ReferenceProperty(User)
	body = db.TextProperty()
	upvotes = db.ListProperty(long)
	downvotes = db.ListProperty(long)
	score = db.FloatProperty()
	ctime = db.DateTimeProperty(auto_now_add=True)
	mtime = db.DateTimeProperty(auto_now=True)