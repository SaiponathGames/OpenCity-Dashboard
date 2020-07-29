import json

from ..base import *


class GuildObject:
    def __init__(self, /, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        keys = sorted(self.__dict__)
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "{}({})".format(type(self).__name__, ", ".join(items))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Guild:
    def __init__(self, payload):
        self.payload = payload
        self.id = int(payload.get("id"))
        self.name = payload.get("name")
        self.icon_hash = payload.get("icon")
        self.is_owner = payload.get("owner")
        self.permissions_value = payload.get("permissions")
        # print(self.name, self.permissions_value)
        self.features = payload.get('features')

    def __repr__(self):
        data = json.dumps(self.payload)
        return str(json.loads(data, object_hook=lambda x: GuildObject(**x)))

    def is_owner_of_guild(self):
        return bool(self.is_owner or (self.permissions_value & 0x8) == 0x8)

    @property
    def icon_url(self):
        if not self.icon_hash:
            return None
        return DISCORD_GUILD_ICON_BASE_URL.format(guild_id=self.id, icon_hash=self.icon_hash) + '?size=1024'
