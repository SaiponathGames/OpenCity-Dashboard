from flask import Flask, redirect, render_template, url_for

from Outh import DiscordOauth2Client

app = Flask(__name__)
app.secret_key = b"random bytes representing flask secret key"
app.config['Client_ID'] = 651420362940088336
app.config['Client_Secret'] = '0-_AhUL6Y01qCnMpsp6GTdf0UCVxxCTu'
app.config['Scopes'] = ['identify', 'guilds']
app.config['Redirect_Url'] = 'https://localhost:5000/'
app.config['Bot_Token'] = None

client = DiscordOauth2Client(app)


@app.route('/')
def hello_world():
    return render_template("html/index.html")


@app.route('/login/', methods=['GET'])
def login():
    return client.create_session()


@app.route('/guilds')
def guilds():
    return client.fetch_guilds()


@app.route('/callback')
def callback():
    client.callback()
    return redirect(url_for('me'))


@app.route('/me')
def me():
    user = client.fetch_user()
    image = user.avatar_url
    return f"""
    <html>
    <body>
    <img src="{image}">
    </body>
    </html>"""


@app.route('/loggedin')
def logged_in():
    return render_template("html/loggedin.html")


if __name__ == '__main__':
    app.run()
