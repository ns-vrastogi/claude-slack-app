# Slack Notify Skill

## Name
`slack-notify`

## Description
Send messages and alerts to Slack channels or users directly from Claude Code CLI. This skill integrates with existing Slack Bot infrastructure to send notifications, status updates, alerts, and deployment summaries.

## Version
1.0.0

## Prerequisites
- Slack Bot Token (SLACK_BOT_TOKEN environment variable or from config)
- Bot must be added to target channels
- Permissions: `chat:write`, `chat:write.public`, `files:write`

## Activation Patterns

The skill should automatically activate when the user says:
- "send message to slack"
- "notify slack channel"
- "post to slack"
- "send alert to slack"
- "slack notify"
- "send slack message"
- "post update to slack"
- "alert [channel] on slack"

## Use Cases

### 1. Deployment Notifications
Send deployment status updates to a team channel
```
User: Send deployment notification to slack
Assistant: Which channel?
User: #deployments
Assistant: What message?
User: VPP IPSEC gateway deployment to iad0 completed successfully
```

### 2. Alert Notifications
Send critical alerts when issues are detected
```
User: Send alert to slack channel #incidents
Assistant: What's the alert message?
User: P1 Incident: ECGW service down in IAD datacenter - investigating
```

### 3. Test Results
Post test results and performance metrics
```
User: Post to slack #testing
Assistant: What message?
User: Scale test completed: 50k tunnels - 99.9% success rate, avg latency 2ms
```

### 4. Status Updates
Keep team informed of ongoing work
```
User: Notify slack #team-updates
Assistant: What update?
User: Starting VPP GRE gateway deployment to phl1 POP - ETA 15 minutes
```

### 5. Direct Messages
Send messages to specific users
```
User: Send slack message to @vikash
Assistant: What message?
User: PDV testing completed for bsb1 - all checks passed
```

## Commands

### 1. Send Simple Message

**Trigger**: "send message to slack", "post to slack"

**Parameters**:
- Channel or user (e.g., `#deployments`, `@vikash`)
- Message text

**Process**:
1. Identify target (channel ID or user ID)
2. Get SLACK_BOT_TOKEN from environment or config
3. Send message using Slack API
4. Confirm delivery with message link

**Example**:
```
User: Send message to slack channel #deployments
Assistant: [Prompts for message]
User: Deployment to IAD0 complete
Assistant: [Sends message]
✓ Message sent to #deployments
🔗 https://netskope.slack.com/archives/C123.../p1234567890
```

### 2. Send Formatted Message

**Trigger**: "send formatted message to slack", "post rich message"

**Parameters**:
- Channel or user
- Title
- Message body
- Optional: Color (good/warning/danger), fields, footer

**Process**:
1. Build Slack Block Kit or attachment payload
2. Send formatted message
3. Return confirmation

**Example**:
```
User: Send formatted alert to slack #incidents
Assistant: [Prompts for details]
Title: P1 Incident - ECGW Service Down
Message: ECGW service unresponsive in IAD datacenter
Color: danger
Assistant: [Sends formatted message with red color bar]
✓ Alert sent to #incidents
```

### 3. Send Message with Thread

**Trigger**: "send threaded message to slack", "reply to slack thread"

**Parameters**:
- Channel
- Thread timestamp (ts)
- Message text

**Process**:
1. Get thread_ts (message timestamp to reply to)
2. Send message with thread_ts parameter
3. Confirm reply posted

### 4. Send File or Snippet

**Trigger**: "send file to slack", "upload to slack", "share code on slack"

**Parameters**:
- Channel
- File path or content
- Optional: Title, comment, filetype

**Process**:
1. Read file content (if file path provided)
2. Upload using files.upload API
3. Return file URL

**Example**:
```
User: Share test results to slack #testing
Assistant: Which file?
User: /tmp/performance_test_results.json
Assistant: [Uploads file]
✓ File uploaded to #testing
📎 performance_test_results.json
🔗 https://netskope.slack.com/files/U123.../F456...
```

## Authentication

### Token Sources (Priority Order)

1. **Environment Variable**: `SLACK_BOT_TOKEN`
   ```bash
   export SLACK_BOT_TOKEN="xoxb-your-token-here"
   ```

2. **Config File**: `~/.claude/slack_config.json`
   ```json
   {
     "slack_bot_token": "xoxb-your-token-here",
     "default_channel": "#general"
   }
   ```

3. **From slack-bot-deployment**: Read from systemd override file
   ```bash
   grep SLACK_BOT_TOKEN /etc/systemd/system/claude-slack-bot.service.d/override.conf
   ```

### Token Verification

Before sending any message, verify token is valid:
```python
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token=slack_bot_token)
try:
    response = client.auth_test()
    print(f"✓ Authenticated as: {response['user']}")
    print(f"  Team: {response['team']}")
    return True
except SlackApiError as e:
    print(f"✗ Authentication failed: {e.response['error']}")
    return False
```

## Slack API Reference

### Send Message (chat.postMessage)

**Endpoint**: `https://slack.com/api/chat.postMessage`

**Parameters**:
- `channel` (required): Channel ID or name (#channel, @user)
- `text` (required): Message text
- `thread_ts` (optional): Timestamp of parent message to reply in thread
- `blocks` (optional): Array of Block Kit blocks for rich formatting
- `attachments` (optional): Array of legacy attachments

**Python Example**:
```python
from slack_sdk import WebClient

client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

response = client.chat_postMessage(
    channel="#deployments",
    text="Deployment completed successfully",
    blocks=[
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🚀 Deployment Complete"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Host*: vppipsecgw04.iad0\n*Build*: 134.0.0.3391\n*Status*: ✅ Success"
            }
        }
    ]
)

print(f"Message sent: {response['ts']}")
print(f"Link: https://netskope.slack.com/archives/{response['channel']}/p{response['ts'].replace('.', '')}")
```

### Bash Example (using curl)

```bash
SLACK_BOT_TOKEN="xoxb-your-token"
CHANNEL="#deployments"
MESSAGE="Deployment to iad0 completed"

curl -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "'$CHANNEL'",
    "text": "'$MESSAGE'"
  }'
```

### Channel ID Lookup

If user provides channel name, convert to ID:

**Method 1**: Use conversations.list API
```python
response = client.conversations_list(types="public_channel,private_channel")
channels = {ch['name']: ch['id'] for ch in response['channels']}
channel_id = channels.get('deployments')  # For #deployments
```

**Method 2**: Use channel name directly (bot must be in channel)
```python
# Slack API accepts both channel IDs and names
client.chat_postMessage(channel="#deployments", text="Hello")
```

## Message Formatting

### Basic Text Formatting

- **Bold**: `*text*` → **text**
- **Italic**: `_text_` → _text_
- **Strikethrough**: `~text~` → ~~text~~
- **Code**: `` `code` `` → `code`
- **Code block**:
  ````
  ```
  multi-line code
  ```
  ````
- **Quote**: `> quoted text`
- **Link**: `<https://example.com|Link Text>`
- **User mention**: `<@U123456>`
- **Channel mention**: `<#C123456>`

### Block Kit Examples

#### Simple Alert
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "⚠️ Alert: High CPU Usage"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Host*: vppipsecgw04.iad0\n*CPU*: 95%\n*Time*: 2026-02-23 10:30 UTC"
      }
    },
    {
      "type": "context",
      "elements": [
        {
          "type": "mrkdwn",
          "text": "Posted by Claude Code"
        }
      ]
    }
  ]
}
```

#### Deployment Summary
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🚀 Deployment Summary"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*POP*\niad0"
        },
        {
          "type": "mrkdwn",
          "text": "*Build*\n134.0.0.3391"
        },
        {
          "type": "mrkdwn",
          "text": "*Hosts*\n5 gateways"
        },
        {
          "type": "mrkdwn",
          "text": "*Duration*\n12 minutes"
        }
      ]
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Status*: ✅ All hosts deployed successfully"
      }
    },
    {
      "type": "divider"
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Deployed Hosts:*\n• vppipsecgw01.iad0 ✓\n• vppipsecgw02.iad0 ✓\n• vppipsecgw03.iad0 ✓\n• vppipsecgw04.iad0 ✓\n• vppipsecgw05.iad0 ✓"
      }
    }
  ]
}
```

#### Test Results
```json
{
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🧪 Scale Test Results"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Test*: VPP IPSEC Gateway - 50k Tunnels\n*Build*: 134.0.0.3391\n*Duration*: 2 hours"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Tunnels Created*\n50,000"
        },
        {
          "type": "mrkdwn",
          "text": "*Success Rate*\n99.95%"
        },
        {
          "type": "mrkdwn",
          "text": "*Avg Latency*\n2.1 ms"
        },
        {
          "type": "mrkdwn",
          "text": "*CPU Usage*\n45%"
        }
      ]
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "✅ *Result*: PASSED - All KPIs within acceptable range"
      }
    }
  ]
}
```

## Implementation Guide

### Step 1: Get Slack Token

```python
import os
import json

def get_slack_token():
    """Get Slack bot token from environment or config."""
    # Try environment variable first
    token = os.environ.get('SLACK_BOT_TOKEN')
    if token:
        return token

    # Try config file
    config_path = os.path.expanduser('~/.claude/slack_config.json')
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
            return config.get('slack_bot_token')

    # Try reading from slack-bot systemd service
    try:
        with open('/etc/systemd/system/claude-slack-bot.service.d/override.conf') as f:
            for line in f:
                if 'SLACK_BOT_TOKEN' in line:
                    return line.split('=')[1].strip().strip('"')
    except FileNotFoundError:
        pass

    return None
```

### Step 2: Send Message

```python
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def send_slack_message(channel, text, thread_ts=None, blocks=None):
    """
    Send message to Slack channel.

    Args:
        channel: Channel name (#channel) or ID
        text: Message text (fallback for notifications)
        thread_ts: Optional thread timestamp to reply in thread
        blocks: Optional Block Kit blocks for rich formatting

    Returns:
        dict: Response with 'ok', 'ts', 'channel', 'message_link'
    """
    token = get_slack_token()
    if not token:
        return {"ok": False, "error": "No Slack token found"}

    client = WebClient(token=token)

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
            "message_link": message_link
        }

    except SlackApiError as e:
        return {
            "ok": False,
            "error": e.response['error'],
            "details": str(e)
        }
```

### Step 3: Usage in Claude Code

When user requests to send a Slack message:

1. **Parse request** to extract channel and message
2. **Get token** using `get_slack_token()`
3. **Format message** (plain text or Block Kit)
4. **Send message** using `send_slack_message()`
5. **Confirm to user** with message link

## Common Channel IDs (Netskope)

Store frequently used channels for quick access:

```json
{
  "channels": {
    "deployments": "C01234ABCD",
    "incidents": "C56789EFGH",
    "testing": "C11111TEST",
    "team-updates": "C22222UPDT",
    "alerts": "C33333ALRT"
  }
}
```

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `not_in_channel` | Bot not added to channel | Invite bot to channel or use public channel |
| `channel_not_found` | Invalid channel ID/name | Verify channel exists and bot has access |
| `invalid_auth` | Invalid token | Check SLACK_BOT_TOKEN is valid |
| `missing_scope` | Bot lacks permission | Add required scopes to Slack app |
| `rate_limited` | Too many requests | Implement rate limiting, wait and retry |
| `message_too_long` | Message exceeds limit | Split into multiple messages or use file upload |

### Example Error Handler

```python
def handle_slack_error(error_code, channel):
    """Provide helpful error messages."""
    if error_code == 'not_in_channel':
        return f"❌ Bot is not in channel {channel}. Please invite the bot first:\n  /invite @Claude"
    elif error_code == 'channel_not_found':
        return f"❌ Channel {channel} not found. Check channel name or ID."
    elif error_code == 'invalid_auth':
        return "❌ Invalid Slack token. Please check SLACK_BOT_TOKEN environment variable."
    elif error_code == 'rate_limited':
        return "⏱️ Rate limited. Please wait a moment and try again."
    else:
        return f"❌ Slack API error: {error_code}"
```

## Integration with Other Skills

### With self-service-skill (Deployments)

After deployment completes, automatically notify Slack:

```python
# After successful deployment
send_slack_message(
    channel="#deployments",
    text="Deployment completed",
    blocks=build_deployment_summary_blocks(deployment_info)
)
```

### With prod-pdv (Testing)

After PDV testing completes, post results:

```python
# After PDV completion
send_slack_message(
    channel="#testing",
    text="PDV test results",
    blocks=build_test_results_blocks(pdv_results)
)
```

### With sumo_logic (Alerts)

When critical issues detected in logs, send alert:

```python
# After log analysis finds issues
send_slack_message(
    channel="#incidents",
    text=f"Alert: {issue_summary}",
    blocks=build_alert_blocks(log_analysis)
)
```

## Example Workflows

### Workflow 1: Manual Message

```
User: Send message to slack #deployments
Assistant: What's the message?
User: Starting deployment to phl1 POP - ETA 15 minutes
Assistant: [Sends message]
✓ Message sent to #deployments
🔗 https://netskope.slack.com/archives/C123.../p1706024400
```

### Workflow 2: Deployment Notification (Automated)

```
User: Deploy build 134.0.0.3391 to vppipsecgw04.iad0 and notify slack
Assistant: [Performs deployment]
Deployment in progress...
[After completion]
✓ Deployment completed successfully
✓ Notification sent to #deployments
🔗 https://netskope.slack.com/archives/C123.../p1706024500
```

### Workflow 3: Test Results Sharing

```
User: Post test results to slack #testing
Assistant: What results should I share?
User: Performance test: 50k tunnels, 99.9% success, 2ms latency
Assistant: [Formats and sends]
✓ Test results posted to #testing
🔗 https://netskope.slack.com/archives/C123.../p1706024600
```

### Workflow 4: Alert on Issue Detection

```
User: Check sumo logs for tenant 18548 and alert if issues found
Assistant: [Queries Sumo Logic]
Found 15 tunnel flaps in last hour for tenant 18548
Should I send alert to Slack?
User: Yes, #incidents
Assistant: [Sends formatted alert]
🚨 Alert sent to #incidents
🔗 https://netskope.slack.com/archives/C123.../p1706024700
```

## Configuration File Format

**Location**: `~/.claude/slack_config.json`

```json
{
  "slack_bot_token": "xoxb-your-slack-bot-token",
  "default_channel": "#general",
  "channels": {
    "deployments": "C01234ABCD",
    "incidents": "C56789EFGH",
    "testing": "C11111TEST",
    "team-updates": "C22222UPDT"
  },
  "auto_notify": {
    "deployments": true,
    "test_results": true,
    "incidents": true
  },
  "mention_users": {
    "vikash": "U01234VKAS",
    "team-lead": "U56789LEAD"
  }
}
```

## Testing

### Test Message Send

```bash
python3 << 'EOF'
from slack_sdk import WebClient
import os

token = os.environ.get('SLACK_BOT_TOKEN')
client = WebClient(token=token)

response = client.chat_postMessage(
    channel="#test-channel",
    text="Test message from Claude Code CLI - slack-notify skill"
)

print(f"✓ Test message sent successfully")
print(f"  Timestamp: {response['ts']}")
print(f"  Channel: {response['channel']}")
EOF
```

### Test Token Verification

```bash
python3 << 'EOF'
from slack_sdk import WebClient
import os

token = os.environ.get('SLACK_BOT_TOKEN')
client = WebClient(token=token)

try:
    response = client.auth_test()
    print(f"✓ Token is valid")
    print(f"  User: {response['user']}")
    print(f"  Team: {response['team']}")
    print(f"  Bot ID: {response['user_id']}")
except Exception as e:
    print(f"✗ Token validation failed: {e}")
EOF
```

## Best Practices

1. **Always include fallback text**: Even when using Block Kit, provide plain text for notifications
2. **Use threads for updates**: Reply in threads to keep channels clean
3. **Format appropriately**: Use Block Kit for rich content, plain text for simple messages
4. **Include context**: Add timestamps, user info, source in message footer
5. **Handle errors gracefully**: Provide clear error messages if send fails
6. **Respect rate limits**: Don't spam channels with too many messages
7. **Use appropriate channels**: Post to correct channel based on message type
8. **Add message links**: Always return the message link for user reference

## Limitations

- Maximum message length: 40,000 characters (plain text), 3,000 characters per block
- Maximum blocks per message: 50
- Rate limit: ~1 message per second per channel (Tier 3)
- File size limit: 1 GB per file
- Bot must be member of private channels to post

## Support

For issues with this skill:
1. Verify SLACK_BOT_TOKEN is valid
2. Check bot is invited to target channel
3. Verify bot has required permissions (chat:write, chat:write.public)
4. Check Slack API status: https://status.slack.com
5. Review error message and consult error handling table

## Future Enhancements

Potential additions:
- Schedule messages for later delivery
- Edit/delete previously sent messages
- Add reactions to messages
- Create/update channel topics
- Send ephemeral messages (visible only to specific user)
- Upload and share files
- Create message templates for common scenarios
- Integration with Claude memory for context-aware notifications