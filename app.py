from flask import Flask, session, redirect, request
from twitter_utils import get_request_token, get_oauth_verifier_url, get_access_token
from user import User
from database import Database

app = Flask(__name__)
app.secret_key = "#!@Hello_World77"

Database.initialize()


@app.route('/')
def homepage():
    return '<h1>Hello World</h1>'


@app.route('/twitter-login')
def twitter_login():
    request_token = get_request_token()
    session['request_token'] = request_token

    return redirect(get_oauth_verifier_url(request_token))


@app.route('/auth/twitter')
def twitter_auth():
    oauth_verifier = request.args.get('oauth_verifier')
    access_token = get_access_token(session['request_token'], oauth_verifier)
    print('access_token')
    user = User.load_data_by_screen_name(access_token['screen_name'])

    if not user:
        user = User(email='harshitsinghai77@gmail.com', fav_club='Chelsea', screen_name=access_token['screen_name'],
                    oauth_token=access_token['oauth_token'],
                    oauth_token_secret=access_token['oauth_token_secret'])
        user.save_to_db()

    session['screen_name'] = user.screen_name

    return user.screen_name


app.run()
