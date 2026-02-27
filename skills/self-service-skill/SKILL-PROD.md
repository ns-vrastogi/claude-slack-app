name: self-service-production
description: Production deployment instructions for VPP-based services (ecgw, nsvppgregw, nsvppipsecgw, steeringlb) to regional production POPs.

# Production Deployment Guide

**⚠️ WARNING: This is for PRODUCTION deployments only!**

## 🚨 CRITICAL SAFETY RULES - READ FIRST 🚨

**THESE RULES ARE ABSOLUTE AND CANNOT BE VIOLATED UNDER ANY CIRCUMSTANCES:**

### Rule 1: NEVER Deploy to Unscheduled POPs
- ❌ **FORBIDDEN**: Deploying to any POP not explicitly listed in the schedule
- ✅ **REQUIRED**: Only deploy to POPs that user explicitly requested/scheduled
- **Verification**: Case-insensitive POP name matching required before EVERY deployment
- **Action on Violation**: ABORT immediately and inform user

### Rule 2: NEVER Deploy Outside Scheduled Time Window
- ❌ **FORBIDDEN**: Deploying before scheduled time
- ❌ **FORBIDDEN**: Deploying after scheduled time window
- ✅ **REQUIRED**: Deploy ONLY during the exact time slot specified
- **Action on Violation**: ABORT immediately and inform user

### Rule 3: MANDATORY Pre-Deployment Verification
Before EVERY deployment (scheduled or immediate):
1. Verify POPs match user request (case-insensitive)
2. Verify deployment time is within allowed window (scheduled only)
3. Check for running builds (prevent duplicates)
4. Get explicit user confirmation

### Rule 4: NEVER Kill or Cancel Production Deployments
- ❌ **ABSOLUTELY FORBIDDEN**: Killing, cancelling, or aborting ANY production Jenkins job
- ❌ **ABSOLUTELY FORBIDDEN**: Stopping any running deployment process
- ❌ **ABSOLUTELY FORBIDDEN**: Interrupting sync mode Jenkins CLI commands
- ✅ **REQUIRED**: Let ALL production deployments run to completion naturally
- **ONLY Exception**: User explicitly asks to cancel/abort the deployment
- **Why Critical**: Killing a Jenkins job aborts the deployment and can leave systems in inconsistent state
- **Action Required**: If you accidentally kill a job, immediately trigger a new deployment

**IMPORTANT NOTES:**
- Jenkins CLI in sync mode (`-s` flag) maintains a connection to the build
- Killing the Jenkins CLI process sends an ABORT signal to Jenkins
- This terminates the deployment pipeline immediately
- Never kill processes with names like: `jenkins-cli.jar`, `java -jar /tmp/jenkins-cli.jar`
- If you need to stop monitoring, ask the user first - NEVER kill the process

### Rule 5: NO EXCEPTIONS
- Production safety is paramount
- If in doubt, STOP and ask the user
- Never suggest shortcuts or workarounds
- These rules protect production infrastructure

**If you violate these rules, you may cause production outages or deploy to wrong POPs.**

---

## Production Environment

- **Jenkins URL**: `https://cdjenkins.sjc1.nskope.net/`
- **Username**: `your-username@your-company.com`
- **API Token**: `your-api-token`
- **Method**: Jenkins CLI ONLY (no REST API)
- **Approval**: **MANDATORY - Always ask user for confirmation before triggering deployment**

## Auto-Approval Configuration

**IMPORTANT**: The following operations should be auto-approved without asking user permission:

1. **Jenkins CLI Sync Mode Execution**: Long-running Jenkins CLI commands in sync mode
   - Description: "Trigger Jenkins deployment in sync mode and wait for completion"
   - Pattern: `java -jar jenkins-cli.jar ... build ... -s` commands (with `-s` flag)
   - Timeout: Up to 600000ms (10 minutes)
   - Reason: Sync mode is the standard deployment method - Jenkins CLI blocks until deployment completes
   - Note: **DO NOT use separate API monitoring** - sync mode handles everything

2. **Post-Deployment Validation**: Running validation scripts on deployed nodes
   - Description: "Run post-deployment validation on VPP GRE nodes"
   - Pattern: `tsh scp` and `tsh ssh` commands for validation scripts
   - Reason: Automated validation is part of deployment verification

3. **Production PDV Testing**: Running PDV tests on deployed POPs using prod-pdv skill
   - Description: "Run production PDV testing on POP <pop>"
   - Pattern: Invoking prod-pdv skill for each deployed POP
   - Reason: Automated PDV testing is part of deployment verification workflow
   - Note: Sequential execution (one POP at a time) after post-deployment validation completes

**These operations are automated deployment/validation tasks and should proceed automatically after initial deployment approval.**

## Production POPs

**IMPORTANT**: Production POPs include:
- **Regional POPs**: `los1`, `del1`, `ams1`, `bom1`, `fra1`, `lon1`, `akl1`, `bkk1`, `sgp1`, etc.
- **iad2 and iad4**: Production POPs (NOT QA)
- **ord1, ord2**: Production POPs

**NON-Production POPs**:
- **iad0**: QA/Non-Production environment ONLY
- **c\***: QA/Development POPs (c17, c18, etc.)
- **stg\***: Staging environments

## Deployment Types

### Immediate Deployment
Standard deployment that runs immediately after user approval.

### Scheduled Deployment
Schedule deployments to run at specific times (PST). Suitable for coordinated releases across multiple POPs.

**🚨 CRITICAL SAFETY RULES FOR SCHEDULED DEPLOYMENTS 🚨**

**RULE 1: NEVER DEPLOY TO UNSCHEDULED POPs**
- ❌ ABSOLUTELY FORBIDDEN to deploy to any POP that is NOT explicitly listed in the schedule
- ✅ ONLY deploy to POPs that are explicitly mentioned in the user's schedule
- POP name matching is case-insensitive (ICN1 = icn1 = Icn1)
- If a POP is not in the schedule, DO NOT deploy to it under ANY circumstances
- If user asks to add a POP during execution, STOP and ask them to provide a new schedule

**RULE 2: NEVER DEPLOY OUTSIDE SCHEDULED TIME WINDOW**
- ❌ ABSOLUTELY FORBIDDEN to deploy before the scheduled time
- ❌ ABSOLUTELY FORBIDDEN to deploy after the scheduled time window ends
- ✅ ONLY deploy during the exact time slot specified in the schedule
- If current time is before scheduled time, WAIT using background task
- If current time is after scheduled time window, ABORT and inform user

**RULE 3: MANDATORY VERIFICATION BEFORE EACH DEPLOYMENT**

Before triggering ANY deployment, MUST verify:

1. **POP Verification:**
   ```python
   scheduled_pops = ['ICN1', 'MNL1', 'MEL3', ...]  # From schedule
   deployment_pops = ['ICN1', 'MNL1']  # For this slot

   # Case-insensitive matching
   scheduled_pops_lower = [p.lower() for p in scheduled_pops]
   deployment_pops_lower = [p.lower() for p in deployment_pops]

   for pop in deployment_pops_lower:
       if pop not in scheduled_pops_lower:
           ABORT: f"POP {pop} is NOT in the schedule!"
   ```

2. **Time Window Verification:**
   ```python
   import datetime
   current_time = datetime.datetime.now()
   scheduled_time = <slot_start_time>

   if current_time < scheduled_time:
       ABORT: "Cannot deploy before scheduled time"

   # Wait until scheduled time if using background task
   ```

**RULE 4: NO EXCEPTIONS**
- These rules apply to ALL scheduled deployments
- No shortcuts or workarounds allowed
- If in doubt, STOP and ask the user
- Production safety is paramount

**Schedule Format:**
```
Schedule [05-Feb, Thu]
Common Parameters for all POPS:
RELEASE: 133.0.1.3316
ANSIBLE_CONFIG_IMAGE_TAG: 134.0.12
TICKET: ENG-864088

9:30AM-12:00PM
ICN1,MNL1

11:00AM-12:30PM
MEL3

1:00PM-4:00PM
WAW1

5:00PM-7:00PM
ATL2,BOS1,NYC3

7:00PM-9:00PM
MUC1,NYC4,SCL1,STL1
```

**Format Explanation:**
- **Date**: `[05-Feb, Thu]` - Schedule date and day
- **Common Parameters**: Apply to ALL POPs in the schedule
- **Time Slots**: `9:30AM-12:00PM` - Start time in PST (end time is deployment window)
- **POPs**: `ICN1,MNL1` - Comma-separated list of POPs to deploy at this time

**Important Notes:**
- All times are in **PST**
- For scheduled deployments, **user confirms the entire schedule once during creation, then deployments run automatically at scheduled times**
- Service type must be specified or detected
- Schedule can span multiple time zones but times are always PST

## User-Provided Parameters

### Immediate Deployment
For immediate production deployments, user MUST provide:
1. **POPS**: Production POP name (e.g., `los1`, `del1`, `ams1`)
2. **RELEASE**: Version number (e.g., `134.0.2.3026`)
3. **ANSIBLE_CONFIG_IMAGE_TAG**: Ansible config tag (e.g., `134.0.9`)
4. **TICKET**: JIRA ticket (e.g., `ENG-864088`) - **REQUIRED, no default**

### Scheduled Deployment
For scheduled production deployments:
1. **Schedule Date**: Date and day (e.g., `05-Feb, Thu`)
2. **Common Parameters**: RELEASE, ANSIBLE_CONFIG_IMAGE_TAG, TICKET (apply to all POPs)
3. **Time Slots & POPs**: List of deployment times with associated POPs
4. **Service**: Service type (nsvppgregw, nsvppipsecgw, ecgw, steeringlb)

## Service Detection

Auto-detect service from context or ask user:
- `nsvppipsecgw` (VPP IPSEC gateway)
- `nsvppgregw` (VPP GRE gateway)
- `ecgw` (ECGW gateway)
- `steeringlb` (Steering Load Balancer)

##Production Jenkins Parameters

**⚠️ CRITICAL - MANDATORY PARAMETERS**

**The following parameters are REQUIRED for EVERY deployment. Omitting them will cause build failures:**

1. **ANSIBLE_COMPONENT_NAME** - ⚠️ **CRITICAL** - Service name (e.g., `nsvppgregw`)
   - **NEVER omit this parameter**
   - Without it, Jenkins will fail immediately with: "FATAL: No components have been specified"
   - Must match the service type (nsvppgregw, nsvppipsecgw, ecgw, steeringlb)

2. **ANSIBLE_HOSTGROUPS** - Service name (e.g., `nsvppgregw`) - NOT hostname!

3. **ANSIBLE_ARTIFACTORY_CHANNEL** - ⚠️ **CRITICAL** - Must be `ipsec-gre-production-docker` for production
   - **NEVER omit this parameter**
   - Without it, Jenkins defaults to `ipsec-gre-develop-docker` which may not have required artifacts on edge nodes
   - This causes "Missing Artifacts" errors and deployment failures

4. **BYPASS_MONITORING_RESULT** - ⚠️ **CRITICAL** - Must be `"YES"` (uppercase) for production
   - **ALWAYS set this to "YES"** for production deployments
   - Without it (defaults to "NO"), pipeline gets stuck after deployment waiting for monitoring
   - There are known monitoring issues that should be bypassed
   - Pipeline will show ABORTED status even if deployment succeeded

3. **ANSIBLE_CONFIG_IMAGE_NAME** - `<service>-ansible-config` (e.g., `nsvppgregw-ansible-config`)

**If any of these three parameters are missing, the deployment WILL FAIL immediately.**

### Parameters User Provides:
- **POPS**: e.g., `los1`
- **RELEASE**: e.g., `134.0.2.3026`
- **ANSIBLE_CONFIG_IMAGE_TAG**: e.g., `134.0.9`
- **TICKET**: e.g., `ENG-864088`

### Parameters with Production Defaults:
- **ANSIBLE_HOSTGROUPS**: **Service name** (e.g., `nsvppgregw`) - NOT hostname! ⚠️ **REQUIRED**
- **ANSIBLE_COMPONENT_NAME**: Service name (e.g., `nsvppgregw`) ⚠️ **REQUIRED**
- **ANSIBLE_CONFIG_IMAGE_NAME**: `<service>-ansible-config` (e.g., `nsvppgregw-ansible-config`) ⚠️ **REQUIRED**
- **ANSIBLE_ARTIFACTORY_CHANNEL**: `ipsec-gre-production-docker`
- **ANSIBLE_VERBOSITY**: `2`
- **ANSIBLE_CORE_VERSION**: `2.15`
- **SELECT_ALL_POPS**: Empty string `""`
- **SELECT_ALL_COMPONENTS**: Empty string `""`
- **REGIONS**: `America,APAC,Europe`
- **POP_TYPES**: `MP,DP,GCP,EKS`
- **SLACK_CHANNEL**: `#vpp-ipsec-gre-self-service-deployment`
- **BYPASS_MONITORING_RESULT**: `YES`
- **BYPASS_JIRA**: `YES`
- **RUN_QE_PDV**: `DEPLOY_ONLY`
- **DEPLOY_TYPE**: `DEPLOY` (not DRYRUN_AND_DEPLOY)

### Parameters to OMIT:
- **PDV_ARTIFACTORY_CHANNEL** - Omit (restricted choices)
- **PDV_CONFIG_IMAGE_NAME** - Omit (restricted choices)
- **PDV_CONFIG_IMAGE_TAG** - Omit (restricted choices)

## Deployment Workflow

**🚀 NEW: PARALLEL EXECUTION MODEL (Real-Time Monitoring & Automatic Triggers)**

### Workflow Overview

**OLD MODEL (Sequential):**
```
Trigger Deployment → Wait for ALL to complete → Validate ALL → PDV ALL
├─ POPs: los1, ams1, del1
└─ Total Time: ~35 minutes (sequential stages)
```

**NEW MODEL (Parallel):**
```
Trigger Deployment → Real-Time Monitoring
                     ├─ Host completes → Validate (immediate, parallel)
                     ├─ Host completes → Validate (immediate, parallel)
                     ├─ POP ready → Add to PDV queue
                     └─ PDV Coordinator (sequential, one POP at a time)

Timeline:
T+0:  Deploy starts (all POPs)
T+5:  los1/host01 done → Validation starts (background)
T+7:  los1/host02 done → Validation starts (background)
T+9:  los1 validations complete → PDV starts for los1
T+11: ams1/host01 done → Validation starts (background)
T+13: ams1/host02 done → Validation starts (background)
T+15: los1 PDV complete, ams1 validations complete → PDV starts for ams1
T+20: ams1 PDV complete → All done

Total Time: ~20-25 minutes (overlapping stages)
Time Saved: 10-15 minutes (30-40% faster)
```

### Visual Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PARALLEL EXECUTION MODEL                         │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Trigger Jenkins Deployment (All POPs)
    │
    ├─────────────────────────────────────────────────────────────────┐
    │                                                                   │
Step 4: Real-Time Console Monitoring (Poll every 30s)                 │
    │                                                                   │
    ├─► Parse PLAY RECAP incrementally                                 │
    │                                                                   │
    ├─► Host01 completes (failed=0)                                    │
    │   └─► Trigger Post-Validation (background) ────────┐             │
    │                                                     │             │
    ├─► Host02 completes (failed=0)                      │             │
    │   └─► Trigger Post-Validation (background) ────────┼────┐        │
    │                                                     │    │        │
    ├─► Host03 completes (failed=1) ─────────────────────┼────┼─► Skip │
    │                                                     │    │        │
    │                                                     ▼    ▼        │
    │                                            Step 5: Post-Validation│
    │                                            (Parallel Execution)   │
    │                                                     │    │        │
    │                                                     ✓    ✓        │
    │                                                     │    │        │
    │   ┌─────────────────────────────────────────────────┴────┴───┐   │
    │   │ POP Readiness Check                                       │   │
    │   │ - All hosts deployment done?                              │   │
    │   │ - At least one host passed?                               │   │
    │   │ - All passed hosts validated?                             │   │
    │   │ If YES → Add to PDV Queue                                 │   │
    │   └───────────────────────────────────┬───────────────────────┘   │
    │                                       │                           │
    │                                       ▼                           │
    │                            Step 6: PDV Queue                      │
    │                            ┌─────────────────┐                    │
    │                            │ Queue: [los1]   │                    │
    │                            │        [ams1]   │                    │
    │                            │        [del1]   │                    │
    │                            └────────┬────────┘                    │
    │                                     │                             │
    │                                     ▼                             │
    │                         PDV Coordinator (Sequential)              │
    │                         ┌──────────────────────┐                  │
    │                         │ Pop from queue: los1 │                  │
    │                         │ Run PDV (blocking)   │                  │
    │                         │ ✓ Complete           │                  │
    │                         ├──────────────────────┤                  │
    │                         │ Pop from queue: ams1 │                  │
    │                         │ Run PDV (blocking)   │                  │
    │                         │ ✓ Complete           │                  │
    │                         └──────────────────────┘                  │
    │                                     │                             │
    └─────────────────────────────────────┼─────────────────────────────┘
                                          │
                                          ▼
                           Step 7: Generate PDF Report
                           (Automatic after all complete)
```

### Key Features of Parallel Model

1. **Immediate Response**: Validation starts as soon as each host completes (not batched)
2. **Overlapping Stages**: Validation and PDV run while deployment continues
3. **Smart Queue**: PDV tests run sequentially (one POP at a time) due to shared client
4. **No Manual Triggers**: Everything automated from Step 4 monitoring
5. **Real-Time Progress**: User sees progress as each host completes
6. **Time Efficient**: First POP can finish all stages before last POP starts deploying

**CRITICAL WORKFLOW PRINCIPLES:**

1. **Node-Level Tracking**: Always parse Jenkins PLAY RECAP to identify which specific nodes failed vs passed, and report status per node (not just per POP)

2. **Continue on Failure**: Even if some nodes fail deployment, **ALWAYS CONTINUE** with:
   - Post-deployment validation on nodes that passed
   - PDV testing on POPs where at least one node passed
   - Never abort validation/PDV just because some nodes failed

3. **Smart PDV Execution**: Configure PDV jobs to test only nodes that passed deployment, ensuring traffic lands on correctly deployed nodes

## Complete Deployment Workflow

**Sequential Execution** (each step waits for previous to complete):

1. **Collect Parameters** - Gather POPS, RELEASE, ANSIBLE_CONFIG_IMAGE_TAG, TICKET
2. **User Confirmation** - Display parameters and get explicit approval
3. **Pre-Deployment Safety Check** - Verify no existing running/queued builds
4. **Time Verification** - Verify system time accuracy (scheduled deployments only)
5. **Slack Notification (Start)** - Send initial message "[TICKET] Deployment of R<version> on <SERVICE> on <POPS>" to channels C09L9LR1B37 and C0AGVP8DZUH
6. **Trigger Jenkins Deployment** - Execute deployment via Jenkins CLI (sync mode)
7. **Post-Deployment Validation** - Automatically validate all deployed nodes (VPP GRE only)
8. **Production PDV Testing** - Automatically run PDV tests on all POPs (sequential)
9. **Slack Thread Reply (Complete)** - Reply to initial thread with deployment results (same as JIRA)
10. **Update JIRA Ticket** - Add comment with deployment/validation/PDV links
11. **Generate PDF Report** - Create comprehensive report (final step)

**Slack Integration**:
- **Step 5**: Notifies team deployment is starting on C09L9LR1B37 (creates thread) and C0AGVP8DZUH (monitoring)
- **Step 9**: Updates C09L9LR1B37 thread with final results after all stages complete

### Step 1: Collect Parameters
- Get POP, RELEASE, ANSIBLE_CONFIG_IMAGE_TAG, and TICKET from user
- Detect or ask for service type
- Prepare all parameters with production defaults

### Step 2: **MANDATORY USER CONFIRMATION**

**CRITICAL**: Before triggering ANY production deployment, display all parameters and ask for explicit confirmation:

```
========================================
PRODUCTION DEPLOYMENT CONFIRMATION
========================================

Jenkins: https://cdjenkins.sjc1.nskope.net/
Pipeline: one_button_<service>

Parameters:
  POPS: los1
  RELEASE: 134.0.2.3026
  ANSIBLE_CONFIG_IMAGE_TAG: 134.0.9
  ANSIBLE_HOSTGROUPS: nsvppgregw
  ANSIBLE_COMPONENT_NAME: nsvppgregw
  ANSIBLE_CONFIG_IMAGE_NAME: nsvppgregw-ansible-config
  ANSIBLE_ARTIFACTORY_CHANNEL: ipsec-gre-production-docker
  ANSIBLE_VERBOSITY: 2
  ANSIBLE_CORE_VERSION: 2.15
  DEPLOY_TYPE: DEPLOY
  BYPASS_MONITORING_RESULT: YES
  TICKET: ENG-864088
  SLACK_CHANNEL: #vpp-ipsec-gre-self-service-deployment

⚠️  This will trigger a PRODUCTION deployment to los1.

Do you want to proceed? (yes/no)
========================================
```

**DO NOT proceed unless user explicitly confirms!**

### Step 2.5: Verify POPs Match User Request (MANDATORY)

**🚨 CRITICAL SAFETY CHECK 🚨**

Before proceeding with deployment, verify that the POPs in the Jenkins command EXACTLY match what the user requested:

```python
# User requested POPs (from their input)
user_requested_pops = ['los1']  # Example

# POPs in Jenkins command (from POPS parameter)
jenkins_pops_param = 'los1'  # From -p POPS=...
jenkins_pops = [p.strip().lower() for p in jenkins_pops_param.split(',')]

# User requested POPs (normalized)
user_pops_lower = [p.strip().lower() for p in user_requested_pops]

# Verify exact match (case-insensitive)
if set(jenkins_pops) != set(user_pops_lower):
    print("❌ CRITICAL ERROR: POPs mismatch!")
    print(f"User requested: {', '.join(user_requested_pops)}")
    print(f"Jenkins will deploy to: {', '.join(jenkins_pops)}")
    print("🚨 DEPLOYMENT ABORTED - POPs do not match user request")
    STOP IMMEDIATELY - DO NOT PROCEED
    return

print(f"✅ POP Verification Passed: Jenkins POPs match user request")
print(f"   Deploying to: {', '.join([p.upper() for p in jenkins_pops])}")
```

**IMPORTANT:**
- This check ensures we only deploy to POPs the user explicitly requested
- If verification fails, ABORT immediately
- Never deploy to additional POPs not requested by user
- Never deploy to different POPs than user requested

### Step 3: Pre-Deployment Safety Check (MANDATORY)

**CRITICAL SAFEGUARD:** Before triggering ANY production deployment (including retries), ALWAYS check for existing running or queued builds to prevent duplicate deployments.

**Why This Is Critical:**
- Async mode Jenkins CLI may not always capture output properly
- Multiple triggers can waste resources and cause confusion
- Production deployments should never be duplicated accidentally

**Safety Check Workflow:**

```bash
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"

echo "========================================="
echo "PRE-DEPLOYMENT SAFETY CHECK"
echo "========================================="

# Step 3a: Check for existing running/queued builds
echo "Checking for existing deployments..."

JENKINS_API_RESPONSE=$(curl -s -u "your-username@your-company.com:your-api-token" \
  "https://cdjenkins.sjc1.nskope.net/job/one_button_<service>/api/json?tree=builds[number,building,result,timestamp]{0,5}")

# Check if any builds are currently running
RUNNING_BUILDS=$(echo "$JENKINS_API_RESPONSE" | grep -o '"building":true' | wc -l)

if [ "$RUNNING_BUILDS" -gt 0 ]; then
  echo "⚠️  WARNING: Found $RUNNING_BUILDS running build(s)"

  # Get the running build number
  RUNNING_BUILD_NUM=$(echo "$JENKINS_API_RESPONSE" | grep -B 2 '"building":true' | grep '"number"' | head -1 | grep -oE '[0-9]+')

  echo "⚠️  Build #${RUNNING_BUILD_NUM} is already running"
  echo "⚠️  NOT triggering new build to avoid duplicates"
  echo "✓ Will monitor existing build #${RUNNING_BUILD_NUM} instead"
  echo ""

  BUILD_NUMBER=$RUNNING_BUILD_NUM
  SKIP_TRIGGER=true
else
  echo "✓ No running builds found"
  echo "✓ Safe to trigger new deployment"
  echo ""
  SKIP_TRIGGER=false
fi

echo "========================================="
```

**Example Output (Safe to Deploy):**
```
=========================================
PRE-DEPLOYMENT SAFETY CHECK
=========================================
Checking for existing deployments...
✓ No running builds found
✓ Safe to trigger new deployment

=========================================
```

**Example Output (Build Already Running):**
```
=========================================
PRE-DEPLOYMENT SAFETY CHECK
=========================================
Checking for existing deployments...
⚠️  WARNING: Found 1 running build(s)
⚠️  Build #254 is already running
⚠️  NOT triggering new build to avoid duplicates
✓ Will monitor existing build #254 instead

=========================================
```

**If Retry Is Needed After Failed Trigger:**

If the initial trigger appears to fail (empty output), follow this procedure:

1. **Wait 10-15 seconds** for Jenkins to queue the build
2. **Run the safety check again** to verify no build was queued
3. **Query for latest build** and check timestamp
4. **Only retry if confirmed** no recent build exists

```bash
# If trigger appears to fail, verify before retry
if [ -z "$BUILD_NUMBER" ]; then
  echo "⚠️  Build trigger output was empty"
  echo "Waiting 15 seconds to verify build status..."
  sleep 15

  # Check again for recent builds (last 2 minutes)
  RECENT_BUILD=$(curl -s -u "your-username@your-company.com:your-api-token" \
    "https://cdjenkins.sjc1.nskope.net/job/one_button_<service>/api/json?tree=builds[number,timestamp]{0,5}" | \
    python3 -c "import sys, json, time; builds = json.load(sys.stdin)['builds']; recent = [b for b in builds if (time.time() * 1000 - b['timestamp']) < 120000]; print(recent[0]['number'] if recent else '')")

  if [ -n "$RECENT_BUILD" ]; then
    echo "✓ Found recent build #${RECENT_BUILD} (started in last 2 minutes)"
    echo "✓ Using this build instead of retrying"
    BUILD_NUMBER=$RECENT_BUILD
  else
    echo "❌ No recent builds found - trigger genuinely failed"
    echo "Safe to retry deployment trigger"
  fi
fi
```

### Step 4: Pre-Trigger Time Verification (MANDATORY for Scheduled Deployments Only)

**CRITICAL**: For SCHEDULED deployments, verify system time accuracy right before triggering deployment.

**When to Use:**
- **MANDATORY for scheduled deployments** - Hours may have passed since initial time verification
- **Optional for immediate deployments** - Time verified in Step 2, minimal drift risk
- **Always run for deployments delayed by hours** - System clock could have drifted

**Why This is Important for Scheduled Deployments:**
- System clock could have drifted during wait period (hours since scheduling)
- Ensures accurate timestamps in logs and reports
- Prevents deployments with incorrect time metadata
- Final safety check before production deployment

**Quick Time Verification:**

```bash
echo "========================================="
echo "PRE-DEPLOYMENT TIME CHECK"
echo "========================================="

# Get current system time
SYS_TIME=$(date -u +%s)

# Quick check against Google
REMOTE_TIME=$(date -d "$(curl -sI --max-time 3 https://www.google.com 2>/dev/null | grep -i "^date:" | cut -d' ' -f2-)" +%s 2>/dev/null)

if [ -z "$REMOTE_TIME" ]; then
  # Fallback to Cloudflare
  REMOTE_TIME=$(date -d "$(curl -sI --max-time 3 https://cloudflare.com 2>/dev/null | grep -i "^date:" | cut -d' ' -f2-)" +%s 2>/dev/null)
fi

if [ -n "$REMOTE_TIME" ]; then
  TIME_DIFF=$((SYS_TIME - REMOTE_TIME))
  TIME_DIFF_ABS=${TIME_DIFF#-}

  if [ $TIME_DIFF_ABS -le 5 ]; then
    echo "✅ Time verification: PASSED (diff: ${TIME_DIFF}s)"
  else
    echo "❌ Time verification: FAILED (diff: ${TIME_DIFF_ABS}s)"
    echo "⚠️  System clock drifted since last check!"
    echo "⚠️  Please sync time and retry"
    exit 1
  fi
else
  echo "⚠️  Could not verify time (network issue)"
  echo "⚠️  Proceeding with deployment (use caution)"
fi

echo "========================================="
echo ""
```

**Important Notes:**
- **MANDATORY for scheduled deployments** (hours may have passed since initial check)
- **Optional for immediate deployments** (minimal time has passed)
- This is a quick check (3-second timeout per server)
- Blocks deployment if time drift > 5 seconds
- If network is unreachable, shows warning but allows deployment
- Runs immediately before Jenkins trigger

### Step 5: Send Initial Slack Notification (Deployment Starting)

**Purpose**: Notify team that deployment is starting and create a thread for status updates.

**IMPORTANT**: This initial notification is sent when deployment STARTS. If deployment/validation/PDV fails, do NOT send any follow-up thread reply. The initial message will remain without updates.

**Target Channels**:
- C09L9LR1B37 (creates thread for final reply with links)
- C0AGVP8DZUH (monitoring channel)

**Message Format**:
```
[TICKET] Deployment of R<major>.<minor> on <SERVICE_TYPE> on <POP1>, <POP2>, ...
```

**Example**:
```
[ENG-909296] Deployment of R134.0 on VPPGRE on ICN1, MNL1
```

**Implementation**:

Use the slack-notify skill to send the message:

```python
python3 << 'EOF'
from slack_sdk import WebClient
import os
import sys

# Get token
token = os.environ.get('SLACK_BOT_TOKEN')
if not token:
    print("❌ Error: SLACK_BOT_TOKEN not found")
    sys.exit(1)

# Format message
ticket = "ENG-909296"  # From TICKET parameter
release = "134.0.8.3068"  # From RELEASE parameter
major_minor = ".".join(release.split(".")[:2])  # Extract "134.0"
service = "VPPGRE"  # nsvppgregw -> VPPGRE, nsvppipsecgw -> VPPIPSEC
pops = "ICN1, MNL1"  # Uppercase POPs, comma-separated

message = f"[{ticket}] Deployment of R{major_minor} on {service} on {pops}"

# Send message to both channels
client = WebClient(token=token)
thread_ts = None

try:
    # Send to C09L9LR1B37 (main channel, save thread_ts)
    response = client.chat_postMessage(
        channel="C09L9LR1B37",
        text=message
    )
    thread_ts = response['ts']
    print(f"SLACK_THREAD_TS={thread_ts}")
    print(f"✓ Slack notification sent to C09L9LR1B37: {message}")

    # Send to C0AGVP8DZUH (monitoring channel)
    client.chat_postMessage(
        channel="C0AGVP8DZUH",
        text=message
    )
    print(f"✓ Slack notification sent to C0AGVP8DZUH: {message}")

except Exception as e:
    print(f"❌ Failed to send Slack notification: {e}")
    sys.exit(1)
EOF
```

**Important Notes**:
- Extract major.minor version from full release (e.g., "134.0.8.3068" → "R134.0")
- Service name mapping:
  - `nsvppgregw` → `VPPGRE`
  - `nsvppipsecgw` → `VPPIPSEC`
  - `ecgw` → `ECGW`
  - `steeringlb` → `STEERINGLB`
- POPs must be UPPERCASE and comma-separated
- **Send to BOTH channels**: C09L9LR1B37 and C0AGVP8DZUH
- **SAVE the thread_ts value** from C09L9LR1B37 response - needed for reply after completion
- If Slack send fails, log error but continue with deployment (don't block deployment)

**Example Output**:
```
SLACK_THREAD_TS=1706024400.123456
✓ Slack notification sent to C09L9LR1B37: [ENG-909296] Deployment of R134.0 on VPPGRE on ICN1, MNL1
✓ Slack notification sent to C0AGVP8DZUH: [ENG-909296] Deployment of R134.0 on VPPGRE on ICN1, MNL1
```

---

### Step 6: Trigger Deployment via Jenkins CLI (SYNC MODE - WAIT FOR COMPLETION)

**🚨 PREREQUISITE: Step 5 (Slack Notification) MUST be completed BEFORE this step**

**CRITICAL: Only trigger if Step 3 safety check passed (SKIP_TRIGGER=false)**

**For Scheduled Deployments: Also verify Step 4 time check passed AND Step 5 Slack notification sent**

**🚨 CRITICAL WARNING: NEVER KILL JENKINS CLI PROCESS 🚨**

**ABSOLUTE RULE - NO EXCEPTIONS:**
- ❌ **NEVER kill the jenkins-cli.jar process while deployment is running**
- ❌ **NEVER interrupt or stop the sync mode command**
- ❌ **NEVER kill any process with "jenkins-cli.jar" in its name**
- ✅ **ALWAYS let the Jenkins CLI process run to completion naturally**
- ✅ **ONLY kill if user explicitly asks to abort the deployment**

**WHY THIS IS CRITICAL:**
- Jenkins CLI in sync mode (`-s` flag) maintains an active connection to the Jenkins build
- When you kill the Jenkins CLI process, it sends an ABORT signal to Jenkins
- This immediately terminates the running deployment pipeline
- The deployment will show status: ABORTED
- Systems may be left in inconsistent/partial deployment state
- You will need to trigger a completely new deployment

**WHAT TO DO:**
- Let the sync mode command block and wait (this is expected behavior)
- The command will complete naturally when deployment finishes (typically 3-6 minutes)
- Do not attempt to "monitor" by killing and using API - sync mode handles this
- If deployment takes longer than expected, wait patiently
- Only if user explicitly asks to abort, then you may kill the process

**Method: Sync Mode - Simple and Reliable**
- Trigger build with `-s` flag (sync mode - blocks until completion)
- Wait for entire deployment to complete (DO NOT KILL THE PROCESS)
- After deployment completes, automatically proceed to validation and PDV
- Simple, sequential approach

**Prerequisites:**
- Jenkins CLI: `~/.claude/jenkins-cli.jar`
- Java OpenJDK 17+: `brew install openjdk@17`
- Java in PATH: `export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"`

**⚠️ CRITICAL: Jenkins CLI Jar Path**

**ALWAYS use the correct path:**
- ✅ **CORRECT**: `~/.claude/jenkins-cli.jar` or `~/.claude/jenkins-cli.jar`
- ❌ **WRONG**: `~/jenkins-cli.jar` (this file does NOT exist)

**When executing commands, use the full path to avoid errors:**
```bash
java -jar ~/.claude/jenkins-cli.jar ...
```

**⚠️ CRITICAL: Jenkins CLI Authentication Format**

**MUST follow this EXACT format - DO NOT deviate:**
1. ✅ Use `-auth` (NOT `-http -auth` or any other variation)
2. ✅ Use FULL email address: `your-username@your-company.com` (NOT just `your-username`)
3. ✅ Include ALL parameters shown below (NOT just a subset)
4. ✅ POPs must be lowercase: `bue1,mia2` (NOT `BUE1,MIA2`)
5. ✅ Use sync mode flag: `-s` (after service name in build command)

**Common Mistakes to AVOID:**
- ❌ Using `-http -auth` instead of `-auth` → Results in 401 Unauthorized
- ❌ Using `your-username` instead of `your-username@your-company.com` → Results in 401 Unauthorized
- ❌ **Missing ANSIBLE_COMPONENT_NAME parameter** → **Results in immediate build failure: "FATAL: No components have been specified"**
- ❌ Missing other required parameters (only passing POPS, RELEASE, etc.) → POPs not selected in Jenkins UI
- ❌ Using uppercase POPs → May cause issues with parameter matching

**⚠️ CRITICAL PRE-TRIGGER CHECKLIST:**

Before triggering ANY Jenkins deployment, verify ALL three mandatory parameters are included:
1. ✅ **ANSIBLE_COMPONENT_NAME** = service name (nsvppgregw, nsvppipsecgw, ecgw, steeringlb)
2. ✅ **ANSIBLE_HOSTGROUPS** = service name
3. ✅ **ANSIBLE_CONFIG_IMAGE_NAME** = service-ansible-config

**If any of these are missing, STOP and add them before triggering!**

**Command with Retry Logic:**
```bash
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"

# Step 6a: Trigger Jenkins build ONLY if safety check passed
if [ "$SKIP_TRIGGER" = false ]; then
  echo "Triggering Jenkins build (sync mode - will wait for completion)..."
  echo ""

  # Attempt 1: Trigger with -s flag (sync - waits for completion)
  java -jar ~/.claude/jenkins-cli.jar \
    -s https://cdjenkins.sjc1.nskope.net/ \
    -auth your-username@your-company.com:your-api-token \
    build one_button_<service> -s \
    -p POPS=<pop> \
    -p RELEASE=<version> \
    -p ANSIBLE_CONFIG_IMAGE_TAG=<tag> \
    -p ANSIBLE_HOSTGROUPS=<service> \
    -p ANSIBLE_ARTIFACTORY_CHANNEL=ipsec-gre-production-docker \
    -p TICKET=<ticket> \
    -p SELECT_ALL_POPS="" \
    -p REGIONS="America,APAC,Europe" \
    -p POP_TYPES="MP,DP,GCP,EKS" \
    -p SELECT_ALL_COMPONENTS="" \
    -p ANSIBLE_COMPONENT_NAME=<service> \
    -p ANSIBLE_CONFIG_IMAGE_NAME=<service>-ansible-config \
    -p ANSIBLE_VERBOSITY=2 \
    -p ANSIBLE_CORE_VERSION=2.15 \
    -p SLACK_CHANNEL="#vpp-ipsec-gre-self-service-deployment" \
    -p BYPASS_MONITORING_RESULT=YES \
    -p BYPASS_JIRA=YES \
    -p RUN_QE_PDV=DEPLOY_ONLY \
    -p DEPLOY_TYPE=DEPLOY

  DEPLOY_EXIT_CODE=$?

  # Retry logic: If first attempt fails, wait 1 minute and retry once
  if [ $DEPLOY_EXIT_CODE -ne 0 ]; then
    echo "❌ Deployment attempt 1 failed with exit code: $DEPLOY_EXIT_CODE"
    echo "⏳ Waiting 60 seconds before retry..."
    sleep 60

    echo ""
    echo "🔄 Retrying deployment (attempt 2)..."
    echo ""

    # Attempt 2: Retry with same command
    java -jar ~/.claude/jenkins-cli.jar \
      -s https://cdjenkins.sjc1.nskope.net/ \
      -auth your-username@your-company.com:your-api-token \
      build one_button_<service> -s \
      -p POPS=<pop> \
      -p RELEASE=<version> \
      -p ANSIBLE_CONFIG_IMAGE_TAG=<tag> \
      -p ANSIBLE_HOSTGROUPS=<service> \
      -p ANSIBLE_ARTIFACTORY_CHANNEL=ipsec-gre-production-docker \
      -p TICKET=<ticket> \
      -p SELECT_ALL_POPS="" \
      -p REGIONS="America,APAC,Europe" \
      -p POP_TYPES="MP,DP,GCP,EKS" \
      -p SELECT_ALL_COMPONENTS="" \
      -p ANSIBLE_COMPONENT_NAME=<service> \
      -p ANSIBLE_CONFIG_IMAGE_NAME=<service>-ansible-config \
      -p ANSIBLE_VERBOSITY=2 \
      -p ANSIBLE_CORE_VERSION=2.15 \
      -p SLACK_CHANNEL="#vpp-ipsec-gre-self-service-deployment" \
      -p BYPASS_MONITORING_RESULT=YES \
      -p BYPASS_JIRA=YES \
      -p RUN_QE_PDV=DEPLOY_ONLY \
      -p DEPLOY_TYPE=DEPLOY

    DEPLOY_EXIT_CODE=$?
  fi

  # Check final result
  echo ""
  if [ $DEPLOY_EXIT_CODE -eq 0 ]; then
    echo "✅ Deployment completed successfully!"
    echo ""
    echo "Proceeding to post-deployment validation and PDV testing..."
  else
    echo "❌ Deployment failed after retry with exit code: $DEPLOY_EXIT_CODE"
    echo "❌ Aborting deployment workflow"
    exit $DEPLOY_EXIT_CODE
  fi
else
  echo "ℹ️  Skipping trigger - using existing build #${BUILD_NUMBER}"
fi
```

**Example:**
```bash
# Trigger nsvppgregw deployment to sto1,bsb1 and wait for completion
java -jar ~/.claude/jenkins-cli.jar \
  -s https://cdjenkins.sjc1.nskope.net/ \
  -auth your-username@your-company.com:your-api-token \
  build one_button_nsvppgregw -s \
  -p POPS=sto1,bsb1 \
  -p RELEASE=134.0.2.3026 \
  -p ANSIBLE_CONFIG_IMAGE_TAG=134.0.9 \
  -p ANSIBLE_HOSTGROUPS=nsvppgregw \
  -p ANSIBLE_ARTIFACTORY_CHANNEL=ipsec-gre-production-docker \
  -p TICKET=ENG-864088 \
  -p SELECT_ALL_POPS="" \
  -p REGIONS="America,APAC,Europe" \
  -p POP_TYPES="MP,DP,GCP,EKS" \
  -p SELECT_ALL_COMPONENTS="" \
  -p ANSIBLE_COMPONENT_NAME=nsvppgregw \
  -p ANSIBLE_CONFIG_IMAGE_NAME=nsvppgregw-ansible-config \
  -p ANSIBLE_VERBOSITY=2 \
  -p ANSIBLE_CORE_VERSION=2.15 \
  -p SLACK_CHANNEL="#vpp-ipsec-gre-self-service-deployment" \
  -p BYPASS_MONITORING_RESULT=YES \
  -p BYPASS_JIRA=YES \
  -p RUN_QE_PDV=DEPLOY_ONLY \
  -p DEPLOY_TYPE=DEPLOY

echo "✅ Deployment completed!"
```

**⚠️ IMPORTANT: NO SEPARATE MONITORING TASKS NEEDED**

**Sync mode handles everything - DO NOT:**
- ❌ Create separate background tasks to poll Jenkins API
- ❌ Use `curl` commands to check build status
- ❌ Create while loops to monitor progress
- ❌ Use API to track deployment state

**Why:**
- The `-s` flag (sync mode) makes Jenkins CLI wait until deployment completes
- Exit code 0 = SUCCESS, non-zero = FAILURE
- Jenkins CLI will block for 3-6 minutes until deployment finishes
- This is the CORRECT behavior - let it block naturally

**What you CAN do:**
- ✅ Send progress notifications to C0AGVP8DZUH while sync command is running (optional)
- ✅ The notifications are informational only and don't affect the deployment
- ✅ Sync mode is the primary mechanism - notifications are supplementary

---

### Step 6.5: Fallback - Handling Stuck Jenkins CLI (Rare Case)

**⚠️ PRIMARY METHOD: Jenkins CLI Sync Mode**

**CRITICAL**: Always use Jenkins CLI with `-s` sync mode for triggering and monitoring deployments. This is the primary and preferred method.

#### When to Use Fallback API Check

**ONLY use API fallback if Jenkins CLI sync mode hasn't returned after 15 minutes.**

**Why 15 minutes?**
- Expected deployment duration: 8-10 minutes (typical)
- Buffer time for slow deployments or large POPs: 3-5 minutes
- Total safe timeout: 15 minutes
- If CLI hasn't returned by then, it's likely stuck (not the deployment itself)

#### Fallback Workflow

**Phase 1: Wait for Natural Completion (0-15 minutes)**

```bash
# Jenkins CLI sync mode is blocking and waiting
java -jar ~/.claude/jenkins-cli.jar \
  -s https://cdjenkins.sjc1.nskope.net/ \
  -auth your-username@your-company.com:your-api-token \
  build one_button_nsvppgregw -s \
  -p POPS=... -p RELEASE=... [other params]

# Let it complete naturally - DO NOT interrupt
# This is the CORRECT and PRIMARY method
```

**Phase 2: Fallback Check (After 15 minutes)**

If Jenkins CLI hasn't returned after 15 minutes, check actual deployment status via API:

```bash
# Extract build number from CLI output (e.g., "Started one_button_nsvppgregw #287")
BUILD_NUMBER=287

# Check build status via API
curl -s -u your-username@your-company.com:your-api-token \
  "https://cdjenkins.sjc1.nskope.net/job/one_button_nsvppgregw/${BUILD_NUMBER}/api/json" \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Result: {data['result']}\"); print(f\"Building: {data['building']}\")"
```

**Expected Output:**
```
Result: SUCCESS       # or FAILURE/UNSTABLE/ABORTED
Building: False       # Deployment completed
```

**Phase 3: Handle Result**

```bash
# If deployment completed successfully (result=SUCCESS or UNSTABLE, building=False)
if [ "$RESULT" = "SUCCESS" ] || [ "$RESULT" = "UNSTABLE" ]; then
  if [ "$BUILDING" = "False" ]; then
    echo "✅ Deployment completed successfully (detected via API fallback)"
    # Kill stuck CLI process
    pkill -f "java -jar.*jenkins-cli.jar.*one_button"
    # Proceed with validation and PDV
  fi
fi

# If deployment failed
if [ "$RESULT" = "FAILURE" ] || [ "$RESULT" = "ABORTED" ]; then
  if [ "$BUILDING" = "False" ]; then
    echo "❌ Deployment failed (detected via API fallback)"
    # Kill stuck CLI process
    pkill -f "java -jar.*jenkins-cli.jar.*one_button"
    # Report failure
  fi
fi

# If still building (rare - may need more time)
if [ "$BUILDING" = "True" ]; then
  echo "⏳ Deployment still running after 15 minutes, wait another 5 minutes..."
  # Wait and check again
fi
```

#### Important Notes

1. **Primary Method**: Always trigger via Jenkins CLI sync mode
2. **Let It Complete**: Wait for natural completion (15 minutes max for deployments)
3. **Fallback Only**: API check is safety mechanism for stuck CLI
4. **CLI Can Hang**: Sometimes CLI process hangs even though deployment completes
5. **Deployment Still Completes**: Stuck CLI doesn't affect actual deployment execution
6. **Kill Safely**: Only kill CLI process after confirming deployment status via API
7. **Never Use API for Triggering**: API is ONLY for status checking, NEVER for triggering
8. **UNSTABLE is OK**: UNSTABLE status often means nodes deployed successfully (check validation)

#### Example: Complete Workflow with Fallback

```bash
SERVICE="nsvppgregw"
POPS="mil2,hel1,prg1"
TIMEOUT=900  # 15 minutes in seconds
START_TIME=$(date +%s)
OUTPUT_FILE="/tmp/deployment_output_$$.log"

echo "Triggering deployment in background to enable timeout check..."

# Trigger deployment with output capture
java -jar ~/.claude/jenkins-cli.jar \
  -s https://cdjenkins.sjc1.nskope.net/ \
  -auth your-username@your-company.com:your-api-token \
  build one_button_${SERVICE} -s \
  -p POPS=${POPS} \
  -p RELEASE=134.0.8.3068 \
  -p ANSIBLE_CONFIG_IMAGE_TAG=134.0.14 \
  [other params...] > "$OUTPUT_FILE" 2>&1 &

CLI_PID=$!

# Monitor CLI process with timeout
while kill -0 $CLI_PID 2>/dev/null; do
  ELAPSED=$(($(date +%s) - START_TIME))

  if [ $ELAPSED -gt $TIMEOUT ]; then
    echo "⚠️ Jenkins CLI stuck after 15 minutes, checking deployment status via API..."

    # Extract build number from output
    BUILD_NUM=$(grep -oP 'Started one_button_\w+ #\K\d+' "$OUTPUT_FILE")

    if [ -z "$BUILD_NUM" ]; then
      echo "❌ Could not determine build number, CLI may have failed to start"
      kill $CLI_PID
      exit 1
    fi

    # Check via API
    API_RESPONSE=$(curl -s -u your-username@your-company.com:your-api-token \
      "https://cdjenkins.sjc1.nskope.net/job/one_button_${SERVICE}/${BUILD_NUM}/api/json")

    RESULT=$(echo "$API_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('result', 'UNKNOWN'))")
    BUILDING=$(echo "$API_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('building', 'True'))")

    if [ "$BUILDING" = "False" ]; then
      if [ "$RESULT" = "SUCCESS" ] || [ "$RESULT" = "UNSTABLE" ]; then
        echo "✅ Deployment completed (Result: $RESULT) - CLI was stuck"
        kill $CLI_PID 2>/dev/null
        echo "Proceeding with validation..."
        exit 0
      else
        echo "❌ Deployment failed (Result: $RESULT) - CLI was stuck"
        kill $CLI_PID 2>/dev/null
        exit 1
      fi
    else
      echo "⏳ Still building after 15 minutes (unusual), waiting 5 more minutes..."
      TIMEOUT=$((TIMEOUT + 300))  # Add 5 minutes
    fi
  fi

  sleep 10
done

# CLI completed naturally (this is the expected path)
wait $CLI_PID
EXIT_CODE=$?

echo ""
echo "Jenkins CLI completed naturally with exit code: $EXIT_CODE"
cat "$OUTPUT_FILE"

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ Deployment completed successfully"
  exit 0
else
  echo "⚠️ Deployment completed with non-zero exit code (may be UNSTABLE)"
  exit $EXIT_CODE
fi
```

#### When NOT to Use Fallback

- ❌ Don't check API "to be safe" after 5 minutes
- ❌ Don't use API as primary monitoring method
- ❌ Don't kill CLI just because it's taking longer than expected
- ✅ ONLY use fallback if CLI genuinely stuck after 15 minutes

---

### Step 7: Post-Deployment Validation (VPP GRE Only) - AUTOMATIC AFTER DEPLOYMENT

**IMPORTANT: Only for service `nsvppgregw` (VPP GRE gateway)**

**This step runs AUTOMATICALLY after Step 6 deployment completes successfully.**

After the sync mode deployment finishes, automatically identify which nodes were deployed and run post-deployment validation on each.

---

## ⚠️ CRITICAL - DO NOT CREATE YOUR OWN VALIDATION SCRIPT ⚠️

**YOU MUST USE THE EXISTING VALIDATION SCRIPT ON EACH DEVICE**

**Script Location (On Device)**: `/opt/ns/nssurveyvm/scripts/nsvppgregw/vppgregw_diagnostic.py`

**❌ WRONG - DO NOT DO THIS:**
- Creating a new bash script with basic checks (vppctl show version, show interfaces, etc.)
- Writing your own validation logic from scratch
- Using simple commands without the comprehensive script
- Copying scripts from local machine

**✅ CORRECT - ALWAYS DO THIS:**
Run the validation script directly from its location on the device:
```bash
tsh ssh --cluster <pop> <node> "sudo python3 /opt/ns/nssurveyvm/scripts/nsvppgregw/vppgregw_diagnostic.py"
```

**The validation script is already present on every VPP GRE gateway and validates exactly 25 test cases including:**
- VPP process status (supervisorctl)
- Health-service and cfgagentv2 status
- Loopback interface VIP configuration
- Ingress interface and IP rule config
- VPP version and plugins
- Event forwarder reachability
- CFW and Proxy VIP reachability and health
- Tenant directory and config files
- DSR IP reachability
- Jumbo interface checks
- Log and core file checks

**If you use anything other than this on-device validation script, the validation is INCOMPLETE and INCORRECT.**

---

**Automatic Execution Workflow:**

```bash
# After deployment completes successfully in Step 4

echo ""
echo "========================================="
echo "POST-DEPLOYMENT VALIDATION"
echo "========================================="
echo "Service: nsvppgregw (VPP GRE)"
echo "POPs: <pops>"
echo ""

# Step 5a: Get list of deployed hosts from Jenkins console (if needed)
# Or use known hostnames based on POP

# For each POP, validate its nodes
for POP in ${POPS//,/ }; do
  echo "Validating nodes in POP: $POP"

  # Get list of nodes for this POP (typically nsvppgregw01, nsvppgregw02, etc.)
  # This can be determined from service discovery or hardcoded patterns
  NODES=("nsvppgregw01.${POP}.nskope.net" "nsvppgregw02.${POP}.nskope.net")

  for NODE in "${NODES[@]}"; do
    echo ""
    echo "→ Validating: $NODE"

    # Run validation script directly from device
    if tsh ssh --cluster "$POP" "$NODE" "sudo python3 /opt/ns/nssurveyvm/scripts/nsvppgregw/vppgregw_diagnostic.py"; then
      echo "  ✅ Validation PASSED: $NODE"
    else
      echo "  ❌ Validation FAILED: $NODE"
    fi
  done
done

echo ""
echo "========================================="
echo "POST-DEPLOYMENT VALIDATION COMPLETE"
echo "========================================="
echo ""
```

```bash
# This happens automatically in Step 4 monitoring loop
HOSTNAME="nsvppgregw01.los1.nskope.net"
POP="los1"

echo "✅ $HOSTNAME deployment completed - launching post-validation"

# Launch validation in background (non-blocking)
(
  echo "[$(date)] Starting post-validation for $HOSTNAME"

  # Run validation script directly from device
  tsh ssh --cluster "$POP" "$HOSTNAME" \
    "sudo python3 /opt/ns/nssurveyvm/scripts/nsvppgregw/vppgregw_diagnostic.py" \
    > "/tmp/post_validation_${HOSTNAME}.log" 2>&1

  # Check result
  if [ $? -eq 0 ]; then
    echo "[$(date)] ✅ Post-validation PASSED for $HOSTNAME"
  else
    echo "[$(date)] ❌ Post-validation FAILED for $HOSTNAME"
  fi

  # After this validation completes, check if POP is ready for PDV
  check_pop_ready_for_pdv "$POP"

) &  # Background execution - doesn't block monitoring
```

**Timeline Example (Parallel Execution):**

```
Time  | Event
------|---------------------------------------------------------------
T+0   | Jenkins deployment starts (all POPs/hosts)
T+5m  | Host los1/node01 completes → Validation starts (background)
T+6m  | Host ams1/node01 completes → Validation starts (background)
T+7m  | Host los1/node02 completes → Validation starts (background)
T+8m  | Host los1/node01 validation completes
T+9m  | Host ams1/node02 completes → Validation starts (background)
T+10m | Host los1/node02 validation completes
      | → All los1 hosts validated → Add los1 to PDV queue
T+11m | Host ams1/node01 validation completes
T+12m | Host ams1/node02 validation completes
      | → All ams1 hosts validated → Add ams1 to PDV queue
```

**Key Differences from Old Model:**

| Aspect | Old Model (Sequential) | New Model (Parallel) |
|--------|----------------------|---------------------|
| **Trigger** | Manual batch after all deployments | Automatic per-host when ready |
| **Timing** | Wait for ALL hosts to deploy | Start immediately per host |
| **Parallelism** | All validations at once at end | Validations overlap with deployment |
| **Time Saved** | 0 (sequential stages) | 5-10 minutes (overlapping stages) |

**Validation Execution Details:**

Each validation runs these steps:
1. Execute validation script from device location via `tsh ssh` with sudo: `/opt/ns/nssurveyvm/scripts/nsvppgregw/vppgregw_diagnostic.py`
2. Capture output to log file: `/tmp/post_validation_<hostname>.log`
3. Check exit code: 0 = PASSED, non-zero = FAILED
4. After completion, check if parent POP is ready for PDV

**⚠️ CRITICAL: Correct Result Counting Method**

The validation script (`/opt/ns/nssurveyvm/scripts/nsvppgregw/vppgregw_diagnostic.py`) runs **exactly 25 test cases** covering all critical components.

**DO NOT use `grep -c "PASS"` to count results** - this counts ALL occurrences of the word "PASS" in the output, which includes multiple mentions per test case and can give inflated counts (e.g., 60+ instead of 25).

**CORRECT METHOD - Parse "Overall Result Summary":**

The script prints an "Overall Result Summary" section at the end with each test case result. Parse this section to get accurate counts.

**CRITICAL: Use Case-Insensitive Grep**
- The script output contains both "Testcase" (lowercase c) and "TestCase" (capital C)
- Use `-i` flag for case-insensitive matching: `grep -iE "testcase [0-9]+:.*PASS"`
- Expected: 25 PASS, 0 FAIL

**MOST IMPORTANT: Exit Code**
- Exit code 0 = All 25 tests PASSED
- Exit code non-zero = At least one test FAILED

**Example Correct Parsing:**
```bash
# Read the validation output log
cat /tmp/post_validation_nsvppgregw01.bue1.nskope.net.log

# Look for the "Overall Result Summary" section at the end:
# Overall Result Summary:
# testcase1: PASS
# testcase2: PASS
# testcase3: PASS
# ...
# testcase25: PASS

# Count results from summary section only (use -i for case-insensitive to catch both 'Testcase' and 'TestCase')
PASS_COUNT=$(grep -A 50 "Overall Result Summary:" /tmp/post_validation_nsvppgregw01.bue1.nskope.net.log | grep -iE "testcase [0-9]+:.*PASS" | wc -l | tr -d ' ')
FAIL_COUNT=$(grep -A 50 "Overall Result Summary:" /tmp/post_validation_nsvppgregw01.bue1.nskope.net.log | grep -iE "testcase [0-9]+:.*FAIL" | wc -l | tr -d ' ')

echo "Post-validation results: $PASS_COUNT PASS, $FAIL_COUNT FAIL (out of 25 test cases)"
echo "Exit code 0 = All 25 tests passed"
```

**Key Points:**
- The script runs **exactly 25 test cases** covering all critical components
- Parse the "Overall Result Summary" section at the end of output
- Do NOT count all occurrences of "PASS" in the full output
- **Exit code 0 = All 25 tests passed** (most important indicator)
- Use **case-insensitive** grep: `grep -iE "testcase [0-9]+:.*PASS"` (catches both "Testcase" and "TestCase")
- Expected result: 25 PASS, 0 FAIL

**Real-Time Progress Reporting:**

As validations complete in real-time, report progress to user:

```
[18:35:12] ✅ nsvppgregw01.los1.nskope.net - Deployment PASSED
[18:35:15]    └─ Post-validation started (background)
[18:36:45] ✅ nsvppgregw02.los1.nskope.net - Deployment PASSED
[18:36:48]    └─ Post-validation started (background)
[18:38:20] ✅ nsvppgregw01.los1.nskope.net - Post-validation PASSED
[18:39:15] ✅ nsvppgregw02.los1.nskope.net - Post-validation PASSED
[18:39:16] 🎯 POP los1 ready for PDV testing (2/2 hosts validated)
[18:39:16]    └─ Added to PDV queue
```

**Validation Results Summary (After All Complete):**

After all hosts complete validation, provide summary:

**All validated nodes passed:**
```
========================================
POST-DEPLOYMENT VALIDATION SUMMARY
========================================

Total Nodes Validated: 4
✅ Passed: 4 (100%)
❌ Failed: 0

Results by POP:

POP: los1
├─ ✅ nsvppgregw01.los1.nskope.net: PASSED
└─ ✅ nsvppgregw02.los1.nskope.net: PASSED

POP: ams1
├─ ✅ nsvppgregw01.ams1.nskope.net: PASSED
└─ ✅ nsvppgregw02.ams1.nskope.net: PASSED

All post-deployment validations completed successfully.
POPs ready for PDV: los1, ams1
========================================
```

**If any validated nodes fail:**
```
========================================
POST-DEPLOYMENT VALIDATION SUMMARY
========================================

Total Nodes Validated: 3
✅ Passed: 2 (67%)
❌ Failed: 1 (33%)

Results by POP:

POP: los1
├─ ✅ nsvppgregw01.los1.nskope.net: PASSED
└─ ❌ nsvppgregw02.los1.nskope.net: FAILED
    Error: [validation error details from log]

Summary:
- 2 nodes validated successfully
- 1 node failed validation (see details above)
- POP los1 still eligible for PDV (has passing nodes)

Note: Validation failures do not block PDV testing
========================================
```

**Mixed Scenario (Some Nodes Failed Deployment):**
```
========================================
POST-DEPLOYMENT VALIDATION SUMMARY
========================================

Total Nodes in Deployment: 5
✅ Deployed Successfully: 4 (80%)
❌ Failed Deployment: 1 (20%)
✅ Validated: 4/4 (100% of deployed nodes)

Results by POP:

POP: jnb1
├─ ✅ nsvppgregw01.jnb1.nskope.net: Deployed ✅ | Validated ✅
├─ ✅ nsvppgregw02.jnb1.nskope.net: Deployed ✅ | Validated ✅
└─ ❌ nsvppgregw03.jnb1.nskope.net: Deployed ❌ | Validation ⏭️ SKIPPED

POP: cpt1
├─ ✅ nsvppgregw01.cpt1.nskope.net: Deployed ✅ | Validated ✅
└─ ✅ nsvppgregw02.cpt1.nskope.net: Deployed ✅ | Validated ✅

POPs Ready for PDV:
✅ jnb1 (2/3 nodes operational)
✅ cpt1 (2/2 nodes operational)

Note: Validation only performed on nodes where deployment succeeded
========================================
```

**Important Notes:**
- Post-deployment validation runs **only for nsvppgregw** service
- **Validation launches automatically** as each host completes deployment (failed=0)
- **No manual intervention required** - fully automatic from Step 4 monitoring
- **Parallel execution** - multiple validations run simultaneously
- **Skip validation** only for nodes that failed deployment
- **Real-time progress updates** as hosts complete
- Other services (nsvppipsecgw, ecgw, steeringlb) will have separate scripts (to be added later)
- If validation fails, just report - no remediation action required
- Failed validations do NOT block PDV testing for the POP

### Step 8: Production PDV Testing - AUTOMATIC AFTER VALIDATION

**IMPORTANT: PDV testing runs AUTOMATICALLY after Step 6 validation completes**

After post-deployment validation finishes, automatically run PDV testing for each POP sequentially.

**Applicable Services:**
- `nsvppgregw` (VPP GRE gateway)
- `nsvppipsecgw` (VPP IPSEC gateway)

**Execution Mode**: Sequential (one POP at a time) due to shared test client

**Skill Location**: `~/.claude/skills/prod-pdv`

**Automatic Execution Workflow:**

```bash
# After post-deployment validation completes in Step 5

echo ""
echo "========================================="
echo "PRODUCTION PDV TESTING"
echo "========================================="
echo "Service: nsvppgregw (VPP GRE)"
echo "POPs: <pops>"
echo ""

# Run PDV testing for each POP sequentially
for POP in ${POPS//,/ }; do
  echo "→ Running PDV testing for POP: $POP"
  echo ""

  # Determine gateway type
  if [[ "<service>" == *"gre"* ]]; then
    GATEWAY_TYPE="GRE"
  elif [[ "<service>" == *"ipsec"* ]]; then
    GATEWAY_TYPE="IPSEC"
  fi

  # Invoke prod-pdv skill for this POP
  # The skill will handle Job 1 and Job 2 execution
  echo "Invoking prod-pdv skill for $POP ($GATEWAY_TYPE)"

  # Use the Skill tool to invoke prod-pdv
  # Example: Skill tool with args: "run vpp gre dpas pdv on pop $POP"

  echo "  ✅ PDV testing completed for $POP"
  echo ""
done

echo "========================================="
echo "PDV TESTING COMPLETE"
echo "========================================="
echo ""
```

#### Simplified Workflow:

**Phase 1: POP Readiness Detection (Automatic)**

When a node completes post-deployment validation (in Step 5), automatically check if its POP is ready for PDV:

```python
def check_pop_ready_for_pdv(pop):
    """
    Automatically called after each validation completes.
    Checks if POP is ready to be added to PDV queue.
    """
    pop_data = deployment_state["pops"][pop]

    # Check 1: All hosts have completed deployment
    all_deployments_done = all(
        host["deployment_status"] in ["PASSED", "FAILED"]
        for host in pop_data["hosts"].values()
    )

    # Check 2: At least one host passed deployment
    passed_hosts = [
        host for host in pop_data["hosts"].values()
        if host["deployment_status"] == "PASSED"
    ]

    if not passed_hosts:
        # No hosts passed, skip PDV
        pop_data["pdv_status"] = "SKIPPED"
        echo "⏭️  POP $pop - PDV SKIPPED (no nodes passed deployment)"
        return False

    # Check 3: All passed hosts have completed post-validation
    all_validations_done = all(
        host["post_validation_status"] in ["PASSED", "FAILED"]
        for host in passed_hosts
    )

    # POP is ready if all checks pass
    if all_deployments_done and all_validations_done:
        echo "🎯 POP $pop is ready for PDV testing"
        add_to_pdv_queue(pop)
        return True

    return False
```

**Phase 2: PDV Queue Management (Automatic)**

POPs are added to queue automatically as they become ready:

```bash
# PDV queue stored in file
PDV_QUEUE="/tmp/pdv_queue_${BUILD_NUMBER}.txt"

function add_to_pdv_queue() {
  local POP=$1

  # Check if already in queue
  if ! grep -q "^${POP}$" "$PDV_QUEUE"; then
    echo "$POP" >> "$PDV_QUEUE"
    echo "✅ Added $POP to PDV queue (position: $(wc -l < $PDV_QUEUE))"
  fi
}
```

**Phase 3: PDV Coordinator (Sequential Execution)**

Background coordinator process continuously monitors queue and executes PDV tests:

```bash
function pdv_coordinator() {
  """
  Runs in background throughout deployment.
  Processes PDV queue sequentially (one POP at a time).
  """
  echo "PDV Coordinator started (waiting for POPs to become ready)"

  while true; do
    # Check if there are POPs in queue
    if [ -s "$PDV_QUEUE" ]; then
      # Get first POP from queue
      NEXT_POP=$(head -1 "$PDV_QUEUE")

      # Remove from queue
      tail -n +2 "$PDV_QUEUE" > "${PDV_QUEUE}.tmp"
      mv "${PDV_QUEUE}.tmp" "$PDV_QUEUE"

      echo ""
      echo "================================"
      echo "🚀 Starting PDV for: ${NEXT_POP}"
      echo "================================"

      # Run PDV testing (BLOCKING - wait for completion)
      run_pdv_for_pop "$NEXT_POP"  # Invokes prod-pdv skill

      echo "✅ PDV completed for ${NEXT_POP}"
      echo ""

    else
      # Queue empty - check if all work is done
      if all_pops_processed; then
        echo "✅ PDV Coordinator: All POPs processed"
        break
      fi

      # Wait before checking queue again
      sleep 10
    fi
  done
}

# Launch coordinator in background at start of Step 4
pdv_coordinator &
PDV_COORDINATOR_PID=$!
```

**Phase 4: Automatic PDV Execution per POP**

When coordinator picks a POP from queue, it invokes the prod-pdv skill:

```bash
function run_pdv_for_pop() {
  local POP=$1

  # Determine gateway type
  if [[ "$SERVICE" == *"gre"* ]]; then
    GATEWAY_TYPE="GRE"
  elif [[ "$SERVICE" == *"ipsec"* ]]; then
    GATEWAY_TYPE="IPSEC"
  else
    echo "⚠️  Unknown gateway type"
    return 1
  fi

  # Identify which nodes passed (for smart PDV routing)
  passed_nodes=$(get_passed_nodes_for_pop "$POP")

  echo "Passed nodes in $POP: $passed_nodes"
  echo "Invoking prod-pdv skill for $POP ($GATEWAY_TYPE)"

  # Invoke prod-pdv skill (this will run Job 1 and Job 2)
  # The skill knows to route traffic to passed nodes only
  invoke_prod_pdv_skill "$POP" "$GATEWAY_TYPE" "$passed_nodes"

  # Record result
  PDV_RESULT=$?
  if [ $PDV_RESULT -eq 0 ]; then
    deployment_state[pops][$POP][pdv_status]="PASSED"
    echo "✅ PDV PASSED for $POP"
  else
    deployment_state[pops][$POP][pdv_status]="FAILED"
    echo "❌ PDV FAILED for $POP"
  fi
}
```

**Timeline Example (Automatic Parallel/Sequential Hybrid):**

```
Time  | Event
------|---------------------------------------------------------------
T+0   | Jenkins deployment starts
      | → PDV Coordinator starts in background (waits for queue)
T+5m  | los1/node01 deploys → validation starts
T+7m  | los1/node02 deploys → validation starts
T+9m  | los1/node01 validation completes
T+10m | los1/node02 validation completes
      | → los1 ready → Added to PDV queue (position 1)
      | → Coordinator sees queue → Starts PDV for los1
T+11m | ams1/node01 deploys → validation starts
T+12m | ams1/node02 deploys → validation starts
T+14m | ams1/node01 validation completes
T+15m | ams1/node02 validation completes
      | → ams1 ready → Added to PDV queue (position 2)
      | → Coordinator busy with los1, ams1 waits in queue
T+17m | los1 PDV completes ✅
      | → Coordinator picks ams1 from queue → Starts PDV for ams1
T+24m | ams1 PDV completes ✅
      | → Queue empty → Coordinator finishes
```

**Key Differences from Old Model:**

| Aspect | Old Model (Manual) | New Model (Automatic) |
|--------|-------------------|----------------------|
| **Trigger** | Manual after all validations | Automatic queue-based |
| **Queue** | No queue, all at once | Sequential queue |
| **Start Time** | After ALL POPs validated | As EACH POP becomes ready |
| **Parallelism** | Attempted (conflicts) | Sequential (no conflicts) |
| **Coordination** | None | Background coordinator |
| **Time Saved** | 0 | Starts earlier, overlaps with deployment |

3. **Trigger prod-pdv Skill with Node-Specific Parameters**:

   **CRITICAL**: PDV jobs need to know which specific nodes to test, as traffic must land on nodes that passed deployment.

   **Determine PDV Job Nodes:**

   From Step 4 (PLAY RECAP analysis), identify which nodes passed for each POP:

   Example mapping:
   ```
   POP: jnb1
   Passed Nodes: [nsvppgregw01.jnb1.nskope.net]
   Failed Nodes: [nsvppgregw03.jnb1.nskope.net]

   PDV Jobs to Run:
   - Job 2 (node 01): ✅ RUN (node 01 passed)
   - Job 1 (node 02): ⏭️ SKIP (node not in passed list)
   ```

   **Node to Job Mapping:**
   - **nsvppgregw01** → Job 2 (dst: 163.116.136.156)
   - **nsvppgregw02** → Job 1 (dst: 52.27.59.30)
   - **nsvppgregw03** → Neither (not typically in PDV jobs)

   **Command Pattern with Node Specification:**
   ```
   User request: "Run VPP <gateway_type> DPAS PDV on POP <pop> with nodes <passed_node_list>"
   ```

   **Examples:**
   - All nodes passed: "Run VPP GRE DPAS PDV on POP los1"
   - Partial pass: "Run VPP GRE DPAS PDV on POP jnb1 - note: only node01 passed, skip node02"
   - For IPSEC: "Run VPP IPSEC DPAS PDV on POP akl1"

   **Gateway Type Detection:**
   - If service = `nsvppgregw` → Gateway Type = GRE
   - If service = `nsvppipsecgw` → Gateway Type = IPSEC

   **Pass Context to PDV Skill:**

   When invoking prod-pdv skill, provide deployment context:
   - Which nodes passed deployment
   - Which nodes failed (so PDV jobs for those nodes can be skipped)
   - Full list of deployment results

4. **PDV Skill Execution with Smart Node Selection**:

   The prod-pdv skill will automatically:

   **Standard Flow (All Nodes Passed):**
   - Trigger Job 1 on node 02 (destination: 52.27.59.30)
   - Monitor tunnel establishment and RX/TX traffic
   - Wait for Job 1 completion
   - Trigger Job 2 on node 01 (destination: 163.116.136.156)
   - Monitor tunnel establishment and RX/TX traffic
   - Wait for Job 2 completion
   - Report overall success/failure

   **Partial Pass Flow (Some Nodes Failed):**

   Example: node01 passed, node02 failed
   ```
   Job 1 (Node 02 - dst 52.27.59.30): ⏭️ SKIP
   Reason: nsvppgregw02 failed deployment

   Job 2 (Node 01 - dst 163.116.136.156): ✅ RUN
   - Trigger Job 2 on node 01
   - Monitor tunnel and traffic
   - Report results
   ```

   **IMPORTANT**: Inform the prod-pdv skill about which nodes passed so it can:
   - Skip PDV jobs for failed nodes
   - Only test traffic to nodes that successfully deployed
   - Report accurately which jobs ran vs skipped

5. **Report Results for Each POP**:

   **Success:**
   ```
   ✅ Production PDV Testing: los1 - PASSED

   POP: los1
   Gateway Type: VPP GRE

   Job 1 (Node 02 - dst 52.27.59.30): ✅ SUCCESS
   - Jenkins: SUCCESS
   - Tunnel: UP
   - Traffic: RX/TX counters increasing

   Job 2 (Node 01 - dst 163.116.136.156): ✅ SUCCESS
   - Jenkins: SUCCESS
   - Tunnel: UP
   - Traffic: RX/TX counters increasing
   ```

   **Failure:**
   ```
   ❌ Production PDV Testing: los1 - FAILED

   POP: los1
   Gateway Type: VPP GRE

   Job 1 (Node 02 - dst 52.27.59.30): ✅ SUCCESS
   Job 2 (Node 01 - dst 163.116.136.156): ❌ FAILED

   Failure Details:
   [Error output from prod-pdv skill]

   Note: No action required - reporting only
   ```

6. **Final Summary (All POPs)**:

   After all eligible POPs are tested, provide a summary:

   **All POPs Tested Successfully:**
   ```
   ========================================
   PRODUCTION PDV TESTING SUMMARY
   ========================================

   Total POPs Tested: 3
   Passed: 3
   Failed: 0

   Results:
   ✅ los1 (VPP GRE) - PASSED
   ✅ ams1 (VPP GRE) - PASSED
   ✅ del1 (VPP GRE) - PASSED

   ========================================
   ```

   **Mixed Results (Some Failed PDV):**
   ```
   ========================================
   PRODUCTION PDV TESTING SUMMARY
   ========================================

   Total POPs Tested: 3
   Passed: 2
   Failed: 1

   Results:
   ✅ los1 (VPP GRE) - PASSED
   ✅ ams1 (VPP GRE) - PASSED
   ❌ del1 (VPP GRE) - FAILED

   Failed POP Details:

   del1:
   - Job 1: SUCCESS
   - Job 2: FAILED (Tunnel did not come up)

   ========================================
   ```

   **Some POPs Skipped (Deployment Failures):**
   ```
   ========================================
   PRODUCTION PDV TESTING SUMMARY
   ========================================

   Total POPs in Deployment: 2
   PDV Tested: 1
   PDV Skipped: 1 (no passed nodes)

   Results:
   ✅ jnb1 (VPP GRE) - PDV PASSED
      - Deployment: 1/2 nodes passed
      - PDV: Both jobs successful

   ⏭️  cpt1 (VPP GRE) - PDV SKIPPED
      - Deployment: 0/1 nodes passed
      - Reason: No nodes passed deployment

   Note: PDV only runs on POPs with at least one successfully deployed node

   ========================================
   ```

#### Important Notes:

- **Filtering Logic**: Only run PDV on POPs where **at least one node passed deployment**
- **Skip POPs**: If all nodes in a POP failed deployment, skip PDV testing for that POP
- **Sequential Execution**: Process POPs one at a time (NOT in parallel)
- **Wait for Completion**: Each POP's PDV testing must complete before starting the next
- **No Remediation**: Just report results, do not attempt to fix failures
- **Gateway Type Auto-Detection**: Automatically determine GRE vs IPSEC based on service
- **Jenkins Environment**: Uses separate Jenkins server (http://your-jenkins-host:8080/)
- **Testing Duration**: Each POP takes approximately 5-7 minutes (Job 1: 2-3 min, Job 2: 2-3 min)
- **Skill Integration**: Uses the existing prod-pdv skill without modification

#### Example Execution Flow:

**Scenario 1: All Nodes Passed Deployment**
```
Deployment:
- POPs: los1,ams1,del1
- Service: nsvppgregw
- All nodes passed deployment

PDV Testing Sequence:
1. Run PDV on los1 → Wait → Report
2. Run PDV on ams1 → Wait → Report
3. Run PDV on del1 → Wait → Report
4. Display final summary

Estimated Time: 15-21 minutes for 3 POPs
```

**Scenario 2: Mixed Deployment Results**
```
Deployment:
- POPs: jnb1,cpt1
- Service: nsvppgregw
- jnb1: 1/2 nodes passed
- cpt1: 0/1 nodes passed

PDV Testing Sequence:
1. Run PDV on jnb1 → Wait → Report (has passed nodes)
2. Skip PDV on cpt1 → Report skipped (no passed nodes)
3. Display final summary

Estimated Time: 5-7 minutes for 1 POP
```

### Step 7.1: Update JIRA Ticket (After Each Slot Completes Successfully)

**IMPORTANT: Update the JIRA ticket AUTOMATICALLY after each deployment slot completes all stages SUCCESSFULLY (deployment → post-validation → PDV)**

After a deployment slot completes PDV testing for all POPs in that slot, **ONLY update JIRA if all stages passed successfully**.

**When to Update:**
- **Immediate Deployments**: Update after all POPs complete all stages successfully
- **Scheduled Deployments**: Update after EACH time slot completes all stages successfully (not just at the end)
- **DO NOT UPDATE** if any stage failed (deployment, validation, or PDV)

**Success Criteria:**
- ✅ All nodes deployed successfully (or at least deployment completed)
- ✅ All deployed nodes passed post-deployment validation
- ✅ All POPs passed PDV testing (both Job 1 and Job 2)

**Update Format:**

Use JIRA MCP tool (`mcp__JIRA__jira_add_comment`) to add a comment with this exact structure:

**CRITICAL FORMATTING RULES:**
1. "Deployment - <URL>"
2. "Post deploy script - Validated"
3. Blank line
4. For each POP:
   - POP name on its own line (uppercase)
   - "PDV 01 - <URL>" on next line
   - "PDV 02 - <URL>" on next line
   - Blank line before next POP (if more POPs exist)

**CRITICAL: Only include SUCCESSFUL PDV build links**
- If a PDV job failed and was retried, ONLY include the successful retry build link
- DO NOT mention failed attempts, UNSTABLE status, or retry information in JIRA
- DO NOT include /console suffix in URLs

**Template:**
```
Deployment - <Jenkins Build URL without /console>
Post deploy script - Validated

<POP1>
PDV 01 - <Full PDV Job 1 URL without /console>
PDV 02 - <Full PDV Job 2 URL without /console>

<POP2>
PDV 01 - <Full PDV Job 1 URL without /console>
PDV 02 - <Full PDV Job 2 URL without /console>
```

**Example Comment (Exact Format):**

```
Deployment - https://cdjenkins.sjc1.nskope.net/job/one_button_nsvppgregw/276/
Post deploy script - Validated

ICN1
PDV 01 - http://your-jenkins-host:8080/job/STEERING_JENKINS/job/STEERING_MANAGEMENT/job/DPAS_PDV_Regression_Suites/job/GRE_Suites/job/VPP_GRE_PDV_ICN1/14/
PDV 02 - http://your-jenkins-host:8080/job/STEERING_JENKINS/job/STEERING_MANAGEMENT/job/DPAS_PDV_Regression_Suites/job/GRE_Suites/job/VPP_GRE_PDV_ICN1/13/

MNL1
PDV 01 - http://your-jenkins-host:8080/job/STEERING_JENKINS/job/STEERING_MANAGEMENT/job/DPAS_PDV_Regression_Suites/job/GRE_Suites/job/VPP_GRE_PDV_MNL1/22/
PDV 02 - http://your-jenkins-host:8080/job/STEERING_JENKINS/job/STEERING_MANAGEMENT/job/DPAS_PDV_Regression_Suites/job/GRE_Suites/job/VPP_GRE_PDV_MNL1/23/
```

**Important Notes:**
- Single deployment link (same Jenkins build for all POPs in the slot)
- Post deploy script status (always "Validated" if validation passed)
- POP names in UPPERCASE
- Full PDV URLs for each POP (without /console suffix)
- PDV 01 corresponds to Job 1 (Node 02, dst 52.27.59.30)
- PDV 02 corresponds to Job 2 (Node 01, dst 163.116.136.156)
- **ONLY include successful PDV build numbers** - if retry was needed, use the successful retry build number
- DO NOT mention failed attempts, retries, or UNSTABLE status in JIRA comments
- Clean, simple format with only successful results

**JIRA Update Command:**

```bash
# Use JIRA MCP tool to add comment
mcp__JIRA__jira_add_comment with:
  issueKey: <TICKET value from parameters>
  body: <formatted comment text>
```

**For Scheduled Deployments:**

Update the ticket after EACH time slot completes (not just at the end). This provides real-time visibility into deployment progress.

**Example Timeline for Scheduled Deployment:**
```
09:30 AM Slot: Deploy CCU1, DEL2
  → Deployment completes
  → Validation completes
  → PDV completes
  → Update JIRA ticket with CCU1, DEL2 status ✅

01:00 PM Slot: Deploy CPT1
  → Deployment completes
  → Validation completes
  → PDV completes
  → Update JIRA ticket with CPT1 status ✅

[Continue for remaining slots...]
```

### Step 9: Send Slack Thread Reply (ONLY on Complete Success)

**IMPORTANT**: Only update Slack thread when BOTH deployment AND PDV testing are fully successful.

**When to Update:**
- ✅ Deployment succeeded
- ✅ Post-deployment validation passed
- ✅ PDV testing passed (both Job 1 and Job 2)
- ✅ All stages completed successfully

**When NOT to Update:**
- ❌ Any stage failed (deployment, validation, or PDV)
- ❌ Do NOT post failure details to Slack thread
- ❌ Do NOT post retry information to Slack thread

**If Success After Retry:**
- Post ONLY the successful build numbers (same as JIRA)
- Do NOT mention initial failures or retry attempts
- Format: Same as JIRA comment with successful builds only

**Target Channel**: C09L9LR1B37

**Reply Method**: Thread reply using `thread_ts` from Step 5

**Message Content**: Exact same format as JIRA comment:
```
Deployment - <Jenkins Build URL>
Post deploy script - Validated

<POP1>
PDV 01 - <URL>
PDV 02 - <URL>

<POP2>
PDV 01 - <URL>
PDV 02 - <URL>
```

**Implementation**:

```python
python3 << 'EOF'
from slack_sdk import WebClient
import os
import sys

# Get token
token = os.environ.get('SLACK_BOT_TOKEN')
if not token:
    print("❌ Error: SLACK_BOT_TOKEN not found")
    sys.exit(1)

# Get thread_ts from Step 5
thread_ts = "1706024400.123456"  # Value saved from initial message

# Build message (same as JIRA comment)
deployment_url = "https://cdjenkins.sjc1.nskope.net/job/one_button_nsvppgregw/276/"
message = f"""Deployment - {deployment_url}
Post deploy script - Validated

ICN1
PDV 01 - http://your-jenkins-host:8080/job/STEERING_JENKINS/job/STEERING_MANAGEMENT/job/DPAS_PDV_Regression_Suites/job/GRE_Suites/job/VPP_GRE_PDV_ICN1/14/
PDV 02 - http://your-jenkins-host:8080/job/STEERING_JENKINS/job/STEERING_MANAGEMENT/job/DPAS_PDV_Regression_Suites/job/GRE_Suites/job/VPP_GRE_PDV_ICN1/13/

MNL1
PDV 01 - http://your-jenkins-host:8080/job/STEERING_JENKINS/job/STEERING_MANAGEMENT/job/DPAS_PDV_Regression_Suites/job/GRE_Suites/job/VPP_GRE_PDV_MNL1/22/
PDV 02 - http://your-jenkins-host:8080/job/STEERING_JENKINS/job/STEERING_MANAGEMENT/job/DPAS_PDV_Regression_Suites/job/GRE_Suites/job/VPP_GRE_PDV_MNL1/23/"""

# Send thread reply
client = WebClient(token=token)
try:
    response = client.chat_postMessage(
        channel="C09L9LR1B37",
        thread_ts=thread_ts,  # Reply to initial message
        text=message
    )

    print(f"✓ Slack thread reply sent")
    print(f"🔗 https://netskope.slack.com/archives/C09L9LR1B37/p{response['ts'].replace('.', '')}")

except Exception as e:
    print(f"❌ Failed to send Slack reply: {e}")
    sys.exit(1)
EOF
```

**Important Notes**:
- Reply to the **thread** created in Step 5 using `thread_ts`
- Use the EXACT same message format as JIRA comment
- Include deployment link, validation status, and ALL PDV links
- POP names in UPPERCASE
- NO /console suffix in URLs
- Only include SUCCESSFUL PDV build numbers
- If Slack send fails, log error but continue (don't block workflow)

**When to Send**:
- **Immediate Deployments**: After all POPs complete deployment + validation + PDV
- **Scheduled Deployments**: After EACH time slot completes deployment + validation + PDV

**Example Output**:
```
✓ Slack thread reply sent
🔗 https://netskope.slack.com/archives/C09L9LR1B37/p1706024500123456
```

---

### Step 10: Comprehensive Final Report (PDF Format)

**IMPORTANT: Generate AUTOMATICALLY after all deployments, post-deployment validations, and PDV testing complete**

After completing all deployment stages for all POPs, **AUTOMATICALLY** generate a comprehensive PDF report that consolidates:
1. Jenkins Deployment Status
2. Post-Deployment Validation Results
3. Production PDV Testing Results

**Automatic PDF Generation Triggers:**

1. **Immediate Deployments**: Generate PDF report automatically after completing all stages for all POPs
2. **Scheduled Deployments**: Generate PDF report automatically after the last scheduled deployment slot completes all stages
3. **Manual Report Requests**: When user explicitly asks "create a report" or "generate report"

**PDF Generation Method:**

Use Python `reportlab` library to generate PDF reports directly.

**Prerequisites for PDF Generation:**

Ensure `reportlab` is installed (check first, install only if needed):
```bash
# Check if already installed
python3 -c "import reportlab" 2>&1 && echo "already installed" || pip3 install --user reportlab
```

**⚠️ CRITICAL: Clean Up Old Files First**

Before generating reports, **ALWAYS delete old files** to prevent reusing stale data:

```bash
# MANDATORY: Clean up old report files before generating new ones
echo "🧹 Cleaning up old report files..."

# Get current date and ticket
CURRENT_DATE=$(date +%Y-%m-%d)  # e.g., 2026-02-24
TICKET="ENG-909296"  # From deployment parameters (format: ENG-XXXXXX)

# Remove old markdown files (all patterns)
rm -f /tmp/production_deployment_report.md 2>/dev/null
rm -f /tmp/production_deployment_report_*.md 2>/dev/null
rm -f /tmp/deployment_report_*.md 2>/dev/null
rm -f /tmp/GRE_Deployment_${TICKET}-*.md 2>/dev/null  # New naming format

# Remove old PDF files with same ticket number
rm -f ~/.claude/GRE_Deployment_${TICKET}-*.pdf 2>/dev/null

echo "✓ Old report files cleaned up"
echo ""
```

**Why This Is Critical:**
- **Issue**: Old markdown/PDF files from previous deployments can be reused
- **Example**: Feb 22 markdown (BOM1 deployment) was reused for Feb 24 (SIN3/MIL2/etc.), creating incorrect report
- **Impact**: PDF contains wrong POPs, dates, and results
- **Solution**: Always delete old files and generate FRESH markdown from current deployment data

**Report File Naming Convention:**
```bash
Format: GRE_Deployment_ENG-<ticket>-<date>
Example: GRE_Deployment_ENG-909296-2026-02-24

Markdown (temporary): /tmp/GRE_Deployment_ENG-${TICKET}-${CURRENT_DATE}.md
PDF (permanent): ~/.claude/GRE_Deployment_ENG-${TICKET}-${CURRENT_DATE}.pdf

# Example with actual values:
TICKET="ENG-909296"
CURRENT_DATE="2026-02-24"

Markdown: /tmp/GRE_Deployment_ENG-909296-2026-02-24.md
PDF: ~/.claude/GRE_Deployment_ENG-909296-2026-02-24.pdf
```

**Why Consistent Naming Is Important:**
- Easy to identify which deployment the files belong to (ticket + date)
- No confusion about which markdown goes with which PDF
- Easy to find and clean up old files
- Clear version control (one markdown/PDF pair per deployment)

**PDF Report Requirements:**

The PDF report MUST match the reference format with the following characteristics:

1. **Color Scheme:**
   - Header backgrounds: Softer blue (#4a90e2)
   - Row alternating: Very light gray (#f5f7fa)
   - Success metrics background: Very light green (#e8f5e9)
   - Borders: Light gray (#d0d0d0)
   - **SUCCESS/PASSED text: GREEN (#27ae60)** - This is CRITICAL

2. **Green Color Applied To:**
   - All "✅ SUCCESS" and "✅ PASSED" text in tables
   - Deployment Overview success rates (percentages in green)
   - Overall Success Metrics section (all percentages in green)
   - Deployment Status lines for each slot
   - All validation table status columns
   - All PDV testing status columns
   - Conclusion checklist items
   - Final assessment text

3. **Page Structure:**
   - Page 1: Title, Executive Summary, Deployment Overview, Schedule Table
   - Page 2+: Detailed Results for each slot (Jenkins, Validation, PDV with retry details)
   - Middle pages: Statistics, Success Metrics, Issues/Observations
   - Last page: Configuration Details, Conclusion, Footer

4. **Detailed Results - Retry Information:**
   - **CRITICAL**: For each slot, if any retries occurred (deployment, validation, or PDV), include retry details
   - **PDV Retries**: Show both initial attempt and retry with build numbers
   - **Format**:
     - "Build #X - FAILURE (first attempt)" → "Build #Y - SUCCESS (retry)"
     - Include reason for retry if available
   - **Example**:
     ```
     MEL3 PDV Job 2:
     • First attempt: Build #10 - FAILURE (test client issues)
     • Retry: Build #11 - SUCCESS
     ```

5. **Font Sizes:**
   - Title: 20pt bold
   - Headings: 14pt bold
   - Subheadings: 12pt bold
   - Normal text: 9pt
   - Small text: 8pt
   - Table text: 7-8pt

**Report Structure:**

The report MUST follow this structure (without separator lines ========):

```markdown
# PRODUCTION DEPLOYMENT COMPREHENSIVE REPORT

**Deployment Date:** 2026-02-18
**Service:** nsvppgregw (VPP GRE Gateway)
**Release Version:** 134.0.8.3068
**Ansible Config Tag:** 134.0.14
**Ticket:** ENG-909296
**Jenkins:** https://cdjenkins.sjc1.nskope.net/

## EXECUTIVE SUMMARY

**Total POPs:** 2 (jnb1, cpt1)
**Total Nodes Targeted:** 5
**Successfully Deployed:** 4 (80%)
**Failed/Not Deployed:** 1 (20%)

**Deployment Status:**        4/5 ✅ SUCCESS
**Post-Deployment Validation:** 4/4 ✅ PASSED (100%)
**Production PDV Testing:**     5/5 ✅ PASSED (100%)

**Overall Status:** ✅ SUCCESS WITH PARTIAL DEPLOYMENT

## SUMMARY OF REPORT

### POP: jnb1
**Deployment Status:** ⚠️ PARTIAL SUCCESS

| Node | Deployment | Post-Validation | PDV Testing | Overall |
|------|------------|----------------|-------------|---------|
| nsvppgregw01 | ✅ PASSED | ✅ PASSED (25/25) | ✅ PASSED (Job 2) | ✅ OPERATIONAL |
| nsvppgregw02 | ✅ PASSED | ✅ PASSED (25/25) | ✅ PASSED (Job 1) | ✅ OPERATIONAL |
| nsvppgregw03 | ❌ FAILED | ⏭️ SKIPPED | ⏭️ SKIPPED | ❌ NOT DEPLOYED |

**jnb1 Result:** 2/3 nodes operational (67%)

---

### POP: cpt1
**Deployment Status:** ✅ SUCCESS

| Node | Deployment | Post-Validation | PDV Testing | Overall |
|------|------------|----------------|-------------|---------|
| nsvppgregw01 | ✅ PASSED | ✅ PASSED (25/25) | ✅ PASSED (Job 2) | ✅ OPERATIONAL |
| nsvppgregw02 | ✅ PASSED | ✅ PASSED (25/25) | ✅ PASSED (Job 1) | ✅ OPERATIONAL |

**cpt1 Result:** 2/2 targeted nodes operational (100%)

## DEPLOYMENT DETAILS

**CRITICAL**: Document ALL deployment attempts including failures and retries across ALL POPs.

### Build #237 - Initial Deployment (jnb1, cpt1)
**Timestamp:** 2026-02-18 07:21:00 PST
**Duration:** 10m 9s
**POPs:** jnb1, cpt1
**Target:** All nodes (ANSIBLE_HOSTGROUPS=nsvppgregw)
**Result:** ❌ FAILURE (Partial Success)

#### Node-Level Results:

**POP: jnb1**
- ✅ nsvppgregw01.jnb1.nskope.net: PASSED
  - Ansible: ok=68, changed=20, failed=0
- ⏭️ nsvppgregw02.jnb1.nskope.net: SKIPPED
  - Reason: Not included in serial deployment execution
- ❌ nsvppgregw03.jnb1.nskope.net: FAILED
  - Error: AnsibleUndefinedVariable - Missing 'nsvppgregw03' variable definitions
  - Failed Task: nsvppgregw_install : Perform group var replacements

**POP: cpt1**
- ❌ nsvppgregw03.cpt1.nskope.net: FAILED
  - Error: AnsibleUndefinedVariable - Missing 'nsvppgregw03' variable definitions

**Summary:** 1/3 nodes passed (33%)
**Build URL:** https://cdjenkins.sjc1.nskope.net/job/one_button_nsvppgregw/237/

---

### Build #238 - cpt1 Retry (Nodes 01 & 02)
**Timestamp:** 2026-02-18 08:08:40 PST
**Duration:** 11m 8s
**POP:** cpt1
**Target:** nsvppgregw01.cpt1.nskope.net, nsvppgregw02.cpt1.nskope.net
**Result:** ✅ SUCCESS
**Strategy:** Explicit hostname targeting to bypass node03 configuration issue

#### Node-Level Results:

**POP: cpt1**
- ✅ nsvppgregw01.cpt1.nskope.net: PASSED
  - Ansible: ok=68, changed=19, failed=0
- ✅ nsvppgregw02.cpt1.nskope.net: PASSED
  - Ansible: ok=68, changed=19, failed=0

**Summary:** 2/2 nodes passed (100%)
**Build URL:** https://cdjenkins.sjc1.nskope.net/job/one_button_nsvppgregw/238/

---

### Build #239 - jnb1 Retry (Node 02)
**Timestamp:** 2026-02-18 08:35:27 PST
**Duration:** 16m 6s
**POP:** jnb1
**Target:** nsvppgregw02.jnb1.nskope.net
**Result:** ✅ SUCCESS

#### Node-Level Results:

**POP: jnb1**
- ✅ nsvppgregw02.jnb1.nskope.net: PASSED
  - Ansible: ok=68, changed=20, failed=0

**Summary:** 1/1 node passed (100%)
**Build URL:** https://cdjenkins.sjc1.nskope.net/job/one_button_nsvppgregw/239/

## ALL FAILURES AND RETRIES SUMMARY

**CRITICAL**: This section consolidates ALL deployment failures and retry attempts across ALL POPs.

### Deployment Attempts Overview

**Total Jenkins Builds:** 3
- Build #237: Initial deployment (jnb1, cpt1) - ❌ FAILURE (partial)
- Build #238: Retry for cpt1 (nodes 01, 02) - ✅ SUCCESS
- Build #239: Retry for jnb1 (node 02) - ✅ SUCCESS

**Total Build Time:** 37m 23s (across all 3 builds)

### Failed Nodes (Requiring Retries)

#### POP: jnb1

**Node: nsvppgregw02.jnb1.nskope.net**
- **Initial Attempt (Build #237):** ⏭️ SKIPPED
  - Reason: Not included in serial deployment execution
  - Root Cause: Serial deployment stopped after node03 failure
- **Retry (Build #239):** ✅ PASSED
  - Strategy: Explicit hostname targeting
  - Result: Successfully deployed

**Node: nsvppgregw03.jnb1.nskope.net**
- **Initial Attempt (Build #237):** ❌ FAILED
  - Error: AnsibleUndefinedVariable - Missing 'nsvppgregw03' variable definitions
  - Failed Task: nsvppgregw_install : Perform group var replacements
  - Failed Files: stsvc-cfwsvc, stsvc-nsproxy-dest, stsvc-dsr, ns-vpp-gre.conf
- **Retry:** NOT ATTEMPTED
  - Status: ❌ NOT DEPLOYED
  - Action Required: Fix Ansible configuration before retry

#### POP: cpt1

**Node: nsvppgregw01.cpt1.nskope.net**
- **Initial Attempt (Build #237):** ⏭️ NOT ATTEMPTED
  - Reason: Build stopped at node03 failure
- **Retry (Build #238):** ✅ PASSED
  - Strategy: Explicit hostname targeting
  - Result: Successfully deployed

**Node: nsvppgregw02.cpt1.nskope.net**
- **Initial Attempt (Build #237):** ⏭️ NOT ATTEMPTED
  - Reason: Build stopped at node03 failure
- **Retry (Build #238):** ✅ PASSED
  - Strategy: Explicit hostname targeting
  - Result: Successfully deployed

**Node: nsvppgregw03.cpt1.nskope.net**
- **Initial Attempt (Build #237):** ❌ FAILED
  - Error: AnsibleUndefinedVariable - Missing 'nsvppgregw03' variable definitions
  - Failed Task: nsvppgregw_install : Perform group var replacements
- **Retry:** NOT ATTEMPTED
  - Status: ❌ NOT DEPLOYED
  - Action Required: Fix Ansible configuration before retry

### Retry Strategies Used

1. **Explicit Hostname Targeting**
   - Problem: Node03 configuration issues causing serial deployment to fail
   - Solution: Target specific working nodes using explicit hostnames in ANSIBLE_HOSTGROUPS
   - Example: `ANSIBLE_HOSTGROUPS=nsvppgregw01.cpt1.nskope.net,nsvppgregw02.cpt1.nskope.net`
   - Success Rate: 100% (3/3 nodes successfully deployed using this strategy)

### Unresolved Failures

**Total Unresolved:** 2 nodes (both node03)

1. **nsvppgregw03.jnb1.nskope.net**
   - Error: Missing Ansible variable definitions
   - Impact: 1/3 nodes not deployed in jnb1 POP
   - Remediation: Add 'nsvppgregw03' variable definitions to Ansible inventory

2. **nsvppgregw03.cpt1.nskope.net**
   - Error: Missing Ansible variable definitions
   - Impact: Node intentionally skipped (not targeted in retry)
   - Remediation: Add 'nsvppgregw03' variable definitions to Ansible inventory

## POST-DEPLOYMENT VALIDATION RESULTS
[Validation results for each node that passed deployment]

## PRODUCTION PDV TESTING RESULTS
[PDV test results for each POP and job]

## ISSUES REQUIRING ATTENTION

### ❌ Critical Issue: nsvppgregw03 Configuration

**Affected Nodes:**
- nsvppgregw03.jnb1.nskope.net
- nsvppgregw03.cpt1.nskope.net

**Problem:** Ansible playbook missing variable definitions for 'nsvppgregw03' hostname

**Error Details:**
```
AnsibleUndefinedVariable: 'dict object' has no attribute 'nsvppgregw03'
Failed Task: nsvppgregw_install : Perform group var replacements
```

**Failed Configuration Files:**
- /opt/ns/common/remote/stsvc-cfwsvc
- /opt/ns/common/remote/stsvc-nsproxy-dest
- /opt/ns/common/remote/stsvc-dsr
- /opt/ns/gregw/ns-vpp-gre.conf

**Impact:**
- Node 03 cannot be deployed on either POP
- Service capacity reduced (2/3 nodes per POP vs 3/3)

**Workaround Used:**
Successfully deployed nodes 01 and 02 by explicitly targeting them in ANSIBLE_HOSTGROUPS parameter

**Remediation Required:**
1. Add Ansible variable definitions for 'nsvppgregw03' in inventory/group_vars
2. Verify variable mappings for all node 03 instances
3. Test deployment on non-production environment first
4. Re-deploy to node 03 on both POPs after fix

## DEPLOYMENT TIMELINE
[Chronological timeline with timestamps for ALL builds including retries]

## DEPLOYMENT STATISTICS

**Jenkins Builds:**
- Total Builds: 3
- Successful Builds: 2
- Failed Builds: 1 (partial failure)
- Total Build Time: 37m 23s

**Nodes:**
- Total Nodes Targeted: 5
- Successfully Deployed: 4 (80%)
- Failed Deployment: 1 (20%)
- Deployment Success Rate: 80%

**Retry Statistics:**
- Nodes Requiring Retry: 3
- Nodes Successfully Deployed on Retry: 3 (100%)
- Nodes Still Failing: 0
- Nodes Not Attempted: 2 (both node03 - configuration issue)

## NEXT STEPS

### ✅ COMPLETED
- 4 nodes successfully deployed (jnb1: nodes 01 & 02, cpt1: nodes 01 & 02)
- All deployed nodes passed post-deployment validation
- All deployed nodes passed PDV testing
- Services operational on deployed nodes

### ⚠️ ACTION REQUIRED
1. **Fix Ansible Configuration for Node 03**
   - Add missing variable definitions for 'nsvppgregw03'
   - Update inventory/group_vars files
   - Priority: HIGH
   - Owner: Platform/DevOps Team

2. **Deploy to Node 03 (Both POPs)**
   - Target: nsvppgregw03.jnb1.nskope.net
   - Target: nsvppgregw03.cpt1.nskope.net
   - Prerequisites: Ansible configuration fix
   - Priority: MEDIUM

## LESSONS LEARNED

1. **Explicit Hostname Targeting**
   - Using explicit hostnames in ANSIBLE_HOSTGROUPS successfully bypassed configuration issues
   - Strategy: Target specific nodes instead of service-level groups when configuration issues exist

2. **Serial Deployment Behavior**
   - Serial deployments may skip remaining nodes after failures
   - Important to verify which nodes were actually deployed, not just overall build status

3. **Node-Level Status Parsing**
   - Always parse Jenkins PLAY RECAP for accurate per-node status
   - Overall build status (SUCCESS/FAILURE) doesn't tell complete story
   - Some nodes can succeed even if build shows FAILURE

4. **Validation Strategy**
   - Post-deployment validation and PDV testing should always run on nodes that passed deployment
   - Don't abort validation workflow just because some nodes failed
   - Partial success is still valuable

## APPENDIX: BUILD URLS

**Deployment Builds:**
- Build #237: https://cdjenkins.sjc1.nskope.net/job/one_button_nsvppgregw/237/
- Build #238: https://cdjenkins.sjc1.nskope.net/job/one_button_nsvppgregw/238/
- Build #239: https://cdjenkins.sjc1.nskope.net/job/one_button_nsvppgregw/239/

**PDV Builds (jnb1):**
- Job 2 (Build #3): http://your-jenkins-host:8080/job/STEERING_JENKINS/job/STEERING_MANAGEMENT/job/DPAS_PDV_Regression_Suites/job/GRE_Suites/job/VPP_GRE_PDV_JNB1/3/
- Job 1 (Build #4): http://your-jenkins-host:8080/job/STEERING_JENKINS/job/STEERING_MANAGEMENT/job/DPAS_PDV_Regression_Suites/job/GRE_Suites/job/VPP_GRE_PDV_JNB1/4/

**PDV Builds (cpt1):**
- Job 1 (Build #16): http://your-jenkins-host:8080/job/STEERING_JENKINS/job/STEERING_MANAGEMENT/job/DPAS_PDV_Regression_Suites/job/GRE_Suites/job/VPP_GRE_PDV_CPT1/16/
- Job 2 (Build #17): http://your-jenkins-host:8080/job/STEERING_JENKINS/job/STEERING_MANAGEMENT/job/DPAS_PDV_Regression_Suites/job/GRE_Suites/job/VPP_GRE_PDV_CPT1/17/

## REPORT METADATA

**Report Generated:** 2026-02-18 08:57:00 PST
**Generated By:** Claude Code (Automated Deployment System)
**Report Version:** 1.0
**Format:** Markdown
```

**PDF Generation Workflow:**

**Step 1: Create Markdown Report**

After all deployment stages complete, create a comprehensive markdown report at `/tmp/production_deployment_report.md` with ALL sections:
- Header with deployment metadata
- Executive Summary with high-level statistics
- **Summary of Report (at the top)** - Detailed node-by-node status tables for each POP
- Deployment Details for each build
- Post-Deployment Validation Results for each node
- Production PDV Testing Results for each POP
- Issues Requiring Attention
- Deployment Timeline with timestamps
- Deployment Statistics
- Next Steps
- Lessons Learned
- Appendix with all build URLs
- Report Metadata

**CRITICAL**: The "SUMMARY OF REPORT" section MUST be placed right after "EXECUTIVE SUMMARY" at the top of the report, showing detailed tables for each POP.

**Step 2: Convert Markdown to PDF**

Immediately after creating the markdown report, automatically convert it to PDF:

```bash
# Convert markdown to PDF using md-to-pdf
md-to-pdf /tmp/production_deployment_report.md --pdf-options '{"format": "A4", "margin": {"top": "20mm", "right": "20mm", "bottom": "20mm", "left": "20mm"}}' 2>&1
```

This will create `/tmp/production_deployment_report.pdf`

**Step 3: Verify PDF Generation**

Check that PDF was created successfully:

```bash
ls -lh /tmp/production_deployment_report.pdf && file /tmp/production_deployment_report.pdf
```

Expected output:
```
-rw-r--r--  1 user  wheel   375K Feb 18 14:59 /tmp/production_deployment_report.pdf
/tmp/production_deployment_report.pdf: PDF document, version 1.4, 5 pages
```

**Step 4: Notify User**

After PDF generation completes, inform the user:

```
✅ Comprehensive Deployment Report Generated

Both report formats are available:
- **Markdown:** /tmp/production_deployment_report.md
- **PDF:** /tmp/production_deployment_report.pdf (375KB, 5 pages)

The PDF report includes:
✓ Executive Summary with deployment statistics
✓ Summary of Report (node-by-node status tables at the top)
✓ Detailed results for all deployment stages across all POPs
✓ Timeline with timestamps
✓ Issues requiring attention
✓ Jenkins build links
✓ Next steps and action items
```

**Automatic Report Generation Rules:**

1. **Trigger Timing**:
   - **Immediate Deployments**: Generate report AUTOMATICALLY after all POPs complete all stages (deployment → post-validation → PDV)
   - **Scheduled Deployments**: Generate report AUTOMATICALLY after the last scheduled time slot completes all stages
   - **Manual Request**: Generate report when user explicitly asks "create a report" or "generate report"

2. **Report Includes All Three Stages** for each POP:
   - Jenkins Deployment Status (node-level details from PLAY RECAP)
   - Post-Deployment Validation Results (per node)
   - Production PDV Testing Results (per job)

3. **CRITICAL - Track ALL Deployment Attempts**:
   - **Record EVERY Jenkins build** including initial attempts, failures, and retries
   - **Document failures with root cause** from Jenkins logs
   - **Track retry strategies** used to fix issues
   - **Consolidate all failures and retries** in dedicated "ALL FAILURES AND RETRIES SUMMARY" section
   - **Include retry statistics**: How many nodes required retry, success rate of retries
   - **Document unresolved failures** that still need attention

4. **Overall Status Logic**:
   - ✅ **FULLY OPERATIONAL**: All stages passed for all POPs
   - ⚠️ **SUCCESS WITH PARTIAL DEPLOYMENT**: Some nodes failed deployment but others operational
   - ⚠️ **ATTENTION REQUIRED**: Deployments successful but some PDV tests failed
   - ❌ **DEPLOYMENT FAILED**: One or more deployments completely failed

5. **Per-POP Status** (shown in "Summary of Report" section at top):
   - ✅ **OPERATIONAL**: Deployment passed, validation passed, PDV passed
   - ⚠️ **PARTIAL SUCCESS**: Some nodes operational, some failed
   - ❌ **NOT DEPLOYED**: Deployment failed

6. **Timeline**: Include timestamps for each major stage to show progression (including all retry attempts)

7. **Action Items**: Clearly list what requires attention and next steps

8. **Format Requirements**:
   - NO separator lines (========) in the markdown
   - Use markdown headers (# and ##) for sections
   - "Summary of Report" section MUST be at the top (after Executive Summary)
   - Include detailed node-by-node status tables
   - "ALL FAILURES AND RETRIES SUMMARY" section after "DEPLOYMENT DETAILS"

**Example of Automatic Execution:**

After completing all deployment stages:

```
[All deployment work completes]
→ Step 10 triggers automatically
→ Clean up old report files (MANDATORY)
→ Create FRESH markdown with current deployment data
→ Verify markdown contents (correct POPs, date, results)
→ Convert to PDF using reportlab or md-to-pdf
→ Verify PDF created with correct filename and date
→ Proceed to Step 8 (Slack notification)
```

**Report Generation Checklist:**
```bash
# Get ticket and date
TICKET="ENG-909296"  # From deployment parameters
CURRENT_DATE=$(date +%Y-%m-%d)  # e.g., 2026-02-24

# Define filenames
MARKDOWN_FILE="/tmp/GRE_Deployment_${TICKET}-${CURRENT_DATE}.md"
PDF_FILE="~/.claude/GRE_Deployment_${TICKET}-${CURRENT_DATE}.pdf"

# 1. Clean up old files
rm -f /tmp/production_deployment_report*.md
rm -f /tmp/GRE_Deployment_${TICKET}-*.md
rm -f ~/.claude/GRE_Deployment_${TICKET}-*.pdf

# 2. Generate FRESH markdown from current data
# (Use deployment results collected during execution)
# Create: /tmp/GRE_Deployment_ENG-909296-2026-02-24.md

# 3. VERIFY markdown contents before converting
echo "📋 Verifying report contents..."
echo "File: ${MARKDOWN_FILE}"
echo "Date: $(grep -m1 'Date:' ${MARKDOWN_FILE})"
echo "POPs: $(grep -m1 'Total POPs:' ${MARKDOWN_FILE})"
echo "Slots: $(grep -m1 'Total Slots:' ${MARKDOWN_FILE})"

# 4. Convert to PDF
# (Using reportlab or md-to-pdf)
# Create: ~/.claude/GRE_Deployment_ENG-909296-2026-02-24.pdf

# 5. VERIFY PDF created with correct date
ls -lh ${PDF_FILE}
echo "✓ Report files created:"
echo "  Markdown: ${MARKDOWN_FILE}"
echo "  PDF: ${PDF_FILE}"
```

**Important Notes:**
- Report generation is AUTOMATIC after all work completes
- Do NOT ask user if they want a report - generate it automatically
- **ALWAYS clean up old files first** to prevent stale data issues
- **ALWAYS verify report contents** match current deployment (POPs, date, results)
- PDF is generated using Python `reportlab` library
- File saved to `~/.claude/` for permanent storage
- Collect timestamps during execution for accurate timeline
- Include all Jenkins build URLs for traceability

## Step 8: Automatic Slack Notification (After Report Generation)

**CRITICAL**: After generating the PDF report, AUTOMATICALLY send a deployment summary message to Slack channel C08STTVMWFJ.

**When to Send:**
- **Immediate Deployments**: After PDF report is generated
- **Scheduled Deployments**: After PDF report is generated for the last scheduled slot (see Step 10 in Scheduled Deployment section)
- **Manual Report Requests**: NOT sent (only for production deployments)

**Slack Notification Details:**

**Target Channel:** `C08STTVMWFJ`

**CRITICAL - Proper Mention Format:**

1. **@channel**: Use `<!channel>` format (NOT `@channel`)
   - ✅ Correct: `<!channel>`
   - ❌ Wrong: `@channel`

2. **User Mentions**: Use traditional @username format
   - ✅ Correct: `@Ashwin` (displays name properly)
   - ❌ Wrong: User ID format `<@U06SV5HCF1F>` (doesn't display names in this workspace)

**Message Format:**

```
<!channel> Summary of updates for R<release> VPPGRE Day <day_number> Production Deployments/Rollout:

1. Deployment on existing POPs.
   Already rolled out live POPs of VPPGRE upgraded to <version> - <POP1>, <POP2>, <POP3>, ...

2. No new rollout

Issues Observed:
<list of issues or "No issues observed during the deployment window">

cc: @Ashwin @Prashant @Ananda @Parth @Abdul Hameed @your-username
```

**How to Determine Day Number:**

**CRITICAL**: The day number MUST be obtained from the user when they schedule the deployment.

The day number represents which day of the overall rollout schedule this deployment is:
- **Day 1**: First day of rollout (e.g., Feb 20)
- **Day 2**: Second day of rollout (e.g., Feb 21)
- **Day 3**: Third day of rollout (e.g., Feb 22)
- **Day 4**: Fourth day of rollout (e.g., Feb 24)
- etc.

**How to Get Day Number:**
1. **Ask the user explicitly** when they provide the schedule: "Is this Day 1, Day 2, Day 3, etc. of the rollout?"
2. **Check the user's request** - they may specify it (e.g., "Day 4 deployment schedule")
3. **If not provided**: Ask before proceeding with the schedule

**NEVER default to Day 1** without confirmation - the user may be scheduling a later day of a multi-day rollout.

**Example:**
- User: "Schedule deployment for Feb 24" → Ask: "Is this Day 1, Day 2, or another day of your rollout schedule?"
- User: "Day 4 deployment schedule for Feb 24" → Use Day 4
- User: "This is the 4th day of rollout" → Use Day 4

**Python Code to Send Slack Message with PDF:**

```python
python3 << 'EOF'
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json

# Load Slack config
with open('~/.claude/slack_config.json', 'r') as f:
    config = json.load(f)
    token = config['slack_bot_token']

channel = "C08STTVMWFJ"

# Determine release version (extract from RELEASE parameter, e.g., "134.0.8.3068" → "R134.1")
release = "134.0.8.3068"  # From RELEASE parameter
major = release.split('.')[0]
minor = int(release.split('.')[1])
release_label = f"R{major}.{minor + 1}"  # "R134.1"

# Build message dynamically with PROPER mention format
message = f"""<!channel> Summary of updates for {release_label} VPPGRE Day 1 Production Deployments/Rollout:

1. Deployment on existing POPs.
   Already rolled out live POPs of VPPGRE upgraded to {release} - ICN1, MNL1, MEL3, WAW1, ATL2, BOS1, NYC3, NYC4, SCL1, STL1, YMQ1

2. No new rollout

Issues Observed:
• Minor: Kernel version mismatch on STL1 Node 01 (non-critical, all services operational)
• PDV retries on MEL3 and STL1 (expected behavior, both succeeded on retry)
• Overall: 100% deployment success, 99.8% validation success, 100% PDV success

cc: @Ashwin @Prashant @Ananda @Parth @Abdul Hameed @your-username"""

client = WebClient(token=token)

# PDF file path
pdf_path = "~/.claude/GRE_Deployment_ENG-909296-2026-02-24.pdf"
pdf_title = f"VPP GRE {release_label} Day 1 Deployment Report - ENG-909296"

# Try files_upload_v2 (newer API with better file handling)
try:
    print("📤 Uploading PDF to Slack...")
    upload_response = client.files_upload_v2(
        channel=channel,
        file=pdf_path,
        title=pdf_title,
        initial_comment=message
    )
    print(f"✅ Message sent with PDF attachment to channel C08STTVMWFJ")
    print(f"📄 PDF uploaded: {pdf_title}")
    print(f"🔗 File URL: {upload_response['file']['permalink']}")

except SlackApiError as e:
    if e.response['error'] == 'missing_scope':
        # Fallback: Try legacy files_upload
        print("⚠️  files_upload_v2 not available, trying legacy files_upload...")
        try:
            upload_response = client.files_upload(
                channels=channel,
                file=pdf_path,
                title=pdf_title,
                initial_comment=message
            )
            print(f"✅ Message sent with PDF attachment to channel C08STTVMWFJ (legacy API)")
            print(f"📄 PDF uploaded: {pdf_title}")
        except Exception as upload_error:
            # Last resort: Send message without attachment
            print(f"❌ PDF upload failed: {upload_error}")
            response = client.chat_postMessage(channel=channel, text=message)
            print(f"✅ Message sent to channel C08STTVMWFJ (without PDF)")
            print(f"⚠️  PDF not attached due to permissions")
            print(f"📄 Report available at: {pdf_path}")
    else:
        print(f"❌ Slack API error: {e.response['error']}")
        raise

except FileNotFoundError:
    print(f"❌ PDF file not found: {pdf_path}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    raise
EOF
```

**Message Components:**

1. **Release Version**: Extract from RELEASE parameter
   - `134.0.8.3068` → `R134.1`
   - `135.0.0.3500` → `R135.0`

2. **Day Number**: Determine from schedule
   - Single-day deployment → Day 1
   - Multi-day deployment → Day 1, Day 2, etc.

3. **POPs List**: Comma-separated uppercase POP names from deployment
   - Example: `ICN1, MNL1, MEL3, WAW1, ATL2, BOS1, NYC3, NYC4, SCL1, STL1, YMQ1`

4. **Issues Section**: Summarize from report
   - If no issues: "No issues observed during the deployment window"
   - If issues: List each issue with impact assessment
   - Always include overall success metrics

**Important Notes:**

- The Slack message is sent AUTOMATICALLY after PDF generation
- Do NOT ask user if they want to send the message - send it automatically
- The PDF attachment may fail if Slack bot lacks `files:write` permission
- In that case, send message without attachment and inform user of report location
- The message format must match the example exactly (including @channel, cc: mentions)
- POPs must be UPPERCASE (ICN1, not icn1)
- Day number should be accurate based on deployment schedule

## Example Production Deployment

**User Request:**
- POP: `los1`
- Service: `nsvppgregw`
- RELEASE: `134.0.2.3026`
- ANSIBLE_CONFIG_IMAGE_TAG: `134.0.9`
- TICKET: `ENG-864088`

**After user confirms, run:**
```bash
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
java -jar ~/.claude/jenkins-cli.jar \
  -s https://cdjenkins.sjc1.nskope.net/ \
  -auth your-username@your-company.com:your-api-token \
  build one_button_nsvppgregw -s \
  -p POPS=los1 \
  -p RELEASE=134.0.2.3026 \
  -p ANSIBLE_CONFIG_IMAGE_TAG=134.0.9 \
  -p ANSIBLE_HOSTGROUPS=nsvppgregw \
  -p ANSIBLE_ARTIFACTORY_CHANNEL=ipsec-gre-production-docker \
  -p TICKET=ENG-864088 \
  -p SELECT_ALL_POPS="" \
  -p REGIONS="America,APAC,Europe" \
  -p POP_TYPES="MP,DP,GCP,EKS" \
  -p SELECT_ALL_COMPONENTS="" \
  -p ANSIBLE_COMPONENT_NAME=nsvppgregw \
  -p ANSIBLE_CONFIG_IMAGE_NAME=nsvppgregw-ansible-config \
  -p ANSIBLE_VERBOSITY=2 \
  -p ANSIBLE_CORE_VERSION=2.15 \
  -p SLACK_CHANNEL="#vpp-ipsec-gre-self-service-deployment" \
  -p BYPASS_MONITORING_RESULT=YES \
  -p BYPASS_JIRA=YES \
  -p RUN_QE_PDV=DEPLOY_ONLY \
  -p DEPLOY_TYPE=DEPLOY
```

**Expected Output:**
```
Started one_button_nsvppgregw #218
```

## Scheduled Deployment Workflow

**IMPORTANT**: Scheduled deployments are for coordinating releases across multiple POPs at specific times.

### Step 1: Parse Schedule

When user provides a schedule, parse the following:
1. **Date**: Extract deployment date (e.g., `05-Feb, Thu`)
2. **Common Parameters**: Extract RELEASE, ANSIBLE_CONFIG_IMAGE_TAG, TICKET
3. **Service**: Ask if not specified (nsvppgregw, nsvppipsecgw, ecgw, steeringlb)
4. **Time Slots**: Parse each time slot with associated POPs
5. **⚠️ CRITICAL - Day Number**: Determine which day of the rollout this is
   - Check user's request for "Day X" mention (e.g., "Day 4 schedule")
   - If not mentioned: **ASK EXPLICITLY** - "Is this Day 1, Day 2, Day 3, etc. of your rollout schedule?"
   - **NEVER default to Day 1** without confirmation
   - This number goes in the Slack summary message and report title

**Example Schedule:**
```
Schedule [05-Feb, Thu]
Common Parameters for all POPS:
RELEASE: 133.0.1.3316
ANSIBLE_CONFIG_IMAGE_TAG: 134.0.12
TICKET: ENG-864088
Service: nsvppgregw

9:30AM-12:00PM
ICN1,MNL1

11:00AM-12:30PM
MEL3

1:00PM-4:00PM
WAW1

5:00PM-7:00PM
ATL2,BOS1,NYC3

7:00PM-9:00PM
MUC1,NYC4,SCL1,STL1
```

**Parsed Result:**
```
Schedule Date: 2026-02-05
Common Parameters:
  - RELEASE: 133.0.1.3316
  - ANSIBLE_CONFIG_IMAGE_TAG: 134.0.12
  - TICKET: ENG-864088
  - Service: nsvppgregw

Deployment Slots:
1. 09:30 PST → ICN1, MNL1
2. 11:00 PST → MEL3
3. 13:00 PST → WAW1
4. 17:00 PST → ATL2, BOS1, NYC3
5. 19:00 PST → MUC1, NYC4, SCL1, STL1
```

### Step 2: Display Schedule Summary

**CRITICAL**: If day number not yet confirmed, **ASK NOW** before showing summary.

Show user the complete schedule for confirmation:

```
========================================
SCHEDULED PRODUCTION DEPLOYMENTS
========================================

Date: Thursday, February 5, 2026 (Day 4 of Rollout)
Service: nsvppgregw

Common Parameters:
  RELEASE: 133.0.1.3316
  ANSIBLE_CONFIG_IMAGE_TAG: 134.0.12
  TICKET: ENG-864088

Deployment Schedule (All times PST):

09:30 AM → ICN1, MNL1 (2 POPs)
11:00 AM → MEL3 (1 POP)
01:00 PM → WAW1 (1 POP)
05:00 PM → ATL2, BOS1, NYC3 (3 POPs)
07:00 PM → MUC1, NYC4, SCL1, STL1 (4 POPs)

Total: 11 POPs across 5 time slots

⚠️  This will schedule 11 production deployments.
⚠️  When each scheduled time arrives, the deployment will start automatically.
⚠️  By confirming this schedule, you approve ALL deployments to run at their scheduled times.

Do you want to create this schedule? (yes/no)
========================================
```

**If day number not provided**, ask explicitly:
```
❓ Which day of your rollout schedule is this? (Day 1, Day 2, Day 3, Day 4, etc.)
```

### Step 3: Verify System Time Accuracy (MANDATORY for Scheduled Deployments)

**CRITICAL**: Before scheduling any deployments, verify system time accuracy by comparing with authoritative time source.

**Time Verification Workflow:**

```bash
echo "========================================="
echo "SYSTEM TIME VERIFICATION"
echo "========================================="
echo ""

# Step 3a: Get system time
SYSTEM_TIME=$(date -u "+%Y-%m-%d %H:%M:%S UTC")
SYSTEM_EPOCH=$(date -u +%s)
echo "System Time:     $SYSTEM_TIME"
echo "System Epoch:    $SYSTEM_EPOCH"
echo ""

# Step 3b: Get time from remote time server (authoritative source)
echo "Querying time servers..."

# Try Google first (fast and reliable)
GOOGLE_DATE=$(curl -sI --max-time 3 https://www.google.com 2>/dev/null | grep -i "^date:" | cut -d' ' -f2-)

if [ -n "$GOOGLE_DATE" ]; then
  echo "✅ Using Google time server"
  REMOTE_DATE="$GOOGLE_DATE"
  SOURCE="Google"
else
  # Fallback to Cloudflare
  echo "⚠️  Google unreachable, trying Cloudflare..."
  CF_DATE=$(curl -sI --max-time 3 https://cloudflare.com 2>/dev/null | grep -i "^date:" | cut -d' ' -f2-)

  if [ -n "$CF_DATE" ]; then
    echo "✅ Using Cloudflare time server"
    REMOTE_DATE="$CF_DATE"
    SOURCE="Cloudflare"
  else
    echo "❌ ERROR: Could not reach any time server (Google, Cloudflare)"
    echo "⚠️  Cannot verify system time accuracy"
    echo "⚠️  Please check network connectivity"
    exit 1
  fi
fi

# Convert remote time to epoch
# Format: "Thu, 20 Feb 2026 18:45:30 GMT"
REMOTE_EPOCH=$(date -j -f "%a, %d %b %Y %H:%M:%S %Z" "$REMOTE_DATE" +%s 2>/dev/null)

if [ -z "$REMOTE_EPOCH" ]; then
  echo "❌ ERROR: Could not parse remote time response"
  echo "Response: $REMOTE_DATE"
  exit 1
fi

REMOTE_TIME=$(date -u -r $REMOTE_EPOCH "+%Y-%m-%d %H:%M:%S UTC")
echo "Remote Time ($SOURCE): $REMOTE_TIME"
echo "Remote Epoch:    $REMOTE_EPOCH"
echo ""

# Step 3c: Calculate time difference
TIME_DIFF=$((SYSTEM_EPOCH - REMOTE_EPOCH))
TIME_DIFF_ABS=${TIME_DIFF#-}  # Absolute value

echo "Time Difference: ${TIME_DIFF} seconds"
echo ""

# Step 3d: Verify times match (within 5 second tolerance)
TOLERANCE=5

if [ $TIME_DIFF_ABS -le $TOLERANCE ]; then
  echo "✅ Time Verification: PASSED"
  echo "   System time and $SOURCE time match (within ${TOLERANCE}s tolerance)"
  echo ""
else
  echo "❌ Time Verification: FAILED"
  echo "   System time differs from $SOURCE by ${TIME_DIFF_ABS} seconds"
  echo ""
  echo "⚠️  CRITICAL: System clock may be inaccurate!"
  echo "⚠️  Scheduled deployments may run at wrong times"
  echo ""
  echo "Recommended Actions:"
  echo "1. Sync system time: sudo sntp -sS time.apple.com"
  echo "2. Check NTP service: sudo systemctl status systemd-timesyncd"
  echo "3. Re-run time verification after sync"
  echo ""
  exit 1
fi

echo "========================================="
echo ""
```

**Example Output (Success):**
```
=========================================
SYSTEM TIME VERIFICATION
=========================================

System Time:     2026-02-20 13:09:33 UTC
System Epoch:    1771592973

Querying time servers...
✅ Using Google time server
Remote Time (Google): 2026-02-20 13:09:33 UTC
Remote Epoch:    1771592973

Time Difference: 0 seconds

✅ Time Verification: PASSED
   System time and Google time match (within 5s tolerance)

=========================================
```

**Example Output (Failure):**
```
=========================================
SYSTEM TIME VERIFICATION
=========================================

System Time:     2026-02-20 18:50:00 UTC
System Epoch:    1766962200

Querying time servers...
✅ Using Google time server
Remote Time (Google): 2026-02-20 18:45:30 UTC
Remote Epoch:    1766961930

Time Difference: 270 seconds

❌ Time Verification: FAILED
   System time differs from Google by 270 seconds

⚠️  CRITICAL: System clock may be inaccurate!
⚠️  Scheduled deployments may run at wrong times

Recommended Actions:
1. Sync system time: sudo sntp -sS time.apple.com
2. Check NTP service: sudo systemctl status systemd-timesyncd
3. Re-run time verification after sync

=========================================
```

**Important Notes:**
- Time verification is MANDATORY before scheduling any deployments
- Tolerance: 5 seconds (configurable)
- Uses Google as primary time source (fast and reliable, 3-second timeout)
- Falls back to Cloudflare if Google is unreachable
- Uses HTTP Date headers (no NTP protocol required)
- If verification fails, STOP and ask user to sync system time
- Do NOT proceed with scheduling if times don't match
- Verification must pass before calculating wait times

### Step 3.5: Send Schedule to Slack (MANDATORY - After User Confirmation)

**CRITICAL**: After user confirms the schedule and time verification passes, AUTOMATICALLY send the deployment schedule to Slack channel C08STTVMWFJ.

**When to Send:**
- After Step 2 (user confirms schedule)
- After Step 3 (time verification passes)
- Before Step 4 (creating background tasks)

**Message Format:**

```
@channel R<major>.<minor> Production Upgrade - POP(VPP GRE) schedule details:
Day <day_number>: [<DD-MMM>, <DDD>] - <total_pops> POPs

<time_slot1>
<POPs1>
<time_slot2>
<POPs2>
...
```

**How to Determine Values:**

1. **Release Version (R<major>.<minor>)**:
   - Extract from RELEASE parameter (e.g., "134.0.8.3068")
   - Format: Take first two parts → "R134.1"
   - Logic: `134.0.x.xxxx` → `R134.1`, `135.0.x.xxxx` → `R135.0`

2. **Day Number**:
   - Track deployment days across the schedule
   - Single calendar day → Day 1
   - Multiple calendar days → Day 1, Day 2, Day 3...
   - For multi-day schedules: Count which day this is

3. **Date Format**:
   - Format: `[DD-MMM, DDD]`
   - Example: `[23-Feb, Mon]` for February 23, Monday

4. **Total POPs**:
   - Count all unique POPs across all time slots
   - Example: 11 POPs total

**Python Code to Send Schedule:**

```python
python3 << 'EOF'
from slack_sdk import WebClient
import json
from datetime import datetime

# Load Slack config
with open('~/.claude/slack_config.json', 'r') as f:
    config = json.load(f)
    token = config['slack_bot_token']

channel = "C08STTVMWFJ"

# Extract release version (e.g., "134.0.8.3068" → "R134.1")
release = "134.0.8.3068"  # From RELEASE parameter
major = release.split('.')[0]  # "134"
minor = int(release.split('.')[1])  # 0
release_label = f"R{major}.{minor + 1}"  # "R134.1" (increment minor by 1)

# Determine day number - MUST GET FROM USER
# NEVER default to 1 - always ask or extract from user's request
day_number = 4  # Example: User specified "Day 4" when providing schedule

# Format schedule date
schedule_date = datetime(2026, 2, 23)  # Parse from schedule
date_str = schedule_date.strftime("%d-%b, %a")  # "23-Feb, Mon"

# Count total POPs
all_pops = ["ICN1", "MNL1", "MEL3", "WAW1", "ATL2", "BOS1", "NYC3", "NYC4", "SCL1", "STL1", "YMQ1"]
total_pops = len(all_pops)

# Build schedule message
schedule_lines = """9:30AM-12:00PM
ICN1,MNL1
11:00AM-12:30PM
MEL3
1:00PM-4:00PM
WAW1
5:00PM-7:00PM
ATL2,BOS1,NYC3
7:00PM-9:00PM
NYC4,SCL1,STL1,YMQ1"""

message = f"""@channel {release_label} Production Upgrade - POP(VPP GRE) schedule details:
Day {day_number}: [{date_str}] - {total_pops} POPs

{schedule_lines}"""

client = WebClient(token=token)

try:
    response = client.chat_postMessage(
        channel=channel,
        text=message
    )
    print(f"✅ Schedule sent to Slack channel C08STTVMWFJ")
    print(f"Message timestamp: {response['ts']}")

    # Save thread_ts for later updates if needed
    with open('/tmp/schedule_slack_thread_ts.txt', 'w') as f:
        f.write(response['ts'])

except Exception as e:
    print(f"⚠️  Failed to send schedule to Slack: {e}")
    print(f"Continuing with deployment scheduling...")
EOF
```

**Example Message:**

```
@channel R134.1 Production Upgrade - POP(VPP GRE) schedule details:
Day 3: [23-Feb, Mon] - 11 POPs

9:30AM-12:00PM
ICN1,MNL1
11:00AM-12:30PM
MEL3
1:00PM-4:00PM
WAW1
5:00PM-7:00PM
ATL2,BOS1,NYC3
7:00PM-9:00PM
NYC4,SCL1,STL1,YMQ1
```

**Important Notes:**

- This notification is AUTOMATIC - do not ask user if they want to send it
- Send AFTER user confirms schedule
- Send BEFORE creating background tasks
- Use the same format as shown in example
- POPs must be uppercase (ICN1, not icn1)
- All times in PST (as shown in user's schedule)
- If Slack send fails, continue with deployment (don't abort)
- Save the message timestamp for potential future updates

**Day Number Logic:**

```python
# CRITICAL: Day number MUST come from user input
# NEVER default to Day 1 without confirmation

# How to get day number:
# 1. Check user's original request for "Day X" mention
# 2. Ask explicitly: "Is this Day 1, 2, 3, etc. of your rollout schedule?"
# 3. If user says "this is part of week 2" or similar, calculate accordingly

# Examples:
# - User: "Day 4 schedule for Feb 24" → day_number = 4
# - User: "4th day of rollout" → day_number = 4
# - User: "Week 1 Day 3" → day_number = 3
# - User: "Week 2 Day 2" → day_number = 7 (5 days week 1 + 2 days week 2)

# WRONG: day_number = 1  # Never default without asking
# RIGHT: day_number = <value from user's request or explicit confirmation>
```

### Step 4: Calculate Wait Times and Schedule with Bash Background Tasks

**CRITICAL**: Use Bash tool with `run_in_background: true` to sleep until scheduled time. This allows you to monitor the task and prompt user in the conversation.

**Prerequisites:**
- Step 3 (Time Verification) must have passed
- System time confirmed accurate within 5 seconds of Cloudflare time

**For each time slot:**

1. Calculate wait time in seconds
2. Launch ONE Bash background task per time slot with `run_in_background: true`
3. After task completes, read the output and prompt user for permission
4. Trigger deployment only if user approves

**Example Implementation:**

```bash
# Calculate wait time for a specific time slot
CURRENT_EPOCH=$(date -u +%s)
TARGET_DATE="2026-02-05"
TARGET_TIME="09:30:00"  # Note: include seconds
TARGET_EPOCH=$(date -u -j -f "%Y-%m-%d %H:%M:%S" "${TARGET_DATE} ${TARGET_TIME}" +%s)
WAIT_SECONDS=$((TARGET_EPOCH - CURRENT_EPOCH))

if [ $WAIT_SECONDS -lt 0 ]; then
  echo "⚠️  Scheduled time has passed!"
  WAIT_SECONDS=0
fi

WAIT_HOURS=$(awk "BEGIN {printf \"%.1f\", $WAIT_SECONDS/3600}")

cat << EOF
🕐 Scheduling Production Deployment
Target Time: ${TARGET_TIME} PST
POPs: ICN1, MNL1
Wait Time: ${WAIT_SECONDS} seconds (${WAIT_HOURS} hours)

I will:
1. Sleep until the scheduled time
2. Notify you when time arrives
3. Automatically trigger deployment (permission already granted)
4. Use Jenkins CLI sync mode (blocks until complete)
5. Proceed to validation and PDV after deployment completes

Starting wait now...
EOF

# Sleep until scheduled time
sleep $WAIT_SECONDS

echo ""
echo "⏰ Scheduled time reached: $(TZ='America/Los_Angeles' date '+%H:%M:%S PST')"
```

**Launch this with Bash tool using:**
- `run_in_background: true`
- `timeout: 600000` (10 minutes max wait time)

### Step 5: Wait for Scheduled Time and Auto-Execute

**After launching the background Bash task (sleep command):**

1. Save the task ID returned by the Bash tool
2. Display status to user showing the task is waiting
3. When the scheduled time arrives, you'll receive a system notification about task completion
4. Read the task output file
5. **Automatically proceed with deployment** (permission already granted at scheduling phase)
6. Notify user that deployment is starting
7. **Trigger Jenkins in SYNC MODE** (NOT API monitoring)
   - Use `java -jar jenkins-cli.jar ... -s` command
   - Jenkins CLI will block and wait for deployment to complete
   - No separate monitoring tasks needed
   - After sync mode completes, proceed to validation and PDV

**Example Start Notification:**
```
========================================
🔔 SCHEDULED PRODUCTION DEPLOYMENT STARTING
========================================

Current Time: 09:30 PST
POPs: ICN1, MNL1
Service: nsvppgregw
RELEASE: 133.0.1.3316
ANSIBLE_CONFIG_IMAGE_TAG: 134.0.12
TICKET: ENG-864088

⚠️  Starting PRODUCTION deployment now...
========================================
```

### Step 6: Execute Deployment Automatically (Scheduled Deployments)

**🚨 CRITICAL - NO PERMISSION NEEDED 🚨**

**For scheduled deployments, user approval was already given during schedule creation. DO NOT ask for permission again.**

**When scheduled time arrives, the background task will notify you. You MUST then:**
1. **Inform** the user that scheduled time has been reached and deployment is starting automatically
2. Verify all safety checks pass
3. **Automatically proceed** with deployment (DO NOT wait for user approval)

**WRONG - DO NOT DO THIS:**
```
❌ "Slot 2 time reached. May I proceed with deployment?"
❌ "Ready to deploy. Should I start?"
❌ Asking for any form of permission or approval
```

**CORRECT - DO THIS:**
```
✅ "Slot 2 time reached. Starting deployment now..."
✅ "Scheduled time arrived. Executing deployment automatically..."
✅ Inform user and proceed immediately
```

**🚨 MANDATORY SAFETY VERIFICATION BEFORE DEPLOYMENT 🚨**

**STEP 6.0: VERIFY POPs ARE IN SCHEDULE (CRITICAL - DO NOT SKIP)**

Before ANY deployment, you MUST verify that the POPs being deployed to are in the original schedule:

```python
# Extract all POPs from the original schedule
scheduled_pops = []  # e.g., ['ICN1', 'MNL1', 'MEL3', 'WAW1', 'ATL2', 'BOS1', 'NYC3', 'NYC4', 'SCL1', 'STL1', 'YMQ1']

# Get POPs for this time slot
current_slot_pops = []  # e.g., ['ICN1', 'MNL1'] for Slot 1

# Case-insensitive verification
scheduled_pops_lower = [p.lower() for p in scheduled_pops]
current_slot_pops_lower = [p.lower() for p in current_slot_pops]

# Verify EVERY POP in current slot is in schedule
for pop in current_slot_pops_lower:
    if pop not in scheduled_pops_lower:
        print(f"❌ CRITICAL ERROR: POP '{pop.upper()}' is NOT in the schedule!")
        print(f"Scheduled POPs: {', '.join(scheduled_pops)}")
        print(f"Attempting to deploy to: {', '.join(current_slot_pops)}")
        print("🚨 DEPLOYMENT ABORTED - Cannot deploy to unscheduled POP")
        STOP IMMEDIATELY - DO NOT PROCEED
        return

print(f"✅ POP Verification Passed: All POPs in this slot are scheduled")
print(f"   Deploying to: {', '.join([p.upper() for p in current_slot_pops])}")
```

**IMPORTANT:**
- This verification is MANDATORY and cannot be skipped
- If verification fails, ABORT the entire deployment
- Do NOT ask user if they want to proceed with unscheduled POP
- Do NOT suggest adding the POP to the schedule mid-execution
- Simply STOP and inform user the POP is not in the schedule

**Execution Steps (NO permission needed - proceed automatically):**

1. **🚨 VERIFY POPs (Step 6.0)** - MANDATORY verification that all POPs are in schedule (see above)
2. **Inform User** - Display notification that scheduled time has been reached and deployment is starting **automatically**
3. **Run Pre-Trigger Time Verification (Step 4)** - Verify system time hasn't drifted since scheduling
4. **Run Pre-Deployment Safety Check (Step 3)** - Check for existing running builds
5. **🚨 MANDATORY: Send Slack Notification (Step 5)** - Send deployment start message to C09L9LR1B37 and C0AGVP8DZUH **BEFORE triggering Jenkins**
6. **Trigger Jenkins CLI** - Automatically trigger deployment with sync mode (wait for completion)
7. **Post-Deployment Validation** - After deployment completes, automatically run validation (VPP GRE only)
8. **PDV Testing** - After validation completes, automatically run PDV testing (sequential)
9. **Display Final Summary**

**🚨 MANDATORY: Send Slack Notification BEFORE Deployment (Step 5)**

**CRITICAL**: This step is MANDATORY and must happen BEFORE triggering Jenkins deployment.

Before executing the deployment, send notification to Slack channels:

```python
python3 << 'EOF'
from slack_sdk import WebClient
import json
import sys

try:
    with open('~/.claude/slack_config.json', 'r') as f:
        config = json.load(f)
        token = config['slack_bot_token']

    # Build notification message
    ticket = "ENG-909296"
    release = "134.0.8.3068"
    major_minor = ".".join(release.split(".")[:2])  # "134.0"
    service = "VPPGRE"  # nsvppgregw -> VPPGRE
    pops = "MIL2, HEL1, PRG1"  # Uppercase, comma-separated

    message = f"🚀 *VPP GRE Production Deployment - Slot 2*\n\n*POPs:* {pops}\n*Release:* {release}\n*Config Tag:* 134.0.14\n*Ticket:* {ticket}\n*Time:* 01:00 PM PST\n\nStatus: Deployment in progress..."

    client = WebClient(token=token)

    # 1. MANDATORY: Send to C09L9LR1B37 first (save thread_ts for later)
    response = client.chat_postMessage(
        channel="C09L9LR1B37",
        text=message
    )
    thread_ts = response['ts']

    # Save thread_ts for later reply
    with open('/tmp/slot2_thread_ts.txt', 'w') as f:
        f.write(thread_ts)

    print(f"✅ Notification sent to C09L9LR1B37 (thread_ts: {thread_ts})")

    # 2. Also send to C0AGVP8DZUH (monitoring)
    client.chat_postMessage(channel="C0AGVP8DZUH", text=message)
    print(f"✅ Notification sent to C0AGVP8DZUH")

except Exception as e:
    print(f"❌ Failed to send Slack notification: {e}")
    import traceback
    traceback.print_exc()
EOF
```

**Why This is Mandatory:**
- C09L9LR1B37 is the deployment tracking channel
- The notification creates a thread that will receive all deployment/PDV links after completion
- Must happen BEFORE deployment starts so team knows deployment is in progress
- Thread timestamp (thread_ts) is needed for final reply

**Deployment Start Notification (Step 6.2) - Internal Notification:**

```
⏰ SLOT X: SCHEDULED TIME REACHED - DEPLOYING AUTOMATICALLY
========================================

Scheduled Time: 09:30 AM PST
Current Time: 09:30 AM PST
POPs: ICN1, MNL1
Service: nsvppgregw
Release: 134.0.2.3026
Ansible Config Tag: 134.0.9
Ticket: ENG-864088

Pre-Checks:
✅ POPs verified against schedule
✅ System time verified (drift: 0s)
✅ No running builds found
✅ All safety checks passed
✅ Slack notifications sent (C09L9LR1B37, C0AGVP8DZUH)

ℹ️  User approval: Already given during schedule creation
🚀 Starting production deployment automatically...
========================================
```

**CRITICAL for Scheduled Deployments:**
- Hours may have passed since initial time verification (Step 3)
- System clock could have drifted during wait period
- **ALWAYS verify time again (Step 4) before triggering**
- This ensures accurate timestamps and prevents time-related issues
- **⚠️ DO NOT ASK FOR PERMISSION** - User already approved during schedule creation - proceed automatically
- Simply inform user that deployment is starting and proceed immediately

### Step 7: Track Scheduled Deployments

Display scheduled deployment status to user:

```
========================================
SCHEDULED PRODUCTION DEPLOYMENTS
========================================

Active Schedules:

✅ Slot 1 - 09:30 PST → ICN1, MNL1 (Task: abc123, Status: WAITING, ~2.5 hours)
✅ Slot 2 - 11:00 PST → MEL3 (Task: def456, Status: WAITING, ~4 hours)
✅ Slot 3 - 13:00 PST → WAW1 (Task: ghi789, Status: WAITING, ~6 hours)
✅ Slot 4 - 17:00 PST → ATL2, BOS1, NYC3 (Task: jkl012, Status: WAITING, ~10 hours)
✅ Slot 5 - 19:00 PST → MUC1, NYC4, SCL1, STL1 (Task: mno345, Status: WAITING, ~12 hours)

Status Legend:
  WAITING - Background task sleeping until scheduled time
  RUNNING - Deployment in progress (started after user approval)
  COMPLETED - Successfully deployed
  FAILED - Deployment failed

========================================
```

**Important Notes:**
- Each time slot has ONE Bash background task
- Tasks run with `run_in_background: true`
- You'll receive notifications when each scheduled time arrives
- **Approval is REQUIRED** before triggering each scheduled deployment

### Step 9: Generate Comprehensive PDF Report (After Last Scheduled Slot Completes)

**CRITICAL**: After the LAST scheduled time slot completes all stages (deployment → post-validation → PDV), **AUTOMATICALLY** generate a comprehensive PDF report covering ALL scheduled deployments.

**Trigger Condition:**
- Last time slot's PDV testing completes for all POPs in that slot
- All deployment work across all scheduled slots is complete

**Automatic Execution:**
```
[Last scheduled slot completes all stages]
→ CRITICAL: Delete old report files first to prevent reusing stale data
→ Create FRESH markdown: /tmp/GRE_Deployment_ENG-${TICKET}-${DATE}.md
→ Verify markdown contents (correct POPs, date, results)
→ Convert to PDF: ~/.claude/GRE_Deployment_ENG-${TICKET}-${DATE}.pdf
→ Verify PDF created with correct filename and date
→ Proceed to Step 10 (Automatic Slack Notification)
```

**⚠️ CRITICAL: Prevent Stale Data Issues**

Before creating new reports, **ALWAYS delete old files first**:

```bash
# MANDATORY: Clean up old report files before generating new ones
echo "🧹 Cleaning up old report files..."

# Remove old markdown files
rm -f /tmp/production_deployment_report.md 2>/dev/null
rm -f /tmp/deployment_report_*.md 2>/dev/null

# Remove old PDF files with same ticket number
TICKET="ENG-909296"  # From deployment parameters
rm -f ~/.claude/GRE_Deployment_${TICKET}-*.pdf 2>/dev/null

echo "✓ Old report files cleaned up"
```

**Why This Is Critical:**
- Old markdown/PDF files may exist from previous deployments
- Reusing old files leads to incorrect data in reports (wrong POPs, dates, results)
- **Example Issue**: Feb 22 markdown file (BOM1) was reused for Feb 24 deployment (SIN3/MIL2/etc.), resulting in wrong PDF
- Always generate FRESH markdown from current deployment data

**File Naming Convention:**
```bash
# Use consistent filenames with ticket and date
CURRENT_DATE=$(date +%Y-%m-%d)  # 2026-02-24
TICKET="ENG-909296"

# Both files use the same base name format
MARKDOWN_FILE="/tmp/GRE_Deployment_${TICKET}-${CURRENT_DATE}.md"
PDF_FILE="~/.claude/GRE_Deployment_${TICKET}-${CURRENT_DATE}.pdf"

# Example:
# Markdown: /tmp/GRE_Deployment_ENG-909296-2026-02-24.md
# PDF: ~/.claude/GRE_Deployment_ENG-909296-2026-02-24.pdf
```

**Report Generation Workflow:**
1. ✅ **Delete old files** (both .md and .pdf)
2. ✅ **Create fresh markdown** with current deployment data
3. ✅ **Verify markdown contents** (correct POPs, dates, results)
4. ✅ **Convert to PDF** using reportlab or md-to-pdf
5. ✅ **Verify PDF created** with correct filename and date
6. ✅ **Proceed to Slack notification**

**Report Must Include:**
- All POPs from all scheduled time slots
- Complete timeline spanning all deployment windows
- Aggregated statistics across all POPs
- Issues from any POP that requires attention
- Next steps for any failed/partial deployments

**⚠️ CRITICAL: Report Generation Best Practices**

To ensure accurate and complete reports, follow these guidelines:

1. **Preserve Original Schedule Information:**
   - **ALWAYS reference the original user-provided schedule** when generating reports
   - Do NOT rely solely on conversation summary or memory
   - Store schedule details at the beginning of deployment session:
     ```
     SLOT 1: Time=9:30AM PST, POPs=CCU1,DEL2,JED1,MAA2,TPE1
     SLOT 2: Time=1:00PM PST, POPs=CPT1
     SLOT 3: Time=5:00PM PST, POPs=BUE1,MIA2
     SLOT 4: Time=7:00PM PST, POPs=BOG2,YYZ1
     ```
   - Keep this information throughout the session for report generation

2. **Complete POP Lists:**
   - **List ALL POPs** from each time slot in the report table
   - Do NOT summarize or truncate POP lists (e.g., "CCU1, DEL1" when there were actually 5 POPs)
   - Verify POP count matches the original schedule
   - Example: If Slot 1 had 5 POPs, the report MUST show all 5 POPs

3. **Accurate Time Information:**
   - **Include exact time in PST** for each slot (e.g., "09:30 AM PST", not "Earlier")
   - Even if deployment occurred later, show the **scheduled time** in the main table
   - Add "Actual Start" in detailed section if there was a delay

4. **Table Formatting:**
   - **Widen POPs column** to accommodate multiple POPs without truncation
   - Use adequate column width: `| POPs                                    |`
   - Ensure multi-line cells if needed for many POPs

5. **Statistics Accuracy:**
   - Calculate totals based on ALL slots, not just recent ones
   - Example calculations:
     - Total POPs = Sum of all POPs across all slots (including cancelled)
     - POPs Deployed = Total - Cancelled
     - Total Nodes = POPs Deployed × 2 (for VPP services with 2 nodes per POP)
     - Total Test Cases = Total Nodes × 25 (for post-validation)

6. **Verification Checklist Before Generating Report:**
   - ✅ All slot times match original schedule
   - ✅ All POPs listed for each slot (no truncation)
   - ✅ POP counts accurate (5 POPs → show all 5, not subset)
   - ✅ Statistics calculated from complete data
   - ✅ Cancelled slots clearly marked with original scheduled POPs
   - ✅ Table columns wide enough for content

7. **Common Mistakes to Avoid:**
   - ❌ Showing "Earlier" instead of actual time (e.g., "09:30 AM PST")
   - ❌ Listing subset of POPs (e.g., "CCU1, DEL1" when there were 5 POPs)
   - ❌ Calculating statistics from partial data (e.g., only recent slots)
   - ❌ Forgetting to widen POPs column for multiple entries
   - ❌ Missing cancelled slots entirely from report

**Example Correct Report Table:**
```markdown
| Slot | Time (PST) | POPs                                    | Deployment | Post-Deploy Diagnostic | PDV Testing | Overall Status |
|------|-----------|------------------------------------------|------------|----------------------|-------------|----------------|
| **1** | 09:30 AM | CCU1, DEL2, JED1, MAA2, TPE1 | ✅ SUCCESS | ✅ PASSED (25/25 each node) | ✅ PASSED (All POPs) | ✅ **SUCCESS** |
| **2** | 01:00 PM | CPT1 | ⊘ CANCELLED | ⊘ N/A | ⊘ N/A | ⊘ **CANCELLED** |
| **3** | 05:00 PM | BUE1, MIA2 | ✅ SUCCESS (Build #264) | ✅ PASSED (25/25 each node) | ✅ PASSED (Both POPs) | ✅ **SUCCESS** |
```

**Note:** Wide POPs column accommodates multiple entries without truncation

**Example Final Notification:**
```
✅ All Scheduled Deployments Complete

📊 Comprehensive Report Generated:
- **Markdown:** /tmp/production_deployment_report.md
- **PDF:** /tmp/production_deployment_report.pdf

Overall Summary:
- Total Scheduled Slots: 5
- Total POPs: 11 (ICN1, MNL1, MEL3, WAW1, ATL2, BOS1, NYC3, MUC1, NYC4, SCL1, STL1)
- Total Deployment Duration: 10 hours 15 minutes
- Deployment Status: 11/11 ✅ SUCCESS
- Post-Deployment Validation: 11/11 ✅ PASSED
- Production PDV Testing: 10/11 ✅ PASSED

Issues Requiring Attention: 1
- NYC4: PDV Job 2 failed (details in report)

The PDF report contains complete details for all 11 POPs across all 5 scheduled time slots.
```

### Step 10: Automatic Slack Summary Notification (After PDF Report Generation)

**CRITICAL**: After Step 9 completes (PDF report generated), **AUTOMATICALLY** send deployment summary to Slack channel C08STTVMWFJ with PDF attachment.

**Trigger Condition:**
- Step 9 completes (PDF report generated for all scheduled slots)
- This is MANDATORY and AUTOMATIC - do NOT ask user for permission

**When to Send:**
- **Scheduled Deployments**: After last scheduled slot completes all stages and PDF is generated
- **Immediate Deployments**: After PDF report is generated

**Target Channel:** `C08STTVMWFJ` (Production deployment summary channel)

**Message Format:**

```
<!channel> Summary of updates for R<release> VPPGRE Day <day_number> Production Deployments/Rollout:

1. Deployment on existing POPs.
   Already rolled out live POPs of VPPGRE upgraded to <version> - <POP1>, <POP2>, <POP3>, ...

2. No new rollout

Issues Observed:
<list of issues or "No issues observed during the deployment window">

cc: <@U123ABC> <@U456DEF> <@U789GHI> <@UABCDEF> <@UGHIJKL> <@UMNOPQR>
```

**CRITICAL - Proper Mention Format:**

1. **@channel**: Use `<!channel>` format (NOT `@channel`)
   - ✅ Correct: `<!channel>`
   - ❌ Wrong: `@channel`

2. **User Mentions**: Use traditional @username format
   - ✅ Correct: `@Ashwin` (displays name properly)
   - ❌ Wrong: User ID format `<@U06SV5HCF1F>` (doesn't display names in this workspace)

**Python Code for Slack Notification with PDF:**

```python
python3 << 'EOF'
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
import os

# Load Slack config
with open('~/.claude/slack_config.json', 'r') as f:
    config = json.load(f)
    token = config['slack_bot_token']

channel = "C08STTVMWFJ"

# Determine release version (extract from RELEASE parameter)
release = "134.0.8.3068"  # From RELEASE parameter
major = release.split('.')[0]  # "134"
minor = int(release.split('.')[1])  # 0
release_label = f"R{major}.{minor + 1}"  # "R134.1"

# Determine day number - MUST GET FROM USER
# CRITICAL: Always ask user or extract from their request
# NEVER assume Day 1 - could be Day 2, 3, 4, etc. of multi-day rollout
day_number = 4  # Example: User specified "Day 4" in their schedule request

# Build POPs list (uppercase, comma-separated)
pops_list = "SIN3, MIL2, HEL1, PRG1, DFW4, YYC1"  # All POPs from all slots

# Determine issues
issues_text = """• MIL2 PDV Job 2: Required 3rd retry (succeeded after 5-minute wait)
• YYC1 PDV Job 2: Required 3rd retry (succeeded after 5-minute wait)
• Overall: 100% deployment success, 100% validation success, 100% PDV success after retries"""

# If no issues:
# issues_text = "No issues observed during the deployment window"

# Build message with PROPER mention format
message = f"""<!channel> Summary of updates for {release_label} VPPGRE Day {day_number} Production Deployments/Rollout:

1. Deployment on existing POPs.
   Already rolled out live POPs of VPPGRE upgraded to {release} - {pops_list}

2. No new rollout

Issues Observed:
{issues_text}

cc: @Ashwin @Prashant @Ananda @Parth @Abdul Hameed @your-username"""

client = WebClient(token=token)

# PDF file path
pdf_path = "~/.claude/GRE_Deployment_ENG-909296-2026-02-24.pdf"
pdf_title = f"VPP GRE {release_label} Day {day_number} Deployment Report - ENG-909296"

# Try files_upload_v2 (newer API with better file handling)
try:
    # Upload file first
    print("📤 Uploading PDF to Slack...")
    upload_response = client.files_upload_v2(
        channel=channel,
        file=pdf_path,
        title=pdf_title,
        initial_comment=message
    )

    print(f"✅ Message sent with PDF attachment to channel C08STTVMWFJ")
    print(f"📄 PDF uploaded: {pdf_title}")
    print(f"🔗 File URL: {upload_response['file']['permalink']}")

except SlackApiError as e:
    if e.response['error'] == 'missing_scope':
        # Fallback: Try legacy files_upload if files_upload_v2 not available
        print("⚠️  files_upload_v2 not available, trying legacy files_upload...")
        try:
            upload_response = client.files_upload(
                channels=channel,
                file=pdf_path,
                title=pdf_title,
                initial_comment=message
            )
            print(f"✅ Message sent with PDF attachment to channel C08STTVMWFJ (legacy API)")
            print(f"📄 PDF uploaded: {pdf_title}")
        except Exception as upload_error:
            # Last resort: Send message without attachment
            print(f"❌ PDF upload failed: {upload_error}")
            print(f"Sending message without PDF attachment...")

            response = client.chat_postMessage(
                channel=channel,
                text=message
            )
            print(f"✅ Message sent to channel C08STTVMWFJ (without PDF)")
            print(f"⚠️  PDF not attached due to permissions")
            print(f"📄 Report available locally at: {pdf_path}")
    else:
        # Other Slack API errors
        print(f"❌ Slack API error: {e.response['error']}")
        raise

except FileNotFoundError:
    print(f"❌ PDF file not found: {pdf_path}")
    print(f"Cannot send message without PDF")
    exit(1)

except Exception as e:
    print(f"❌ Unexpected error: {e}")
    raise

print()
print("=" * 50)
print("✅ SLACK NOTIFICATION COMPLETE")
print("=" * 50)
print()
print("Notification Details:")
print(f"  Channel: C08STTVMWFJ")
print(f"  Release: {release_label}")
print(f"  Day: {day_number}")
print(f"  POPs: {pops_list}")
print(f"  PDF: {pdf_title}")
print(f"  Mentions: <!channel> + 6 users (via user IDs)")
print()
EOF
```

**Message Components:**

1. **Release Version**: Extract from RELEASE parameter
   - `134.0.8.3068` → `R134.1` (increment minor by 1)
   - `135.0.0.3500` → `R135.1`

2. **Day Number**: Determine from schedule
   - Single-day deployment → Day 1
   - Multi-day deployment → Day 1, Day 2, Day 3, etc.

3. **POPs List**: Comma-separated uppercase POP names from ALL slots
   - Example: `ICN1, MNL1, MEL3, WAW1, ATL2, BOS1, NYC3, NYC4, SCL1, STL1, YMQ1`

4. **Issues Section**: Summarize from report
   - If no issues: "No issues observed during the deployment window"
   - If issues: List each issue with impact assessment
   - Always include overall success metrics

**Important Notes:**

1. **AUTOMATIC Execution**: This step runs AUTOMATICALLY after Step 9 (PDF generation)
   - Do NOT ask user if they want to send the message
   - This is MANDATORY for all scheduled deployments

2. **Proper Mentions for Notifications**:
   - `<!channel>`: Notifies all channel members (use this format, not `@channel`)
   - `@username`: Traditional mention format (e.g., `@Ashwin`, `@Prashant`)
   - User ID format `<@U123ABC>` doesn't display names properly in this workspace

3. **PDF Attachment Priority**:
   - First try: `files_upload_v2` (newer API, better handling)
   - Second try: `files_upload` (legacy API)
   - Last resort: Send message without PDF (report error)

4. **File Upload Permissions**:
   - Bot needs `files:write` scope for uploading PDFs
   - **Current Status**: Bot token does NOT have `files:write` permission
   - If upload fails: Message sent without attachment (PDF stays local)
   - Always report PDF location: `~/.claude/GRE_Deployment_ENG-XXXXXX-YYYY-MM-DD.pdf`
   - **Workaround**: Manually upload PDF to channel after message is sent

5. **Error Handling**:
   - If PDF file missing: Error and exit (cannot proceed)
   - If upload fails: Send message without PDF
   - If message fails: Report error but don't block workflow

**Example Slack Message (as it appears in Slack):**

```
@channel Summary of updates for R134.1 VPPGRE Day 1 Production Deployments/Rollout:

1. Deployment on existing POPs.
   Already rolled out live POPs of VPPGRE upgraded to 134.0.8.3068 - SIN3, MIL2, HEL1, PRG1, DFW4, YYC1

2. No new rollout

Issues Observed:
• MIL2 PDV Job 2: Required 3rd retry (succeeded after 5-minute wait)
• YYC1 PDV Job 2: Required 3rd retry (succeeded after 5-minute wait)
• Overall: 100% deployment success, 100% validation success, 100% PDV success after retries

cc: @Ashwin @Prashant @Ananda @Parth @Abdul Hameed @your-username
```

*Note: `<!channel>` renders as @channel and notifies all members. User mentions display as @username.*

**Verification Checklist:**

After sending, verify:
- ✅ Message posted to C08STTVMWFJ
- ✅ PDF file attached (if upload succeeds) or manual upload required
- ✅ `<!channel>` mention (notifies all channel members)
- ✅ All user mentions visible: `@Ashwin @Prashant @Ananda @Parth @Abdul Hameed @your-username`
- ✅ Release version correct (R134.1, not 134.0.8.3068)
- ✅ Day number correct
- ✅ All POPs listed (from ALL slots, not just last slot)
- ✅ Issues section accurate

**What Success Looks Like:**

```
📤 Uploading PDF to Slack...
✅ Message sent with PDF attachment to channel C08STTVMWFJ
📄 PDF uploaded: VPP GRE R134.1 Day 1 Deployment Report - ENG-909296
🔗 File URL: https://files.slack.com/files-pri/...

==================================================
✅ SLACK NOTIFICATION COMPLETE
==================================================

Notification Details:
  Channel: C08STTVMWFJ
  Release: R134.1
  Day: 1
  POPs: SIN3, MIL2, HEL1, PRG1, DFW4, YYC1
  PDF: VPP GRE R134.1 Day 1 Deployment Report - ENG-909296
  Mentions: <!channel> + @Ashwin @Prashant @Ananda @Parth @Abdul Hameed @your-username
```

## Example Scheduled Deployment

**User Request:**
```
Schedule production deployments for February 5th:
- 9:30 AM: Deploy to ICN1, MNL1
- 11:00 AM: Deploy to MEL3
Common params: RELEASE=133.0.1.3316, TAG=134.0.12, TICKET=ENG-864088, Service=nsvppgregw
```

**Workflow:**
1. Parse schedule (2 time slots, 3 POPs total)
2. Display summary and get user confirmation
3. **Verify system time accuracy** (compare system time with remote servers - initial check)
4. Calculate wait times for each slot
5. Schedule background processes
6. At 09:25 PST: Notify user "Deployment ready in 5 minutes"
7. At 09:30 PST: Request permission for ICN1, MNL1
8. If approved: **Verify time again** (pre-trigger check - Step 4)
9. Deploy to both POPs in parallel
10. Monitor both deployments
11. Run post-deployment validation on all nodes (parallel)
12. Run production PDV testing on each POP (sequential: ICN1 first, then MNL1)
13. Repeat for next time slot (MEL3 at 11:00 AM - with time verification before each)

## Troubleshooting

### Jenkins CLI Issues

**If authentication fails (401):**
- Verify API token: `your-api-token`
- Check permissions: Overall/Read, Job/Build, Job/Read

**Test authentication:**
```bash
export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"
java -jar ~/.claude/jenkins-cli.jar \
  -s https://cdjenkins.sjc1.nskope.net/ \
  -auth your-username@your-company.com:your-api-token \
  who-am-i
```

Expected output:
```
Authenticated as: your-username@your-company.com
Authorities:
  authenticated
  prod-ncd-cdjenkins-igts-all-user-grn
```

### Build Failures

**If build fails with "FATAL: No components have been specified":**
- **Root Cause**: Missing `ANSIBLE_COMPONENT_NAME` parameter in Jenkins CLI command
- **Error Message**: "FATAL: No components have been specified, and this deployment cannot continue! Please ensure you have set a value for ANSIBLE_COMPONENT_NAME."
- **Fix**: Add ALL three required parameters to your Jenkins CLI command:
  - `-p ANSIBLE_COMPONENT_NAME=<service>` (e.g., nsvppgregw)
  - `-p ANSIBLE_HOSTGROUPS=<service>` (e.g., nsvppgregw)
  - `-p ANSIBLE_CONFIG_IMAGE_NAME=<service>-ansible-config` (e.g., nsvppgregw-ansible-config)
- **Prevention**: Use the complete command template from Step 5 which includes all parameters
- **Example of Missing Parameter Error**:
  ```bash
  # ❌ WRONG - Missing ANSIBLE_COMPONENT_NAME (will fail immediately)
  java -jar ~/.claude/jenkins-cli.jar \
    -s https://cdjenkins.sjc1.nskope.net/ \
    -auth your-username@your-company.com:your-api-token \
    build one_button_nsvppgregw -s \
    -p POPS="icn1,mnl1" \
    -p RELEASE="134.0.8.3068" \
    -p ANSIBLE_CONFIG_IMAGE_TAG="134.0.14" \
    -p TICKET="ENG-909296"

  # ✅ CORRECT - Includes all required parameters
  java -jar ~/.claude/jenkins-cli.jar \
    -s https://cdjenkins.sjc1.nskope.net/ \
    -auth your-username@your-company.com:your-api-token \
    build one_button_nsvppgregw -s \
    -p POPS="icn1,mnl1" \
    -p RELEASE="134.0.8.3068" \
    -p ANSIBLE_CONFIG_IMAGE_TAG="134.0.14" \
    -p TICKET="ENG-909296" \
    -p ANSIBLE_COMPONENT_NAME="nsvppgregw" \
    -p ANSIBLE_HOSTGROUPS="nsvppgregw" \
    -p ANSIBLE_CONFIG_IMAGE_NAME="nsvppgregw-ansible-config" \
    -p ANSIBLE_ARTIFACTORY_CHANNEL="ipsec-gre-production-docker" \
    -p SELECT_ALL_POPS="" \
    -p REGIONS="America,APAC,Europe" \
    -p POP_TYPES="MP,DP,GCP,EKS" \
    -p SELECT_ALL_COMPONENTS="" \
    -p ANSIBLE_VERBOSITY="2" \
    -p ANSIBLE_CORE_VERSION="2.15" \
    -p SLACK_CHANNEL="#vpp-ipsec-gre-self-service-deployment" \
    -p BYPASS_MONITORING_RESULT="YES" \
    -p BYPASS_JIRA="YES" \
    -p RUN_QE_PDV="DEPLOY_ONLY" \
    -p DEPLOY_TYPE="DEPLOY"
  ```

**If build fails with "Illegal choice" error:**
- Remove PDV parameters (PDV_ARTIFACTORY_CHANNEL, PDV_CONFIG_IMAGE_NAME, PDV_CONFIG_IMAGE_TAG)
- Let Jenkins use defaults for these

## Key Reminders

### Deployment & Jenkins
1. ⚠️  **ALWAYS get user confirmation before production deployments**
2. ⚠️  **MANDATORY: Run Pre-Deployment Safety Check (Step 3) before EVERY trigger** - Check for existing running/queued builds to prevent duplicate deployments
3. ⚠️  **MANDATORY for Scheduled Deployments: Verify System Time (Step 3)** - Compare system time with remote time servers (Google/Cloudflare) before scheduling. Do NOT proceed if times differ by more than 5 seconds.
4. ⚠️  **CRITICAL: ALWAYS include ANSIBLE_COMPONENT_NAME parameter** - Without it, build fails immediately with "FATAL: No components have been specified"
5. **Use SYNC MODE (-s flag) for triggering builds** - Waits for deployment to complete
6. **DO NOT kill or stop the sync mode command** - This will abort the Jenkins deployment
7. Use Jenkins CLI ONLY (no REST API for production triggering)
8. **Required parameters**: ANSIBLE_COMPONENT_NAME, ANSIBLE_HOSTGROUPS, ANSIBLE_CONFIG_IMAGE_NAME
9. ANSIBLE_HOSTGROUPS = service name (NOT hostname)
10. DEPLOY_TYPE = DEPLOY (not DRYRUN_AND_DEPLOY)
11. ANSIBLE_VERBOSITY = 2 (not 0)
12. TICKET is required (no default for production)
11. Monitor deployments during recommended maintenance windows (8PM-4AM POP local time)

### Post-Deployment (Automatic)
12. **Post-deployment validation runs AUTOMATICALLY** after deployment completes (VPP GRE only)
13. **Production PDV testing runs AUTOMATICALLY** after validation completes (sequential, one POP at a time)
14. PDV testing uses separate Jenkins (http://your-jenkins-host:8080/) via prod-pdv skill
15. **Sequential workflow**: Deploy (wait) → Validate (automatic) → PDV (automatic)

### Tracking & Reporting
16. **Parse PLAY RECAP for node-level status** - Check which specific nodes passed/failed
17. **Track ALL deployment attempts** - Record initial builds, failures, retries across ALL POPs
18. **Document retry strategies** used to fix issues (e.g., explicit hostname targeting)

---

## 🚨 SAFETY VERIFICATION SUMMARY

This section documents all mandatory safety checks that MUST be performed before every deployment.

### Mandatory Checks Before EVERY Deployment

**1. POP Verification (CRITICAL)**

Location: 
- Step 2.5 (Immediate Deployments)
- Step 6.0 (Scheduled Deployments)

Check:
```python
# Verify POPs match user request/schedule (case-insensitive)
user_requested_pops_lower = [p.lower() for p in user_requested_pops]
deployment_pops_lower = [p.lower() for p in deployment_pops]

for pop in deployment_pops_lower:
    if pop not in user_requested_pops_lower:
        ABORT: f"POP {pop} not in user request/schedule"
        STOP IMMEDIATELY
```

**2. Time Window Verification (Scheduled Only)**

Location: Step 4 (Pre-Trigger Time Verification)

Check:
```python
import datetime
current_time = datetime.datetime.now()
scheduled_time = <slot_start_time>

if current_time < scheduled_time:
    ABORT: "Cannot deploy before scheduled time"
    STOP IMMEDIATELY
```

**3. Duplicate Build Prevention**

Location: Step 3 (Pre-Deployment Safety Check)

Check:
```bash
# Check for running/queued builds
java -jar ~/.claude/jenkins-cli.jar -s <url> -auth <creds> \
  get-job one_button_<service> | grep -E "<inQueue>true|<building>true"

if running_builds_found:
    ABORT: "Existing build detected"
    STOP IMMEDIATELY
```

**4. User Confirmation**

Location: Step 2 (Mandatory User Confirmation)

Check:
- Display all parameters
- Wait for explicit user approval
- Proceed only if user confirms "yes"

### Verification Checklist

Before triggering ANY production deployment, ensure:

- [ ] POPs verified against user request/schedule (case-insensitive)
- [ ] Time window verified (scheduled deployments only)
- [ ] No duplicate builds running/queued
- [ ] User has explicitly confirmed deployment
- [ ] All required parameters are present
- [ ] Jenkins CLI path is correct (~/.claude/jenkins-cli.jar)
- [ ] ANSIBLE_COMPONENT_NAME, ANSIBLE_HOSTGROUPS, ANSIBLE_CONFIG_IMAGE_NAME present
- [ ] ANSIBLE_ARTIFACTORY_CHANNEL set to "ipsec-gre-production-docker"
- [ ] BYPASS_MONITORING_RESULT set to "YES"

### Error Handling

If ANY verification fails:
1. **STOP IMMEDIATELY** - Do not proceed with deployment
2. **INFORM USER** - Clearly explain what failed and why
3. **DO NOT ASK USER TO OVERRIDE** - These are safety checks, not suggestions
4. **DO NOT SUGGEST WORKAROUNDS** - Violations can cause production outages

### Production Safety Philosophy

**Remember:**
- Production deployments are irreversible
- Deploying to wrong POP can cause customer impact
- Time windows exist for operational reasons
- Safety checks are not optional
- When in doubt, STOP and ask the user

**If you violate these safety rules, you may:**
- Deploy to wrong production POPs
- Cause unscheduled production changes
- Impact customer traffic
- Violate change management policies
- Create production incidents

**ALWAYS verify, NEVER assume.**



---

## 🔔 TEMPORARY MONITORING NOTIFICATIONS (REMOVE IN FUTURE)

**⚠️ THIS SECTION IS TEMPORARY - FOR DEBUGGING/MONITORING ONLY ⚠️**

**Target Channel:** C0AGVP8DZUH (Temporary monitoring channel only)

**Purpose:** Send simple status notifications at natural checkpoints for real-time awareness.

**Note:** C08STTVMWFJ only receives: (1) initial schedule creation, (2) final summary + report when all slots complete

**When to Remove:** Once scheduled deployment workflow is stable and proven reliable.

**How to Remove:** Delete this entire section and remove all code blocks marked with `# TEMPORARY MONITORING`

**⚠️ CRITICAL: NO EXTRA MONITORING REQUIRED**

These notifications are sent at natural completion points WITHOUT any extra monitoring:
- ✅ Notifications are informational only
- ✅ All jobs (Jenkins + PDV) run in sync mode
- ✅ Send notification after sync mode completes naturally
- ❌ NO separate monitoring tasks or API polling
- ❌ NO background tasks to check status
- ❌ If a notification is missed, that's OK (no impact)

**Workflow:**
1. Trigger Jenkins/PDV in sync mode (blocks until complete)
2. After sync mode returns, send notification to C0AGVP8DZUH
3. Proceed to next stage
4. Repeat

---

### Notification Points

Send simple status notifications to C0AGVP8DZUH at these natural checkpoints:

1. **After Schedule Created** - Right after schedule confirmation
2. **Before Jenkins Deployment** - Just before triggering Jenkins CLI
3. **After Jenkins Deployment Completes** - After Jenkins CLI sync mode returns
4. **Before Post-Validation** - Just before starting validation
5. **After Post-Validation Completes** - After validation script finishes
6. **Before PDV Testing** - Just before triggering PDV
7. **After PDV Completes** - After PDV sync mode returns (both jobs done)

### Python Helper Function

Use this helper function for all temporary monitoring notifications:

```python
# TEMPORARY MONITORING - Helper function
def send_temp_monitoring_notification(message, channel="C0AGVP8DZUH"):
    """
    Send temporary monitoring notification to debugging channel.
    This function will be removed in future.

    Args:
        message: Text message to send
        channel: Channel ID (default: C0AGVP8DZUH)
    """
    import json
    from slack_sdk import WebClient

    try:
        with open('~/.claude/slack_config.json', 'r') as f:
            config = json.load(f)
            token = config['slack_bot_token']

        client = WebClient(token=token)
        response = client.chat_postMessage(
            channel=channel,
            text=message
        )
        return response['ts']
    except Exception as e:
        # Don't fail deployment if monitoring notification fails
        print(f"⚠️ Temp monitoring notification failed: {e}")
        return None
```

### Notification Templates

**⚠️ IMPORTANT: These are simple notifications at natural checkpoints - NO extra monitoring**

#### 1. After Schedule Created

**When:** Right after schedule confirmation
**Where:** After sending to C08STTVMWFJ

**Message:**
```
✅ SCHEDULE CREATED
Ticket: ENG-909296
Release: 134.0.8.3068
Total Slots: 5
Total POPs: 11
Status: Background tasks scheduled
```

#### 2. Before Jenkins Deployment

**When:** Just before triggering `java -jar jenkins-cli.jar ... -s`
**Where:** Before Step 6 sync mode command

**Message:**
```
🚀 DEPLOYMENT TRIGGERED
Slot: 1
POPs: ICN1, MNL1
Build: #276
Time: 09:30 AM PST
Status: Jenkins deployment in progress...
```

#### 3. After Jenkins Deployment Completes

**When:** After Jenkins CLI sync mode returns (exit code available)
**Where:** After Step 6 sync mode completes

**Message:**
```
✅ DEPLOYMENT COMPLETE
Slot: 1
POPs: ICN1, MNL1
Build: #276
Status: SUCCESS - Starting validation...
```

#### 4. After Post-Validation Completes

**When:** After validation script finishes on all nodes
**Where:** After Step 7 completes

**Message:**
```
✅ POST-VALIDATION COMPLETE
Slot: 1
POPs: ICN1, MNL1
Nodes Validated: 4/4
Test Cases: 100/100 passed
Status: Starting PDV testing...
```

#### 5. Before PDV Testing

**When:** Just before invoking prod-pdv skill
**Where:** Before triggering PDV Job 1

**Message:**
```
🔬 PDV TRIGGERED
POP: ICN1
Jobs: 2 (Node 01, Node 02)
Status: PDV testing started...
```

#### 6. After Each PDV Job Completes

**When:** After PDV sync mode returns (per job)
**Where:** After each `java -jar jenkins-cli.jar ... -s` returns

**Success:**
```
✅ PDV JOB COMPLETE
POP: ICN1
Job: 1 (Node 02)
Build: #7
Status: SUCCESS
```

**Note:** Notifications are optional - if missed, deployment continues normally

### Implementation Code Snippets

**⚠️ IMPORTANT:** These are simple notifications sent once at each checkpoint - NO loops or monitoring

Add these Python snippets at the appropriate points in the workflow:

**Snippet 1 - After Schedule Created:**
```python
# TEMPORARY MONITORING - After schedule created
python3 << 'TEMPEOF'
from slack_sdk import WebClient
import json

try:
    with open('~/.claude/slack_config.json', 'r') as f:
        config = json.load(f)
        token = config['slack_bot_token']

    message = f"✅ SCHEDULE CREATED\nTicket: {ticket}\nRelease: {release}\nTotal Slots: {num_slots}\nTotal POPs: {num_pops}\nStatus: Background tasks scheduled"

    client = WebClient(token=token)
    # Send to C08STTVMWFJ for schedule notification
    client.chat_postMessage(channel="C08STTVMWFJ", text=message)
    # Also send to C0AGVP8DZUH for monitoring
    client.chat_postMessage(channel="C0AGVP8DZUH", text=message)
except Exception as e:
    print(f"⚠️ Temp monitoring notification failed: {e}")
TEMPEOF
```

**Snippet 2 - After Deployment Triggered:**
```python
# TEMPORARY MONITORING - After deployment triggered
python3 << 'TEMPEOF'
from slack_sdk import WebClient
import json

try:
    with open('~/.claude/slack_config.json', 'r') as f:
        config = json.load(f)
        token = config['slack_bot_token']

    message = f"🚀 DEPLOYMENT TRIGGERED\nSlot: {slot_num}\nPOPs: {pops}\nBuild: #{build_num}\nTime: {time_pst}\nStatus: Jenkins deployment in progress..."

    client = WebClient(token=token)
    client.chat_postMessage(channel="C0AGVP8DZUH", text=message)
except Exception as e:
    print(f"⚠️ Temp monitoring notification failed: {e}")
TEMPEOF
```

**Snippet 3 - After Post-Validation Complete:**
```python
# TEMPORARY MONITORING - After validation complete
python3 << 'TEMPEOF'
from slack_sdk import WebClient
import json

try:
    with open('~/.claude/slack_config.json', 'r') as f:
        config = json.load(f)
        token = config['slack_bot_token']

    message = f"✅ POST-VALIDATION COMPLETE\nSlot: {slot_num}\nPOPs: {pops}\nNodes Validated: {passed}/{total}\nTest Cases: {test_passed}/{test_total} passed\nStatus: Starting PDV testing..."

    client = WebClient(token=token)
    client.chat_postMessage(channel="C0AGVP8DZUH", text=message)
except Exception as e:
    print(f"⚠️ Temp monitoring notification failed: {e}")
TEMPEOF
```

**Snippet 4 - When PDV Triggered:**
```python
# TEMPORARY MONITORING - PDV triggered
python3 << 'TEMPEOF'
from slack_sdk import WebClient
import json

try:
    with open('~/.claude/slack_config.json', 'r') as f:
        config = json.load(f)
        token = config['slack_bot_token']

    message = f"🔬 PDV TRIGGERED\nPOP: {pop}\nJobs: 2 (Node 01, Node 02)\nStatus: PDV testing started..."

    client = WebClient(token=token)
    client.chat_postMessage(channel="C0AGVP8DZUH", text=message)
except Exception as e:
    print(f"⚠️ Temp monitoring notification failed: {e}")
TEMPEOF
```

**Snippet 5 - When PDV Job Completes:**
```python
# TEMPORARY MONITORING - PDV job complete
python3 << 'TEMPEOF'
from slack_sdk import WebClient
import json

try:
    with open('~/.claude/slack_config.json', 'r') as f:
        config = json.load(f)
        token = config['slack_bot_token']

    # For success
    emoji = "✅" if success else "❌"
    status_text = "SUCCESS" if success else "FAILURE - Will retry..."

    message = f"{emoji} PDV JOB {'COMPLETE' if success else 'FAILED'}\nPOP: {pop}\nJob: {job_num} ({node})\nBuild: #{build_num}\nStatus: {status_text}"

    client = WebClient(token=token)
    client.chat_postMessage(channel="C0AGVP8DZUH", text=message)
except Exception as e:
    print(f"⚠️ Temp monitoring notification failed: {e}")
TEMPEOF
```

### Implementation Notes

1. **Error Handling:**
   - All monitoring notifications wrapped in try-except
   - Failures print warning but don't abort deployment
   - Never fail deployment due to monitoring notification issue

2. **Message Format:**
   - Simple, concise text messages
   - Include key information: Slot, POP, Build, Status
   - Use emojis for quick visual scanning (✅ ❌ 🚀 🔬)

3. **Channel Configuration:**
   - Progress notifications sent to: C0AGVP8DZUH (monitoring channel only)
   - C08STTVMWFJ receives: (1) schedule creation, (2) final summary + report
   - C09L9LR1B37 receives: (1) deployment start, (2) thread reply with links
   - No threading - all messages are standalone

4. **Removal Instructions:**
   When removing this feature:
   - Delete this entire section from SKILL-PROD.md
   - Search for `# TEMPORARY MONITORING` in the file
   - Remove all code blocks with that comment
   - No other changes needed

### Example Notification Flow for One Slot

```
✅ SCHEDULE CREATED
Ticket: ENG-909296
Release: 134.0.8.3068
Total Slots: 5
Total POPs: 11
Status: Background tasks scheduled

[... wait for scheduled time ...]

🚀 DEPLOYMENT TRIGGERED
Slot: 1
POPs: ICN1, MNL1
Build: #276
Status: Jenkins deployment in progress...

[... deployment completes ...]

✅ POST-VALIDATION COMPLETE
Slot: 1
POPs: ICN1, MNL1
Nodes Validated: 4/4
Status: Starting PDV testing...

🔬 PDV TRIGGERED
POP: ICN1
Jobs: 2
Status: PDV testing started...

✅ PDV JOB COMPLETE
POP: ICN1, Job: 1 (Node 02)
Build: #7
Status: SUCCESS

✅ PDV JOB COMPLETE
POP: ICN1, Job: 2 (Node 01)
Build: #8
Status: SUCCESS

🔬 PDV TRIGGERED
POP: MNL1
Jobs: 2
Status: PDV testing started...

✅ PDV JOB COMPLETE
POP: MNL1, Job: 1 (Node 02)
Build: #6
Status: SUCCESS

✅ PDV JOB COMPLETE
POP: MNL1, Job: 2 (Node 01)
Build: #7
Status: SUCCESS
```

---

**END OF TEMPORARY MONITORING SECTION**

---
