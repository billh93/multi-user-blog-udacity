from models import *
from handlers.helpers import *


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
                    self.response.headers.add_header(
                        'Set-Cookie', 'user=;Path=/;expires=-10')
                    self.redirect('/')
                else:
                    self.redirect('/')
            else:
                self.redirect('/')
        else:
            self.redirect("/")
