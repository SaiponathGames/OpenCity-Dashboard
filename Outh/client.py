import functools
import os

from flask import abort, redirect, request, session

from .base import DISCORD_AUTHORIZATION_BASE_URL
from .http import AioClient


class DiscordOauth2Client(object):
    def __init__(self, app):
        self.MyClient = AioClient(app)
        self.redirect_url = self.MyClient.redirect_url
        self.client_id = self.MyClient.client_id

    @staticmethod
    def token_remover():
        session["DISCORD_OAUTH2_TOKEN"] = None

    def callback(self):

        discord = self.MyClient._make_session(state=session.get('DISCORD_OAUTH2_STATE'))
        # self.MyClient.token_updater(access_token.get('access_token'))
        token = discord.fetch_token(self.MyClient.token_url, client_secret=self.MyClient.client_secret, authorization_response=request.url)
        session['DISCORD_OAUTH2_TOKEN'] = token.get('access_token')
        # print(token.get('access_token'))
        # return redirect(url_for('index'))

    def fetch_user(self):
        return self.MyClient.fetch_user()

    @staticmethod
    def is_logged_in(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if "DISCORD_OAUTH2_TOKEN" in session:
                func(*args, **kwargs)
            else:
                abort(401)

        return inner

    def fetch_guilds(self):
        return self.MyClient.fetch_guilds()

    def create_session(self):
        if 'http://' in self.redirect_url:
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
        authorization_url, state = self.MyClient._make_session().authorization_url(DISCORD_AUTHORIZATION_BASE_URL)
        session['DISCORD_OAUTH2_STATE'] = state
        # print(redirect(self.MyClient._make_session().authorization_url(DISCORD_AUTHORIZATION_BASE_URL)))
        return redirect(authorization_url)
