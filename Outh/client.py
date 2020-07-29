import urllib.parse
from . import exceptions
from flask import redirect, session
import json
from .models import guild
from .base import *
from .http import AioClient


class DiscordOauth2Client(object):
    def __init__(self, app):
        self.MyClient = AioClient(app)
        self.redirect_url = self.MyClient.redirect_url

    @staticmethod
    def token_updater(token):
        session["DISCORD_OAUTH2_TOKEN"] = token

    @staticmethod
    def token_remover():
        session["DISCORD_OAUTH2_TOKEN"] = None

    def callback(self):
        access_token = self.MyClient.callback()
        self.token_updater(access_token.get('access_token'))

    def fetch_user(self):
        return self.MyClient.fetch_user()

    def fetch_guilds(self):
        return self.MyClient.fetch_guilds()

    def create_session(self):
        return redirect(self.redirect_url)
