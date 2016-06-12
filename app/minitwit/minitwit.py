# -*- coding: utf-8 -*-
"""
    MiniTwit
    ~~~~~~~~

    A microblogging application written with Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import time
import psycopg2
import psycopg2.extensions
import hvac
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
    render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash
from werkzeug.exceptions import BadRequest

# configuration
DB_DATABASE = 'postgres'
DB_HOST = 'app_db_1'
DB_PORT = 5432

PER_PAGE = 30
DEBUG = True

SECRET_KEY = 'development key'

VAULT_HOST = 'http://178.33.83.162'
VAULT_PORT = 8200
VAULT_CRED_URL = 'postgresql/creds/rw'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('MINITWIT_SETTINGS', silent=True)

USERNAME = 'username'
EMAIL = 'email'
PW_HASH = 'pw_hash'
ID = 'user_id'


def set_up_vault_client(token: str) -> hvac.Client:
    client = hvac.Client(url='{}:{}'.format(VAULT_HOST, VAULT_PORT))
    client.token = token
    if not client.is_authenticated():
        raise BadRequest(description="Could not set up the vault, maybe the token is invalid ?")
    return client


def get_creds_from_vault() -> (str, str):
    top = _app_ctx_stack.top
    if not hasattr(top, 'vault_client'):
        raise BadRequest(description="The server has not been initialized yet")
    raw_creds = top.vault_client.read(VAULT_CRED_URL)
    return raw_creds['username'], raw_creds['password']


def create_db_client() -> psycopg2.extensions.connection:
    db_client = None
    username, password = get_creds_from_vault()
    while not db_client:
        try:
            db_client = psycopg2.connect(host=app.config['HOST'], database=app.config['DATABASE'],
                                         user=username, password=password, port=app.config['PORT'])
        except psycopg2.OperationalError as e:
            app.logger.error('Could not connect to the db {} on host {}:{} : {}'.format(app.config['DATABASE'],
                                                                                        app.config['HOST'],
                                                                                        app.config['PORT'],
                                                                                        str(e)))
            time.sleep(1)
    return db_client


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    top = _app_ctx_stack.top
    if not hasattr(top, 'postgre_db'):
        top.postgre_db = create_db_client()
    elif top.postgre_db.closed:
        top.postgre_db.close()
        top.postgre_db = create_db_client()
    return top.postgre_db


@app.teardown_appcontext
def close_database(exception):
    """Closes the database again at the end of the request."""
    top = _app_ctx_stack.top
    if hasattr(top, 'postgre_db'):
        top.postgre_db.close()


def init_db():
    """Initializes the database."""
    with get_db() as db:
        with db.cursor() as cur:
            with app.open_resource('schema.sql', mode='r') as f:
                cur.execute(f.read())


def initdb_command():
    """Creates the database tables."""
    init_db()
    app.logger.info('Initialized the database.')


def query_db(query, args=(), one=False):
    """Queries the database and returns a list of dictionaries."""
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute(query, args)
            rv = cur.fetchall()
            fields = [desc[0] for desc in cur.description]

    return ({colname: val for colname, val in zip(fields, rv[0])} if rv else None) if one else [
        {colname: val for colname, val in zip(fields, vals)} for vals in rv]


def get_user_id(username):
    """Convenience method to look up the id for a username."""
    rv = query_db('SELECT user_id FROM twituser WHERE username = (%s)',
                  [username], one=True)
    return rv['user_id'] if rv else None


def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')


def gravatar_url(email, size=80):
    """Return the gravatar image for the given email address."""
    return 'http://www.gravatar.com/avatar/%s?d=identicon&s=%d' % \
           (md5(email.strip().lower().encode('utf-8')).hexdigest(), size)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = query_db('SELECT * FROM twituser WHERE user_id = (%s)',
                          [session['user_id']], one=True)


@app.route('/init', methods=['POST'])
def init():
    """
    Initialize everything, once vault is good. The token is sent through here
    """
    json = request.get_json(force=True)
    if not json or not json['token']:
        app.logger.error('No token was provided for initialization')
    _app_ctx_stack.top.vault_client = set_up_vault_client(json['token'])
    initdb_command()


@app.route('/')
def timeline():
    """Shows a users timeline or if no user is logged in it will
    redirect to the public timeline.  This timeline shows the user's
    messages as well as all the messages of followed users.
    """
    if not g.user:
        return redirect(url_for('public_timeline'))
    return render_template('timeline.html', messages=query_db('''
        SELECT message.*, twituser.* FROM message, twituser
        WHERE message.author_id = twituser.user_id AND (
            twituser.user_id = (%s) OR
            twituser.user_id IN (SELECT whom_id FROM follower
                                    WHERE who_id = (%s)))
        ORDER BY MESSAGE.pub_date DESC LIMIT (%s)''', [session['user_id'], session['user_id'], PER_PAGE]))


@app.route('/public')
def public_timeline():
    """Displays the latest messages of all users."""
    return render_template('timeline.html', messages=query_db('''
        SELECT message.*, twituser.* FROM message, twituser
        WHERE message.author_id = twituser.user_id
        ORDER BY message.pub_date DESC LIMIT (%s)''', [PER_PAGE]))


@app.route('/<username>')
def user_timeline(username):
    """Display's a users tweets."""
    profile_user = query_db('SELECT * FROM twituser WHERE username = (%s)',
                            [username], one=True)
    if profile_user is None:
        abort(404)
    followed = False
    if g.user:
        followed = query_db('''SELECT 1 FROM follower WHERE
            follower.who_id = (%s) AND follower.whom_id = (%s)''',
                            [session['user_id'], profile_user[ID]],
                            one=True) is not None
    return render_template('timeline.html',
                           messages=query_db('''
                                SELECT message.*, twituser.* FROM message, twituser WHERE
                                twituser.user_id = message.author_id AND twituser.user_id = (%s)
                                ORDER BY message.pub_date DESC LIMIT (%s)''',
                                             [profile_user[ID], PER_PAGE]),
                           followed=followed, profile_user=profile_user)


@app.route('/<username>/follow')
def follow_user(username):
    """Adds the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute('INSERT INTO follower (who_id, whom_id) VALUES ((%s), (%s))',
                        [session['user_id'], whom_id])
    flash('You are now following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/<username>/unfollow')
def unfollow_user(username):
    """Removes the current user as follower of the given user."""
    if not g.user:
        abort(401)
    whom_id = get_user_id(username)
    if whom_id is None:
        abort(404)
    with get_db() as db:
        with db.cursor() as cur:
            cur.execute('DELETE FROM follower WHERE who_id=(%s) AND whom_id=(%s)',
                        [session['user_id'], whom_id])
    flash('You are no longer following "%s"' % username)
    return redirect(url_for('user_timeline', username=username))


@app.route('/add_message', methods=['POST'])
def add_message():
    """Registers a new message for the user."""
    if 'user_id' not in session:
        abort(401)
    if request.form['text']:
        with get_db() as db:
            with db.cursor() as cur:
                cur.execute('''INSERT INTO message (author_id, text, pub_date)
                  VALUES ((%s), (%s), (%s))''', (session['user_id'], request.form['text'],
                                                 int(time.time())))
    flash('Your message was recorded')
    return redirect(url_for('timeline'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Logs the user in."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        user = query_db('''SELECT * FROM twituser WHERE
            username = (%s)''', [request.form['username']], one=True)
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user[PW_HASH],
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in')
            session['user_id'] = user[ID]
            return redirect(url_for('timeline'))
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                        '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            with get_db() as db:
                with db.cursor() as cur:
                    cur.execute('''INSERT INTO twituser (
                      username, email, pw_hash) VALUES ((%s), (%s), (%s))''',
                                [request.form['username'], request.form['email'],
                                 generate_password_hash(request.form['password'])])
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    """Logs the user out."""
    flash('You were logged out')
    session.pop('user_id', None)
    return redirect(url_for('public_timeline'))


# add some filters to jinja
app.jinja_env.filters['datetimeformat'] = format_datetime
app.jinja_env.filters['gravatar'] = gravatar_url

if __name__ == "__main__":
    app.run()
