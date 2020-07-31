import os

from flask import Flask, redirect, render_template, render_template_string, request, url_for

from Outh import DiscordOauth2Client, Unauthorized

app = Flask(__name__)
app.secret_key = b"random bytes representing flask secret key"
app.config['DISCORD_CLIENT_ID'] = 651420362940088336
app.config['DISCORD_CLIENT_SECRET'] = '0-_AhUL6Y01qCnMpsp6GTdf0UCVxxCTu'
app.config['SCOPES'] = ['identify', 'guilds']
app.config['DISCORD_REDIRECT_URI'] = os.getenv('REDIRECT_URL') or 'http://127.0.0.1:5000/callback'
app.config['DISCORD_BOT_TOKEN'] = None

client = DiscordOauth2Client(app)


@app.route('/')
def index():
    # print(session)
    try:
        return render_template("html/index.html", logined='access_token', user_name=client.fetch_user().name)
    except Unauthorized:
        return render_template("html/index.html", logined=request.args.get('logged_in'))


@app.route('/login/', methods=['GET'])
def login():
    return client.create_session()


def return_guild_names_owner(guilds_):
    return list(sorted([fetch_guild.name for fetch_guild in guilds_ if fetch_guild.is_owner_of_guild()]))


def search_guilds_for_name(guilds_, query):
    # print(list(sorted([fetch_guild.name for fetch_guild in guilds_ if fetch_guild.is_owner_of_guild() and fetch_guild.name == query])))
    return list(sorted([fetch_guild.name for fetch_guild in guilds_ if fetch_guild.is_owner_of_guild() and fetch_guild.name == query]))


@app.route('/guilds')
def guilds():
    if request.args.get('guild_name'):
        return render_template('html/guilds.html', guild_names=search_guilds_for_name(client.fetch_guilds(), request.args.get('guild_name')))
    return render_template('html/guilds.html', guild_names=return_guild_names_owner(client.fetch_guilds()))


@app.route('/callback')
def callback():
    client.callback()
    return redirect(url_for('index'))


@app.route('/me')
@client.is_logged_in
def me():
    user = client.fetch_user()
    image = user.avatar_url
    # noinspection HtmlUnknownTarget
    return render_template_string("""
        <html lang="en">
            <body>
                <p>Login Successful</p>
                <img src="{{ image_url }}" alt="Avatar url">
            </body>
        </html>
        """, image_url=image)


@app.route('/loggedin')
@client.is_logged_in
def logged_in():
    return render_template("html/loggedin.html", name=client.fetch_user().name)


@app.route('/logout', methods=['GET'])
@client.is_logged_in
def logout():
    client.logout()
    return redirect(url_for('index'))


@app.errorhandler(401)
def unauthorized_exception(error):
    print(error)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
