# Credentials & Configuration Setup Guide

All sensitive credentials have been replaced with placeholder keywords in this repository.
Follow this guide to restore your configuration with real values.

---

## 1. `config.json` — Main Claude Code CLI Config

| Placeholder | What to Replace With | Where to Find It |
|-------------|---------------------|-----------------|
| `your-anthropic-api-key` | Anthropic API key | [console.anthropic.com](https://console.anthropic.com) → API Keys |
| `your-gateway-hostname.your-cluster.netskope.com` | SSH gateway host for MCP SSH server | Your QA/dev gateway hostname |
| `your-jenkins-host.netskope.com` | Jenkins base URL | Jenkins instance URL (internal) |
| `your-username@your-company.com` | Jenkins login email | Your Netskope email |
| `your-api-token` *(REST_BASIC_PASSWORD)* | Jenkins API token (QA) | Jenkins → User Settings → API Token |
| `your-sumo-api-id` | Sumo Logic Access ID | Sumo Logic → Admin → Security → Access Keys |
| `your-sumo-api-key` | Sumo Logic Access Key | Same as above |
| `your-org.atlassian.net` | Your Atlassian org URL | Your Atlassian workspace |
| `your-api-token` *(CONFLUENCE_API_TOKEN)* | Atlassian API token | [id.atlassian.com](https://id.atlassian.com) → Security → API Tokens |

---

## 2. `.mcp.json` — JIRA MCP Server Config

| Placeholder | What to Replace With | Where to Find It |
|-------------|---------------------|-----------------|
| `your-org.atlassian.net` | Your Atlassian org URL | Your JIRA workspace URL |
| `your-username@your-company.com` | Your JIRA login email | Your Atlassian email |
| `your-api-token` | Atlassian API token | [id.atlassian.com](https://id.atlassian.com) → Security → API Tokens |

---

## 3. `slack_config.json` — Slack Bot Config

| Placeholder | What to Replace With | Where to Find It |
|-------------|---------------------|-----------------|
| `xoxb-your-slack-bot-token` | Slack Bot OAuth token | Slack API → Your App → OAuth & Permissions → Bot Token |
| `your-channel-id` (deployments) | Slack channel ID for #deployments | Right-click channel → View channel details → Channel ID |
| `your-channel-id` (incidents) | Slack channel ID for #incidents | Same as above |
| `your-channel-id` (testing) | Slack channel ID for #testing | Same as above |
| `your-channel-id` (team-updates) | Slack channel ID for #team-updates | Same as above |
| `your-channel-id` (alerts) | Slack channel ID for #alerts | Same as above |

---

## 4. `skills/self-service-skill/SKILL.md` & `SKILL-QA.md`

| Placeholder | What to Replace With | Where to Find It |
|-------------|---------------------|-----------------|
| `your-username@your-company.com` | Jenkins QA login email | Your Netskope email |
| `your-api-token` *(QA)* | Jenkins QA API token | QA Jenkins → User Settings → API Token |

---

## 5. `skills/self-service-skill/SKILL-PROD.md`

| Placeholder | What to Replace With | Where to Find It |
|-------------|---------------------|-----------------|
| `your-username@your-company.com` | Jenkins Prod login email | Your Netskope email |
| `your-api-token` *(Prod)* | Jenkins Production API token | Prod Jenkins → User Settings → API Token |

---

## 6. `skills/self-service-skill/deploy_monitor.sh`

| Placeholder | What to Replace With | Where to Find It |
|-------------|---------------------|-----------------|
| `your-username@your-company.com:your-api-token` | `JENKINS_AUTH` — Prod Jenkins credential | Your email + Prod Jenkins API token |

---

## 7. `skills/prod-pdv/SKILL.md`

| Placeholder | What to Replace With | Where to Find It |
|-------------|---------------------|-----------------|
| `your-username` | Jenkins username (short form) | Your Netskope username (e.g., `jdoe`) |
| `your-api-token` | Jenkins PDV API token | PDV Jenkins → User Settings → API Token |
| `http://your-jenkins-host:8080/` | PDV Jenkins internal URL | Internal Jenkins URL for PDV testing |

---

## 8. `skills/JIRA-skill/SKILL.md`

| Placeholder | What to Replace With | Where to Find It |
|-------------|---------------------|-----------------|
| `your-username@your-company.com` | Your Atlassian email | Your Atlassian login |
| `your-api-token` | Atlassian API token | [id.atlassian.com](https://id.atlassian.com) → Security → API Tokens |
| `your-jira-account-id` | Your JIRA account ID | JIRA → Profile → `accountId` in URL |

---

## 9. `skills/legacy_deployment/deploy_legacy_gateway.py`

| Placeholder | What to Replace With | Where to Find It |
|-------------|---------------------|-----------------|
| `your-ansible-password` | Ansible/deployment password | Internal Ansible vault / team credentials |

---

## 10. `skills/database/SKILL.md`

| Placeholder | What to Replace With | Where to Find It |
|-------------|---------------------|-----------------|
| `your-api-token` *(Production tenant)* | Production tenant API key | Internal tenant management |
| `your-api-token` *(QA tenant)* | QA tenant API key | Your QA tenant credentials |
| `your-username.qa.boomskope.com` | Your QA tenant URL | Internal QA tenant portal |
| `your-prod-client.compute-1.amazonaws.com` | Production client EC2 hostname | AWS EC2 instance hostname |

---

## 11. `skills/ipsec_tunnel_create/SKILL.md` & `gateway_tunn_creation.py`

| Placeholder | What to Replace With | Where to Find It |
|-------------|---------------------|-----------------|
| `your-psk-value` | Default IPsec PSK (base64) | Internal default PSK for test tunnels |

---

## 12. Path Placeholders

Several files contain `~/` or `/home/your-username/` path references. These are relative paths that automatically resolve to your home directory on your machine. No changes needed for these — they're intentionally generic.

---

## Quick Setup Checklist

- [ ] Replace Anthropic API key in `config.json`
- [ ] Replace Jenkins API tokens (QA + Prod) in `config.json`, `SKILL.md` files, and `deploy_monitor.sh`
- [ ] Replace Sumo Logic credentials in `config.json`
- [ ] Replace JIRA/Confluence API token in `.mcp.json` and `config.json`
- [ ] Replace Slack bot token in `slack_config.json`
- [ ] Update Slack channel IDs in `slack_config.json`
- [ ] Replace PDV Jenkins username and token in `skills/prod-pdv/SKILL.md`
- [ ] Replace Ansible password in `skills/legacy_deployment/deploy_legacy_gateway.py`
- [ ] Replace tenant API tokens in `skills/database/SKILL.md`
- [ ] Replace IPsec PSK in `skills/ipsec_tunnel_create/`
- [ ] Update `skills/vpp_scale_performance/SKILL.md` with actual script paths
