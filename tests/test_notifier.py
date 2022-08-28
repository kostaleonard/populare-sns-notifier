"""Tests notifier.py."""

from tempfile import NamedTemporaryFile
import pytest
from requests_mock.mocker import Mocker
from populare_sns_notifier.notifier import (
    publish_message,
    SMS_MESSAGE_MAX_LEN,
    get_sns_topic_arn,
    get_recent_posts,
    POPULARE_DB_PROXY_GRAPHQL_URL,
    DEFAULT_NUM_POSTS
)

with open(
        "tests/fixtures/read_posts_response.txt", "r", encoding="utf-8"
) as infile:
    SAMPLE_READ_POSTS_RESPONSE = infile.read()


def test_get_recent_posts_returns_post_bodies(requests_mock: Mocker) -> None:
    """Tests that get_recent_posts returns recent post bodies.

    :param requests_mock: Mocks responses to HTTP requests.
    """
    requests_mock.post(
        POPULARE_DB_PROXY_GRAPHQL_URL,
        text=SAMPLE_READ_POSTS_RESPONSE
    )
    posts = get_recent_posts()
    assert len(posts) == DEFAULT_NUM_POSTS
    assert posts[0] == "hello posts 6"
    assert posts[-1] == "hello posts 2"


def test_get_topic_arn_reads_file() -> None:
    """Tests that get_topic_arn reads the given file."""
    with NamedTemporaryFile(mode="w") as arn_file:
        arn_file.write("test:arn")
        arn_file.seek(0)
        arn = get_sns_topic_arn(config_filename=arn_file.name)
    assert arn == "test:arn"


def test_publish_message_sends_to_sns(mocked_sns: dict) -> None:
    """Tests that publish_message sends a message to SNS.

    :param mocked_sns: The mocked SNS instance.
    """
    topic_arn = mocked_sns["TopicArn"]
    message = {"default": "Hello SNS"}
    # Currently cannot add assertion to check sent messages--see #1.
    publish_message(topic_arn, message)


def test_publish_message_too_long_for_sms_raises_error(
        mocked_sns: dict
) -> None:
    """Tests that publish_message raises an error when the message is too long
    for a single SMS text.

    :param mocked_sns: The mocked SNS instance.
    """
    topic_arn = mocked_sns["TopicArn"]
    message = {"default": "Hello SNS", "sms": "A" * (SMS_MESSAGE_MAX_LEN + 1)}
    with pytest.raises(ValueError):
        publish_message(topic_arn, message)
