from models import *
from handlers.helpers import *
from handlers.users import *
from handlers.comments import *
from handlers.posts import *
from handlers.likes import *


class MainPage(Handler):

    def render_front(self):
        user_cookie = self.request.cookies.get('user')
        posts = Post.all().order('-created')
        self.render("front.html", posts=posts, user_cookie=user_cookie)

    def get(self):
        self.render_front()

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
