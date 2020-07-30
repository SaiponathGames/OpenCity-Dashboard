import json
import urllib.parse

import requests
from flask import request, session
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
        base_redirect = 'https://discord.com/api/oauth2/authorize?'
        url_variables = {'client_id': self.client_id, 'redirect_url': self.redirect_url,
                         'response_type': 'code'}
        self.discord_url = base_redirect + urllib.parse.urlencode(url_variables)
        if self.scopes:
            self.discord_url += ('&scope=' + '%20'.join(self.scopes))

        # print(self.redirect_url)

    @staticmethod
    def token_updater(token):
        session["DISCORD_OAUTH2_TOKEN"] = token

    @staticmethod
    def _request(**kwargs):
        res = requests
        _method = getattr(res, kwargs.pop('type'))
        return _method(**kwargs)

    def callback(self):
        code = request.args.get('code')
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_url': self.redirect_url,
            'scope': '%20'.join(self.scopes)
        }

        headers = {
            'Content-type': 'application/x-www-form-urlencoded'
        }
        access_token = self._request(type='post', url=self.token_url, data=payload, headers=headers)
        if access_token.status_code != 200:
            raise Unauthorized
        return access_token.json()

    def _make_session(self, token=None, state=None, scope=None):
        if scope is None:
            scope = self.scopes or ['identity', 'guilds']
        return OAuth2Session(
            client_id=self.client_id,
            token=token,
            scope=scope,
            state=state,
            redirect_uri=self.redirect_url,
            auto_refresh_kwargs={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
            },
            auto_refresh_url=self.token_url,
            token_updater=self.token_updater)

    @staticmethod
    def fetch_user():
        access_token = session.get('DISCORD_OAUTH2_TOKEN')
        # print(access_token)
        url = DISCORD_API_BASE_URL + '/users/@me'
        headers = {
            "Authorization": "Bearer {}".format(access_token)
        }
        data: requests.Response = AioClient._request(type='get', url=url, headers=headers)
        if data.status_code == 401:
            raise Unauthorized
        try:
            response = data.json()
        except json.decoder.JSONDecodeError:
            response = data.text
        return User(response)

    @staticmethod
    def fetch_guilds():
        access_token = session.get('DISCORD_OAUTH2_TOKEN')
        url = DISCORD_API_BASE_URL + '/users/@me/guilds'
        headers = {
            "Authorization": "Bearer {}".format(access_token)
        }
        data = AioClient._request(type='get', url=url, headers=headers)
        if data.status_code == 401:
            raise Unauthorized
        try:
            response = data.json()
        except json.decoder.JSONDecodeError:
            response = data.text()
        list_ = []
        for res in response:
            list_.append(Guild(res))
        return list_
