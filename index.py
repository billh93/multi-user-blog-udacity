import os
import re
import hashlib
import time
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
	last_modified = db.DateTimeProperty(auto_now=True)


class Like(db.Model):
	user_id = db.IntegerProperty(required=True)
	post_id = db.IntegerProperty(required=True)
	
	
class Comment(db.Model):
	user_id = db.IntegerProperty(required=True)
	post_id = db.IntegerProperty(required=True)
	comment = db.TextProperty()
	created = db.DateTimeProperty(auto_now_add=True)
	last_modified = db.DateTimeProperty(auto_now=True)
	

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
	
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))


class EditPostPage(Handler):
	def get(self, posts_id):
		user_cookie = self.request.cookies.get('user')
		if user_cookie:
			user_id_cookie = user_cookie.split('|')[0]
			user_hash_cookie = user_cookie.split('|')[1]
			db_user_id = User.get_by_id(int(user_id_cookie))
			if db_user_id:
				if user_hash_cookie == db_user_id.password:
					post = Post.get_by_id(int(posts_id))
					user_id_from_post = post.user_id
					if user_id_from_post == int(user_id_cookie):
						if post:
							self.render("edit-post.html", posts=[post])
						else:
							self.redirect("/")
					else:
						self.redirect('/')
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
			self.render("edit-post.html", subject=subject,
			            content=content,
			            error=error)


class AddPostPage(Handler):
	def get(self):
		user_cookie = self.request.cookies.get('user')
		if user_cookie:
			user_id_cookie = user_cookie.split('|')[0]
			user_hash_cookie = user_cookie.split('|')[1]
			db_user_id = User.get_by_id(int(user_id_cookie))
			if db_user_id:
				if user_hash_cookie == db_user_id.password:
					self.render("new-post.html")
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
			self.render("new-post.html", subject=subject,
			            content=content,
			            error=error)
		

class AddCommentPage(Handler):
	def get(self, post_id):
		user_cookie = self.request.cookies.get('user')
		if user_cookie:
			user_id_cookie = user_cookie.split('|')[0]
			user_hash_cookie = user_cookie.split('|')[1]
			db_user_id = User.get_by_id(int(user_id_cookie))
			if db_user_id:
				if user_hash_cookie == db_user_id.password:
					self.render("add-comment.html", post_id=post_id)
				else:
					self.redirect('/signup')
			else:
				self.redirect('/signup')
		else:
			self.redirect('/signup')
		
	def post(self, post_id):
		comment = self.request.get("comment")
		user_cookie = self.request.cookies.get('user')
		user_id_cookie = user_cookie.split('|')[0]
		if comment:
			c = Comment(comment=comment, post_id=int(post_id),
			            user_id=int(user_id_cookie))
			c.put()
			time.sleep(0.5)
			self.redirect("/post/%d" % int(post_id))
		else:
			error = "We need a comment!"
			self.render("comment.html", comment=comment, error=error)
		
		
class EditCommentPage(Handler):
	def get(self, comment_id):
		user_cookie = self.request.cookies.get('user')
		if user_cookie:
			user_id_cookie = user_cookie.split('|')[0]
			user_hash_cookie = user_cookie.split('|')[1]
			db_user_id = User.get_by_id(int(user_id_cookie))
			if db_user_id:
				if user_hash_cookie == db_user_id.password:
					comment = Comment.get_by_id(int(comment_id))
					user_id_from_comment = comment.user_id
					if user_id_from_comment == int(user_id_cookie):
						if comment:
							self.render("edit-comment.html", comments=[comment])
						else:
							self.redirect("/")
					else:
						self.redirect('/')
				else:
					self.redirect('/')
			else:
				self.redirect('/')
		else:
			self.redirect('/')
	
	def post(self, comment_id):
		comment = self.request.get("comment")
		post_id = self.request.get("post_id")
		if comment:
			c = Comment.get_by_id(int(comment_id))
			c.comment = comment
			c.put()
			time.sleep(0.5)
			self.redirect("/post/%d" % int(post_id))
		else:
			error = "We need the comment"
			self.render("edit-comment.html", comment=comment,
			            error=error)


class LikePostHandler(Handler):
	def get(self, post_id):
		user_cookie = self.request.cookies.get('user')
		if user_cookie:
			user_id_cookie = user_cookie.split('|')[0]
			check_like = db.GqlQuery("SELECT * FROM Like WHERE "
			                         "user_id = :1 AND post_id = :2",
			                         int(user_id_cookie), int(post_id))
			can_user_like = Post.get_by_id(int(post_id))
			if int(user_id_cookie) == can_user_like.user_id:
				self.write("Sorry, you can't like your own post.")
			else:
				if check_like.count():
					if int(user_id_cookie) == check_like.get().user_id:
						users_like = check_like[0]
						users_like.delete()
						time.sleep(0.5)
						self.redirect("/post/%d" % int(post_id))
				else:
					l = Like(user_id=int(user_id_cookie), post_id=int(post_id))
					l.put()
					time.sleep(0.5)
					self.redirect("/post/%d" % int(post_id))
		else:
			self.redirect("/login")


class DeleteCommentPage(Handler):
	def get(self, comment_id):
		user_cookie = self.request.cookies.get('user')
		user_id_cookie = user_cookie.split('|')[0]
		comment = Comment.get_by_id(int(comment_id))
		if int(user_id_cookie) == comment.user_id:
			self.render("delete-comment.html", comments=[comment])
		else:
			self.redirect("/")
		
	def post(self, comment_id):
		post_id = self.request.get("post_id")
		comment = Comment.get_by_id(int(comment_id))
		comment.delete()
		time.sleep(0.5)
		self.redirect("/post/%d" % int(post_id))
			
		
class PostPage(Handler):
	def get(self, post_id):
		user_cookie = self.request.cookies.get('user')
		post = Post.get_by_id(int(post_id))
		user_id_from_post = post.user_id
		if post:
			if user_cookie:
				user_id_cookie = user_cookie.split('|')[0]
				if user_id_from_post == int(user_id_cookie):
					user_owns_post = True
				else:
					user_owns_post = False
			else:
				user_owns_post = False
				user_id_cookie = False
			
			check_like = db.GqlQuery("SELECT * FROM Like WHERE "
			                         "user_id = :1 AND post_id = :2",
			                         int(user_id_cookie), int(post_id))
			if check_like.count():
				if_user_liked = True
			else:
				if_user_liked = False
			
			comment = db.Query(Comment).filter('post_id =', int(post_id)).order(
				'-created')
			
			self.render("post.html", posts=[post], user_owns_post=user_owns_post,
			            comments=comment, user_id_cookie=int(user_id_cookie),
			            if_user_liked=if_user_liked)
		else:
			self.redirect("/")
			
	def post(self, post_id):
		post = Post.get_by_id(int(post_id))
		post.delete()
		time.sleep(0.5)
		self.redirect("/")
		
		
class MainPage(Handler):
	def render_front(self):
		user_cookie = self.request.cookies.get('user')
		posts = Post.all().order('-created')
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
                               ('/new-post', AddPostPage),
                               ('/edit-post/(\d+)', EditPostPage),
                               ('/post/(\d+)', PostPage),
                               ('/add-comment/(\d+)', AddCommentPage),
                               ('/edit-comment/(\d+)', EditCommentPage),
                               ('/delete-comment/(\d+)', DeleteCommentPage),
                               ('/like-post/(\d+)', LikePostHandler)],
                              debug=True)
