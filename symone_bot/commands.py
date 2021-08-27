import logging
import os
from typing import Dict, Callable, List, Any
from google.cloud import datastore

from symone_bot.aspects import Aspect
from symone_bot.metadata import QueryMetaData

GAME_MASTER = os.getenv("GAME_MASTER")
PROJECT_ID = os.getenv("PROJECT_ID")
MESSAGE_RESPONSE_CHANNEL = "in_channel"
MESSAGE_RESPONSE_EPHEMERAL = "ephemeral"

DATA_KEY_CAMPAIGN = "campaign"


# TODO bot functions:
# GM add gold
# Any add loot
# Did they level?
# Set next level (plus set xp... might avoid having to build an xp table..)


def create_client(project_id: str):
    return datastore.Client(project_id)


class Command:
    """
    Wrapper around a callable that returns a Flask Response object.
    This wrapper exists to add metadata to the callable.
    """

    def __init__(self, name: str, help_info: str, function: Callable, aspect_type=None):
        self.name = name
        self.help_info = help_info
        if not callable(function):
            raise AttributeError("'function' must be type Callable.")
        self.callable = function
        self.aspect_type = aspect_type

    def help(self) -> str:
        return f"`{self.name}`: {self.help_info}."


def default_response(metadata: QueryMetaData) -> dict:
    logging.info(f"Default response triggered by user: {metadata.user_id}")
    return {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": "I am Symone Bot. I keep track of party gold, XP, and loot. Type `/symone help` to see what I can do.",
    }


def help_message(metadata: QueryMetaData) -> dict:
    """Auto generates help message by gathering the help info from each SymoneCommand."""
    logging.info(f"Default response triggered by user: {metadata.user_id}")
    text = """"""
    for command in command_list:
        if not command.callable == default_response:
            text += f"{command.help()}\n"
    return {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": text,
    }


def add(metadata: QueryMetaData, aspect: Aspect, value: Any) -> Dict[str, str]:
    """
    Adds a given value to the given aspect.
    :param metadata: metadata about the query.
    :param aspect: aspect to operate on.
    :param value: value to add to aspect.
    :return: dictionary representing json for a Slack response.
    """
    logging.info(f"'add' command invoked on {aspect.name} by {metadata.user_id}")
    if metadata.user_id not in aspect.allowed_users:
        logging.warning(
            f"Unauthorized user attempted to execute add command on {aspect.name} Aspect."
        )
        return {
            "response_type": MESSAGE_RESPONSE_CHANNEL,
            "text": "Nice try...",
        }

    datastore_client = create_client(PROJECT_ID)
    query = datastore_client.query(kind=DATA_KEY_CAMPAIGN).fetch()
    result = query.next()

    current_value = result[aspect.name]
    new_value = current_value + value
    result[aspect.name] = new_value
    datastore_client.put(result)

    logging.info(f"Updated {aspect.name} to {new_value}")

    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"Updated {aspect.name} to {new_value}",
    }


def current(metadata: QueryMetaData, aspect: Aspect) -> Dict[str, str]:
    """
    Returns the current value for a given aspect.
    :param metadata: metadata about the query.
    :param aspect: aspect to operate on.
    :return: dictionary representing json for a Slack response.
    """
    logging.info(f"'current' command invoked on {aspect.name} by {metadata.user_id}")
    datastore_client = create_client(PROJECT_ID)
    query = datastore_client.query(kind=DATA_KEY_CAMPAIGN).fetch()
    result = query.next()
    current_value = result[aspect.name]


command_list: List[Command] = [
    Command("default", "", default_response),
    Command("help", "retrieves help info", help_message),
    Command("add", "adds a given value to a given aspect.", add),
]
