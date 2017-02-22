from models import *
from helpers import user_owns_comment
from helpers import user_logged_in
from helpers import post_exists
from helpers import comment_exists


class AddCommentPage(Handler):

    def get(self, post_id):

        post_exists(post_id)

        user_cookie = self.request.cookies.get('user')
        if user_cookie:
            if user_logged_in(user_cookie):
                self.render("add-comment.html", post_id=post_id,
                            user_cookie=user_cookie)
            else:
                self.redirect('/signup')
        else:
            self.redirect('/signup')

    def post(self, post_id):

        post_exists(post_id)

        comment = self.request.get("comment")
        user_cookie = self.request.cookies.get('user')
        user_id_cookie = user_cookie.split('|')[0]
        if user_logged_in(user_cookie):
            if comment:
                c = Comment(comment=comment, post_id=int(post_id),
                            user_id=int(user_id_cookie))
                c.put()
                time.sleep(0.5)
                self.redirect("/post/%d" % int(post_id))
            else:
                error = "We need a comment!"
                self.render("comment.html", comment=comment, error=error,
                            user_cookie=user_cookie)
        else:
            self.redirect('/')


class EditCommentPage(Handler):

    def get(self, comment_id):

        comment_exists(comment_id)

        user_cookie = self.request.cookies.get('user')
        if user_cookie:
            user_id_cookie = user_cookie.split('|')[0]
            if user_logged_in(user_cookie):
                if user_owns_comment(comment_id, user_id_cookie):
                    self.render(
                        "edit-comment.html",
                        comments=[
                            user_owns_comment(
                                comment_id,
                                user_id_cookie)],
                        user_cookie=user_cookie)
                else:
                    self.redirect("/")
            else:
                self.redirect('/')
        else:
            self.redirect('/')

    def post(self, comment_id):

        comment_exists(comment_id)

        user_cookie = self.request.cookies.get('user')
        comment = self.request.get("comment")
        post_id = self.request.get("post_id")
        if user_logged_in(user_cookie):
            if comment:
                c = Comment.get_by_id(int(comment_id))
                c.comment = comment
                c.put()
                time.sleep(0.5)
                self.redirect("/post/%d" % int(post_id))
            else:
                error = "We need the comment"
                self.render("edit-comment.html", comment=comment,
                            user_cookie=user_cookie,
                            error=error)
        else:
            self.redirect('/')


class DeleteCommentPage(Handler):

    def get(self, comment_id):

        comment_exists(comment_id)

        user_cookie = self.request.cookies.get('user')
        user_id_cookie = user_cookie.split('|')[0]
        if user_logged_in(user_cookie):
            if user_owns_comment(comment_id, user_id_cookie):
                self.render(
                    "delete-comment.html",
                    comments=[
                        user_owns_comment(
                            comment_id,
                            user_id_cookie)],
                    user_cookie=user_cookie)
            else:
                self.redirect("/")
        else:
            self.redirect("/")

    def post(self, comment_id):

        comment_exists(comment_id)

        user_cookie = self.request.cookies.get('user')
        if user_logged_in(user_cookie):
            post_id = self.request.get("post_id")
            self.delete_comment(comment_id)
            time.sleep(0.5)
            self.redirect("/post/%d" % int(post_id))
        else:
            self.redirect('/')

    def delete_comment(self, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        comment.delete()
