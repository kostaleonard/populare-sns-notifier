"""Contains test fixtures."""

import os
import pytest
import boto3
from moto import mock_sns

TEST_REGION = "us-east-2"


@pytest.fixture(name="aws_credentials", scope="session")
def fixture_aws_credentials() -> None:
    """Mocked AWS credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = TEST_REGION


@pytest.fixture(name="mocked_sns", scope="session")
def fixture_mocked_sns(aws_credentials: None) -> dict:
    """Creates a mocked SNS instance for tests.

    :param aws_credentials: Mocked AWS credentials.
    :return: The mocked SNS topic JSON object.
    """
    # pylint: disable=unused-argument
    with mock_sns():
        client = boto3.client("sns", region_name=TEST_REGION)
        yield client.create_topic(Name="test-topic")
