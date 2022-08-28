"""Publishes messages to SNS."""

from typing import Any
import json
import requests
import boto3

POPULARE_DB_PROXY_GRAPHQL_URL = "http://populare-db-proxy/graphql"
REQUEST_HEADERS = {"Content-Type": "application/graphql"}
DEFAULT_NUM_POSTS = 5
SNS_TOPIC_CONFIG_PATH = "/etc/populare-sns-notifier/populare-sns-topic-arn"
SMS_MESSAGE_MAX_LEN = 140


def get_recent_posts(
        db_proxy_graphql_url: str = POPULARE_DB_PROXY_GRAPHQL_URL,
        num_posts: int = DEFAULT_NUM_POSTS
) -> list[str]:
    """Returns the most recent num_posts posts from the database.

    :param db_proxy_graphql_url: The database proxy GraphQL URL to which a
        request should be sent to read the most recent posts.
    :param num_posts: The number of recent posts to return.
    :return: The most recent num_posts posts from the database.
    """
    payload = f"{{ readPosts(limit: {num_posts}) }}"
    resp = requests.post(
        db_proxy_graphql_url,
        data=payload,
        headers=REQUEST_HEADERS,
        timeout=10
    )
    resp_json = json.loads(resp.text)
    post_bodies = [
        json.loads(post)["text"] for post in resp_json["data"]["readPosts"]
    ]
    return post_bodies


def get_sns_topic_arn(config_filename: str = SNS_TOPIC_CONFIG_PATH) -> str:
    """Returns the SNS topic ARN.

    The SNS topic ARN is loaded from config_filename, which is a Kubernetes
    ConfigMap volume mount. If the file is absent, this operation will raise
    a FileNotFoundError.

    :param config_filename: The path to the file containing the SNS topic ARN.
    :return: The SNS topic ARN.
    """
    with open(config_filename, "r", encoding="utf-8") as infile:
        return infile.read().strip()


def publish_message(
        target_arn: str,
        message: dict[str, Any]
) -> dict[str, Any]:
    """Publishes a message to SNS and returns the response.

    Documentation on AWS-supported protocols for SNS is available here:
    https://docs.aws.amazon.com/sns/latest/api/API_Subscribe.html

    To limit potential charges, messages over SMS (cell phone) are limited to a
    single text, and so must be no longer than 140 characters.

    :param target_arn: The ARN of the SNS topic to which to publish the
        message.
    :param message: The JSON-encoded message to publish. The keys are the
        AWS-supported protocols to which you would like to send the message,
        one of which must be "default". The values are the JSON objects that
        you would like to send over each protocol.
    :return: The JSON response from the AWS API.
    """
    if "sms" in message and len(message["sms"]) > SMS_MESSAGE_MAX_LEN:
        raise ValueError(
            f"SMS messages must contain no more than {SMS_MESSAGE_MAX_LEN} "
            "characters"
        )
    client = boto3.client("sns", region_name="us-east-2")
    return client.publish(
        TargetArn=target_arn,
        Message=json.dumps(message),
        Subject="Populare SNS Notifier Update",
        MessageStructure="json"
    )


def main() -> None:
    """Runs the program."""
    target_arn = get_sns_topic_arn()
    posts = get_recent_posts()
    message = {"default": "\n".join(posts)}
    publish_message(target_arn, message)


if __name__ == "__main__":
    main()
