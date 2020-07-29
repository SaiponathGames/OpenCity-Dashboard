import requests
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template("html/index.html")


@app.route('/loggedin')
def logged_in():
    return render_template("html/loggedin.html")


API_ENDPOINT = 'https://discord.com/api/v7'
CLIENT_ID = '651420362940088336'
CLIENT_SECRET = '0-_AhUL6Y01qCnMpsp6GTdf0UCVxxCTu'
REDIRECT_URI = 'https://opencity-dashboard.herokuapp.com/loggedin'


def exchange_code(code):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'scope': 'identify guilds'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers)
    r.raise_for_status()
    return r.json()


if __name__ == '__main__':
    app.run()
