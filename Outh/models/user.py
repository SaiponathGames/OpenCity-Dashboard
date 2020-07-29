from ..base import *

class User:
    def __init__(self, payload):
        self.id = int(payload['id'])
        self.name = payload['username']
        self.discriminator = int(payload['discriminator'])
        self.email = payload['email']
        self.verified = payload['verified']
        self.locale = payload['locale']
        self.public_flags = payload['public_flags']
        self.flags = payload['flags']
        self.avatar_hash = payload['avatar']
        self.mfa_enabled = payload['mfa_enabled']

    @property
    def is_avatar_animated(self):
        return self.avatar_hash.startswith('a_')

    @property
    def avatar_url(self):
        """A property returning direct URL to user's avatar."""
        if not self.avatar_hash:
            return
        image_format = DISCORD_ANIMATED_IMAGE_FORMAT \
            if self.is_avatar_animated else DISCORD_IMAGE_FORMAT
        return (DISCORD_USER_AVATAR_BASE_URL.format(
            user_id=self.id, avatar_hash=self.avatar_hash, format=image_format) + '?size=1024')

    @property
    def default_avatar_url(self):
        """A property which returns the default avatar URL as when user doesn't has any avatar set."""
        return DISCORD_DEFAULT_USER_AVATAR_BASE_URL.format(modulo5=int(self.discriminator) % 5)
