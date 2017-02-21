from models import *
from handlers.helpers import *
from handlers.users import *
from handlers.posts import *
from handlers.comments import *
from handlers.likes import *

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
