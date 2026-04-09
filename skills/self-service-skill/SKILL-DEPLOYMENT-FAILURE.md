name: deployment-failure-handling
description: What to do when a Jenkins deployment build returns FAILURE — failure analysis, per-POP/host diagnosis, and retry workflow.

# Deployment Failure Handling

## When This Applies

Invoked when the Jenkins deployment build finishes with result = **FAILURE**.

Note: **UNSTABLE** does NOT trigger this — UNSTABLE means partial success and the normal post-deployment flow continues.

---

## CRITICAL RULES

- **NEVER auto-retry** without explicit user permission
- **NEVER rerun the full job** if only some POPs failed — retry only the failed POPs
- **Always diagnose before asking** — fetch console log, identify failed hosts/POPs and reason, THEN present findings

---

## Step-by-Step Failure Workflow

### Step 1: Fetch Jenkins Console Log

```bash
# Add --max-time 120 to prevent indefinite hangs on large logs
curl -sg --max-time 120 --connect-timeout 15 \
  -u "${JENKINS_USERNAME}:${JENKINS_PROD_TOKEN}" \
  "${JENKINS_PROD_URL}/job/${JENKINS_JOB_PREFIX}_${SERVICE}/${BUILD_NUMBER}/consoleText" \
  -o /tmp/console_${BUILD_NUMBER}.log

echo "Log size: $(wc -l < /tmp/console_${BUILD_NUMBER}.log) lines"
```

The `/consoleText` endpoint returns the full log (Jenkins UI may show a truncated view — ignore that).

---

### Step 2: Identify Failed POPs and Hosts

Parse the console log to find which POPs and hosts failed:

```bash
# Find Ansible host failures
FAILED_HOSTS=$(grep -oP 'fatal: \[\K[^\]]+(?=\]: FAILED)' /tmp/console_${BUILD_NUMBER}.log | sort -u)

# Count "NO MORE HOSTS LEFT" occurrences (all hosts in a group unreachable)
NO_MORE_HOSTS=$(grep -c "NO MORE HOSTS LEFT" /tmp/console_${BUILD_NUMBER}.log)
```

**Parse PLAY RECAP for per-host status:**

```bash
grep -A 100 "PLAY RECAP" /tmp/console_${BUILD_NUMBER}.log | grep -v "^$\|PLAY RECAP" | while read line; do
  HOST=$(echo "$line" | awk '{print $1}')
  FAILED=$(echo "$line" | grep -oP 'failed=\K\d+')
  UNREACHABLE=$(echo "$line" | grep -oP 'unreachable=\K\d+')
  OK=$(echo "$line" | grep -oP 'ok=\K\d+')

  # Extract POP from hostname — adjust pattern to match your hostname format
  # Example: nsvppipsecgw01.sfo1.company.com → sfo1
  POP=$(echo "$HOST" | grep -oP '\.\K[a-z]{2,4}\d+(?=\.)')

  if [ "$FAILED" -gt 0 ] || [ "$UNREACHABLE" -gt 0 ]; then
    echo "FAILED: $HOST (POP: $POP) — failed=$FAILED unreachable=$UNREACHABLE"
  elif [ "$OK" -gt 0 ]; then
    echo "PASSED: $HOST (POP: $POP)"
  fi
done
```

**Note**: Update the hostname-to-POP extraction pattern to match your infrastructure's hostname format.

---

### Step 3: Identify Failure Reason

```bash
grep -i "unreachable\|Permission denied\|publickey\|Connection closed\|kex_exchange" /tmp/console_${BUILD_NUMBER}.log | tail -5
grep -i "artifactory\|Connection failed\|Unable to fetch\|rpc error.*docker\|unknown blob" /tmp/console_${BUILD_NUMBER}.log | tail -5
grep -i "vault\|timed out.*kms\|connect timeout" /tmp/console_${BUILD_NUMBER}.log | tail -5
grep -i "Version did not increase\|NO MORE HOSTS LEFT\|postdeploy.*ERROR\|fatal.*FAILED" /tmp/console_${BUILD_NUMBER}.log | tail -10
```

**Common Error Patterns:**

| Error Pattern | Reason | Retry Safe? |
|---------------|--------|-------------|
| `Permission denied (publickey)` / `Authorized access only` | Ansible SSH auth failure — deploy key rejected | Yes, or raise ops ticket if persists |
| `Connection closed` / `kex_exchange_identification` | SSH key/host issue | Check host availability, retry |
| `Connection timed out` / `SSH timeout` | Host slow or unreachable | Check host is up, retry |
| `Artifactory` + `Connection failed` / `Unable to fetch` | Artifact download timeout | Retry |
| `rpc error.*docker` / `unknown blob` | Container image pull failure | Retry, validate artifact exists |
| `vault` + `timeout` / `connect timeout.*kms` | Secrets/vault connectivity issue | Retry |
| `Version did not increase` | Host already at target version or downgrade attempted | Investigate version mismatch |
| `NO MORE HOSTS LEFT` | All hosts in POP unreachable | Check POP health |
| `postdeploy.*ERROR` | Post-deploy script failed | Check logs, may need manual intervention |

---

### Step 4: Present Findings to User

Display the analysis block — do NOT take any action yet. Fill in all real values:

```
========================================
DEPLOYMENT FAILURE ANALYSIS
========================================
Build:   #<build_number>
Service: <service>
URL:     <JENKINS_PROD_URL>/job/<JENKINS_JOB_PREFIX>_<service>/<build_number>/

FAILED POPs / Hosts:
  • <pop1>: <host1>, <host2> — <reason>
  • <pop2>: ALL HOSTS — unreachable

PASSED POPs / Hosts:
  • <pop3>: <host1>, <host2> — deployed successfully

Failure Reason: <e.g., Ansible SSH timeout — hosts unreachable>

Recommended Next Steps:
  1. <e.g., Check that target hosts are up and SSH is accessible>
  2. <e.g., Retry deployment on failed POPs only: <pop1>, <pop2>>
  3. <e.g., If retry fails, open a support ticket with the build URL and error snippet>

Do you want to retry the deployment on the failed POPs (<pop1>, <pop2>)? (yes/no)
========================================
```

---

### Step 5: Handle User's Retry Decision

**WAIT for explicit user response before retrying.**

#### If user says YES:

Trigger a **new Jenkins build** with ONLY the failed POPs:

```bash
# Only failed POPs — NOT the full original list
FAILED_POPS="<pop1>,<pop2>"   # lowercase, comma-separated

TRIGGER_RESPONSE=$(curl -sg -D - -o /dev/null -X POST \
  -u "${JENKINS_USERNAME}:${JENKINS_PROD_TOKEN}" \
  "${JENKINS_PROD_URL}/job/${JENKINS_JOB_PREFIX}_${SERVICE}/buildWithParameters" \
  --data-urlencode "POPS=${FAILED_POPS}" \
  --data-urlencode "RELEASE=${RELEASE}" \
  --data-urlencode "ANSIBLE_CONFIG_IMAGE_TAG=${TAG}" \
  --data-urlencode "ANSIBLE_COMPONENT_NAME=${SERVICE}" \
  --data-urlencode "ANSIBLE_HOSTGROUPS=${SERVICE}" \
  --data-urlencode "ANSIBLE_CONFIG_IMAGE_NAME=${SERVICE}-ansible-config" \
  # Add remaining parameters from CONFIG.md (fixed production parameters)
  # Use the same parameter list as the original deployment trigger
  )

HTTP_CODE=$(echo "$TRIGGER_RESPONSE" | grep -oP '^HTTP/\S+ \K\d+' | tail -1)
echo "Retry triggered for: ${FAILED_POPS} (HTTP $HTTP_CODE)"
```

Then follow the standard monitoring workflow (Steps 5–6 of SKILL-PROD-IMMEDIATE.md) for this retry build.

**After retry completes, output a clear final status:**
```
✅ Retry build #<N> completed — STATUS: SUCCESS
❌ Retry build #<N> FAILED — see console for details
```

- If SUCCESS/UNSTABLE: deployment complete
- If FAILURE again: present a second failure analysis and ask user what to do next

#### If user says NO:

- Do not trigger any new build
- Note which POPs were not retried in your summary

---

### Step 6: Update State File (Scheduled Deployments Only)

Mark failed POPs in the state file — passed POPs keep their SUCCESS status. Continue to the next scheduled slot.

```bash
jq ".slots[${SLOT_NUM}].status = \"PARTIAL_FAILURE\" | .slots[${SLOT_NUM}].failed_pops = \"${FAILED_POPS}\"" \
  /tmp/scheduled_deployment_${TICKET}.json \
  > /tmp/tmp_state_${TICKET}.json && mv /tmp/tmp_state_${TICKET}.json /tmp/scheduled_deployment_${TICKET}.json
```

**Do NOT abort remaining scheduled slots due to a partial failure in one slot.**

---

## Summary Table

| Action | On FAILURE |
|--------|-----------|
| Auto-retry | ❌ NEVER — always ask user first |
| Fetch console log | ✅ Immediately |
| Identify failed POPs/hosts | ✅ Parse PLAY RECAP + fatal errors |
| Identify failure reason | ✅ Match to error pattern table |
| Present findings | ✅ Show full analysis, then ask yes/no |
| Retry scope | Only failed POPs — never the full POP list |
| Next scheduled slot | Continue regardless of failure |
