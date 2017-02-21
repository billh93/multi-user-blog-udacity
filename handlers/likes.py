from models import *


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
