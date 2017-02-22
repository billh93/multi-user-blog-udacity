from models import *
from helpers import user_owns_post
from helpers import user_logged_in
from helpers import post_exists


class AddPostPage(Handler):

    def get(self):
        user_cookie = self.request.cookies.get('user')
        if user_cookie:
            if user_logged_in(user_cookie):
                self.render("new-post.html", user_cookie=user_cookie)
            else:
                self.redirect('/signup')
        else:
            self.redirect('/signup')

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        user_cookie = self.request.cookies.get('user')

        if user_cookie:
            user_id_cookie = user_cookie.split('|')[0]
            if user_logged_in(user_cookie):
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
            else:
                self.redirect("/signup")
        else:
            self.redirect("/signup")


class EditPostPage(Handler):

    def get(self, post_id):

        post_exists(post_id)

        user_cookie = self.request.cookies.get('user')
        if user_cookie:
            user_id_cookie = user_cookie.split('|')[0]
            if user_logged_in(user_cookie):
                if user_owns_post(post_id, user_id_cookie):
                    self.render("edit-post.html", posts=[post_exists(post_id)],
                                user_cookie=user_cookie)
                else:
                    self.redirect('/')
            else:
                self.redirect('/')
        else:
            self.redirect('/signup')

    def post(self, post_id):

        post_exists(post_id)

        user_cookie = self.request.cookies.get('user')
        subject = self.request.get("subject")
        content = self.request.get("content")
        if user_cookie:
            if user_logged_in(user_cookie):
                if subject and content:
                    p = Post.get_by_id(int(post_id))
                    p.subject = subject
                    p.content = content
                    p = p.put()

                    self.redirect("/post/%d" % p.id())
                else:
                    error = "We need the subject and some content!"
                    self.render("edit-post.html", subject=subject,
                                content=content, user_cookie=user_cookie,
                                error=error)
            else:
                self.redirect('/')
        else:
            self.redirect("/signup")


class PostPage(Handler):

    def get(self, post_id):

        post_exists(post_id)

        user_cookie = self.request.cookies.get('user')

        if user_cookie:
            user_id_cookie = user_cookie.split('|')[0]
        else:
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
            posts=[post_exists(post_id)],
            user_owns_post=user_owns_post(post_id, user_id_cookie),
            comments=comment,
            user_id_cookie=int(user_id_cookie),
            user_cookie=user_cookie,
            if_user_liked=if_user_liked)

    def post(self, post_id):

        post_exists(post_id)

        user_cookie = self.request.cookies.get('user')

        if user_cookie:
            user_id_cookie = user_cookie.split('|')[0]
            if user_owns_post(post_id, user_id_cookie):
                self.delete_post(post_id)
                time.sleep(0.5)
                self.redirect("/")
            else:
                self.redirect("/")
        else:
            self.redirect("/")

    def delete_post(self, post_id):
        post = Post.get_by_id(int(post_id))
        post.delete()
