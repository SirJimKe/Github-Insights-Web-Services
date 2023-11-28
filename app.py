from flask import Flask, render_template, request
import requests

app = Flask(__name__)

access_token = 'use_ your github_token'
headers = {'Authorization': f'token {access_token}'}

@app.route('/')
def index():
    return 'Welcome to the Github User Info App!'


@app.route('/user/<username>')
def get_user(username):
    """Gets users data"""

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
        return f'User "{username}" not found on Github.'
    else:
        return f'Error: Unable to fetch data from GitHub API. Status code: {response.status_code}'


@app.route('/user/<username>/repositories')
def get_user_repositories(username):
    repos_api_url = f'https://api.github.com/users/{username}/repos'

    response = requests.get(repos_api_url, headers=headers)
    if response.status_code == 200:
        repositories = response.json()

        return render_template('user_repositories.html',
                               username=username,
                               repositories=repositories)
    else:
        return f'Error: Unable to fetch repositories from GitHub API. Status code: {repos_response.status_code}'


if __name__ == '__main__':
    app.run(debug=True)
