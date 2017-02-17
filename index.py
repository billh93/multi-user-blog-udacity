import os
import re
import hashlib
import logging
from random import choice
from string import ascii_lowercase

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)


def make_salt():
	return ''.join(choice(ascii_lowercase) for i in range(5))


def make_pw_hash(name, pw, salt=None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s|%s' % (h, salt)


def valid_pw(name, pw, h):
	salt = h.split('|')[1]
	return h == make_pw_hash(name, pw, salt)


def valid_username(username):
	user_re = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
	return username and user_re.match(username)


def valid_password(password):
	pass_re = re.compile(r"^.{3,20}$")
	return password and pass_re.match(password)


def valid_email(email):
	email_re = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
	return not email or email_re.match(email)


class User(db.Model):
	username = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	salt = db.StringProperty(required=True)
	email = db.StringProperty()
	

class Post(db.Model):
	subject = db.StringProperty(required=True)
	content = db.TextProperty(required=True)
	user_id = db.IntegerProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)

""" Join Query:
SELECT link.* FROM link,user WHERE link.user_id = user.id
AND username = 'spez'
"""


class Likes(db.Model):
	# If user likes a post, it will create a entity if it's not in the db
	# If there is a post in db and user unlikes it delete
	# entity by using the user_id and post_id
	user_id = db.IntegerProperty(required=True)
	post_id = db.IntegerProperty(required=True)
	
	
class Comments(db.Model):
	user_id = db.IntegerProperty(required=True)
	post_id = db.IntegerProperty(required=True)
	comment = db.TextProperty()
	

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
	
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))


class EditPage(Handler):
	def get(self, posts_id):
		user_cookie = self.request.cookies.get('user')
		if user_cookie:
			user_id_cookie = user_cookie.split('|')[0]
			user_hash_cookie = user_cookie.split('|')[1]
			db_user_id = User.get_by_id(int(user_id_cookie))
			
			if db_user_id:
				if user_hash_cookie == db_user_id.password:
					post = Post.get_by_id(int(posts_id))
					if post:
						self.render("editpost.html", posts=[post])
					else:
						self.redirect("/")
				else:
					self.redirect('/signup')
			else:
				self.redirect('/signup')
		else:
			self.redirect('/signup')
	
	def post(self, posts_id):
		subject = self.request.get("subject")
		content = self.request.get("content")
		
		if subject and content:
			p = Post.get_by_id(int(posts_id))
			p.subject = subject
			p.content = content
			p = p.put()
			
			self.redirect("/post/%d" % p.id())
		else:
			error = "We need the subject and some content!"
			self.render("editpost.html", subject=subject,
			            content=content,
			            error=error)


class FormPage(Handler):
	def get(self):
		user_cookie = self.request.cookies.get('user')
		if user_cookie:
			user_id_cookie = user_cookie.split('|')[0]
			user_hash_cookie = user_cookie.split('|')[1]
			db_user_id = User.get_by_id(int(user_id_cookie))
			
			if db_user_id:
				if user_hash_cookie == db_user_id.password:
					self.render("newpost.html")
				else:
					self.redirect('/signup')
			else:
				self.redirect('/signup')
		else:
			self.redirect('/signup')

	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")
		user_cookie = self.request.cookies.get('user')
		user_id_cookie = user_cookie.split('|')[0]
		
		if subject and content:
			p = Post(subject=subject, content=content,
			         user_id=int(user_id_cookie))
			p = p.put()
			
			self.redirect("/post/%d" % p.id())
		else:
			error = "We need the subject and some content!"
			self.render("newpost.html", subject=subject,
			            content=content,
			            error=error)
		
		
class PostPage(Handler):
	def get(self, posts_id):
		post = Post.get_by_id(int(posts_id))
		if post:
			self.render("post.html", posts=[post])
		else:
			self.redirect("/")

		
class MainPage(Handler):
	def render_front(self):
		user_cookie = self.request.cookies.get('user')
		posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
		self.render("front.html", posts=posts, user_cookie=user_cookie)
	
	def get(self):
		self.render_front()


class WelcomeHandler(Handler):
	def get(self):
		user_cookie = self.request.cookies.get('user')
		if user_cookie:
			user_id_cookie = user_cookie.split('|')[0]
			user_hash_cookie = user_cookie.split('|')[1]
			db_user_id = User.get_by_id(int(user_id_cookie))
			
			if db_user_id:
				if user_hash_cookie == db_user_id.password:
					self.render("welcome.html", username=db_user_id.username)
				else:
					self.redirect('/signup')
			else:
				self.redirect('/signup')
		else:
			self.redirect('/signup')


class SignupHandler(Handler):
	def get(self):
		user_cookie = self.request.cookies.get('user')
		if user_cookie:
			user_id_cookie = user_cookie.split('|')[0]
			user_hash_cookie = user_cookie.split('|')[1]
			db_user_id = User.get_by_id(int(user_id_cookie))
			
			if db_user_id:
				if user_hash_cookie == db_user_id.password:
					self.redirect("/")
				else:
					self.redirect('/')
			else:
				self.redirect('/')
		else:
			self.render('signup.html')
	
	def post(self):
		have_error = False
		username = self.request.get('username')
		password = self.request.get('password')
		verify = self.request.get('verify')
		email = self.request.get('email')
		
		params = dict(username=username, email=email)
		
		if not valid_username(username):
			params['username_error'] = "That's not a valid username."
			have_error = True
		
		if not valid_password(password):
			params['password_error'] = "That wasn't a valid password."
			have_error = True
		elif password != verify:
			params['verify_error'] = "Your passwords didn't match."
			have_error = True
		
		if not valid_email(email):
			params['email_error'] = "That's not a valid email."
			have_error = True
		
		if have_error:
			self.render('signup.html', **params)
		else:
			check_user = db.GqlQuery("SELECT * FROM User WHERE username='" +
			                         username + "'")
			if check_user.count():
				if username == check_user.get().username:
					params[
						'username_exists_error'] = "Username already exists."
					self.render('signup.html', **params)
			else:
				h = make_pw_hash(username, password)
				user_hash = h.split('|')[0]
				user_salt = h.split('|')[1]
				
				user = User(username=username, password=user_hash,
				            salt=user_salt, email=email)
				user.put()
				
				user_id = user.key().id()
				
				user_info = "%s|%s" % (user_id, user_hash)
				
				self.response.headers['Content-Type'] = 'text/plain'
				self.response.headers.add_header('Set-Cookie',
				                                 'user=%s;Path=/' % user_info)
				self.redirect("/welcome")


class LoginHandler(Handler):
	def get(self):
		user_cookie = self.request.cookies.get('user')
		if user_cookie:
			user_id_cookie = user_cookie.split('|')[0]
			user_hash_cookie = user_cookie.split('|')[1]
			db_user_id = User.get_by_id(int(user_id_cookie))
			
			if db_user_id:
				if user_hash_cookie == db_user_id.password:
					self.redirect("/")
				else:
					self.redirect('/')
			else:
				self.redirect('/')
		else:
			self.render("login.html", error="", username="", password="")
	
	def post(self):
		have_error = False
		username = self.request.get("username")
		password = self.request.get("password")
		params = dict(username=username)
		
		if not valid_username(username):
			params['username_error'] = "That's not a valid username."
			have_error = True
		
		if not valid_password(password):
			params['password_error'] = "That wasn't a valid password."
			have_error = True
		if have_error:
			self.render('signup.html', **params)
		else:
			check_user = db.GqlQuery("SELECT * FROM User WHERE username='" +
			                         username + "'")
			if check_user.count():
				db_user_id = check_user.get().key().id_or_name()
				db_password = check_user.get().password
				db_salt = check_user.get().salt
				db_password_and_salt = db_password + "|" + db_salt
				if db_password_and_salt == make_pw_hash(username, password,
				                                        db_salt):
					user_info = "%s|%s" % (db_user_id, db_password)
					
					self.response.headers['Content-Type'] = 'text/plain'
					self.response.headers.add_header('Set-Cookie',
					                                 'user=%s;Path=/' % str(
						                                 user_info))
					self.redirect("/welcome")
				else:
					params['incorrect_password'] = "Incorrect Password."
					self.render('signup.html', **params)
			else:
				params['user_not_found'] = "User not found."
				self.render('login.html', **params)


class LogoutHandler(Handler):
	def get(self):
		user_cookie = self.request.cookies.get('user')
		if user_cookie:
			user_id_cookie = user_cookie.split('|')[0]
			user_hash_cookie = user_cookie.split('|')[1]
			db_user_id = User.get_by_id(int(user_id_cookie))
			
			if db_user_id:
				if user_hash_cookie == db_user_id.password:
					self.response.headers.add_header('Set-Cookie',
					                                 'user=;Path=/;expires=-10')
					self.redirect('/')
				else:
					self.redirect('/')
			else:
				self.redirect('/')
		else:
			self.redirect("/")


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/signup', SignupHandler),
                               ('/login', LoginHandler),
                               ('/welcome', WelcomeHandler),
                               ('/logout', LogoutHandler),
                               ('/newpost', FormPage),
                               ('/editpost/(\d+)', EditPage),
                               ('/post/(\d+)', PostPage)], debug=True)
