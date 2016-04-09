from django.core.cache import cache
from mongoAuthApp.cookiesUtils import delete_cookie

class Session():
    @staticmethod
    def do_login(user_id):
        id = str(user_id)
        logged_users = cache.get('logged')
        if not logged_users:
            logged_users = []
        try:
            logged_users.index(id)
        except ValueError:
            logged_users.append(id)
            cache.set('logged', logged_users)

    @staticmethod
    def do_logout(response,user_id):
        id = str(user_id)
        logged_users = cache.get('logged')
        if logged_users:
            logged_users.remove(id)
            cache.set('logged', logged_users)
            delete_cookie(response,user_id)

    @staticmethod
    def verify_current_session(user_id):
        id = str(user_id)
        logged_users = cache.get('logged')
        print "logged_users"
        print logged_users
        if logged_users:
            try:
                logged_users.index(id)
                user = {'isverify': True,'username': user_id}
                return user
            except:
                user = {'isverify': False,'username': ""}
                return user
        else:
            return {'isverify': False,'username': ""}