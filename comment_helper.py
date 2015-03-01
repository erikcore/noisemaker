from google.appengine.api import memcache
from google.appengine.ext import db
import os
import models

def get_top_level_comment_dict(item):
	comment_dict = {}
	comments = models.Comment.all().filter("parent_type =", "top").filter("parent_id =", item.key().id()).order("-score")
	if comments:
		comment_ids = [comment.key().id() for comment in comments]
		replies = models.Comment.all().filter("parent_type =", "comment").filter("parent_id in", comment_ids).order("-ctime")
	for comment in comments:
		comment_dict[comment] = []
		[comment_dict[comment].append(reply) for reply in replies if reply.parent_id == comment.key().id()]
	return comment_dict

def get_comment_count_for_comment_dict(comment_dict):
	count = 0
	for key in comment_dict:
		count = count + 1 + len(comment_dict[key])
	return count

def get_comment_count_for_item(item):
	comment_dict = get_top_level_comment_dict(item)
	return get_comment_count_for_comment_dict(comment_dict)

def get_karma_for_user(user):
	if user:
		karma = memcache.get("karma_%d" % user['id'])
		if not karma:
			karma_count = 0
			this_user_posts = models.Post.all().filter("author =", db.Key(user['key']))
			for post in this_user_posts:
				karma_count += len(post.upvotes) - len(post.downvotes) - 1 
			this_user_comments = models.Comment.all().filter("author =", db.Key(user['key']))
			for comment in this_user_comments:
				karma_count += len(comment.upvotes) - len(comment.downvotes) - 1
			memcache.add(key="karma_%d" % user['id'], value=karma_count)
			karma = karma_count
		print karma
		return karma
	else:
		return None