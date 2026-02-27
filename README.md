# Claude Code Configuration & Skills

This repository contains the complete Claude Code CLI configuration and skill set for Netskope IPSEC/GRE infrastructure operations.

## Overview

This configuration powers a Claude Code CLI setup specialized for:
- **IPSEC/GRE gateway** operations, deployment, and troubleshooting
- **VPP (Vector Packet Processing)** performance testing and debugging
- **ECGW** (Enterprise Cloud Gateway) management
- **Scale & performance testing** automation
- **Production deployment** workflows with safety guardrails
- **Sumo Logic** log analysis and tunnel flap diagnostics
- **JIRA** automated ticket creation and management
- **Slack** notification integration

---

## Repository Structure

```
├── config.json              # Claude Code MCP server configuration
├── .mcp.json                # JIRA MCP server configuration
├── settings.json            # Claude Code hooks and model settings
├── CLAUDE.md                # Main Claude agent instructions
├── slack_config.json        # Slack bot configuration
├── CREDENTIALS_SETUP.md     # Guide to fill in credentials
└── skills/                  # Custom Claude Code skills
    ├── database/            # Device inventory (clients, gateways, tenants)
    ├── DITA/                # Test case generation assistant
    ├── ecgw-skill/          # ECGW gateway operations
    ├── feature-skill/       # Feature documentation (HC, CTAP, QoS)
    ├── ipsec_tunnel_create/ # IPsec tunnel creation automation
    ├── JIRA-skill/          # JIRA deployment ticket automation
    ├── legacy_deployment/   # Legacy gateway deployment via Ansible
    ├── legacy_scale_performance/ # Legacy GRE/IPSEC scale testing
    ├── polaris/             # VM/IP/DNS management (Polaris tool)
    ├── prod-pdv/            # Production PDV (DPAS) testing
    ├── self-service-skill/  # VPP gateway self-service deployment (QA + Prod)
    ├── slack-notify/        # Slack notification sender
    ├── sumo_logic/          # Sumo Logic log analysis & RCA
    ├── to-do-skill/         # Task management
    ├── topology-finder-skill/ # Network topology discovery
    ├── vpp_scale_performance/ # VPP GRE/IPSEC scale testing
    └── vpp-skill/           # VPP commands reference
```

---

## Getting Started

### 1. Prerequisites

- [Claude Code CLI](https://claude.ai/claude-code) installed
- `tsh` (Teleport) for remote access
- Python 3.x with `slack-sdk` (`pip3 install slack-sdk`)
- Node.js (for MCP servers)
- Access to internal Netskope infrastructure

### 2. Clone and Configure

```bash
git clone https://github.com/ns-vrastogi/claude-slack-app.git
cd claude-slack-app
```

### 3. Fill in Credentials

See **[CREDENTIALS_SETUP.md](CREDENTIALS_SETUP.md)** for a complete guide on which credentials to fill in and where to get them.

All sensitive values have been replaced with placeholder keywords like:
- `your-anthropic-api-key`
- `your-api-token`
- `your-username@your-company.com`
- `xoxb-your-slack-bot-token`

### 4. Place Config Files

```bash
cp config.json ~/.claude/config.json
cp .mcp.json ~/.claude/.mcp.json
cp settings.json ~/.claude/settings.json
cp CLAUDE.md ~/.claude/CLAUDE.md
cp slack_config.json ~/.claude/slack_config.json
cp -r skills/ ~/.claude/skills/
```

---

## Key Skills

### Deployment Skills
| Skill | Purpose |
|-------|---------|
| `self-service-skill` | VPP IPSEC/GRE/ECGW deployment (QA + Production) with auto-scheduling |
| `legacy_deployment` | Legacy gateway deployment via Ansible |

### Testing Skills
| Skill | Purpose |
|-------|---------|
| `vpp_scale_performance` | VPP scale & performance testing automation |
| `legacy_scale_performance` | Legacy GRE/IPSEC scale testing |
| `prod-pdv` | Production PDV/DPAS validation testing |
| `DITA` | Dynamic test case generation |

### Operations Skills
| Skill | Purpose |
|-------|---------|
| `topology-finder-skill` | Discover and map network topology |
| `sumo_logic` | Sumo Logic log queries and tunnel flap analysis |
| `ipsec_tunnel_create` | Create IPsec tunnels on VPP/legacy gateways |

### Infrastructure Skills
| Skill | Purpose |
|-------|---------|
| `polaris` | VM creation, IP allocation, DNS management |
| `database` | Device inventory and reservation |
| `ecgw-skill` | ECGW-specific operations |
| `vpp-skill` | VPP commands reference |

### Notification/Tracking Skills
| Skill | Purpose |
|-------|---------|
| `slack-notify` | Send messages and alerts to Slack |
| `JIRA-skill` | Create and manage deployment tickets |
| `to-do-skill` | Personal task list management |
| `feature-skill` | Feature documentation and HC/CTAP/QoS reference |

---

## Architecture

All three gateway types (IPSEC, GRE, ECGW) share:
- Traffic flows from **Steering LB** → Gateway → **Proxy/CFW**
- Remote service configs in `/opt/nc/common/remote/`
- Tenant configs in `/opt/ns/tenant/<tenant-id>/`
- Health checks from gateway to Proxy and CFW

---

## Security Note

All credentials, API tokens, passwords, and personal identifiers have been removed from this repository. See [CREDENTIALS_SETUP.md](CREDENTIALS_SETUP.md) for setup instructions.

**Never commit real credentials to this repository.**

---

## Excluded Skills

The following skills are not included in this repository (personal/environment-specific):
- `survey-tool` — Survey VM Tool configuration (separate repo: `survey_vm_conf`)
- `slack-bot-deployment` — Slack bot VM deployment (environment-specific)
