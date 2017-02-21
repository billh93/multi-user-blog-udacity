from models import *


class AddPostPage(Handler):

    def get(self):
        user_cookie = self.request.cookies.get('user')
        if user_cookie:
            user_id_cookie = user_cookie.split('|')[0]
            user_hash_cookie = user_cookie.split('|')[1]
            db_user_id = User.get_by_id(int(user_id_cookie))
            if db_user_id:
                if user_hash_cookie == db_user_id.password:
                    self.render("new-post.html", user_cookie=user_cookie)
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
                        content=content, user_cookie=user_cookie,
                        error=error)


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
                            self.render("edit-post.html", posts=[post],
                                        user_cookie=user_cookie)
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
        user_cookie = self.request.cookies.get('user')
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
                        content=content, user_cookie=user_cookie,
                        error=error)


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

            comment = db.Query(Comment).filter(
                'post_id =', int(post_id)).order('-created')

            self.render(
                "post.html",
                posts=[post],
                user_owns_post=user_owns_post,
                comments=comment,
                user_id_cookie=int(user_id_cookie),
                user_cookie=user_cookie,
                if_user_liked=if_user_liked)
        else:
            self.redirect("/")

    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        post.delete()
        time.sleep(0.5)
        self.redirect("/")
