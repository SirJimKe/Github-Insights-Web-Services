from flask import Flask, render_template, request, redirect, url_for, session
from flask_oauthlib.client import OAuth
from dotenv import load_dotenv
import os
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

oauth = OAuth(app)

github = oauth.remote_app(
    'github',
    consumer_key=os.environ.get('GITHUB_CLIENT_ID'),
    consumer_secret=os.environ.get('GITHUB_CLIENT_SECRET'),
    request_token_params={'scope': 'user'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

@app.route('/')
def index():
    return 'Welcome to the Github User Info App!'

@app.route('/login')
def login():
    return github.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('github_token', None)
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    response = github.authorized_response()

    if response is None or response.get('access_token') is None:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )

    session['github_token'] = (response['access_token'], '')
    return redirect(url_for('index'))

@github.tokengetter
def get_github_auth_token():
    return session.get('github_token')

@app.route('/user')
def get_authenticated_user():
    access_token = session.get('github_token')

    if access_token is None:
        return 'Error: GitHub access token not found. Please log in.'

    headers = {'Authorization': f'token {access_token[0]}'}
    api_url = 'https://api.github.com/user'
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        return render_template('user_profile.html', user_data=user_data)
    else:
        return f'Error: Unable to fetch user data from GitHub API. Status code: {response.status_code}'

@app.route('/user/<username>')
def get_user(username):
    access_token = session.get('github_token')

    if access_token is None:
        return 'Error: GitHub access token not found. Please log in.'

    headers = {'Authorization': f'token {access_token[0]}'}
    api_url = f'https://api.github.com/users/{username}'

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        user_data = response.json()

        name = user_data.get('name', 'N/A')
        bio = user_data.get('bio', 'N/A')
        followers = user_data.get('followers', 'N/A')
        following = user_data.get('following', 'N/A')

        return render_template('user_data.html',
                               username=username,
                               name=name,
                               bio=bio,
                               followers=followers,
                               following=following)
    elif response.status_code == 404:
        return f'User "{username}" not found on GitHub.'
    else:
        return f'Error: Unable to fetch data from GitHub API. Status code: {response.status_code}'

@app.route('/user/<username>/repositories')
def get_user_repositories(username):
    access_token = session.get('github_token')

    if access_token is None:
        return 'Error: GitHub access token not found. Please log in.'

    headers = {'Authorization': f'token {access_token[0]}'}
    repos_api_url = f'https://api.github.com/users/{username}/repos'

    response = requests.get(repos_api_url, headers=headers)
    if response.status_code == 200:
        repositories = response.json()

        return render_template('user_repositories.html',
                               username=username,
                               repositories=repositories)
    else:
        return f'Error: Unable to fetch repositories from GitHub API. Status code: {response.status_code}'

if __name__ == '__main__':
    app.run(debug=True)
