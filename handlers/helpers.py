from models import *


def comment_exists(comment_id):
    key = db.Key.from_path('Comment', int(comment_id))
    comment = db.get(key)
    if not comment:
        return self.redirect('/')
    else:
        return comment


def post_exists(post_id):
    key = db.Key.from_path('Post', int(post_id))
    post = db.get(key)
    if not post:
        return self.redirect('/')
    else:
        return post


def user_logged_in(user_cookie):
    user_id_cookie = user_cookie.split('|')[0]
    user_hash_cookie = user_cookie.split('|')[1]
    db_user_id = User.get_by_id(int(user_id_cookie))
    if db_user_id:
        if user_hash_cookie == db_user_id.password:
            return True
        else:
            return False
    else:
        return False


def user_owns_post(post_id, user_id_cookie):
    post = Post.get_by_id(int(post_id))
    user_id_from_post = post.user_id
    if user_id_from_post == int(user_id_cookie):
        return True
    else:
        return False


def user_owns_comment(comment_id, user_id_cookie):
    comment = Comment.get_by_id(int(comment_id))
    user_id_from_comment = comment.user_id
    if user_id_from_comment == int(user_id_cookie):
        return comment
    else:
        return False


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
