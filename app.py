from flask import Flask, redirect, render_template, render_template_string, request, url_for

from Outh import DiscordOauth2Client, Unauthorized

app = Flask(__name__)
app.secret_key = b"random bytes representing flask secret key"
app.config['Client_ID'] = 651420362940088336
app.config['Client_Secret'] = '0-_AhUL6Y01qCnMpsp6GTdf0UCVxxCTu'
app.config['Scopes'] = ['identify', 'guilds']
app.config['Redirect_Url'] = 'https://localhost:5000/'
app.config['Bot_Token'] = None

client = DiscordOauth2Client(app)


@app.route('/')
def index():
    try:
        return render_template("html/index.html", logined=request.args.get('logged_in'), user_name=client.fetch_user().name)
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
    return redirect(url_for('index', logged_in=True))


@app.route('/me')
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
def logged_in():
    return render_template("html/loggedin.html", name=client.fetch_user().name)


if __name__ == '__main__':
    app.run()
