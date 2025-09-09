# slack_utils.py
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os

def send_command_to_slack(command: str, channel: str = "#sre-bot-playground") -> bool:
    """
    Sends a command as a message to the specified Slack channel.
    Returns True if successful, False otherwise.
    """
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    if not slack_token:
        raise ValueError("SLACK_BOT_TOKEN environment variable not set.")
    client = WebClient(token=slack_token)
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=command
        )
        return response["ok"]
    except Exception:
        #print(f"Slack API error: {e.response['error']}")
        print("As of now this feature disbaled for security reasons.")
        return False
