import json

import requests
from flask import session
from requests_oauthlib import OAuth2Session

from .base import *
from .exceptions import *
from .models.guild import Guild
from .models.user import User


class AioClient:
    def __init__(self, app):
        self.client_id = app.config['DISCORD_CLIENT_ID']
        self.client_secret = app.config['DISCORD_CLIENT_SECRET']
        self.scopes = app.config['SCOPES']
        self.redirect_url = app.config['DISCORD_REDIRECT_URI']
        self.discord_bot_token = app.config['DISCORD_BOT_TOKEN']
        self.token_url = 'https://discordapp.com/api/oauth2/token'
        # base_redirect = 'https://discord.com/api/oauth2/authorize?'
        # url_variables = {'client_id': self.client_id, 'redirect_url': self.redirect_url,
        #                  'response_type': 'code'}
        # self.discord_url = base_redirect + urllib.parse.urlencode(url_variables)
        # if self.scopes:
        #     self.discord_url += ('&scope=' + '%20'.join(self.scopes))

        # print(self.redirect_url)

    @staticmethod
    def token_updater(token):
        session["DISCORD_OAUTH2_TOKEN"] = token

    @staticmethod
    def _request(**kwargs):
        res = requests
        _method = getattr(res, kwargs.pop('type'))
        return _method(**kwargs)

    # def callback(self):
    # discord = self._make_session(state=session.get('DISCORD_OAUTH2_STATE'))
    # # self.MyClient.token_updater(access_token.get('access_token'))
    # token = discord.fetch_token(self.token_url, client_secret=self.client_secret, authorization_response=request.url)
    # session['DISCORD_OAUTH2_TOKEN'] = token
    # .get('access_token')

    def _make_session(self, token=None, state=None, scope=None):
        if scope is None:
            scope = self.scopes or ['identity', 'guilds']
        return OAuth2Session(
            client_id=self.client_id,
            token=token or session.get("DISCORD_OAUTH2_TOKEN"),
            scope=scope,
            state=state or session.get("DISCORD_OAUTH2_STATE"),
            redirect_uri=self.redirect_url,
            auto_refresh_kwargs={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            },
            auto_refresh_url=self.token_url,
            token_updater=self.token_updater)

    def fetch_user(self):
        # access_token = session.get('DISCORD_OAUTH2_TOKEN')
        # print(access_token)
        discord = self._make_session()
        # headers = {
        #     "Authorization": "Bearer {}".format(access_token)
        # }
        # data: requests.Response = self._request(type='get', url=url, headers=headers)
        # if data.status_code == 401:
        #     raise Unauthorized
        # try:
        #     response = data.json()
        # except json.decoder.JSONDecodeError:
        #     response = data.text
        # return User(response)
        # response = None
        response = discord.get(DISCORD_API_BASE_URL + '/users/@me')
        if response.status_code == 401:
            raise Unauthorized
        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            data = response.text
        return User(data)

    def fetch_guilds(self):
        # access_token =
        # url = DISCORD_API_BASE_URL + '/users/@me/guilds'
        # headers = {
        #     "Authorization": "Bearer {}".format(access_token)
        # }
        # data = AioClient._request(type='get', url=url, headers=headers)
        # if data.status_code == 401:
        #     raise Unauthorized
        # try:
        #     response = data.json()
        # except json.decoder.JSONDecodeError:
        #     response = data.text()
        # response = None
        discord = self._make_session()
        try:
            response = discord.get(DISCORD_API_BASE_URL + '/users/@me/guilds')
        except AttributeError as e:
            print(e)
            return

        if response.status_code == 401:
            raise Unauthorized
        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            data = response.text
        return [Guild(datum) for datum in data]
