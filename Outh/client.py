import functools
import os

from flask import redirect, request, session, url_for

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
        if redirect_url_after_login := session.get("REDIRECT_URL_AFTER_LOGIN"):
            return redirect(redirect_url_after_login)
        else:
            return redirect(url_for('index'))

        # .get('access_token')
        # print(token.get('access_token'))
        # return redirect(url_for('index'))

    @staticmethod
    def is_logged_in(redirect_to_previous_page=True):
        def decorator(view):
            @functools.wraps(view)
            def inner(*args, **kwargs):
                if session.get('DISCORD_OAUTH2_TOKEN'):
                    return view(*args, **kwargs)
                else:
                    if redirect_to_previous_page:
                        session['REDIRECT_URL_AFTER_LOGIN'] = request.url
                    return redirect(url_for('login'))

            return inner

        return decorator

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
