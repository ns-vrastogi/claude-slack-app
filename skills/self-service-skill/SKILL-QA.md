name: self-service-qa
description: QA/Non-production deployment instructions for VPP-based services (ecgw, nsvppgregw, nsvppipsecgw, steeringlb) with full automation support.

# QA/Non-Production Deployment Guide

## QA Environment

- **Jenkins URL**: `https://cdjenkins.betaskope.iad0.netskope.com`
- **Username**: `your-username@your-company.com`
- **API Token**: `your-api-token`
- **Methods**: Jenkins CLI (preferred) or REST API
- **Automation**: Full automation with POP detection and parameter defaults
- **Approval**: No confirmation required (auto-deploy)

## QA POPs

POPs starting with:
- `c*` where * is a digit: `c1`, `c7`, `c18`, `c19`
- `iad*`: `iad0`, `iad2`, `iad4`
- `stg*`: `stg01`

Examples: `c7-iad0`, `c18-iad0`, `iad0`, `iad2`, `stg01`

## Prerequisites

### GitHub Token Setup

Required for POP detection automation.

```bash
# Add to ~/.zshrc or ~/.bash_profile
export GITHUB_TOKEN="your_token_here"
source ~/.zshrc
```

**Token Requirements:**
- Scope: `repo` (for private repository access)
- SSO: Must be authorized for the `netSkope` organization
- Generate at: https://github.com/settings/tokens

### Java Setup

Required for Jenkins CLI.

```bash
# Install Java OpenJDK 17+
brew install openjdk@17

# Add to PATH
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"

# Add to ~/.zshrc for persistence
echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc
```

## Automation Scripts

### 1. POP Detection Script

**Location**: `~/.claude/scripts/detect_pop.sh`

**Purpose**: Auto-detect correct POP from hostname by searching GitHub inventory files.

**Why needed**: A hostname like `vppipsecgw04.c18.iad0.netskope.com` might actually be in the `c7-iad0` inventory, not `c18`.

**Usage:**
```bash
./detect_pop.sh "vppipsecgw04.c18.iad0.netskope.com"
```

**Returns**: Matching POP(s) from inventory (e.g., `c7-iad0`, `c18-iad0`)

**Service Auto-Detection:**
- `vppipsecgw*` or `ipsecgw*` → nsvppipsecgw
- `ecgw*` → ecgw
- `gregw*` or `vppgregw*` → nsvppgregw
- `steeringlb*` → steeringlb

**Repository Mapping:**
- nsvppipsecgw → `netSkope/nsvppipsecgw-ansible-config`
- ecgw → `netSkope/ecgw-ansible-config`
- nsvppgregw → `netSkope/nsvppgregw-ansible-config`
- steeringlb → `netSkope/steeringlb-ansible-config`

### 2. Latest Tag Fetching Script

**Location**: `~/.claude/scripts/get_latest_tag.sh`

**Purpose**: Fetch latest release version for ANSIBLE_CONFIG_IMAGE_TAG from GitHub.

**Usage:**
```bash
./get_latest_tag.sh nsvppipsecgw
# Output: 133.0.14

./get_latest_tag.sh nsvppgregw
# Output: 134.0.2

./get_latest_tag.sh ecgw
# Output: 133.0.1
```

## Deployment Types

### Immediate Deployment
Standard deployment that runs immediately without waiting.

### Scheduled Deployment
Schedule deployments to run at specific times (UTC). Useful for coordinated QA releases or testing scheduled workflows.

**Schedule Format:**
```
Schedule [05-Feb, Thu]
Common Parameters for all POPS:
RELEASE: 133.0.1.3316
ANSIBLE_CONFIG_IMAGE_TAG: 134.0.12
TICKET: ENG-12345
Service: nsvppgregw

9:30AM-12:00PM
c7-iad0,c18-iad0

11:00AM-12:30PM
iad0

1:00PM-4:00PM
c1-iad0
```

**Format Explanation:**
- **Date**: `[05-Feb, Thu]` - Schedule date and day
- **Common Parameters**: Apply to ALL POPs in the schedule
- **Time Slots**: `9:30AM-12:00PM` - Start time in UTC
- **POPs**: `c7-iad0,c18-iad0` - Comma-separated list of QA POPs

**Important Notes:**
- All times are in **UTC**
- For scheduled deployments, **permission is required before each job runs**
- Service type must be specified
- Supports both immediate and scheduled deployments for testing

## User-Provided Parameters

### Immediate Deployment
For immediate QA deployments, user typically provides:
1. **Hostname**: (e.g., `vppipsecgw04.c18.iad0.netskope.com`)
2. **RELEASE**: Version number (e.g., `133.0.3.2830`)
3. **ANSIBLE_CONFIG_IMAGE_TAG** (optional): Can override auto-fetched value
4. **TICKET** (optional): Default is `ENG-12345`

### Hash-Based Deployments (QA Only)

**IMPORTANT**: When user provides a **git commit hash** instead of a version tag for `ansible_tags`, special parameters are required:

**Hash Deployment Indicators:**
- User provides a 40-character hexadecimal string (e.g., `2c08974df661897412d1cb9edd111ef4088a2a0a`)
- User explicitly mentions "hash" or "ansible_tags as hash"
- User specifies `ANSIBLE_ARTIFACTORY_CHANNEL` as `ipsec-gre-develop-docker` or `ipsec-gre-fevelop-docker`

**Parameter Changes for Hash Deployments:**
1. **ANSIBLE_CONFIG_IMAGE_TAG**: Use the provided hash (not the auto-fetched version tag)
2. **ANSIBLE_ARTIFACTORY_CHANNEL**: Use `ipsec-gre-develop-docker` (NOT `ipsec-gre-release-docker`)

**Example Hash Deployment Request:**
```
User: "Deploy build 133.1.0.3020 on vppipsecgw04.c18.iad0.netskope.com,
       use ansible_tags as 2c08974df661897412d1cb9edd111ef4088a2a0a,
       ANSIBLE_ARTIFACTORY_CHANNEL will be ipsec-gre-develop-docker"
```

**Parameters to use:**
- RELEASE: `133.1.0.3020`
- ANSIBLE_CONFIG_IMAGE_TAG: `2c08974df661897412d1cb9edd111ef4088a2a0a` (the hash)
- ANSIBLE_ARTIFACTORY_CHANNEL: `ipsec-gre-develop-docker`

**Note**: Hash-based deployments are **QA-only**. Production deployments do NOT support hash concept.

## Automated Parameters

The following are automatically determined:
- **POPS**: Auto-detected via `detect_pop.sh` script
- **Service**: Auto-detected from hostname pattern
- **ANSIBLE_CONFIG_IMAGE_TAG**:
  - **Regular deployments**: Auto-fetched via `get_latest_tag.sh` (if not provided)
  - **Hash deployments**: Use the provided git commit hash
- **ANSIBLE_HOSTGROUPS**: Uses the hostname provided by user
- **ANSIBLE_ARTIFACTORY_CHANNEL**:
  - **Regular deployments**: `ipsec-gre-release-docker`
  - **Hash deployments**: `ipsec-gre-develop-docker`
- **TICKET**: Default `ENG-12345` (if not provided)

## QA Jenkins Parameters

### Parameters User Provides:
- **Hostname**: e.g., `vppipsecgw04.c18.iad0.netskope.com`
- **RELEASE**: e.g., `133.0.3.2830`
- **ANSIBLE_CONFIG_IMAGE_TAG** (optional): e.g., `133.0.14` (auto-fetched if not provided)
- **TICKET** (optional): e.g., `ENG-12345` (default)

### Parameters Automated/Default:
- **POPS**: Auto-detected (e.g., `c7-iad0`)
- **ANSIBLE_HOSTGROUPS**: User's hostname
- **ANSIBLE_COMPONENT_NAME**: Service name (e.g., `nsvppipsecgw`)
- **ANSIBLE_CONFIG_IMAGE_NAME**: `<service>-ansible-config`
- **ANSIBLE_ARTIFACTORY_CHANNEL**: `ipsec-gre-release-docker`
- **ANSIBLE_VERBOSITY**: `0`
- **SELECT_ALL_POPS**: `Unselect All`
- **SELECT_ALL_COMPONENTS**: `SELECT_ALL`
- **REGIONS**: `America,APAC,Europe`
- **POP_TYPES**: `MP,DP,GCP,EKS`
- **SLACK_CHANNEL**: `#vpp-ipsec-gre-self-service-deployment`
- **BYPASS_MONITORING_RESULT**: `NO`
- **BYPASS_JIRA**: `YES`
- **RUN_QE_PDV**: `DEPLOY_ONLY`
- **DEPLOY_TYPE**: `DEPLOY`

### Parameters to OMIT:
- **PDV_ARTIFACTORY_CHANNEL** - Omit (restricted choices)
- **PDV_CONFIG_IMAGE_NAME** - Omit (restricted choices)
- **PDV_CONFIG_IMAGE_TAG** - Omit (restricted choices)

## Deployment Workflow

### Step 1: Parse Hostname
Extract service and POP hint from hostname:
```
Input: "vppipsecgw04.c18.iad0.netskope.com"
Service: nsvppipsecgw (detected from "vppipsecgw")
POP hint: c18 (for script lookup)
```

### Step 2: Auto-Detect POP
Run POP detection script:
```bash
./detect_pop.sh "vppipsecgw04.c18.iad0.netskope.com"
```

**Possible outcomes:**
- **Single match**: Use automatically (e.g., `c7-iad0`)
- **Multiple matches**: Ask user to choose (e.g., `c7-iad0` or `c18-iad0`)
- **No match**: Ask user to provide POP manually

### Step 3: Auto-Fetch Latest Tag
Fetch latest ANSIBLE_CONFIG_IMAGE_TAG (if not provided by user):
```bash
./get_latest_tag.sh nsvppipsecgw
# Returns: 133.0.14
```

### Step 4: Prepare Parameters
Collect all parameters with automation and defaults:
- POPS: from Step 2
- RELEASE: from user
- ANSIBLE_CONFIG_IMAGE_TAG: from Step 3 (or user override)
- ANSIBLE_HOSTGROUPS: from user's hostname
- TICKET: `ENG-12345` (default)
- All other parameters: use QA defaults

### Step 5: Trigger Deployment (Jenkins CLI - Recommended)

**Command Template:**
```bash
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
java -jar ~/.claude/jenkins-cli.jar \
  -s https://cdjenkins.betaskope.iad0.netskope.com/ \
  -auth your-username@your-company.com:your-api-token \
  build one_button_<service> -s \
  -p POPS=<pop> \
  -p RELEASE=<version> \
  -p ANSIBLE_CONFIG_IMAGE_TAG=<tag> \
  -p ANSIBLE_HOSTGROUPS=<hostname> \
  -p ANSIBLE_ARTIFACTORY_CHANNEL=ipsec-gre-release-docker \
  -p TICKET=<ticket> \
  -p SELECT_ALL_POPS="Unselect All" \
  -p REGIONS="America,APAC,Europe" \
  -p POP_TYPES="MP,DP,GCP,EKS" \
  -p SELECT_ALL_COMPONENTS=SELECT_ALL \
  -p ANSIBLE_COMPONENT_NAME=<service> \
  -p ANSIBLE_CONFIG_IMAGE_NAME=<service>-ansible-config \
  -p ANSIBLE_VERBOSITY=0 \
  -p SLACK_CHANNEL="#vpp-ipsec-gre-self-service-deployment" \
  -p BYPASS_MONITORING_RESULT=NO \
  -p BYPASS_JIRA=YES \
  -p RUN_QE_PDV=DEPLOY_ONLY \
  -p DEPLOY_TYPE=DEPLOY
```

### Step 6: Monitor Deployment (AUTOMATIC)

**Monitoring Strategy:**
- **First check**: Wait 5 minutes after triggering (300 seconds)
- **Subsequent checks**: Every 60 seconds until completion
- **Typical duration**: 6-10 minutes for QA deployments
- **Why 5 minutes**: Initial stages (pulling images, setup, dry-run) take time

**Implementation:**
```bash
# Step 1: Wait 5 minutes before first check
echo "Waiting 5 minutes before first status check..."
sleep 300

# Step 2: Check build status (single-line format)
curl -s "https://cdjenkins.betaskope.iad0.netskope.com/job/one_button_<service>/<BUILD_NUMBER>/api/json" -u "your-username@your-company.com:your-api-token" | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"Building: {data.get('building')}\nResult: {data.get('result')}\nDuration: {data.get('duration', 0) / 1000:.1f}s\")"

# Step 3: If still building, wait 60 seconds and check again
# Repeat until building = false

# Step 4: Report final status to user
```

**Status Check Fields:**
```json
{
  "building": true/false,    // Is build currently running?
  "result": "SUCCESS/FAILURE/ABORTED",  // Final result (null if building)
  "duration": 123456         // Build duration in milliseconds
}
```

**Build URL**: `https://cdjenkins.betaskope.iad0.netskope.com/job/one_button_<service>/<BUILD_NUMBER>/`

**Success Notification Format:**
```
✅ QA Deployment Completed!

Build #312 completed in 6 minutes 45 seconds

Final Status: ✅ SUCCESS

Build URL: https://cdjenkins.betaskope.iad0.netskope.com/job/one_button_nsvppipsecgw/312/

Deployment Summary:
- Host: vppipsecgw04.c18.iad0.netskope.com
- POP: c7-iad0
- Service: nsvppipsecgw
- Version: 133.0.3.2830
- ANSIBLE_CONFIG_IMAGE_TAG: 133.0.14
```

## Example QA Deployments

### Example 1: Regular Deployment (Version Tag)

**User Request:**
- Hostname: `vppipsecgw04.c18.iad0.netskope.com`
- RELEASE: `133.0.3.2830`

**Automated Steps:**
1. Detect service: `nsvppipsecgw`
2. Run POP detection: `./detect_pop.sh "vppipsecgw04.c18.iad0.netskope.com"`
   - Result: `c7-iad0` (single match)
3. Fetch latest tag: `./get_latest_tag.sh nsvppipsecgw`
   - Result: `133.0.14`
4. Set default ticket: `ENG-12345`

**Deploy Command:**
```bash
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
java -jar ~/.claude/jenkins-cli.jar \
  -s https://cdjenkins.betaskope.iad0.netskope.com/ \
  -auth your-username@your-company.com:your-api-token \
  build one_button_nsvppipsecgw -s \
  -p POPS=c7-iad0 \
  -p RELEASE=133.0.3.2830 \
  -p ANSIBLE_CONFIG_IMAGE_TAG=133.0.14 \
  -p ANSIBLE_HOSTGROUPS=vppipsecgw04.c18.iad0.netskope.com \
  -p ANSIBLE_ARTIFACTORY_CHANNEL=ipsec-gre-release-docker \
  -p TICKET=ENG-12345 \
  -p SELECT_ALL_POPS="Unselect All" \
  -p REGIONS="America,APAC,Europe" \
  -p POP_TYPES="MP,DP,GCP,EKS" \
  -p SELECT_ALL_COMPONENTS=SELECT_ALL \
  -p ANSIBLE_COMPONENT_NAME=nsvppipsecgw \
  -p ANSIBLE_CONFIG_IMAGE_NAME=nsvppipsecgw-ansible-config \
  -p ANSIBLE_VERBOSITY=0 \
  -p SLACK_CHANNEL="#vpp-ipsec-gre-self-service-deployment" \
  -p BYPASS_MONITORING_RESULT=NO \
  -p BYPASS_JIRA=YES \
  -p RUN_QE_PDV=DEPLOY_ONLY \
  -p DEPLOY_TYPE=DEPLOY
```

**Expected Output:**
```
Started one_button_nsvppipsecgw #312
```

### Example 2: Hash-Based Deployment (Git Commit Hash)

**User Request:**
- Hostname: `vppipsecgw04.c18.iad0.netskope.com`
- RELEASE: `133.1.0.3020`
- POP: `c7-iad0`
- ansible_tags: `2c08974df661897412d1cb9edd111ef4088a2a0a` (git hash)
- ANSIBLE_ARTIFACTORY_CHANNEL: `ipsec-gre-develop-docker`

**Key Differences:**
- ANSIBLE_CONFIG_IMAGE_TAG uses the **git commit hash** (not version tag)
- ANSIBLE_ARTIFACTORY_CHANNEL is `ipsec-gre-develop-docker` (not release)

**Deploy Command:**
```bash
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
java -jar ~/.claude/jenkins-cli.jar \
  -s https://cdjenkins.betaskope.iad0.netskope.com/ \
  -auth your-username@your-company.com:your-api-token \
  build one_button_nsvppipsecgw -s \
  -p POPS=c7-iad0 \
  -p RELEASE=133.1.0.3020 \
  -p ANSIBLE_CONFIG_IMAGE_TAG=2c08974df661897412d1cb9edd111ef4088a2a0a \
  -p ANSIBLE_HOSTGROUPS=vppipsecgw04.c18.iad0.netskope.com \
  -p ANSIBLE_ARTIFACTORY_CHANNEL=ipsec-gre-develop-docker \
  -p TICKET=ENG-12345 \
  -p SELECT_ALL_POPS="Unselect All" \
  -p REGIONS="America,APAC,Europe" \
  -p POP_TYPES="MP,DP,GCP,EKS" \
  -p SELECT_ALL_COMPONENTS=SELECT_ALL \
  -p ANSIBLE_COMPONENT_NAME=nsvppipsecgw \
  -p ANSIBLE_CONFIG_IMAGE_NAME=nsvppipsecgw-ansible-config \
  -p ANSIBLE_VERBOSITY=0 \
  -p SLACK_CHANNEL="#vpp-ipsec-gre-self-service-deployment" \
  -p BYPASS_MONITORING_RESULT=NO \
  -p BYPASS_JIRA=YES \
  -p RUN_QE_PDV=DEPLOY_ONLY \
  -p DEPLOY_TYPE=DEPLOY
```

**Expected Output:**
```
Started one_button_nsvppipsecgw #1035
Completed one_button_nsvppipsecgw #1035 133.1.0.3020 : SUCCESS
```

## Alternative: REST API Method

**Note**: Jenkins CLI is recommended. Use REST API only as fallback.

### Get Jenkins Crumb
```bash
curl -s "https://cdjenkins.betaskope.iad0.netskope.com/crumbIssuer/api/json" \
  -u "your-username@your-company.com:your-api-token"
```

### Trigger Build with curl
**CRITICAL**: Use `--data-urlencode` for each parameter (Jenkins requires `application/x-www-form-urlencoded` format)

```bash
curl -X POST "https://cdjenkins.betaskope.iad0.netskope.com/job/one_button_<service>/buildWithParameters" \
  -u "your-username@your-company.com:your-api-token" \
  -H "Jenkins-Crumb: <crumb-value>" \
  --data-urlencode "POPS=c7-iad0" \
  --data-urlencode "RELEASE=133.0.3.2830" \
  --data-urlencode "ANSIBLE_CONFIG_IMAGE_TAG=133.0.1" \
  --data-urlencode "ANSIBLE_HOSTGROUPS=ecgw02.iad0.netskope.com" \
  --data-urlencode "ANSIBLE_ARTIFACTORY_CHANNEL=ipsec-gre-release-docker" \
  --data-urlencode "TICKET=ENG-12345" \
  --data-urlencode "SELECT_ALL_POPS=Unselect All" \
  --data-urlencode "REGIONS=America,APAC,Europe" \
  --data-urlencode "POP_TYPES=MP,DP,GCP,EKS" \
  --data-urlencode "SELECT_ALL_COMPONENTS=SELECT_ALL" \
  --data-urlencode "ANSIBLE_COMPONENT_NAME=ecgw" \
  --data-urlencode "ANSIBLE_CONFIG_IMAGE_NAME=ecgw-ansible-config" \
  --data-urlencode "ANSIBLE_VERBOSITY=0" \
  --data-urlencode "SLACK_CHANNEL=#vpp-ipsec-gre-self-service-deployment" \
  --data-urlencode "BYPASS_MONITORING_RESULT=NO" \
  --data-urlencode "BYPASS_JIRA=YES" \
  --data-urlencode "RUN_QE_PDV=DEPLOY_ONLY" \
  --data-urlencode "DEPLOY_TYPE=DEPLOY" \
  -w "\nHTTP Status: %{http_code}\n"
```

## Troubleshooting

### POP Detection Issues

**If POP detection fails:**
```bash
# Verify GITHUB_TOKEN is set
echo $GITHUB_TOKEN

# Test the script manually
~/.claude/scripts/detect_pop.sh "vppipsecgw04.c18.iad0.netskope.com"
```

**If service cannot be auto-detected:**
- Hostname might not match standard patterns
- Manually specify the service: `./detect_pop.sh "hostname" "service"`
- Supported services: nsvppipsecgw, nsvppgregw, ecgw, steeringlb

**If hostname not found in inventory:**
- Verify hostname is correct
- Check if it exists in GitHub repository manually
- Host might be dynamically provisioned (check with user)

**If multiple POPs found:**
- Normal for some hosts (appear in multiple inventory files)
- Ask user to specify which POP to deploy to
- Common: Host appears in both old and new cluster configurations

### Jenkins CLI Issues

**If Java not found:**
```bash
brew install openjdk@17
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc
```

**If authentication fails (401):**
- Verify API token: `your-api-token`
- Check permissions: Overall/Read, Job/Build, Job/Read
- Create new token if needed

**Test authentication:**
```bash
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
java -jar ~/.claude/jenkins-cli.jar \
  -s https://cdjenkins.betaskope.iad0.netskope.com/ \
  -auth your-username@your-company.com:your-api-token \
  who-am-i
```

**If Jenkins CLI jar not found:**
```bash
cd ~/.claude
curl -O https://cdjenkins.betaskope.iad0.netskope.com/jnlpJars/jenkins-cli.jar
ls -lh ~/.claude/jenkins-cli.jar
```

### Build Failures

**If build fails with "No components specified":**
- Ensure `ANSIBLE_COMPONENT_NAME` is set to service name
- Do NOT leave it empty

**If build fails with "Illegal choice" error:**
- Remove PDV parameters (PDV_ARTIFACTORY_CHANNEL, PDV_CONFIG_IMAGE_NAME, PDV_CONFIG_IMAGE_TAG)
- Let Jenkins use defaults for these

**If build fails with "Illegal choice for parameter ANSIBLE_ARTIFACTORY_CHANNEL":**
- Check for typos: `ipsec-gre-fevelop-docker` should be `ipsec-gre-develop-docker`
- Valid choices for QA:
  - `ipsec-gre-release-docker` (for regular version tag deployments)
  - `ipsec-gre-develop-docker` (for hash-based deployments)

## Scheduled Deployment Workflow (QA)

**IMPORTANT**: When user provides a schedule format, follow this workflow to schedule deployments at specific UTC times.

### Step 1: Parse Schedule

Extract from schedule text:
1. **Date**: Schedule date (e.g., `05-Feb`)
2. **Common Parameters**: RELEASE, ANSIBLE_CONFIG_IMAGE_TAG, TICKET, Service
3. **Time Slots**: Each time with list of POPs

**Example Input:**
```
Schedule [05-Feb, Thu]
Common Parameters for all POPS:
RELEASE: 133.0.1.3316
ANSIBLE_CONFIG_IMAGE_TAG: 134.0.12
TICKET: ENG-12345
Service: nsvppgregw

9:30AM
c7-iad0,c18-iad0

11:00AM
iad0
```

**Parsed Output:**
- Date: 2026-02-05
- RELEASE: 133.0.1.3316
- ANSIBLE_CONFIG_IMAGE_TAG: 134.0.12
- TICKET: ENG-12345
- Service: nsvppgregw
- Time Slot 1: 09:30 UTC → c7-iad0, c18-iad0
- Time Slot 2: 11:00 UTC → iad0

### Step 2: Display Schedule Summary

Show the user:
```
========================================
SCHEDULED QA DEPLOYMENTS
========================================

Date: Thursday, February 5, 2026
Service: nsvppgregw
Environment: QA

Common Parameters:
  RELEASE: 133.0.1.3316
  ANSIBLE_CONFIG_IMAGE_TAG: 134.0.12
  TICKET: ENG-12345

Deployment Schedule (All times UTC):

09:30 AM → c7-iad0, c18-iad0 (2 POPs)
11:00 AM → iad0 (1 POP)

Total: 3 POPs across 2 time slots

⚠️  This will schedule 3 QA deployments.
⚠️  Permission will be requested before each time slot deployment.

Do you want to create this schedule? (yes/no)
========================================
```

### Step 3: Calculate Wait Times and Schedule with Bash Background Tasks

**CRITICAL**: Use Bash tool with `run_in_background: true` to sleep until scheduled time. This allows you to monitor the task and prompt user in the conversation.

**For each deployment (or time slot):**

1. Calculate wait time in seconds
2. Launch ONE Bash background task per deployment with `run_in_background: true`
3. After task completes, read the output and prompt user for permission
4. Trigger deployment only if user approves

**Example Implementation:**

```bash
# Calculate wait time for a specific deployment
CURRENT_EPOCH=$(date -u +%s)
TARGET_DATE="2026-02-05"
TARGET_TIME="09:30:00"  # Note: include seconds
TARGET_EPOCH=$(date -u -j -f "%Y-%m-%d %H:%M:%S" "${TARGET_DATE} ${TARGET_TIME}" +%s)
WAIT_SECONDS=$((TARGET_EPOCH - CURRENT_EPOCH))

if [ $WAIT_SECONDS -lt 0 ]; then
  echo "⚠️  Scheduled time has passed!"
  WAIT_SECONDS=0
fi

WAIT_MINUTES=$(awk "BEGIN {printf \"%.1f\", $WAIT_SECONDS/60}")

cat << EOF
🕐 Scheduling Deployment
Target Time: ${TARGET_TIME} UTC
Wait Time: ${WAIT_SECONDS} seconds (${WAIT_MINUTES} minutes)

I will:
1. Sleep until the scheduled time
2. Notify you in this conversation
3. Ask for your permission
4. Trigger deployment if approved
5. Monitor and show build status here

Starting wait now...
EOF

# Sleep until scheduled time
sleep $WAIT_SECONDS

echo ""
echo "⏰ Scheduled time reached: $(date -u '+%H:%M:%S UTC')"
```

**Launch this with Bash tool using:**
- `run_in_background: true`
- `timeout: 600000` (10 minutes max wait time)

### Step 4: Monitor Background Task and Request Permission

**After launching the background Bash task:**

1. Save the task ID returned by the Bash tool
2. Display status to user showing the task is waiting
3. When the scheduled time arrives, you'll receive a system notification about task completion
4. Read the task output file
5. **Prompt user for permission in the conversation** using regular text message or AskUserQuestion tool
6. Only proceed if user approves

**Example:**
```
Task b4e4cdd is sleeping until 08:30 UTC...

[Wait for task completion notification]

[Read task output to confirm time reached]

🔔 Scheduled deployment ready!
POP: c7-iad0
Host: vppipsecgw04.c18.iad0.netskope.com
Release: 134.0.8.3068

Do you want to proceed with this deployment?
```

### Step 5: Trigger Deployment After Approval

Once user approves in the conversation, trigger the Jenkins deployment:

```bash
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
java -jar ~/.claude/jenkins-cli.jar \
  -s https://cdjenkins.betaskope.iad0.netskope.com/ \
  -auth your-username@your-company.com:your-api-token \
  build one_button_nsvppipsecgw -s \
  -p POPS=c7-iad0 \
  -p RELEASE=134.0.8.3068 \
  -p ANSIBLE_CONFIG_IMAGE_TAG=134.0.10 \
  -p ANSIBLE_HOSTGROUPS=vppipsecgw04.c18.iad0.netskope.com \
  -p ANSIBLE_ARTIFACTORY_CHANNEL=ipsec-gre-release-docker \
  -p TICKET=ENG-12345 \
  -p SELECT_ALL_POPS="Unselect All" \
  -p REGIONS="America,APAC,Europe" \
  -p POP_TYPES="MP,DP,GCP,EKS" \
  -p SELECT_ALL_COMPONENTS=SELECT_ALL \
  -p ANSIBLE_COMPONENT_NAME=nsvppipsecgw \
  -p ANSIBLE_CONFIG_IMAGE_NAME=nsvppipsecgw-ansible-config \
  -p ANSIBLE_VERBOSITY=0 \
  -p SLACK_CHANNEL="#vpp-ipsec-gre-self-service-deployment" \
  -p BYPASS_MONITORING_RESULT=NO \
  -p BYPASS_JIRA=YES \
  -p RUN_QE_PDV=DEPLOY_ONLY \
  -p DEPLOY_TYPE=DEPLOY
```

Extract build number from output and then follow Step 6 for monitoring.

### Step 6: Monitor Build Status

After triggering deployment, automatically monitor and display status updates in the conversation:

```bash
# Wait 5 minutes before first check
sleep 300

# Monitor build status every 60 seconds
while true; do
  STATUS=$(curl -s "${JENKINS_URL}job/one_button_${SERVICE}/${BUILD_NUMBER}/api/json" \
    -u "${JENKINS_USER}:${JENKINS_TOKEN}" | \
    python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"{data.get('building')}|{data.get('result')}|{data.get('duration', 0)}\")")

  BUILDING=$(echo "$STATUS" | cut -d'|' -f1)
  RESULT=$(echo "$STATUS" | cut -d'|' -f2)
  DURATION=$(echo "$STATUS" | cut -d'|' -f3)

  if [ "$BUILDING" = "False" ]; then
    DURATION_MIN=$(awk "BEGIN {printf \"%.1f\", $DURATION/60000}")
    echo "✅ Build #${BUILD_NUMBER} completed in ${DURATION_MIN} minutes"
    echo "Final Status: $RESULT"
    break
  fi

  echo "Build still running..."
  sleep 60
done
```

Display final status to user in the conversation with build URL and summary.

### Important Notes for Scheduled Deployments

**DO:**
- ✅ Use ONE Bash background task per deployment with `run_in_background: true`
- ✅ Prompt user for permission IN THE CONVERSATION after wait completes
- ✅ Show all status updates in the conversation
- ✅ Check if scheduled time has passed and set WAIT_SECONDS=0 if so
- ✅ Use timeout of 600000ms (10 minutes) for background tasks

**DON'T:**
- ❌ Use nohup with scripts that have `read -p` prompts (they don't work)
- ❌ Launch duplicate processes
- ❌ Trigger deployments without user permission
- ❌ Use complex shell scripts with subshells and `&` for background processes

**Why This Approach Works:**
- Claude's Bash tool with `run_in_background: true` creates a managed background task
- You receive notifications when the task completes
- You can prompt the user naturally in the conversation
- You maintain full control and visibility of the process

## Key Reminders

1. ✅ Full automation with POP detection and parameter defaults
2. ✅ No user confirmation required (auto-deploy)
3. Use Jenkins CLI (preferred) or REST API
4. ANSIBLE_HOSTGROUPS = hostname (not service name)
5. DEPLOY_TYPE = DEPLOY (same as production)
6. ANSIBLE_VERBOSITY = 0 (not 2)
7. TICKET default is ENG-12345
8. Ensure GITHUB_TOKEN is set for POP detection
9. **Hash-based deployments (QA only):**
   - When user provides git commit hash → Use `ipsec-gre-develop-docker` channel
   - ANSIBLE_CONFIG_IMAGE_TAG = the provided hash
   - Production does NOT support hash deployments
10. **Scheduled deployments (QA & Production):**
   - Use Bash tool with `run_in_background: true` (ONE task per deployment)
   - Sleep until scheduled time, then prompt user IN THE CONVERSATION
   - NEVER use nohup scripts with `read -p` prompts (they don't work)
   - Request permission before triggering each deployment
   - Show all status updates in the conversation
