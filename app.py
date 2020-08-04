import os
import random
import string

from flask import Flask, redirect, render_template, render_template_string, request, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from Outh import DiscordOauth2Client, Unauthorized

__version__ = '0.7.0-alpha'
version = __version__

app = Flask(__name__)
app.secret_key = "".join([random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(1000)])
app.config['DISCORD_CLIENT_ID'] = 651420362940088336
app.config['DISCORD_CLIENT_SECRET'] = '0-_AhUL6Y01qCnMpsp6GTdf0UCVxxCTu'
app.config['SCOPES'] = ['identify', 'guilds']
app.config['DISCORD_REDIRECT_URI'] = os.getenv('REDIRECT_URL') or 'http://127.0.0.1:5000/callback'
app.config['DISCORD_BOT_TOKEN'] = None
app.config['CSRF_ENABLED'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5858/Flask-Database-for-Dashboard-Test'

# app.register_blueprint(admin.admin)

client = DiscordOauth2Client(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import Text_For_Indexes


# from admin import admin
# app.register_blueprint(admin.admin)


@app.route('/')
def index():
    # print(session)
    tfi_s = [Text_For_Indexes("Add to your server!",
                              "Hello there, I am OpenCityBot, I do levels, gatekeeper, reaction roles and much more, I have a custom leveling role set based leveling roles, which gives so much abilities to use our advanced leveling system. Please visit our docs for more info.",
                              "Add to your server."),
             Text_For_Indexes("Want to know more? See Features",
                              "I have so much of features running, if you check the features, you'll get your jaw-opened, as I am a high quality bot, you don't need other bots, I can manage everything. From Leveling to Fun commands, I can manage everything you want.",
                              "See features"),
             Text_For_Indexes("About my developers!",
                              """My developers made me a high quality bot, and also my developers made me OpenSource so you can see the code <a href="https://github.com/sairam4123/OpenCityBot-MovingJSON-PostGreSQL">here</a>.""",
                              "Learn more")]
    try:
        return render_template("html/index.html", texts=tfi_s, logined='access_token', user_name_1=client.fetch_user().name, avatar_url=client.fetch_user().avatar_url,
                               version_1=version)
    except Unauthorized:
        return render_template("html/index.html", texts=tfi_s, logined=request.args.get('logged_in'), version_1=version)


@app.route('/login/', methods=['GET'])
def login():
    return client.create_session()


def return_guild_names_owner(guilds_):
    return list(sorted([fetch_guild.name for fetch_guild in guilds_ if fetch_guild.is_owner_of_guild()]))


def search_guilds_for_name(guilds_, query):
    # print(list(sorted([fetch_guild.name for fetch_guild in guilds_ if fetch_guild.is_owner_of_guild() and fetch_guild.name == query])))
    return list(sorted([fetch_guild.name for fetch_guild in guilds_ if fetch_guild.is_owner_of_guild() and fetch_guild.name == query]))


@app.route('/guilds', methods=['GET', 'POST'])
@client.is_logged_in()
def guilds():
    if request.method == "POST":
        if guild_name := request.form['guild_name']:
            return render_template('html/guilds.html', guild_names=search_guilds_for_name(client.fetch_guilds(), guild_name), user_name_1=client.fetch_user().name,
                                   avatar_url=client.fetch_user().avatar_url, version_1=version)
        else:
            return render_template('html/guilds.html', guild_names=return_guild_names_owner(client.fetch_guilds()), user_name_1=client.fetch_user().name,
                                   avatar_url=client.fetch_user().avatar_url, version_1=version)
    return render_template('html/guilds.html', guild_names=return_guild_names_owner(client.fetch_guilds()), user_name_1=client.fetch_user().name,
                           avatar_url=client.fetch_user().avatar_url, version_1=version)


@app.route('/callback')
def callback():
    return client.callback()


@app.route('/me')
@client.is_logged_in()
def me():
    user = client.fetch_user()
    image = user.avatar_url
    # noinspection HtmlUnknownTarget
    return render_template_string("""
        {% extends "html/base.html" %}
        {% block title %}Me{% endblock %}
        {% block user_name %}
        {{ user_name_1 }}
        {% endblock %}
        {% block content %}
        <img src="{{ image_url }}" alt="Avatar url">
        {% endblock %}
        """, image_url=image, user_name_1=client.fetch_user().name, avatar_url=client.fetch_user().avatar_url, version_1=version)


@app.route('/loggedin')
@client.is_logged_in()
def logged_in():
    return render_template("html/loggedin.html", name=client.fetch_user().name)


@app.route('/logout', methods=['GET'])
@client.is_logged_in()
def logout():
    client.logout()
    return redirect(url_for('index'))


@app.route('/home')
@app.route('/index')
def index_or_home():
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
