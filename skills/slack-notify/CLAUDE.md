# Slack Notify Skill - Agent Instructions

## Overview
This skill enables sending messages to Slack channels and users. Use it to send notifications, alerts, deployment updates, test results, and status messages.

## When to Activate

Automatically activate this skill when user requests:
- "send message to slack"
- "notify slack channel"
- "post to slack"
- "send alert to slack"
- "slack notify [channel]"
- "alert [channel] on slack"
- "post update to slack"

## Implementation Approach

### Method 1: Direct Bash with Python (Recommended)

Use inline Python script with Bash tool to send messages:

```python
python3 << 'EOF'
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
import sys

# Get token
token = os.environ.get('SLACK_BOT_TOKEN')
if not token:
    print("❌ Error: SLACK_BOT_TOKEN not found in environment")
    sys.exit(1)

# Initialize client
client = WebClient(token=token)

# Send message
try:
    response = client.chat_postMessage(
        channel="#CHANNEL_NAME",
        text="MESSAGE_TEXT",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "MESSAGE_TEXT"
                }
            }
        ]
    )

    # Build message link
    channel_id = response['channel']
    message_ts = response['ts'].replace('.', '')
    message_link = f"https://netskope.slack.com/archives/{channel_id}/p{message_ts}"

    print(f"✓ Message sent to #CHANNEL_NAME")
    print(f"🔗 {message_link}")

except SlackApiError as e:
    print(f"❌ Error sending message: {e.response['error']}")
    sys.exit(1)
EOF
```

### Method 2: Using Helper Script

If slack_send.py exists in skill directory:

```bash
cd ~/.claude/skills/slack-notify
python3 slack_send.py --channel "#deployments" --message "Deployment completed"
```

## Message Flow

### 1. Simple Text Message

When user says: "Send message to slack #deployments saying deployment complete"

1. Extract channel: `#deployments`
2. Extract message: `deployment complete`
3. Send using Bash + Python inline script
4. Return confirmation with message link

### 2. Formatted Message

When user wants rich formatting (title, fields, colors):

1. Prompt for details if not provided:
   - Title
   - Message body
   - Color (optional: good/warning/danger)
2. Build Block Kit payload
3. Send with blocks parameter
4. Return confirmation

### 3. Automated Notification

After completing an operation (deployment, test, etc.):

1. Ask user: "Should I notify Slack?"
2. If yes, ask which channel
3. Generate appropriate summary
4. Send formatted message
5. Continue with remaining tasks

## Token Acquisition

Priority order:

1. **Check environment**: `echo $SLACK_BOT_TOKEN`
2. **Check config**: `cat ~/.claude/slack_config.json`
3. **Check systemd service**: `grep SLACK_BOT_TOKEN /etc/systemd/system/claude-slack-bot.service.d/override.conf`

If no token found:
```
❌ Slack token not found. Please set SLACK_BOT_TOKEN:
   export SLACK_BOT_TOKEN="xoxb-your-token-here"
```

## Block Kit Message Patterns

### Deployment Summary

```python
blocks = [
    {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": "🚀 Deployment Complete"
        }
    },
    {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": f"*POP*\n{pop}"},
            {"type": "mrkdwn", "text": f"*Build*\n{build}"},
            {"type": "mrkdwn", "text": f"*Hosts*\n{host_count}"},
            {"type": "mrkdwn", "text": f"*Duration*\n{duration}"}
        ]
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Status*: ✅ {status_message}"
        }
    }
]
```

### Alert Message

```python
blocks = [
    {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"🚨 {alert_level}: {alert_title}"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": alert_message
        }
    },
    {
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"Posted by Claude Code • {timestamp}"
            }
        ]
    }
]
```

### Test Results

```python
blocks = [
    {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": "🧪 Test Results"
        }
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"*Test*: {test_name}\n*Build*: {build_version}\n*Duration*: {duration}"
        }
    },
    {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": f"*Success Rate*\n{success_rate}"},
            {"type": "mrkdwn", "text": f"*Avg Latency*\n{latency}"},
            {"type": "mrkdwn", "text": f"*Throughput*\n{throughput}"},
            {"type": "mrkdwn", "text": f"*CPU Usage*\n{cpu_usage}"}
        ]
    },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"{result_icon} *Result*: {result_status}"
        }
    }
]
```

## Integration Examples

### With self-service-skill

After deployment completes:

```python
# Inside deployment completion handler
if deployment_successful:
    # Ask user
    response = ask_user("Should I notify Slack about this deployment?")
    if response == "yes":
        channel = ask_user("Which channel?") or "#deployments"
        send_deployment_notification(channel, deployment_info)
```

### With prod-pdv

After PDV testing:

```python
# After PDV completion
if pdv_completed:
    send_slack_message(
        channel="#testing",
        text=f"PDV test completed for {pop}",
        blocks=build_pdv_results_blocks(results)
    )
```

### With sumo_logic

After log analysis finds issues:

```python
# After analyzing logs
if critical_issues_found:
    send_slack_message(
        channel="#incidents",
        text=f"Critical: {issue_count} tunnel flaps detected",
        blocks=build_incident_alert_blocks(log_analysis)
    )
```

## Error Handling

### Common Errors and Responses

| Error | User Message | Action |
|-------|-------------|--------|
| `not_in_channel` | "❌ Bot is not in channel {channel}. Please invite bot: `/invite @Claude`" | Stop and inform user |
| `channel_not_found` | "❌ Channel {channel} not found. Please check the channel name." | Ask user to provide correct channel |
| `invalid_auth` | "❌ Invalid Slack token. Please set SLACK_BOT_TOKEN environment variable." | Stop and provide instructions |
| `rate_limited` | "⏱️ Rate limited. Waiting 1 second and retrying..." | Wait and retry once |

### Error Handler Template

```python
except SlackApiError as e:
    error_code = e.response['error']
    if error_code == 'not_in_channel':
        print(f"❌ Bot is not in channel {channel}")
        print("   Please invite the bot: /invite @Claude")
    elif error_code == 'channel_not_found':
        print(f"❌ Channel {channel} not found")
        print("   Check the channel name or ID")
    elif error_code == 'invalid_auth':
        print("❌ Invalid Slack token")
        print("   Set SLACK_BOT_TOKEN: export SLACK_BOT_TOKEN='xoxb-...'")
    elif error_code == 'rate_limited':
        print("⏱️ Rate limited. Waiting 1 second...")
        time.sleep(1)
        # Retry once
    else:
        print(f"❌ Slack API error: {error_code}")
        print(f"   Details: {str(e)}")
```

## Response Format

After sending message successfully:

```
✓ Message sent to #CHANNEL_NAME
🔗 https://netskope.slack.com/archives/C123ABC/p1706024400000000
```

For formatted messages, add preview:

```
✓ Deployment summary sent to #deployments
📊 Summary:
   • POP: iad0
   • Build: 134.0.0.3391
   • Hosts: 5 gateways
   • Status: All successful
🔗 https://netskope.slack.com/archives/C123ABC/p1706024400000000
```

## Channel Name Handling

Accept multiple formats:
- `#channel-name` (with hash)
- `channel-name` (without hash)
- `C123456ABC` (channel ID)
- `@username` (direct message)
- `U123456ABC` (user ID)

Normalize before sending:
```python
def normalize_channel(channel):
    """Normalize channel input."""
    channel = channel.strip()
    # Slack API handles both #channel and channel formats
    # No need to strip # prefix
    return channel
```

## Best Practices for Agent

1. **Always confirm before sending**: Show message preview and ask "Send this to Slack?"
   - Exception: When user explicitly says "and notify slack" in the same command

2. **Use appropriate formatting**:
   - Plain text for simple messages
   - Block Kit for summaries, alerts, results

3. **Include context**: Add timestamp, source, relevant metadata in footer

4. **Handle errors gracefully**: Provide clear, actionable error messages

5. **Return message link**: Always provide the Slack message URL for reference

6. **Don't spam**: If sending multiple updates, ask user first or use threads

7. **Verify token once**: Check token validity before first message, cache result

8. **Use common channels**: For Netskope:
   - `#deployments` - deployment notifications
   - `#testing` - test results
   - `#incidents` - alerts and incidents
   - `#team-updates` - general status updates

## Example Interactions

### Example 1: Simple Message

```
User: Send message to slack #deployments
Agent: What message should I send?
User: Deployment to iad0 started
Agent: [Sends message using inline Python]
✓ Message sent to #deployments
🔗 https://netskope.slack.com/archives/C123/p1706024400
```

### Example 2: Formatted Alert

```
User: Send alert to slack #incidents
Agent: What's the alert?
User: P1 Incident: ECGW service down in IAD datacenter
Agent: [Builds formatted alert with Block Kit]
✓ Alert sent to #incidents
🚨 P1 Incident: ECGW service down in IAD datacenter
🔗 https://netskope.slack.com/archives/C123/p1706024500
```

### Example 3: Automated Notification

```
User: Deploy build 134.0.0.3391 to vppipsecgw04.iad0 and notify slack
Agent: [Performs deployment]
Deployment in progress...
[Deployment completes successfully]
✓ Deployment completed
✓ Notification sent to #deployments
🔗 https://netskope.slack.com/archives/C123/p1706024600
```

### Example 4: Integration with Test Results

```
User: Run PDV on phl1 and post results to slack
Agent: [Runs PDV tests]
Running PDV tests on phl1...
[Tests complete]
✓ PDV tests completed - all checks passed
✓ Results posted to #testing
🔗 https://netskope.slack.com/archives/C123/p1706024700
```

## Token Security

**IMPORTANT**: Never log or display the full token. If showing token info:

```
✓ Using Slack token: xoxb-****-****-****-**********wx (last 4 chars: ...vwx)
```

## Dependencies

Required Python packages:
```bash
pip3 install slack-sdk
```

Verify installation:
```bash
python3 -c "from slack_sdk import WebClient; print('✓ slack-sdk installed')"
```

## Testing This Skill

Before using in production:

1. **Test token**:
   ```bash
   python3 -c "from slack_sdk import WebClient; import os; client = WebClient(token=os.environ['SLACK_BOT_TOKEN']); print(client.auth_test())"
   ```

2. **Test message**:
   ```bash
   python3 << 'EOF'
from slack_sdk import WebClient
import os
client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
response = client.chat_postMessage(channel="#test", text="Test from claude-notify skill")
print(f"✓ Test message sent: {response['ts']}")
EOF
   ```

3. **Test error handling**:
   - Send to non-existent channel (should handle gracefully)
   - Send with invalid token (should provide clear error)
   - Send to channel bot is not in (should guide user)

## Notes

- This skill requires `slack-sdk` Python package
- Token must have `chat:write` and `chat:write.public` scopes
- Bot must be invited to private channels before posting
- Rate limit is ~1 message/second per channel
- Message length limit: 40,000 characters (text), 3,000 per block
- Maximum 50 blocks per message

## Troubleshooting

**Message not appearing?**
- Check bot is in channel: `/invite @Claude`
- Verify token has correct scopes
- Check channel name spelling

**"not_in_channel" error?**
- Invite bot to channel first
- For public channels, enable `chat:write.public` scope

**"invalid_auth" error?**
- Verify SLACK_BOT_TOKEN is set
- Check token starts with `xoxb-`
- Regenerate token if expired

**Rate limited?**
- Wait 1 second between messages
- Use threads for multiple updates
- Batch updates into single formatted message