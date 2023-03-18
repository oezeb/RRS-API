import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from reservation_system.db import get_cnx, insert_users, get_user

from mysql.connector import Error, errorcode

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        user = dict(request.form)
        error = None

        if not user['username']:
            error = 'Username is required.'
        elif not user['password']:
            error = 'Password is required.'

        if error is None:
            user['password'] = generate_password_hash(user['password'])
            try:
                insert_users([user])
            except Error as err:
                print(err)
                if err.errno == errorcode.ER_DUP_ENTRY:
                    error = f"Username {user['username']} already exists" # msg
                else:
                    error = "Registration failed. Please try again later" # msg
            else:
                return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = get_user(username)

        if user is None or not check_password_hash(user['password'], password):
            error = 'Invalid username or password'

        if error is None:
            session.clear()
            session['username'] = user['username']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    username = session.get('username')

    if username is None: g.user = None
    else: g.user = get_user(username)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view