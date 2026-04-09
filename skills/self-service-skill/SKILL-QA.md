name: self-service-qa
description: QA/Non-production deployment for VPP-based services. Full automation with optional POP detection.

# QA Deployment Guide

---

## Required Environment Variables

```bash
JENKINS_QA_URL     # e.g. https://your-qa-jenkins.company.com/
JENKINS_USERNAME   # e.g. user@company.com
JENKINS_QA_TOKEN   # Jenkins API token for QA
JENKINS_JOB_PREFIX # e.g. one_button  → job = one_button_<service>

# Optional — only needed for auto POP detection via GitHub
GITHUB_TOKEN       # GitHub personal access token (repo scope)
```

---

## QA POPs

- `c*` where `*` is a digit — `c1`, `c7`, `c18`
- `iad0`
- `stg*` — `stg01`

---

## User-Provided Parameters

| Parameter | Required | Notes |
|-----------|----------|-------|
| `POPS` or hostname | Yes | POP name or hostname to detect POP from |
| `RELEASE` | Yes | Build version, e.g. `133.0.3.2830` |
| `ANSIBLE_CONFIG_IMAGE_TAG` | No | Auto-fetched from GitHub if not provided |
| `TICKET` | No | Defaults to `ENG-12345` |
| `SERVICE` | No | Auto-detected from hostname pattern |

### Service Auto-Detection from Hostname

| Hostname pattern | Service |
|-----------------|---------|
| `vppipsecgw*`, `ipsecgw*` | `nsvppipsecgw` |
| `ecgw*` | `ecgw` |
| `gregw*`, `vppgregw*` | `nsvppgregw` |
| `steeringlb*` | `steeringlb` |

---

## POP Detection (Optional Automation)

If the user provides a hostname instead of a POP, auto-detect the POP from GitHub inventory repos.

**GitHub repo mapping:**

| Service | Inventory Repo |
|---------|---------------|
| `nsvppipsecgw` | `<your-org>/nsvppipsecgw-ansible-config` |
| `nsvppgregw` | `<your-org>/nsvppgregw-ansible-config` |
| `ecgw` | `<your-org>/ecgw-ansible-config` |
| `steeringlb` | `<your-org>/steeringlb-ansible-config` |

Search the repo's inventory files for the hostname to find which POP it belongs to. Update the repo paths above to match your organization.

If `GITHUB_TOKEN` is not set or POP detection fails, ask the user to provide the POP manually.

---

## Deployment Workflow

### Immediate Deployment

No confirmation required for QA. Deploy automatically once parameters are gathered.

**Step 1 — Collect Parameters**

```
Input:   vppipsecgw04.c18.iad0.company.com
Service: nsvppipsecgw  (detected from hostname)
POP:     c18-iad0      (detected via GitHub inventory, or provided by user)
TAG:     auto-fetch latest from GitHub, or use user-provided value
RELEASE: from user
TICKET:  from user, or default ENG-12345
```

**Step 2 — Trigger Jenkins**

Read `CONFIG.md` for the correct job name and parameter list for QA, then build the command:

```bash
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"

java -jar ~/.claude/jenkins-cli.jar \
  -s "${JENKINS_QA_URL}" \
  -auth "${JENKINS_USERNAME}:${JENKINS_QA_TOKEN}" \
  build "<job name from CONFIG.md>" -s \
  -p POPS=<pop> \
  -p ANSIBLE_HOSTGROUPS=<hostname> \
  -p RELEASE=<version> \
  -p ANSIBLE_CONFIG_IMAGE_TAG=<tag> \
  -p ANSIBLE_COMPONENT_NAME=<SERVICE> \
  -p ANSIBLE_CONFIG_IMAGE_NAME=<SERVICE>-ansible-config \
  # Add/remove remaining -p flags based on QA Fixed Parameters in CONFIG.md

echo "✅ QA deployment complete"
```

**Note**: `ANSIBLE_HOSTGROUPS` uses the **hostname** in QA (unlike Production which uses the service name). All other parameters come from `CONFIG.md`.

---

### Hash-Based Deployment (QA Only)

When the user provides a git commit hash instead of a release tag for `ANSIBLE_CONFIG_IMAGE_TAG`:

```bash
# Use develop channel instead of release channel
-p ANSIBLE_CONFIG_IMAGE_TAG=<40-char-hash> \
-p ANSIBLE_ARTIFACTORY_CHANNEL=ipsec-gre-develop-docker
```

Indicators: user mentions "hash", "ansible_tags as hash", or provides a 40-character hex string.

---

### Scheduled Deployment (QA)

Follows the same format as Production scheduled deployments. All times in **UTC**.

```
Schedule [DD-Mon, Day]
Common Parameters:
  RELEASE: 133.0.3.2830
  SERVICE: nsvppgregw

9:30AM UTC
  c7-iad0, c18-iad0

2:00PM UTC
  iad0
```

For each slot: sleep until scheduled time → notify user → ask permission → trigger deployment.
