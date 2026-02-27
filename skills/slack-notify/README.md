# Slack Notify Skill

Send messages and alerts to Slack channels directly from Claude Code CLI.

## Quick Start

### 1. Set up Slack token

```bash
export SLACK_BOT_TOKEN="xoxb-your-token-here"
```

Or create config file:

```bash
mkdir -p ~/.claude
cat > ~/.claude/slack_config.json << 'EOF'
{
  "slack_bot_token": "xoxb-your-token-here",
  "default_channel": "#general"
}
EOF
```

### 2. Install dependencies

```bash
pip3 install slack-sdk
```

### 3. Send a message

#### Using Python helper script:

```bash
cd ~/.claude/skills/slack-notify
python3 slack_send.py --channel "#general" --message "Hello from Claude!"
```

#### Using Claude Code:

```
You: Send message to slack #deployments
Claude: What message should I send?
You: Deployment to iad0 completed successfully
Claude: ✓ Message sent to #deployments
        🔗 https://netskope.slack.com/archives/...
```

## Usage Examples

### Simple message

```bash
python3 slack_send.py --channel "#deployments" --message "Deployment complete"
```

### Formatted alert

```bash
python3 slack_send.py \
    --channel "#incidents" \
    --title "🚨 P1 Incident" \
    --message "ECGW service down in IAD datacenter" \
    --color danger \
    --field "Status:Investigating" \
    --field "Impact:Customer Facing"
```

### Thread reply

```bash
python3 slack_send.py \
    --channel "#general" \
    --message "Update: issue resolved" \
    --thread-ts 1706024400.123456
```

### Custom Block Kit

```bash
python3 slack_send.py \
    --channel "#deployments" \
    --blocks deployment_summary.json
```

## Common Channels (Netskope)

- `#deployments` - Deployment notifications
- `#incidents` - Alerts and incidents
- `#testing` - Test results
- `#team-updates` - General status updates

## Activation Patterns

Say any of these to activate the skill:
- "send message to slack"
- "notify slack channel"
- "post to slack"
- "send alert to slack"
- "alert #channel on slack"

## Files

- `SKILL.md` - Complete skill documentation
- `CLAUDE.md` - Agent implementation instructions
- `slack_send.py` - Python helper script
- `README.md` - This file
- `example_blocks.json` - Example Block Kit JSON
- `slack_config.example.json` - Example configuration

## Verification

Test your setup:

```bash
python3 slack_send.py --verify
```

## Documentation

See `SKILL.md` for complete documentation including:
- All available commands
- Block Kit message examples
- Integration with other skills
- Error handling
- API reference

## Support

Common issues:

**"SLACK_BOT_TOKEN not found"**
- Set environment variable: `export SLACK_BOT_TOKEN="xoxb-..."`
- Or create config: `~/.claude/slack_config.json`

**"not_in_channel" error**
- Invite bot to channel: `/invite @Claude` in Slack

**"invalid_auth" error**
- Verify token starts with `xoxb-`
- Check token is not expired
- Regenerate token in Slack app settings

## Integration

This skill integrates with:
- `self-service-skill` - Post deployment notifications
- `prod-pdv` - Share test results
- `sumo_logic` - Alert on issues found in logs
- `polaris` - Notify about infrastructure changes