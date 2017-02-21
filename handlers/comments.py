from models import *


class AddCommentPage(Handler):

    def get(self, post_id):
        user_cookie = self.request.cookies.get('user')
        if user_cookie:
            user_id_cookie = user_cookie.split('|')[0]
            user_hash_cookie = user_cookie.split('|')[1]
            db_user_id = User.get_by_id(int(user_id_cookie))
            if db_user_id:
                if user_hash_cookie == db_user_id.password:
                    self.render("add-comment.html", post_id=post_id,
                                user_cookie=user_cookie)
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
            self.render("comment.html", comment=comment, error=error,
                        user_cookie=user_cookie)


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
                            self.render(
                                "edit-comment.html", comments=[comment],
                                user_cookie=user_cookie)
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
        user_cookie = self.request.cookies.get('user')
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
                        user_cookie=user_cookie,
                        error=error)


class DeleteCommentPage(Handler):

    def get(self, comment_id):
        user_cookie = self.request.cookies.get('user')
        user_id_cookie = user_cookie.split('|')[0]
        comment = Comment.get_by_id(int(comment_id))
        if int(user_id_cookie) == comment.user_id:
            self.render("delete-comment.html", comments=[comment],
                        user_cookie=user_cookie)
        else:
            self.redirect("/")

    def post(self, comment_id):
        post_id = self.request.get("post_id")
        comment = Comment.get_by_id(int(comment_id))
        comment.delete()
        time.sleep(0.5)
        self.redirect("/post/%d" % int(post_id))
