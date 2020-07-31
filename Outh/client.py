import functools
import os

from flask import abort, redirect, request, session

from .base import DISCORD_AUTHORIZATION_BASE_URL
from .http import AioClient


class DiscordOauth2Client(AioClient):
    def __init__(self, app):
        super().__init__(app)

    @staticmethod
    def token_remover():
        session["DISCORD_OAUTH2_TOKEN"] = None

    def callback(self):

        discord = self._make_session()
        # self.MyClient.token_updater(access_token.get('access_token'))
        token = discord.fetch_token(self.token_url, client_secret=self.client_secret, authorization_response=request.url)
        self.token_updater(token)
        # .get('access_token')
        # print(token.get('access_token'))
        # return redirect(url_for('index'))

    @staticmethod
    def is_logged_in(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            if session.get('DISCORD_OAUTH2_TOKEN'):
                return func(*args, **kwargs)
            else:
                return abort(401)

        return inner

    @staticmethod
    def logout():
        session.pop('DISCORD_OAUTH2_TOKEN')
        session.pop('DISCORD_OAUTH2_STATE')
        # print(redirect(url_for('index')))

    def create_session(self):
        if 'http://' in self.redirect_url:
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
        authorization_url, state = self._make_session().authorization_url(DISCORD_AUTHORIZATION_BASE_URL)
        session['DISCORD_OAUTH2_STATE'] = state
        # print(redirect(self.MyClient._make_session().authorization_url(DISCORD_AUTHORIZATION_BASE_URL)))
        return redirect(authorization_url)
