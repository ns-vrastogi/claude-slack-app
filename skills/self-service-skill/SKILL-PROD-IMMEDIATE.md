name: self-service-production-immediate
description: Immediate production deployment for VPP-based services (ecgw, nsvppgregw, nsvppipsecgw, steeringlb) to regional production POPs.

# Production Immediate Deployment Guide

**⚠️ WARNING: This is for IMMEDIATE PRODUCTION deployments only!**

## 🚨 CRITICAL SAFETY RULES - NEVER VIOLATE 🚨

### Rule 1: MANDATORY Pre-Deployment Verification
- POPs must match request
- **Service type MUST be explicitly stated by the user** — NEVER auto-detect or assume
- **NEVER deploy to a service other than the one user explicitly requested**
- Check for duplicate/running builds before triggering new ones
- If build already running, offer option to monitor existing build

### Rule 2: NEVER Kill Running Deployments
- Let ALL Jenkins jobs complete naturally
- Only abort if user explicitly requests

### Rule 3: MANDATORY Deployment Confirmation
- **ALWAYS display complete deployment details** before triggering
- **MUST include**: POPs, Service, all parameters
- **MUST ask**: "Do you want to proceed with this deployment? (yes/no)"
- **WAIT for explicit user confirmation** (yes) before deploying
- **If user says no**: ABORT immediately
- **The block MUST show actual values** — Service, POPs, RELEASE, TAG, TICKET — never placeholders

### Rule 4: NO EXPERIMENTATION in Production Environment
- **NEVER experiment or try new approaches** without explicit user permission
- **If something fails**: STOP and ASK before trying anything new
- **ALWAYS get user approval** before attempting any workaround or alternative approach
- **When in doubt**: Describe the issue and proposed solution, then WAIT for approval

---

## Environment Configuration

```bash
# Required env vars — set in ~/.bashrc before use
JENKINS_PROD_URL      # e.g. https://your-jenkins.company.com/
JENKINS_USERNAME      # e.g. user@company.com
JENKINS_PROD_TOKEN    # Jenkins API token
JENKINS_JOB_PREFIX    # e.g. one_button  → job = one_button_<service>
```

**ALWAYS use env vars directly in commands:**
```bash
curl -u "${JENKINS_USERNAME}:${JENKINS_PROD_TOKEN}" ...
```

**If `$JENKINS_PROD_TOKEN` is empty**: Stop and tell the user to run `source ~/.bashrc`.

---

## Service to Jenkins Job Mapping

| Service | Jenkins Job | Description |
|---------|------------|-------------|
| `nsvppgregw` | `${JENKINS_JOB_PREFIX}_nsvppgregw` | VPP GRE Gateway |
| `nsvppipsecgw` | `${JENKINS_JOB_PREFIX}_nsvppipsecgw` | VPP IPSEC Gateway |
| `ecgw` | `${JENKINS_JOB_PREFIX}_ecgw` | ECGW Gateway |
| `steeringlb` | `${JENKINS_JOB_PREFIX}_steeringlb` | Steering Load Balancer |

**CRITICAL**: Service type MUST be explicitly provided by user. Never auto-detect from hostname or context.

---

## Required Parameters

All parameters MUST be explicitly provided by the user — never assumed or auto-detected.

- **RELEASE**: Version (e.g., `134.0.8.3068`)
- **ANSIBLE_CONFIG_IMAGE_TAG**: Config tag (e.g., `134.0.14`)
- **TICKET**: Ticket reference (e.g., `ENG-909296`)
- **SERVICE**: Must be explicitly stated — `nsvppgregw`, `nsvppipsecgw`, `ecgw`, or `steeringlb`
- **POPs**: Target POPs (e.g., `del1,ams1,los1`) — lowercase

⚠️ **If service type is NOT explicitly stated, ASK the user before proceeding.**

---

## Complete Immediate Deployment Workflow

### Step 1: Parse Request

- Extract all parameters from user request
- Service type MUST be explicitly stated — if not provided, ASK
- Valid services: `nsvppgregw`, `nsvppipsecgw`, `ecgw`, `steeringlb`

---

### Step 2: Pre-Deployment Safety Check

```bash
echo "========================================="
echo "PRE-DEPLOYMENT SAFETY CHECK"
echo "========================================="
echo "Checking for existing deployments..."

JENKINS_API_RESPONSE=$(curl -sg -u "${JENKINS_USERNAME}:${JENKINS_PROD_TOKEN}" \
  "${JENKINS_PROD_URL}/job/${JENKINS_JOB_PREFIX}_${SERVICE}/api/json?tree=builds[number,building,result,timestamp]{0,5}")

RUNNING_BUILDS=$(echo "$JENKINS_API_RESPONSE" | grep -o '"building":true' | wc -l)

if [ "$RUNNING_BUILDS" -gt 0 ]; then
  RUNNING_BUILD_NUM=$(echo "$JENKINS_API_RESPONSE" | grep -B 2 '"building":true' | grep '"number"' | head -1 | grep -oE '[0-9]+')
  echo "⚠️  Build #${RUNNING_BUILD_NUM} is already running for ${SERVICE}"
  echo ""
  echo "Do you want to:"
  echo "1) Monitor the existing build #${RUNNING_BUILD_NUM}"
  echo "2) Trigger a new deployment anyway (not recommended)"
  echo "3) Abort"
  # If 1: BUILD_NUMBER=$RUNNING_BUILD_NUM, SKIP_TRIGGER=true
  # If 2: SKIP_TRIGGER=false
  # If 3: ABORT
else
  echo "✅ No running builds — safe to trigger"
  SKIP_TRIGGER=false
fi
echo "========================================="
```

---

### Step 3: Display Deployment Details & Get Confirmation (MANDATORY)

Output the block below with REAL values — do NOT use placeholders:

```
========================================
IMMEDIATE PRODUCTION DEPLOYMENT
========================================
Service:      <service name, e.g. nsvppgregw>
Target POPs:  <pops in lowercase, e.g. del1,ams1>

Parameters:
  RELEASE:                  <version>
  ANSIBLE_CONFIG_IMAGE_TAG: <tag>
  TICKET:                   <ticket>
  Jenkins Job:              <JENKINS_JOB_PREFIX>_<service>
  Jenkins URL:              <JENKINS_PROD_URL>

⚠️  WARNING: This will IMMEDIATELY deploy to production!
⚠️  There is NO undo after confirmation.

Do you want to proceed with this deployment? (yes/no)
========================================
```

**WAIT for explicit "yes" — ABORT if "no".**

---

### Step 4: Trigger Jenkins Deployment

```bash
if [ "$SKIP_TRIGGER" = "true" ]; then
  echo "Using existing build #${BUILD_NUMBER}"
else
  # Final safety check immediately before triggering (Step 2 check may be stale)
  FINAL_CHECK=$(curl -sg -u "${JENKINS_USERNAME}:${JENKINS_PROD_TOKEN}" \
    "${JENKINS_PROD_URL}/job/${JENKINS_JOB_PREFIX}_${SERVICE}/api/json?tree=builds[number,building]{0,3}" | \
    grep -o '"building":true' | wc -l)
  if [ "$FINAL_CHECK" -gt 0 ]; then
    echo "❌ A build started after safety check — ABORTING to prevent duplicate"
    exit 1
  fi

  # Trigger via REST API — capture queue URL from Location header
  TRIGGER_RESPONSE=$(curl -sg -D - -o /dev/null -X POST \
    -u "${JENKINS_USERNAME}:${JENKINS_PROD_TOKEN}" \
    "${JENKINS_PROD_URL}/job/${JENKINS_JOB_PREFIX}_${SERVICE}/buildWithParameters" \
    --data-urlencode "POPS=${POPS}" \
    --data-urlencode "RELEASE=${RELEASE}" \
    --data-urlencode "ANSIBLE_CONFIG_IMAGE_TAG=${TAG}" \
    --data-urlencode "ANSIBLE_COMPONENT_NAME=${SERVICE}" \
    --data-urlencode "ANSIBLE_HOSTGROUPS=${SERVICE}" \
    --data-urlencode "ANSIBLE_CONFIG_IMAGE_NAME=${SERVICE}-ansible-config" \
    --data-urlencode "ANSIBLE_ARTIFACTORY_CHANNEL=ipsec-gre-production-docker" \
    --data-urlencode "TICKET=${TICKET}" \
    --data-urlencode "ANSIBLE_VERBOSITY=2" \
    --data-urlencode "ANSIBLE_CORE_VERSION=2.15" \
    --data-urlencode "REGIONS=America,APAC,Europe" \
    --data-urlencode "POP_TYPES=MP,DP,GCP,EKS" \
    --data-urlencode "BYPASS_MONITORING_RESULT=YES" \
    --data-urlencode "BYPASS_JIRA=YES" \
    --data-urlencode "RUN_QE_PDV=DEPLOY_ONLY" \
    --data-urlencode "DEPLOY_TYPE=DEPLOY" \
    --data-urlencode "SELECT_ALL_POPS=" \
    --data-urlencode "SELECT_ALL_COMPONENTS=")

  HTTP_CODE=$(echo "$TRIGGER_RESPONSE" | grep -oP '^HTTP/\S+ \K\d+' | tail -1)
  QUEUE_URL=$(echo "$TRIGGER_RESPONSE" | grep -i '^Location:' | awk '{print $2}' | tr -d '\r')

  # HTTP 201 or 303 = build queued successfully
  if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "303" ]; then
    echo "✅ Deployment triggered (HTTP $HTTP_CODE)"
    echo "   Queue URL: ${QUEUE_URL}"
  else
    echo "❌ Failed to trigger deployment (HTTP $HTTP_CODE) — ABORTING"
    exit 1
  fi

  # Poll queue until build number is assigned
  BUILD_NUMBER=""
  for i in $(seq 1 6); do
    sleep 5
    BUILD_NUMBER=$(curl -sg -u "${JENKINS_USERNAME}:${JENKINS_PROD_TOKEN}" \
      "${QUEUE_URL}api/json" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'executable' in d:
    print(d['executable']['number'])
" 2>/dev/null)
    [ -n "$BUILD_NUMBER" ] && break
  done

  if [ -z "$BUILD_NUMBER" ]; then
    echo "⚠️ Could not get build number from queue — falling back to latest build"
    BUILD_NUMBER=$(curl -sg -u "${JENKINS_USERNAME}:${JENKINS_PROD_TOKEN}" \
      "${JENKINS_PROD_URL}/job/${JENKINS_JOB_PREFIX}_${SERVICE}/api/json?tree=builds[number]{0,1}" | \
      python3 -c "import sys,json; print(json.load(sys.stdin)['builds'][0]['number'])")
  fi

  echo "Jenkins build #${BUILD_NUMBER} started"
  echo "URL: ${JENKINS_PROD_URL}/job/${JENKINS_JOB_PREFIX}_${SERVICE}/${BUILD_NUMBER}/"
fi
```

**Note**: Use the parameter list from `CONFIG.md` — add or remove `--data-urlencode` lines to match your pipeline exactly.

---

### Step 5: Monitor Deployment Progress

**⚠️ CRITICAL: Use `nohup ... &` shell backgrounding. Do NOT use `run_in_background: true` or `timeout:` on the Bash tool.**

```bash
# Step 5a: Launch background monitor
# Use `nohup env VAR=value bash -c '...'` to pass env vars into the subshell
nohup env JENKINS_USERNAME="${JENKINS_USERNAME}" JENKINS_PROD_TOKEN="${JENKINS_PROD_TOKEN}" bash -c '
  while true; do
    STATUS_JSON=$(curl -sg -u "${JENKINS_USERNAME}:${JENKINS_PROD_TOKEN}" \
      "'"${JENKINS_PROD_URL}"'/job/'"${JENKINS_JOB_PREFIX}"'_'"${SERVICE}"'/'"${BUILD_NUMBER}"'/api/json?tree=building,result")

    BUILDING=$(echo "$STATUS_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)[\"building\"])" 2>/dev/null)
    RESULT=$(echo "$STATUS_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get(\"result\",\"null\"))" 2>/dev/null)

    echo "[$(date -u +%H:%M:%S)] Building: $BUILDING | Result: $RESULT"

    if [ "$BUILDING" = "False" ]; then
      echo "DONE:$RESULT"
      break
    fi

    sleep 60
  done
' > /tmp/monitor_${BUILD_NUMBER}.log 2>&1 &
echo "Monitor started (PID: $!)"
```

```bash
# Step 5b: Poll the log every ~60s until "DONE:" appears
sleep 10
tail -20 /tmp/monitor_${BUILD_NUMBER}.log
# Repeat tail until output contains "DONE:"
```

---

### Step 6: Check Deployment Result

```bash
DEPLOY_RESULT=$(grep "^DONE:" /tmp/monitor_${BUILD_NUMBER}.log | cut -d: -f2)

if [ "$DEPLOY_RESULT" = "FAILURE" ]; then
  echo "❌ Deployment FAILED — follow SKILL-DEPLOYMENT-FAILURE.md"
  exit 0
fi

echo "✅ Deployment ${DEPLOY_RESULT} — Build #${BUILD_NUMBER}"
echo "URL: ${JENKINS_PROD_URL}/job/${JENKINS_JOB_PREFIX}_${SERVICE}/${BUILD_NUMBER}/"
```

If result is **FAILURE** → follow **SKILL-DEPLOYMENT-FAILURE.md**.
If result is **SUCCESS** or **UNSTABLE** → deployment complete.

---

## Jenkins Parameters Reference

**Job name and parameter list come from `CONFIG.md`** — do not use hardcoded values.

Read `CONFIG.md` to determine:
- The correct Jenkins job name for the requested service
- Which parameters to include (user-provided + derived + fixed)
- Which fixed parameters to omit (those not applicable to your pipeline)

Build the `curl --data-urlencode` command using exactly those parameters.

---

## Common Mistakes to Avoid

- ❌ Using hardcoded credentials instead of env vars
- ❌ Assuming or auto-detecting service type — user must explicitly state it
- ❌ Triggering without checking for running builds first
- ❌ Not validating HTTP response after trigger — HTTP 303 is also success (same as 201)
- ❌ Re-triggering after HTTP 303 — that means the build was already queued
- ❌ Using uppercase POPs in parameters — always lowercase
- ❌ Missing `ANSIBLE_COMPONENT_NAME` — causes immediate build failure
- ❌ Deploying without explicit user confirmation

## See Also
- `SKILL-DEPLOYMENT-FAILURE.md` — failure diagnosis and retry workflow
- `SKILL-PROD-SCHEDULED.md` — scheduled deployment workflow
