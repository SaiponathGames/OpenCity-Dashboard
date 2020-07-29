import requests
import urllib.parse
from flask import request
from .exceptions import *
from .base import *
import json
from .models.user import User
from .models.guild import Guild
from flask import session


class AioClient:
    def __init__(self, app):
        self.client_id = app.config['Client_ID']
        self.client_secret = app.config['Client_Secret']
        self.scopes = app.config['Scopes']
        self.redirect_url = app.config['Redirect_Url']
        self.discord_bot_token = app.config['Bot_Token']
        self.token_url = 'https://discordapp.com/api/oauth2/token'
        base_redirect = 'https://discord.com/api/oauth2/authorize?'
        url_variables = {'client_id': self.client_id, 'redirect_url': self.redirect_url,
                         'response_type': 'code'}
        self.redirect_url = base_redirect + urllib.parse.urlencode(url_variables)
        if self.scopes:
            self.redirect_url += ('&scope=' + '%20'.join(self.scopes))

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

    @staticmethod
    def fetch_user():
        access_token = session.get('DISCORD_OAUTH2_TOKEN')
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
