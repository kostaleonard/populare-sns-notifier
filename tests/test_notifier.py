"""Tests notifier.py."""

from tempfile import NamedTemporaryFile
import pytest
from populare_sns_notifier.notifier import (
    publish_message, SMS_MESSAGE_MAX_LEN, get_sns_topic_arn
)


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
