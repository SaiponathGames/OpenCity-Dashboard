import itertools
import os
import random
import string

from flask import Flask, Markup, redirect, render_template, render_template_string, request, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from Outh import DiscordOauth2Client, Unauthorized

__version__ = '0.8.0-beta'
version = __version__

from jinja2 import Template

app = Flask(__name__)


@app.template_filter()
def inner_render(value, context):
    return Template(value).render(context)


app.secret_key = (os.urandom(1000) + "".join([random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(10000)]).encode())
app.config['DISCORD_CLIENT_ID'] = 651420362940088336
app.config['DISCORD_CLIENT_SECRET'] = '0-_AhUL6Y01qCnMpsp6GTdf0UCVxxCTu'
app.config['SCOPES'] = ['identify', 'guilds']
app.config['DISCORD_REDIRECT_URI'] = os.getenv('REDIRECT_URL') or 'http://127.0.0.1:5000/callback'
app.config['DISCORD_BOT_TOKEN'] = None
app.config['CSRF_ENABLED'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5858/Flask-Database-for-Dashboard-Test'
app.jinja_env.filters['zip'] = itertools.zip_longest
app.jinja_env.filters['inner_render'] = inner_render
app.jinja_env.filters['repeat'] = itertools.repeat

# print(app.secret_key)

# app.register_blueprint(admin.admin)

client = DiscordOauth2Client(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# from admin import admin
# app.register_blueprint(admin.admin)


@app.route('/')
def index():
    from models import Text_For_Indexes
    # print(session)
    tfi_s = [Text_For_Indexes("Add to your server!",
                              "Hello there, I am OpenCityBot, I do levels, gatekeeper, reaction roles and much more. I have a custom leveling role set based leveling roles, which gives many abilities to configure our advanced leveling system. Please visit our docs for more info.",
                              "Add to your server."),
             Text_For_Indexes("Want to know more? See Features",
                              "I am a feature-rich bot, the number of my {} are jaw dropping, I can manage many things from Leveling to Fun commands, I can manage everything you want.",
                              "See features"),
             Text_For_Indexes("About my developers!",
                              "My developers made me an open source and high-quality bot. You can check out my code {}.",
                              "Learn more")]
    formatters = [[""], [Markup("<a href={{ url_for('features') }}>features</a>")], ['<a href="https://github.com/sairam4123/OpenCityBot-MovingJSON-PostGreSQL">here</a>']]
    button_links = ["https://discord.com/api/oauth2/authorize?client_id=693401671836893235&permissions=8&scope=bot", "{{ url_for('features') }}",
                    "{{ url_for('this_does_nothing') }}"]
    try:
        return render_template("html/index.html", texts=tfi_s, formatters=formatters, button_links=button_links, logined='access_token',
                               user=client.fetch_user(),
                               version_1=version)
    except Unauthorized:
        return render_template("html/index.html", texts=tfi_s, formatters=formatters, button_links=button_links, logined=request.args.get('logged_in'), version_1=version)


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
        # noinspection PyCompatibility
        if guild_name := request.form['guild_name']:
            return render_template('html/guilds.html', guild_names=search_guilds_for_name(client.fetch_guilds(), guild_name), user=client.fetch_user(), version_1=version)
        else:
            return render_template('html/guilds.html', guild_names=return_guild_names_owner(client.fetch_guilds()), user=client.fetch_user(), version_1=version)
    return render_template('html/guilds.html', guild_names=return_guild_names_owner(client.fetch_guilds()), user=client.fetch_user(), version_1=version)


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
        {{ user.name }}
        {% endblock %}
        {% block content %}
        <img src="{{ user.avatar_url }}" alt="Avatar url">
        {% endblock %}
        """, image_url=image, user=client.fetch_user(), version_1=version)


@app.route('/loggedin')
@client.is_logged_in()
def logged_in():
    return render_template("html/loggedin.html", user=client.fetch_user())


@app.route('/logout', methods=['GET'])
@client.is_logged_in()
def logout():
    client.logout()
    return redirect(url_for('index'))


@app.route('/home')
@app.route('/index')
def index_or_home():
    return redirect(url_for('index'))


@app.route('/features')
def features():
    from models import Features
    fts = [Features("Leveling", "I have a good featured leveling system. Please visit docs for more info."),
           Features("Moderation", "My developers are working day and night to implement a good moderation system for me."),
           Features("Auto-Moderator", "I can be a good moderator. If a raid is going on in your server, I can ban the raiders.")]
    fts_2 = list(itertools.chain.from_iterable(list(itertools.repeat(fts, 15))))
    # print(fts_2)
    try:
        return render_template('html/features.html', features=fts_2, user=client.fetch_user(), version_1=version)
    except Unauthorized:
        return render_template('html/features.html', features=fts_2, version_1=version)


@app.route('/this-does-nothing')
def this_does_nothing():
    return "Really, this does nothing!, LOL"


if __name__ == '__main__':
    app.run()
