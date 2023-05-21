from flask import Response
from flask.views import MethodView

from reservation_system import db


class Logout(MethodView):
    def post(self):
        """Logout
        ---
        summary: Logout
        description: Clears the JWT access token cookie.
        tags:
          - Auth
        responses:
          200:
            description: OK
        """
        resp = Response()
        resp.set_cookie('access_token', '', expires=0)
        return resp
