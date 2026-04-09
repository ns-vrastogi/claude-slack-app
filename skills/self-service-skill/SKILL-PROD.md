name: self-service-production
description: Production deployment for VPP-based services. Supports immediate and scheduled deployments via Jenkins CLI.

# Production Deployment Guide

---

## Safety Rules

1. **Mandatory confirmation** — Always show full parameters and get explicit user approval before triggering
2. **Never kill Jenkins CLI** — Sync mode (`-s`) blocks until completion; killing it sends ABORT to Jenkins and may leave systems in inconsistent state
3. **Never deploy to unlisted POPs** — Only deploy to POPs the user explicitly requested
4. **No retries without checking** — If trigger appears to fail, verify no build was queued before retrying
5. **When in doubt, stop and ask**

---

## Required Environment Variables

```bash
JENKINS_PROD_URL     # e.g. https://your-jenkins.company.com/
JENKINS_USERNAME     # e.g. user@company.com
JENKINS_PROD_TOKEN   # Jenkins API token
JENKINS_JOB_PREFIX   # e.g. one_button  → job = one_button_<service>
```

---

## User-Provided Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `POPS` | Target POP(s), comma-separated, lowercase | `los1,ams1` |
| `RELEASE` | Build version | `134.0.2.3026` |
| `ANSIBLE_CONFIG_IMAGE_TAG` | Ansible config tag | `134.0.9` |
| `TICKET` | Ticket reference | `ENG-864088` |
| `SERVICE` | Service name | `nsvppgregw` |

---

## Deployment Workflow

### Step 1 — Collect Parameters

Ask the user for: POPS, RELEASE, ANSIBLE_CONFIG_IMAGE_TAG, TICKET, SERVICE.

Auto-derive:
- `ANSIBLE_HOSTGROUPS` = SERVICE
- `ANSIBLE_COMPONENT_NAME` = SERVICE
- `ANSIBLE_CONFIG_IMAGE_NAME` = `<SERVICE>-ansible-config`

---

### Step 2 — Mandatory Confirmation

Display the full parameter block and wait for explicit **yes** before proceeding:

```
========================================
PRODUCTION DEPLOYMENT CONFIRMATION
========================================
Jenkins:  ${JENKINS_PROD_URL}
Job:      ${JENKINS_JOB_PREFIX}_<SERVICE>

POPS:                     <pops>
RELEASE:                  <version>
ANSIBLE_CONFIG_IMAGE_TAG: <tag>
ANSIBLE_HOSTGROUPS:       <SERVICE>
ANSIBLE_COMPONENT_NAME:   <SERVICE>
ANSIBLE_CONFIG_IMAGE_NAME:<SERVICE>-ansible-config
TICKET:                   <ticket>

⚠️  This will trigger a PRODUCTION deployment.

Proceed? (yes/no)
========================================
```

**DO NOT proceed unless user says yes.**

---

### Step 3 — Pre-Deployment Safety Check

Check for running builds before triggering:

```bash
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"

RUNNING=$(curl -s -u "${JENKINS_USERNAME}:${JENKINS_PROD_TOKEN}" \
  "${JENKINS_PROD_URL}/job/${JENKINS_JOB_PREFIX}_<SERVICE>/api/json?tree=builds[number,building]{0,5}" \
  | python3 -c "import sys,json; builds=json.load(sys.stdin)['builds']; print(next((str(b['number']) for b in builds if b['building']),'')")

if [ -n "$RUNNING" ]; then
  echo "⚠️  Build #${RUNNING} already running — monitoring existing build instead of triggering new one"
  BUILD_NUMBER=$RUNNING
  SKIP_TRIGGER=true
else
  echo "✅ No running builds — safe to trigger"
  SKIP_TRIGGER=false
fi
```

---

### Step 4 — Time Verification (Scheduled Deployments Only)

For scheduled deployments, verify system clock accuracy immediately before triggering:

```bash
SYS_TIME=$(date -u +%s)
REMOTE_TIME=$(date -d "$(curl -sI --max-time 3 https://www.google.com | grep -i '^date:' | cut -d' ' -f2-)" +%s 2>/dev/null)

if [ -n "$REMOTE_TIME" ]; then
  DIFF=$(( ${SYS_TIME#-} - ${REMOTE_TIME#-} ))
  DIFF_ABS=${DIFF#-}
  [ "$DIFF_ABS" -le 5 ] && echo "✅ Time OK" || { echo "❌ Clock drift ${DIFF_ABS}s — sync and retry"; exit 1; }
fi
```

---

### Step 5 — Trigger Jenkins Deployment

```bash
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"

if [ "$SKIP_TRIGGER" = false ]; then
  java -jar ~/.claude/jenkins-cli.jar \
    -s "${JENKINS_PROD_URL}" \
    -auth "${JENKINS_USERNAME}:${JENKINS_PROD_TOKEN}" \
    build "${JENKINS_JOB_PREFIX}_<SERVICE>" -s \
    -p POPS=<pops> \
    -p RELEASE=<version> \
    -p ANSIBLE_CONFIG_IMAGE_TAG=<tag> \
    -p ANSIBLE_HOSTGROUPS=<SERVICE> \
    -p ANSIBLE_COMPONENT_NAME=<SERVICE> \
    -p ANSIBLE_CONFIG_IMAGE_NAME=<SERVICE>-ansible-config \
    -p TICKET=<ticket> \
    -p DEPLOY_TYPE=DEPLOY \
    -p BYPASS_MONITORING_RESULT=YES \
    -p BYPASS_JIRA=YES \
    -p RUN_QE_PDV=DEPLOY_ONLY

  echo $? && echo "✅ Deployment complete"
fi
```

**Notes:**
- `BYPASS_JIRA=YES` and `RUN_QE_PDV=DEPLOY_ONLY` skip JIRA updates and PDV inside Jenkins — remove these if your pipeline doesn't have these parameters
- If trigger fails, wait 15s and check for a recently queued build before retrying
- **Never retry without verifying** — duplicate deployments are worse than a failed trigger

---

## Scheduled Deployment

### Schedule Format

```
Schedule [DD-Mon, Day]
Common Parameters:
  RELEASE: 134.0.2.3026
  ANSIBLE_CONFIG_IMAGE_TAG: 134.0.9
  TICKET: ENG-12345
  SERVICE: nsvppgregw

9:30AM-12:00PM PST
  los1, ams1

2:00PM-4:00PM PST
  del1, bom1
```

### How Scheduled Deployments Work

1. User provides schedule → skill displays full summary and asks for **one-time confirmation**
2. A background task sleeps until each time slot
3. When slot arrives, skill notifies user and asks for **go/no-go** before triggering
4. Deployment runs automatically after approval
5. Repeat for each slot

### POP Safety Check for Scheduled Deployments

Before each slot, verify POPs match the schedule (case-insensitive):

```python
scheduled = [p.lower() for p in scheduled_pops]
deploying  = [p.lower() for p in slot_pops]
for p in deploying:
    if p not in scheduled:
        raise Exception(f"POP {p} is NOT in the approved schedule — aborting")
```

**Never deploy to a POP that wasn't in the original approved schedule.**
