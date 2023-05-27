from flask import Blueprint, Response

bp = Blueprint('api_logout', __name__, url_prefix='/api/logout')

@bp.route('/', methods=['POST'])
def post():
    """Logout
    ---
    post:
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
