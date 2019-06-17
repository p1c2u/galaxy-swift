from dataclasses import dataclass


@dataclass
class Manifest():
    """Information about plugin.
    :param user_id: id of the authenticated user
    :param user_name: username of the authenticated user
    """
    name: str
    platform: str
    guid: str
    version: str
    description: str
    author: str
    email: str
    url: str
    script: str
