# Production PDV Testing Skill

## Metadata
- **Skill Name**: `prod_pdv`
- **Purpose**: Run PDV (Production Data Validation) on production POPs for VPP IPSEC/GRE gateways. Executes two Jenkins jobs: Job 1 (node 02) and Job 2 (node 01). **PDV pass/fail is determined solely by Jenkins job result.** Tunnel monitoring is optional and informational only. **MANDATORY: Always retry failed jobs at least once.**
- **Execution Type**: Jenkins CLI in **sync mode** (blocks until completion) + automatic retry

## Configuration
- **Jenkins Base URL**: http://your-jenkins-host:8080/
- **Jenkins Username**: your-username
- **API Token**: your-api-token
- **Jenkins CLI**: Pre-installed (use `java -jar jenkins-cli.jar` with `-http` flag)
- **Suites Location**: http://your-jenkins-host:8080/job/STEERING_JENKINS/job/STEERING_MANAGEMENT/job/DPAS_PDV_Regression_Suites/

## Supported Gateway Types
- VPP GRE
- VPP IPSEC

## Job Structure
```
Base Suite URL:
└── GRE_Suites/
    └── VPP_GRE_PDV_{POP}/  (e.g., VPP_GRE_PDV_AKL1, VPP_GRE_PDV_PHL1)
└── IPSec_Suites/
    └── VPP_IPSec_PDV_{POP}/  (e.g., VPP_IPSec_PDV_AKL1)

Note: POP names are case-insensitive
Note: Pipeline names start with VPP_GRE_PDV_ or VPP_IPSec_PDV_
```

---

## Execution Workflow

**IMPORTANT**: All Jenkins jobs use **sync mode** (`-s` flag). Jenkins CLI blocks and waits for job completion. **No separate monitoring or status polling is needed.**

### Job 1: First Test (Node 02)

#### Step 1.1: Trigger Job 1 (Sync Mode)
- **Job Path Pattern**:
  - GRE: `STEERING_JENKINS/STEERING_MANAGEMENT/DPAS_PDV_Regression_Suites/GRE_Suites/VPP_GRE_PDV_{POP}`
  - IPSEC: `STEERING_JENKINS/STEERING_MANAGEMENT/DPAS_PDV_Regression_Suites/IPSec_Suites/VPP_IPSec_PDV_{POP}`
- **Jenkins CLI Command (Sync Mode)**:
  ```bash
  java -jar jenkins-cli.jar -s http://your-jenkins-host:8080/ -http -auth your-username:your-api-token build "STEERING_JENKINS/STEERING_MANAGEMENT/DPAS_PDV_Regression_Suites/GRE_Suites/VPP_GRE_PDV_{POP}" -s -p public_ip=52.27.59.30 -p floating_ip=52.27.59.30 -p left_ip=172.31.29.183
  ```
  **Note**: The `-s` flag after `build` enables **sync mode** - Jenkins CLI will block and wait for job completion.

- **Parameters**:
  ```
  public_ip: 52.27.59.30
  floating_ip: 52.27.59.30
  left_ip: 172.31.29.183
  ```
- **Expected Duration**: 2-3 minutes
- **Target Gateway**: `nsvppgregw02.{pop}.nskope.net` (node 02)
- **Expected Tunnel Destination**: 52.27.59.30
- **Success Criteria**: Jenkins CLI exits with code 0 (success)

#### Step 1.2: Optional Tunnel Monitoring (Informational Only)
**NOTE**: This step is OPTIONAL and for informational purposes only. PDV pass/fail is determined solely by Jenkins job exit code.

**Login Command**:
```bash
tsh ssh --cluster {pop} nsvppgregw02.{pop}.nskope.net
```

**Monitoring Start Time**: 30 seconds after job starts

**Informational Checks**:
1. **Check for GRE tunnel** (optional):
   ```bash
   sudo vppctl show gre tunnel | grep 52.27.59.30
   ```
   - **Key Identifier**: Destination IP **52.27.59.30** (Job 1 tunnel)
   - **Expected Output Format**:
     ```
     [109] instance 261 src <gregw_vip> dst 52.27.59.30 fib-idx 0 sw-if-idx 122 payload L3 point-to-point
     ```
   - **Extract**: Interface name (e.g., `gre261`)

2. **Monitor RX/TX packets** (optional):
   ```bash
   sudo vppctl show interface {interface_name}
   ```
   - **Informational**: Check if tunnel is UP and RX/TX packets are incrementing
   - **Note**: This is for debugging/information only and does NOT affect PDV pass/fail status

---

### Job 2: Second Test (Node 01)

#### Step 2.1: Trigger Job 2 (Sync Mode)
- **Requirement**: Job 1 MUST complete successfully (exit code 0) before proceeding
- **Job Path**: Same as Job 1
- **Jenkins CLI Command (Sync Mode)**:
  ```bash
  java -jar jenkins-cli.jar -s http://your-jenkins-host:8080/ -http -auth your-username:your-api-token build "STEERING_JENKINS/STEERING_MANAGEMENT/DPAS_PDV_Regression_Suites/GRE_Suites/VPP_GRE_PDV_{POP}" -s -p public_ip=163.116.136.156 -p floating_ip=10.136.126.111 -p left_ip=198.18.99.254
  ```
  **Note**: The `-s` flag after `build` enables **sync mode** - Jenkins CLI will block and wait for job completion.

- **Parameters**:
  ```
  public_ip: 163.116.136.156
  floating_ip: 10.136.126.111
  left_ip: 198.18.99.254
  ```
- **Expected Duration**: 2-3 minutes
- **Target Gateway**: `nsvppgregw01.{pop}.nskope.net` (node 01)
- **Expected Tunnel Destination**: 163.116.136.156
- **Success Criteria**: Jenkins CLI exits with code 0 (success)

#### Step 2.2: Optional Tunnel Monitoring (Informational Only)
**NOTE**: This step is OPTIONAL and for informational purposes only. PDV pass/fail is determined solely by Jenkins job exit code.

**Login Command**:
```bash
tsh ssh --cluster {pop} nsvppgregw01.{pop}.nskope.net
```

**Monitoring Start Time**: 30 seconds after job starts

**Informational Checks**:
1. **Check for GRE tunnel** (optional):
   ```bash
   sudo vppctl show gre tunnel | grep 163.116.136.156
   ```
   - **Key Identifier**: Destination IP **163.116.136.156** (Job 2 tunnel)
   - **Expected Output Format**:
     ```
     [109] instance 261 src <gregw_vip> dst 163.116.136.156 fib-idx 0 sw-if-idx 122 payload L3 point-to-point
     ```
   - **Extract**: Interface name (e.g., `gre261`)

2. **Monitor RX/TX packets** (optional):
   ```bash
   sudo vppctl show interface {interface_name}
   ```
   - **Informational**: Check if tunnel is UP and RX/TX packets are incrementing
   - **Note**: This is for debugging/information only and does NOT affect PDV pass/fail status

---

## Success Criteria

### Overall Success
**PDV pass/fail is determined SOLELY by Jenkins CLI exit code:**
- ✅ Job 1 Jenkins CLI exits with code 0 (SUCCESS)
- ✅ Job 2 Jenkins CLI exits with code 0 (SUCCESS)

**IMPORTANT**: Tunnel monitoring is OPTIONAL and informational only. It does NOT affect PDV pass/fail status.

### Failure Conditions
- ❌ **Complete Failure**: Jenkins CLI exits with non-zero code (FAILURE/ABORTED/UNSTABLE)
- ❌ **Complete Failure**: Command timeout or error

**Note**: If Jenkins CLI exits with code 0, PDV is considered PASSED regardless of tunnel monitoring observations.

---

## Fallback: Handling Stuck Jenkins CLI (Rare Case)

### ⚠️ PRIMARY METHOD: Jenkins CLI Sync Mode

**CRITICAL**: Always use Jenkins CLI with `-s` sync mode for triggering and monitoring PDV jobs. This is the primary and preferred method.

### When to Use Fallback API Check

**ONLY use API fallback if Jenkins CLI sync mode hasn't returned after 6 minutes.**

**Why 6 minutes?**
- Expected PDV job duration: 2-3 minutes
- Buffer time for slow jobs: 3-4 minutes
- Total safe timeout: 6 minutes
- If CLI hasn't returned by then, it's likely stuck (not the job itself)

### Fallback Workflow

**Step 1: Wait for Natural Completion (0-6 minutes)**
```bash
# Jenkins CLI sync mode is blocking and waiting
java -jar jenkins-cli.jar -s http://your-jenkins-host:8080/ -http \
  -auth your-username:your-api-token \
  build "STEERING_JENKINS/.../VPP_GRE_PDV_{POP}" -s \
  -p public_ip=... -p floating_ip=... -p left_ip=...

# Let it complete naturally - DO NOT interrupt
```

**Step 2: Fallback Check (After 6 minutes)**

If Jenkins CLI hasn't returned after 6 minutes, check actual job status via API:

```bash
# Extract build number from CLI output (e.g., "Started ... #10")
BUILD_NUMBER=10

# Check job status via API
curl -s -u your-username:your-api-token \
  "http://your-jenkins-host:8080/job/STEERING_JENKINS/job/STEERING_MANAGEMENT/job/DPAS_PDV_Regression_Suites/job/GRE_Suites/job/VPP_GRE_PDV_{POP}/${BUILD_NUMBER}/api/json" \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"Status: {data['result']}\"); print(f\"Building: {data['building']}\")"
```

**Expected Output:**
```
Status: SUCCESS    # or FAILURE/UNSTABLE/ABORTED
Building: False    # Job completed
```

**Step 3: Handle Result**

```bash
# If job completed successfully (result=SUCCESS, building=False)
if [ "$RESULT" = "SUCCESS" ] && [ "$BUILDING" = "False" ]; then
  echo "✅ PDV Job completed successfully (detected via API fallback)"
  # Kill stuck CLI process if needed
  pkill -f "jenkins-cli.jar.*VPP_GRE_PDV_{POP}"
  # Continue with next job or report success
fi

# If job failed
if [ "$RESULT" != "SUCCESS" ] && [ "$BUILDING" = "False" ]; then
  echo "❌ PDV Job failed (detected via API fallback)"
  # Kill stuck CLI process if needed
  pkill -f "jenkins-cli.jar.*VPP_GRE_PDV_{POP}"
  # Apply retry policy
fi

# If still building (rare)
if [ "$BUILDING" = "True" ]; then
  echo "⏳ Job still running, wait another 2 minutes..."
  # Wait and check again
fi
```

### Important Notes

1. **Primary Method**: Always trigger via Jenkins CLI sync mode
2. **Let It Complete**: Wait for natural completion (6 minutes max)
3. **Fallback Only**: API check is safety mechanism for stuck CLI
4. **CLI Can Hang**: Sometimes CLI process hangs even though job completes
5. **Job Still Completes**: Stuck CLI doesn't affect actual job execution
6. **Kill Safely**: Only kill CLI process after confirming job status via API
7. **Never Use API for Triggering**: API is ONLY for status checking, NEVER for triggering

### Example: Complete Workflow with Fallback

```bash
POP="mil2"
TIMEOUT=360  # 6 minutes in seconds
START_TIME=$(date +%s)

# Trigger job in background to enable timeout check
java -jar jenkins-cli.jar -s http://your-jenkins-host:8080/ -http \
  -auth your-username:your-api-token \
  build "STEERING_JENKINS/STEERING_MANAGEMENT/DPAS_PDV_Regression_Suites/GRE_Suites/VPP_GRE_PDV_${POP}" -s \
  -p public_ip=163.116.136.156 \
  -p floating_ip=10.136.126.111 \
  -p left_ip=198.18.99.254 &

CLI_PID=$!

# Wait for CLI to complete or timeout
while kill -0 $CLI_PID 2>/dev/null; do
  ELAPSED=$(($(date +%s) - START_TIME))

  if [ $ELAPSED -gt $TIMEOUT ]; then
    echo "⚠️ Jenkins CLI stuck after 6 minutes, checking job status via API..."

    # Get build number from output
    BUILD_NUM=$(grep -oP 'Started.*#\K\d+' /tmp/pdv_output.log)

    # Check via API
    RESULT=$(curl -s -u your-username:your-api-token \
      "http://your-jenkins-host:8080/job/STEERING_JENKINS/job/STEERING_MANAGEMENT/job/DPAS_PDV_Regression_Suites/job/GRE_Suites/job/VPP_GRE_PDV_${POP}/${BUILD_NUM}/api/json" \
      | python3 -c "import sys, json; print(json.load(sys.stdin)['result'])")

    if [ "$RESULT" = "SUCCESS" ]; then
      echo "✅ Job completed successfully (CLI was stuck)"
      kill $CLI_PID
      exit 0
    elif [ "$RESULT" = "FAILURE" ]; then
      echo "❌ Job failed (CLI was stuck)"
      kill $CLI_PID
      exit 1
    fi
  fi

  sleep 5
done

# CLI completed naturally
wait $CLI_PID
EXIT_CODE=$?
echo "Jenkins CLI completed with exit code: $EXIT_CODE"
```

---

## Retry Policy

### ⚠️ MANDATORY RETRY RULE

**CRITICAL**: In case of PDV failure, **ALWAYS retry at least once** before marking as final failure.

### Retry Strategy - 3 Attempts with Smart Deferral

**NEW: Up to 3 attempts per job with intelligent retry timing**

#### Overview

Each PDV job (Job 1 and Job 2) gets **up to 3 attempts**:
1. **Attempt 1**: Initial execution
2. **Attempt 2**: Immediate retry after 30s (if attempt 1 fails)
3. **Attempt 3**: Deferred retry (if attempt 2 fails) - timing depends on context

#### Retry Execution Flow

**Phase 1: Immediate Retries (Attempts 1 & 2)**

```bash
# Attempt 1
java -jar jenkins-cli.jar ... -s
EXIT_CODE_1=$?

if [ $EXIT_CODE_1 -ne 0 ]; then
  echo "❌ Attempt 1 FAILED - Retrying in 30 seconds..."
  sleep 30

  # Attempt 2 (immediate retry)
  java -jar jenkins-cli.jar ... -s
  EXIT_CODE_2=$?

  if [ $EXIT_CODE_2 -eq 0 ]; then
    echo "✅ Attempt 2 PASSED (retry successful)"
    # Success - continue
  else
    echo "❌ Attempt 2 FAILED - Deferring 3rd attempt"
    # Add to deferred retry queue
    add_to_retry_queue "$POP" "$JOB_NUM" "$NODE"
  fi
else
  echo "✅ Attempt 1 PASSED"
fi
```

**Phase 2: Deferred 3rd Retry**

If both attempts 1 and 2 fail, defer the 3rd retry based on context:

**Rule 1: Multi-POP Deployment**
- Add failed job to retry queue
- Continue PDV testing on other POPs
- After ALL other POPs complete their PDV → Execute 3rd retry

**Rule 2: Single POP or Last Job**
- No other POPs to process
- Wait 5 minutes (allows system to stabilize)
- Execute 3rd retry immediately after wait

#### Smart Retry - Job-Specific Tracking

**CRITICAL**: Only retry the specific job that failed. Do NOT re-run jobs that already passed.

**Example:**
```
MIL2 PDV:
  Job 1 (Node 02): ✅ PASSED on attempt 1
  Job 2 (Node 01): ❌ FAILED on attempts 1 & 2

3rd Retry Queue: MIL2 - Job 2 only
DO NOT re-run: MIL2 - Job 1 (already passed)
```

#### Detailed Retry Logic

**1. When to Trigger Attempt 2 (Immediate)**:
   - ❌ Attempt 1: Jenkins CLI exits with non-zero code
   - ❌ Attempt 1: Command timeout or error
   - ⏱️ Wait: 30 seconds
   - 🔄 Action: Retry same job with identical parameters

**2. When to Trigger Attempt 3 (Deferred)**:
   - ❌ Attempt 2: Jenkins CLI exits with non-zero code
   - ❌ Attempt 2: Command timeout or error
   - 📋 Action: Add to deferred retry queue

   **Deferral Decision Tree:**
   ```
   Is this a multi-POP deployment?
   ├─ YES → Are there more POPs to process?
   │         ├─ YES → Defer until all POPs complete
   │         └─ NO  → This is the last POP → Wait 5 min, retry
   └─ NO  → Single POP → Wait 5 min, retry
   ```

**3. Executing Deferred 3rd Retry**:

```bash
# After all POPs processed OR 5-minute wait elapsed
for failed_job in retry_queue; do
  POP="${failed_job[pop]}"
  JOB_NUM="${failed_job[job_num]}"
  NODE="${failed_job[node]}"

  echo "🔄 3rd Retry: $POP - Job $JOB_NUM ($NODE)"
  echo "Waiting 5 minutes for system stabilization..."
  sleep 300

  # Attempt 3 (final retry)
  java -jar jenkins-cli.jar ... -s
  EXIT_CODE_3=$?

  if [ $EXIT_CODE_3 -eq 0 ]; then
    echo "✅ Attempt 3 PASSED (final retry successful)"
  else
    echo "❌ Attempt 3 FAILED - All retries exhausted"
    echo "FINAL RESULT: FAILURE after 3 attempts"
  fi
done
```

**4. Success After Any Retry**:
   - Mark overall PDV as SUCCESS if any attempt (2 or 3) passes
   - Document all attempts in report
   - Note: Failures followed by successful retries are expected and acceptable

**5. Final Failure Criteria**:
   - ONLY mark as final failure if ALL 3 attempts fail:
     - Attempt 1: FAILED
     - Attempt 2: FAILED (immediate retry)
     - Attempt 3: FAILED (deferred retry)
   - Report all 3 attempts with detailed failure information
   - Escalate for manual investigation

#### Example Scenarios

**Scenario 1: Multi-POP with Deferred Retry**

```
PDV Execution Order:

1. MIL2 PDV:
   - Job 1 (Node 02): ✅ Attempt 1 PASSED
   - Job 2 (Node 01): ❌ Attempt 1 FAILED → ❌ Attempt 2 FAILED
   - Add to queue: MIL2-Job2

2. HEL1 PDV:
   - Job 1 (Node 02): ✅ Attempt 1 PASSED
   - Job 2 (Node 01): ✅ Attempt 1 PASSED

3. PRG1 PDV:
   - Job 1 (Node 02): ✅ Attempt 1 PASSED
   - Job 2 (Node 01): ✅ Attempt 1 PASSED

4. All POPs Complete → Process Retry Queue:
   - Wait 5 minutes
   - MIL2 Job 2: ✅ Attempt 3 PASSED

Final Result: All POPs PASSED
```

**Scenario 2: Single POP with Immediate 5-Min Wait**

```
PDV Execution Order:

1. MIL2 PDV (Single POP):
   - Job 1 (Node 02): ✅ Attempt 1 PASSED
   - Job 2 (Node 01): ❌ Attempt 1 FAILED → ❌ Attempt 2 FAILED
   - No other POPs → Wait 5 minutes immediately
   - Job 2: ✅ Attempt 3 PASSED

Final Result: MIL2 PASSED
```

**Scenario 3: Last Job in Multi-POP Fails**

```
PDV Execution Order:

1. MIL2 PDV: ✅ Both jobs PASSED
2. HEL1 PDV: ✅ Both jobs PASSED
3. PRG1 PDV (Last POP):
   - Job 1 (Node 02): ✅ Attempt 1 PASSED
   - Job 2 (Node 01): ❌ Attempt 1 FAILED → ❌ Attempt 2 FAILED
   - This is the last POP → Wait 5 minutes immediately
   - Job 2: ✅ Attempt 3 PASSED

Final Result: All POPs PASSED
```

**Scenario 4: Multiple Failures Across POPs**

```
PDV Execution Order:

1. MIL2 PDV:
   - Job 1: ✅ PASSED
   - Job 2: ❌ Fail × 2 → Queue: MIL2-Job2

2. HEL1 PDV:
   - Job 1: ✅ PASSED
   - Job 2: ✅ PASSED

3. PRG1 PDV:
   - Job 1: ✅ PASSED
   - Job 2: ❌ Fail × 2 → Queue: PRG1-Job2

4. All POPs Complete → Process Retry Queue:
   - Wait 5 minutes
   - MIL2 Job 2: ✅ Attempt 3 PASSED
   - Wait 5 minutes
   - PRG1 Job 2: ❌ Attempt 3 FAILED (final)

Final Result:
  - MIL2: PASSED (after 3rd retry)
  - HEL1: PASSED
  - PRG1: PARTIAL (Job 1 passed, Job 2 failed all 3 attempts)
```

#### Implementation Notes

**Tracking Failed Jobs:**
```python
# Retry queue structure
retry_queue = [
    {
        "pop": "MIL2",
        "job_num": 2,
        "node": "Node 01",
        "dest_ip": "163.116.136.156",
        "parameters": {...},
        "attempt_1_build": 8,
        "attempt_2_build": 9
    }
]
```

**Never Re-Run Passed Jobs:**
```bash
# WRONG - Re-running entire POP
run_pdv_for_pop "MIL2"  # This runs both Job 1 and Job 2

# CORRECT - Only retry failed job
run_pdv_job "MIL2" "Job 2" "Node 01" "163.116.136.156"
```

### Retry Rationale

PDV tests involve multiple systems (Jenkins, test clients, gateways, network infrastructure). Transient failures are common due to:
- Test client infrastructure issues
- Timing/synchronization problems
- Network hiccups
- Tunnel teardown timing

**Historical Data**:
- Job 1 (node 02): 100% first-attempt success rate across deployments
- Job 2 (node 01): ~67% first-attempt success, ~100% success after single retry
- Retries typically resolve transient issues without requiring gateway fixes

### Example Retry Workflow - Simple Case

```
Job 2 fails on first attempt but passes on 2nd:
1. Attempt 1: Jenkins CLI exits with non-zero code (Build #8 FAILED)
2. Record failure details
3. Wait 30 seconds
4. Attempt 2: Trigger retry with same parameters (using -s sync mode)
5. Attempt 2: Jenkins CLI exits with code 0 (Build #9 SUCCESS)
6. Mark overall result as SUCCESS with retry annotation
7. Document both attempts in report
8. No 3rd retry needed
```

### Example Retry Workflow - Deferred 3rd Retry

```
Multi-POP scenario - Job 2 fails twice on MIL2:
1. MIL2 Job 2 Attempt 1: FAILED (Build #8)
2. Wait 30 seconds
3. MIL2 Job 2 Attempt 2: FAILED (Build #9)
4. Add MIL2-Job2 to retry queue
5. Continue with HEL1 PDV (both jobs pass)
6. Continue with PRG1 PDV (both jobs pass)
7. All POPs complete → Process retry queue
8. Wait 5 minutes for system stabilization
9. MIL2 Job 2 Attempt 3: SUCCESS (Build #10)
10. Mark MIL2 as SUCCESS with 3-attempt annotation
11. Document all 3 attempts in report
```

---

## Safety and Constraints

### ⚠️ CRITICAL RULES
1. **DO NOT** run any commands except those explicitly mentioned above
2. **DO NOT** attempt to fix or troubleshoot failures
3. **DO NOT** modify any configuration
4. **DO NOT** delete anything
5. **ONLY** monitor and validate using specified commands

### If Failure Occurs
- **FIRST**: Apply the mandatory 3-attempt retry policy (see Retry Policy section)
  - Attempt 2: Immediate retry after 30 seconds
  - Attempt 3: Deferred retry (after all POPs OR 5-minute wait)
- **Report the failure** with details from all attempts (up to 3 attempts)
- **DO NOT** attempt remediation beyond the 3 retries
- **Escalate** to user for manual investigation only if all 3 attempts fail
- **Smart Retry**: Only retry the specific failed job, not jobs that already passed

---

## Gateway Node Mapping

| POP | Gateway Type | Node 01 (Custom) | Node 02 (Default) |
|-----|--------------|------------------|-------------------|
| Any | VPP GRE      | nsvppgregw01.{pop}.nskope.net | nsvppgregw02.{pop}.nskope.net |
| Any | VPP IPSEC    | nsvppipsecgw01.{pop}.nskope.net | nsvppipsecgw02.{pop}.nskope.net |

---

## Monitoring Reference

| Job   | Target Node | Tunnel Destination IP | Grep Command | Parameters |
|-------|-------------|----------------------|--------------|------------|
| Job 1 | Node 02     | **52.27.59.30**      | `grep 52.27.59.30` | public_ip=52.27.59.30<br>floating_ip=52.27.59.30<br>left_ip=172.31.29.183 |
| Job 2 | Node 01     | **163.116.136.156**  | `grep 163.116.136.156` | public_ip=163.116.136.156<br>floating_ip=10.136.126.111<br>left_ip=198.18.99.254 |

**Key Point**: We only care about the **destination IP** on the gateway tunnel, NOT the source IP.
- Job 1 creates tunnel to destination **52.27.59.30** on node 02
- Job 2 creates tunnel to destination **163.116.136.156** on node 01

---

## Example Execution Flow

```
User Request: "Run VPP GRE DPAS PDV on POP akl1"

1. Identify: Gateway Type = GRE, POP = akl1

2. Job 1 (Node 02 - dst 52.27.59.30):
   - Trigger: Jenkins CLI with -s sync mode flag
   - Parameters: public_ip=52.27.59.30, floating_ip=52.27.59.30, left_ip=172.31.29.183
   - Wait: Jenkins CLI blocks until job completes (2-3 minutes)
   - Result: Exit code 0 → Job 1 PASSED
   - Optional: Monitor tunnel on gateway for informational purposes

3. Job 2 (Node 01 - dst 163.116.136.156):
   - Trigger: Jenkins CLI with -s sync mode flag
   - Parameters: public_ip=163.116.136.156, floating_ip=10.136.126.111, left_ip=198.18.99.254
   - Wait: Jenkins CLI blocks until job completes (2-3 minutes)
   - Result: Exit code 0 → Job 2 PASSED
   - Optional: Monitor tunnel on gateway for informational purposes

4. Report: PDV SUCCESS (both Jenkins jobs passed)
```

---

## Notes
- All POPs have 2 VPP IPSEC nodes and 2 VPP GRE nodes
- Job 1 tests node 02 (default node)
- Job 2 tests node 01 (custom node)
- **CRITICAL - Sync Mode Usage**:
  - **Always use `-s` flag after `build` command for sync mode**
  - Jenkins CLI blocks and waits for job completion (2-3 minutes)
  - No separate monitoring or polling needed
  - Exit code 0 = SUCCESS, non-zero = FAILURE
- **CRITICAL - PDV Pass/Fail Criteria**:
  - **PDV result is determined SOLELY by Jenkins CLI exit code**
  - Exit code 0 → PDV PASSED
  - Non-zero exit code → PDV FAILED
  - Tunnel monitoring is OPTIONAL and for informational/debugging purposes only
- **Optional Tunnel Monitoring**:
  - Can optionally monitor destination IP in GRE tunnel output:
    - Job 1: Look for `dst 52.27.59.30` on node 02
    - Job 2: Look for `dst 163.116.136.156` on node 01
  - Can optionally check RX/TX traffic counters on tunnel interface
  - These checks do NOT affect PDV pass/fail status
  - Useful for debugging if Jenkins passes but issues suspected
- **MANDATORY - Retry Policy (3 Attempts)**:
  - **Up to 3 attempts per job**: Attempt 1 → Attempt 2 (immediate, 30s) → Attempt 3 (deferred)
  - **Attempt 2**: Immediate retry after 30 seconds if attempt 1 fails
  - **Attempt 3**: Deferred retry - execute after all POPs complete (multi-POP) OR after 5-minute wait (single POP/last job)
  - **Smart Retry**: Only retry the specific job that failed (don't re-run jobs that passed)
  - **Success Rate**: ~67% pass on attempt 1, ~95% pass by attempt 2, ~99% pass by attempt 3
  - Only escalate if ALL 3 attempts fail
  - See "Retry Policy" section for complete details and scenarios
