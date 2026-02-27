#!/usr/bin/env python3
"""
Slack Notify - Helper script to send messages to Slack channels

Usage:
    python3 slack_send.py --channel "#deployments" --message "Deployment complete"
    python3 slack_send.py --channel "#incidents" --title "P1 Alert" --message "Service down" --color danger
    python3 slack_send.py --channel "#testing" --blocks blocks.json

Environment:
    SLACK_BOT_TOKEN: Required Slack bot token (xoxb-...)

Examples:
    # Simple message
    python3 slack_send.py --channel "#general" --message "Hello from Claude"

    # Formatted alert
    python3 slack_send.py --channel "#incidents" \
        --title "🚨 P1 Incident" \
        --message "ECGW service down in IAD" \
        --color danger \
        --field "Status:Investigating" \
        --field "Impact:Customer Facing"

    # Custom blocks from JSON file
    python3 slack_send.py --channel "#deployments" --blocks deployment_summary.json

    # Thread reply
    python3 slack_send.py --channel "#general" --message "Update" --thread-ts 1706024400.123456
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
except ImportError:
    print("❌ Error: slack-sdk not installed")
    print("   Install with: pip3 install slack-sdk")
    sys.exit(1)


def get_slack_token() -> Optional[str]:
    """Get Slack bot token from environment or config."""
    # Try environment variable
    token = os.environ.get('SLACK_BOT_TOKEN')
    if token:
        return token

    # Try config file
    config_path = os.path.expanduser('~/.claude/slack_config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                config = json.load(f)
                return config.get('slack_bot_token')
        except Exception as e:
            print(f"⚠️  Warning: Could not read config file: {e}")

    # Try systemd service file (if running on bot host)
    systemd_path = '/etc/systemd/system/claude-slack-bot.service.d/override.conf'
    if os.path.exists(systemd_path):
        try:
            with open(systemd_path) as f:
                for line in f:
                    if 'SLACK_BOT_TOKEN' in line and '=' in line:
                        return line.split('=', 1)[1].strip().strip('"\'')
        except Exception as e:
            print(f"⚠️  Warning: Could not read systemd file: {e}")

    return None


def verify_token(client: WebClient) -> bool:
    """Verify Slack token is valid."""
    try:
        response = client.auth_test()
        print(f"✓ Authenticated as: {response['user']}")
        print(f"  Team: {response['team']}")
        return True
    except SlackApiError as e:
        print(f"❌ Authentication failed: {e.response['error']}")
        return False


def build_simple_blocks(title: Optional[str], message: str, fields: Optional[List[str]] = None,
                       color: Optional[str] = None, footer: Optional[str] = None) -> List[Dict]:
    """Build Block Kit blocks for formatted message."""
    blocks = []

    # Add header if title provided
    if title:
        blocks.append({
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": title
            }
        })

    # Add main message
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": message
        }
    })

    # Add fields if provided
    if fields:
        field_blocks = []
        for field in fields:
            if ':' in field:
                key, value = field.split(':', 1)
                field_blocks.append({
                    "type": "mrkdwn",
                    "text": f"*{key.strip()}*\n{value.strip()}"
                })

        if field_blocks:
            blocks.append({
                "type": "section",
                "fields": field_blocks
            })

    # Add footer with timestamp
    if footer or True:  # Always add footer
        footer_text = footer or "Posted by Claude Code"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"{footer_text} • {timestamp}"
                }
            ]
        })

    return blocks


def send_message(client: WebClient, channel: str, text: str,
                thread_ts: Optional[str] = None, blocks: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """
    Send message to Slack channel.

    Args:
        client: Slack WebClient instance
        channel: Channel name or ID (#channel, @user, C123...)
        text: Message text (fallback for notifications)
        thread_ts: Optional thread timestamp to reply in thread
        blocks: Optional Block Kit blocks for rich formatting

    Returns:
        dict with 'ok', 'ts', 'channel', 'message_link' keys
    """
    try:
        response = client.chat_postMessage(
            channel=channel,
            text=text,
            thread_ts=thread_ts,
            blocks=blocks
        )

        # Build message link
        channel_id = response['channel']
        message_ts = response['ts'].replace('.', '')
        message_link = f"https://netskope.slack.com/archives/{channel_id}/p{message_ts}"

        return {
            "ok": True,
            "ts": response['ts'],
            "channel": channel_id,
            "message_link": message_link,
            "response": response
        }

    except SlackApiError as e:
        error_code = e.response['error']
        return {
            "ok": False,
            "error": error_code,
            "details": str(e),
            "response": e.response
        }


def handle_error(error_code: str, channel: str) -> str:
    """Return helpful error message for common Slack API errors."""
    error_messages = {
        'not_in_channel': f"❌ Bot is not in channel {channel}\n   Invite the bot first: /invite @Claude",
        'channel_not_found': f"❌ Channel {channel} not found\n   Check the channel name or ID",
        'invalid_auth': "❌ Invalid Slack token\n   Set SLACK_BOT_TOKEN: export SLACK_BOT_TOKEN='xoxb-...'",
        'rate_limited': "⏱️  Rate limited\n   Please wait a moment and try again",
        'missing_scope': "❌ Bot lacks required permissions\n   Add chat:write or chat:write.public scope to bot",
        'message_too_long': "❌ Message exceeds length limit\n   Split into multiple messages or use file upload",
    }

    return error_messages.get(error_code, f"❌ Slack API error: {error_code}")


def main():
    parser = argparse.ArgumentParser(
        description='Send messages to Slack channels',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Required arguments
    parser.add_argument('--channel', '-c', required=True,
                       help='Channel name or ID (#channel, @user, C123...)')
    parser.add_argument('--message', '-m',
                       help='Message text')

    # Formatting options
    parser.add_argument('--title', '-t',
                       help='Message title (for formatted messages)')
    parser.add_argument('--color',
                       choices=['good', 'warning', 'danger'],
                       help='Message color (good=green, warning=yellow, danger=red)')
    parser.add_argument('--field', '-f', action='append',
                       help='Add field in "Key:Value" format (can be used multiple times)')
    parser.add_argument('--footer',
                       help='Footer text (default: "Posted by Claude Code")')

    # Advanced options
    parser.add_argument('--blocks', '-b',
                       help='Path to JSON file with Block Kit blocks')
    parser.add_argument('--thread-ts', '--thread',
                       help='Thread timestamp to reply in thread')

    # Utility options
    parser.add_argument('--verify', action='store_true',
                       help='Verify token and exit')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Get token
    token = get_slack_token()
    if not token:
        print("❌ Error: SLACK_BOT_TOKEN not found")
        print("\nSet token with:")
        print("  export SLACK_BOT_TOKEN='xoxb-your-token-here'")
        print("\nOr create config file:")
        print("  ~/.claude/slack_config.json")
        sys.exit(1)

    # Initialize client
    client = WebClient(token=token)

    # Verify token if requested
    if args.verify:
        if verify_token(client):
            print("✓ Token is valid and ready to use")
            sys.exit(0)
        else:
            sys.exit(1)

    # Require message or blocks
    if not args.message and not args.blocks:
        print("❌ Error: Either --message or --blocks is required")
        parser.print_help()
        sys.exit(1)

    # Build blocks if formatting requested
    blocks = None
    if args.blocks:
        # Load blocks from JSON file
        try:
            with open(args.blocks) as f:
                blocks = json.load(f)
        except Exception as e:
            print(f"❌ Error loading blocks file: {e}")
            sys.exit(1)
    elif args.title or args.field or args.color:
        # Build blocks from arguments
        blocks = build_simple_blocks(
            title=args.title,
            message=args.message,
            fields=args.field,
            footer=args.footer
        )

    # Send message
    if args.verbose:
        print(f"Sending to channel: {args.channel}")
        if blocks:
            print(f"Using {len(blocks)} blocks")
        print()

    result = send_message(
        client=client,
        channel=args.channel,
        text=args.message or "Message (see blocks for formatting)",
        thread_ts=args.thread_ts,
        blocks=blocks
    )

    # Handle result
    if result['ok']:
        print(f"✓ Message sent to {args.channel}")
        print(f"🔗 {result['message_link']}")

        if args.verbose:
            print(f"\nDetails:")
            print(f"  Timestamp: {result['ts']}")
            print(f"  Channel ID: {result['channel']}")

        sys.exit(0)
    else:
        error_msg = handle_error(result['error'], args.channel)
        print(error_msg)

        if args.verbose:
            print(f"\nDetails: {result['details']}")

        sys.exit(1)


if __name__ == '__main__':
    main()
