import re

import pytest

from symone_bot.aspects import Aspect
from symone_bot.commands import Command
from symone_bot.parser import generate_tokens, QueryEvaluator, Token


@pytest.fixture
def test_commands():
    return [Command("foo", "", lambda: 1 + 1)]


@pytest.fixture
def test_aspects():
    return [Aspect("bar", "", int)]


@pytest.fixture
def query_evaluator(test_commands, test_aspects):
    return QueryEvaluator(test_commands, test_aspects)


def test_generate_tokens():
    num = r"(?P<NUM>\d+)"
    ws = r"(?P<WS>\s+)"
    pattern = re.compile("|".join([num, ws]))
    token_generator = generate_tokens("1 2 3 foo", pattern)

    token_list = list(token_generator)

    for token in token_list:
        assert token[0] == "NUM"


def test_parse(query_evaluator):
    response = query_evaluator.parse("foo bar 3")

    assert response.command.name == "foo"
    assert response.aspect.name == "bar"
    assert response.value == 3


def test__get_master_pattern(query_evaluator):
    pattern = query_evaluator._get_master_pattern()

    assert type(pattern) == re.Pattern
    assert pattern == re.compile(
        "(?P<CMD>\\bfoo\\b)|(?P<ASPECT>\\bbar\\b)|(?P<NUM>\\d+)|(?P<WS>\\s+)"
    )


def test__lookup_function(query_evaluator):
    cmd_token = Token("CMD", "foo")
    command = query_evaluator._lookup_command(cmd_token)

    assert command.name == "foo"
    assert command.help_info == ""


def test__lookup_aspect(query_evaluator):
    aspect_token = Token("ASPECT", "bar")
    aspect = query_evaluator._lookup_aspect(aspect_token)

    assert aspect.name == "bar"
    assert aspect.help_info == ""
    assert aspect.value_type == int