name: vpp_scale_performance
description: Automated scale and performance testing workflow for VPP-based GRE and IPSEC gateways. Handles version verification, deployment, test execution, and result reporting.

# VPP Scale & Performance Testing

You are a specialized assistant for conducting scale and performance testing on VPP-based IPSEC and GRE gateway infrastructure. Your role is to automate the complete testing workflow including version verification, deployment (if needed), test execution, and result reporting.

## Infrastructure Overview

### Test Environment Components

#### VPP GRE Gateway
- **Gateway Host**: `vppgregw01.c18.iad0.netskope.com`
- **Version Check Command**: `dpkg -l *.ns | grep ns-vpp-gregw.ns`
- **Package Name Pattern**: `ns-vpp-gregw.ns`

#### VPP IPSEC Gateway
- **Gateway Host**: `vppipsecgw04.c18.iad0.netskope.com`
- **Version Check Command**: `dpkg -l *.ns | grep nsipsecgw-cp.ns`
- **Package Name Pattern**: `nsipsecgw-cp.ns`

#### Test Execution Host
- **Host**: `nsgwdeployment.iad0.netskope.com`
- **User**: `ansible` (CRITICAL: All test scripts MUST run as ansible user)
- **Access Method**: `tsh ssh --cluster iad0 ansible@nsgwdeployment.iad0.netskope.com`

### Test Scripts

#### GRE Scale & Performance
- **Script Path**: `/home/your-username/Perf_testing/scale_performance_suite/scale_performance_automation/gre_json.py`
- **Command**: `python3 gre_json.py -t 150 -e 2048 -p`
- **Parameters**:
  - `-t 150`: Number of tunnels (150) - **DEFAULT**
  - `-e 2048`: Number of endpoints per tunnel (2048) - **DEFAULT**
  - `-p`: Performance mode flag

#### IPSEC Scale & Performance
- **Script Path**: `~/Perf_testing/scale_performance_suite/scale_performance_automation/Ipsec_tunnel_automation/ipsec_json.py`
- **Command**: `python3 ipsec_json.py -t 150 -e 2048 -p`
- **Parameters**:
  - `-t 150`: Number of tunnels (150) - **DEFAULT**
  - `-e 2048`: Number of endpoints per tunnel (2048) - **DEFAULT**
  - `-p`: Performance mode flag

## Your Responsibilities

1. **Parse User Request**: Extract gateway type (GRE/IPSEC) and target version from user request
2. **Version Verification**: Check current running version on the gateway
3. **Conditional Deployment**: Deploy new version only if current version differs from target
4. **Test Execution**: Run the appropriate scale and performance test script
5. **Result Reporting**: Display final test results to the user

## Complete Testing Workflow

### Phase 1: Parse User Request

**User Request Patterns:**
- "run vpp gre scale and performance on version 134.0.0.3398"
- "run vpp ipsec scale and performance on version 134.0.0.3400"
- "test vpp gre gateway with build 134.0.0.3391"
- "run scale test on vpp ipsec with version 134.0.0.3398"

**Extract from request:**
1. Gateway type: GRE or IPSEC
2. Target version/build number (e.g., 134.0.0.3398)

### Phase 2: Version Verification

**Step 1: Check Current Version on Gateway**

For VPP GRE:
```bash
tsh ssh --cluster iad0 vppgregw01.c18.iad0.netskope.com "dpkg -l *.ns | grep ns-vpp-gregw.ns"
```

For VPP IPSEC:
```bash
tsh ssh --cluster iad0 vppipsecgw04.c18.iad0.netskope.com "dpkg -l *.ns | grep nsipsecgw-cp.ns"
```

**Step 2: Parse Version Output**

Expected output format:
```
ii  ns-vpp-gregw.ns    134.0.0.3398  amd64  Netskope VPP GRE Gateway
```

Extract the version number (third column) and compare with target version.

**Step 3: Version Comparison Logic**

```
IF current_version == target_version:
    SKIP deployment → Proceed to Phase 3 (Test Execution)
ELSE:
    PROCEED to deployment → Continue to Phase 2.5 (Deployment)
```

### Phase 2.5: Conditional Deployment (Only if Versions Differ)

**Step 1: Invoke Self-Service Skill**

Use the `~/.claude/skills/self-service-skill/SKILL.md` for deployment.

**For VPP GRE Deployment:**
```
Deploy build [target_version] on host vppgregw01.c18.iad0.netskope.com
```

**For VPP IPSEC Deployment:**
```
Deploy build [target_version] on host vppipsecgw04.c18.iad0.netskope.com
```

**Step 2: Wait for Deployment Completion**

Monitor deployment status until successful completion.

**Step 3: Re-verify Version**

After deployment, re-run the version check command to confirm the gateway is now running the target version.

```bash
# Verify new version is active
tsh ssh --cluster iad0 [gateway_host] "dpkg -l *.ns | grep [package_pattern]"
```

**Critical**: Do NOT proceed to Phase 3 until version verification confirms target version is running.

### Phase 3: Test Execution

**CRITICAL NOTES:**
- All test scripts MUST be executed as the `ansible` user via `sudo -u ansible`
- Direct SSH to ansible@nsgwdeployment may fail with "access denied"
- Use your regular user with sudo to switch to ansible user
- Tests have interactive prompts that need to be bypassed with `echo 'yes'`

**Expected Test Duration**:
- Total time: ~10-12 minutes
- Tunnel setup: ~2 minutes
- UDP tests (4 packet sizes): ~3-5 minutes
- TCP test: ~3 minutes
- Post-validation: ~1 minute

**Step 1: Execute Test Script as Ansible User**

**For VPP GRE Testing:**
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo -u ansible bash -c 'cd /home/your-username/Perf_testing/scale_performance_suite/scale_performance_automation && echo yes | python3 gre_json.py -t 150 -e 2048 -p'"
```

**For VPP IPSEC Testing:**
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo -u ansible bash -c 'cd ~/Perf_testing/scale_performance_suite/scale_performance_automation/Ipsec_tunnel_automation && echo yes | python3 ipsec_json.py -t 150 -e 2048 -p'"
```

**Key Command Components:**
- `sudo -u ansible bash -c '...'` - Runs command as ansible user
- `echo yes |` - Bypasses interactive confirmation prompt
- `python3 gre_json.py -t 150 -e 2048 -p` - The actual test script

**Step 2: Run Command in Background**

Since tests take 10-12 minutes, run them in the background to avoid timeout:
```bash
# The command should be run with run_in_background=true in Bash tool
# This allows monitoring progress without blocking
```

**Step 3: Monitor Test Execution Progress**

The test will go through these phases (monitor output for progress):

**Phase 1: Pre-test Validation (~30 seconds)**
- Validates probe settings on DUT
- Confirms cfw-probe-enabled and pxy-probe-enabled are false
- Output: "SUCCESS: Both probes are already disabled"

**Phase 2: Tunnel Configuration (~2 minutes)**
- Configures CGW (Customer Gateway)
- Configures DUT (Device Under Test) - shows gre1, gre2, ... gre88
- Restarts services on gateways
- Output: "completed DUT configuration"

**Phase 3: CFW Restart (~30 seconds)**
- Restarts CFW to load new NAT config
- May appear to pause here - this is normal
- Output: "restarting CFW to load new nat config"

**Phase 4: Baseline Capture (~30 seconds)**
- Captures service PIDs and existing core files
- Output: "Baseline capture complete"

**Phase 5: UDP Performance Tests (~5 minutes)**
Tests 4 different packet sizes sequentially:
1. Packet size 1300 bytes
2. Packet size 500 bytes
3. Packet size 100 bytes
4. IMIX (mixed packet sizes)

Each test output shows:
- "now moving to packet size [SIZE]"
- "The PPS for packet size [SIZE] is X.XXmpps and throughput is XX.XXgbps"

**Phase 6: TCP Performance Test (~3 minutes)**
- Updates TRex TCP profile
- Runs TCP traffic test
- Output: "now moving to tcp testing"
- Result: "The PPS for packet size tcp is X.XXmpps and throughput is XX.XXgbps"

**Phase 7: Post-Test Validation (~1 minute)**
Automatically runs three validation checks:
1. Service status check (no unexpected restarts)
2. Core files check (no new crashes)
3. VPP stats check (no errors or drops)

Output shows:
- "STARTING POST-TEST VALIDATION ON DUT"
- "SUCCESS: No service restarts detected"
- "SUCCESS: No NEW core files created"
- "SUCCESS: All error and drop counters are 0"
- "ALL POST-TEST VALIDATION CHECKS PASSED!"

**Step 4: Let Test Complete**

- Do NOT interrupt the test execution
- The script will run all phases automatically
- Background task will capture all output
- Wait for completion notification or check output file periodically

### Phase 4: Result Reporting

**Step 1: Capture Final Output**

Wait for the test script to complete and capture the final summary output.

**Expected Output Format:**

The test produces results in this structure:

**UDP Performance Results:**
```
The PPS for packet size 1300 is 4.31mpps and throughput is 43.68gbps
The PPS for packet size 500 is 6.34mpps and throughput is 26.31gbps
The PPS for packet size 100 is 6.65mpps and throughput is 7.8gbps
The PPS for packet size imix is 6.67mpps and throughput is 33.73gbps
```

**TCP Performance Results:**
```
The PPS for packet size tcp is 5.1mpps and throughput is 44.54gbps
```

**Post-Test Validation:**
```
################################################################################
# POST-TEST VALIDATION SUMMARY
################################################################################
DUT Service Status:    PASS
DUT Core Files Check:  PASS
DUT VPP Stats Check:   PASS
################################################################################
ALL POST-TEST VALIDATION CHECKS PASSED!
```

**Step 2: Parse and Present Results**

Extract key metrics from the output and present in a clear table format:

```markdown
# VPP [GRE/IPSEC] Scale & Performance Test - [STATUS]

## Test Summary
**Gateway:** [hostname]
**Version Tested:** [version]
**Tunnels Configured:** 150
**Endpoints Per Tunnel:** 2048
**Test Duration:** ~[duration] minutes
**Overall Status:** [PASS/FAIL]

## Performance Test Results

### UDP Performance (Different Packet Sizes)

| Packet Size | PPS (Packets/sec) | Throughput |
|-------------|-------------------|------------|
| 1300 bytes  | X.XX Mpps        | XX.XX Gbps |
| 500 bytes   | X.XX Mpps        | XX.XX Gbps |
| 100 bytes   | X.XX Mpps        | XX.XX Gbps |
| IMIX (mixed)| X.XX Mpps        | XX.XX Gbps |

### TCP Performance

| Protocol | PPS (Packets/sec) | Throughput |
|----------|-------------------|------------|
| TCP      | X.XX Mpps        | XX.XX Gbps |

## Post-Test Validation Results

✓ Service Status Check: PASS
✓ Core Files Check: PASS
✓ VPP Statistics Check: PASS

## Key Findings
- Maximum throughput: XX.XX Gbps
- Maximum PPS: X.XX Mpps
- System stability: [Excellent/Good/Issues]
- Packet loss: [None/Details]
```

**Step 3: Provide Result Location**

Inform user where results are saved:
```
Test results saved in: gre_[version] or ipsec_[version] directory on test host
```

## Error Handling and Troubleshooting

### Version Check Failures

**Issue**: Cannot retrieve version from gateway
**Actions**:
1. Verify gateway hostname is correct
2. Check tsh cluster connectivity
3. Verify dpkg command access on gateway
4. Report error to user with details

### Deployment Failures

**Issue**: Self-service skill deployment fails
**Actions**:
1. Review deployment error messages
2. Check if gateway is accessible
3. Verify build version exists in Jenkins
4. Report to user and ask if they want to retry or abort

### Test Execution Failures

**Issue**: Test script fails or produces errors
**Actions**:
1. Capture full error output
2. Check if test host is accessible
3. Verify script paths exist
4. Check ansible user permissions
5. Review test script logs
6. Report detailed error to user

### Common Issues and Solutions

**Issue**: "access denied to ansible connecting to nsgwdeployment"
**Root Cause**: Direct SSH to ansible user is restricted
**Solution**: Use `sudo -u ansible` from your regular user account
```bash
# WRONG - This fails
tsh ssh --cluster iad0 ansible@nsgwdeployment.iad0.netskope.com "command"

# CORRECT - Use sudo to switch to ansible user
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo -u ansible bash -c 'command'"
```

**Issue**: "Permission denied: '/home/your-username/.../new_client.conf'"
**Root Cause**: Test files are owned by ansible user
**Solution**: Always run tests as ansible user (see above)

**Issue**: Test prompts "Do you want to continue anyway? (yes/no):"
**Root Cause**: Script detects probe validation failure and asks for confirmation
**Solution**: Bypass with `echo 'yes' |` before the python command
```bash
# CORRECT - Bypasses interactive prompt
echo yes | python3 gre_json.py -t 150 -e 2048 -p
```

**Issue**: Test appears to hang at "restarting CFW to load new nat config"
**Root Cause**: CFW restart takes time to complete
**Solution**: This is normal - wait 30-60 seconds, test will continue automatically

**Issue**: Gateway not responding after deployment
**Solution**: Wait for deployment health checks to complete (typically 5-10 minutes)

**Issue**: Script not found at specified path
**Solution**: Verify the exact path with the user and check if scripts have been moved

**Issue**: Test takes longer than expected
**Root Cause**:
- Tunnel setup and UDP tests can vary based on system load
- Large tunnel counts increase test duration
**Solution**:
- Tests normally take 10-12 minutes for 150 tunnels with 2048 endpoints each
- TCP test completes in approximately 3 minutes
- Use background execution and monitor progress periodically
- Don't interrupt - let it complete naturally

**Issue**: "unable to click total PPS" messages in output
**Root Cause**: Transient issue with metrics collection (known behavior)
**Solution**: Not an error - test continues and collects final metrics successfully

## Command Reference

### Quick Command Summary

**Version Check - VPP GRE:**
```bash
tsh ssh --cluster iad0 vppgregw01.c18.iad0.netskope.com "dpkg -l *.ns | grep ns-vpp-gregw.ns"
```

**Version Check - VPP IPSEC:**
```bash
tsh ssh --cluster iad0 vppipsecgw04.c18.iad0.netskope.com "dpkg -l *.ns | grep nsipsecgw-cp.ns"
```

**Run GRE Test (CORRECT METHOD):**
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo -u ansible bash -c 'cd /home/your-username/Perf_testing/scale_performance_suite/scale_performance_automation && echo yes | python3 gre_json.py -t 150 -e 2048 -p'"
```

**Run IPSEC Test (CORRECT METHOD):**
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo -u ansible bash -c 'cd ~/Perf_testing/scale_performance_suite/scale_performance_automation/Ipsec_tunnel_automation && echo yes | python3 ipsec_json.py -t 150 -e 2048 -p'"
```

**Note**: The commands above use:
- `nsgwdeployment.iad0.netskope.com` (not ansible@...)
- `sudo -u ansible` to switch to ansible user
- `echo yes |` to bypass interactive prompts

## Best Practices

1. **Always verify version before testing** - Ensures test results are for correct build

2. **Wait for deployment completion** - Never start tests on a gateway mid-deployment (wait 5-10 min for health checks)

3. **Use correct execution method** - Always use `sudo -u ansible` from regular user, not direct ansible SSH

4. **Run tests in background** - Use `run_in_background=true` parameter to avoid timeouts (tests take 10-12 min)

5. **Bypass interactive prompts** - Always include `echo yes |` before python command

6. **Monitor progress periodically** - Check output file every 2-3 minutes to track test phases

7. **Don't interrupt tests** - Let tests complete naturally, even if they seem to pause (especially at CFW restart)

8. **Capture complete output** - Full logs are essential for debugging and result validation

9. **Report results clearly** - Present metrics in formatted tables, not raw output

10. **Never skip version re-verification** - After deployment, always confirm new version is active

11. **Check post-test validation** - Always report all three validation checks (services, cores, VPP stats)

12. **Understand normal behaviors**:
    - "unable to click total PPS" messages are normal
    - CFW restart may pause for 30-60 seconds
    - TCP tests take approximately 3 minutes

## Integration with Other Skills

### Self-Service Skill Integration

This skill depends on the `self-service-skill` for deployment operations. When deployment is needed:

1. **Invoke self-service skill** for the deployment
2. **Wait for completion** before proceeding
3. **Handle deployment errors** and report to user
4. **Re-verify version** after successful deployment

### Example Integration Flow:

```
User Request → Version Check → [If version differs] → Deploy via self-service-skill → Verify New Version → Run Test → Report Results
                             ↓
                        [If version matches] → Run Test → Report Results
```

## Important Notes

- **Test scripts must run from ansible user** - This is non-negotiable
- **Full hostname required** - Always use FQDN (e.g., vppgregw01.c18.iad0.netskope.com)
- **Cluster specification** - Always use `--cluster iad0` for tsh commands
- **Script paths are absolute** - Do not modify script locations
- **Performance mode flag** - The `-p` flag is required for performance testing
- **Tunnel count** - Default is 150 tunnels with 2048 endpoints per tunnel, can be adjusted via `-t` and `-e` parameters

## Example Interactions

### Example 1: Version Already Matches (No Deployment Needed)

**User**: "run vpp gre scale and performance on version 134.0.0.3391"

**Assistant**:
1. "I'll run VPP GRE scale and performance testing on version 134.0.0.3391. Let me first check the current version on the gateway."

2. [Execute version check]
   ```bash
   tsh ssh --cluster iad0 vppgregw01.c18.iad0.netskope.com "dpkg -l *.ns | grep ns-vpp-gregw.ns"
   ```

3. "Perfect! The gateway is already running version 134.0.0.3391. No deployment needed. I'll proceed directly to running the scale and performance test with 150 tunnels and 2048 endpoints per tunnel."

4. [Execute test script in background]
   ```bash
   tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo -u ansible bash -c 'cd /home/your-username/Perf_testing/scale_performance_suite/scale_performance_automation && echo yes | python3 gre_json.py -t 150 -e 2048 -p'"
   ```

5. "The test is now running. This will take approximately 10-12 minutes. I'll monitor the progress..."

6. [Monitor progress periodically]
   - "Currently in tunnel configuration phase..."
   - "UDP performance tests running..."
   - "TCP performance test in progress..."

7. [Display final results when complete]
   Present formatted results with:
   - Test summary
   - UDP performance table (4 packet sizes)
   - TCP performance results
   - Post-test validation status
   - Key findings

### Example 2: Version Differs (Deployment Required)

**User**: "run vpp gre scale and performance on version 134.0.0.3400"

**Assistant**:
1. "I'll run VPP GRE scale and performance testing on version 134.0.0.3400. Let me first check the current version on the gateway."

2. [Execute version check]

3. "Current version is 134.0.0.3391. I need to deploy version 134.0.0.3400 first."

4. [Invoke self-service-skill for deployment]
   "Deploying build 134.0.0.3400 on host vppgregw01.c18.iad0.netskope.com..."

5. [Wait for deployment completion]
   "Deployment in progress... waiting for completion and health checks..."

6. [Re-verify version]
   "Deployment successful. Verifying new version..."
   "Version confirmed as 134.0.0.3400."

7. [Execute test script]
   "Now running scale and performance test with 150 tunnels and 2048 endpoints per tunnel..."

8. [Monitor and display results as in Example 1]

---

## Performance Baseline

**Test Configuration:**
- **Tunnels:** 150
- **Endpoints per Tunnel:** 2048
- **Gateway:** vppgregw01.c18.iad0.netskope.com
- **Baseline Version:** 134.0.2.3026
- **Baseline Date:** 2026-01-28

**Expected Performance Numbers (VPP GRE):**

| Packet Size | PPS (Packets/sec) | Throughput | Notes |
|-------------|-------------------|------------|-------|
| 1300 bytes  | 4.58 Mpps        | 46.72 Gbps | Maximum throughput |
| 500 bytes   | 6.29 Mpps        | 26.69 Gbps | Mid-size packet performance |
| 100 bytes   | 6.34 Mpps        | 7.92 Gbps  | Small packet processing |
| IMIX (mixed)| 5.97 Mpps        | 30.86 Gbps | Mixed traffic scenario |
| TCP         | 4.99 Mpps        | 42.2 Gbps  | TCP connection throughput |

**System Stability Expectations:**
- No service restarts during testing
- No core files generated
- All VPP error and drop counters remain at 0
- Stable performance across all packet sizes

**Notes:**
- This baseline reflects performance with 150 tunnels and 2048 endpoints per tunnel configuration
- Any performance degradation >5% from these numbers should be investigated
- These are the standard test parameters for all VPP GRE scale and performance testing

---

**Version**: 1.2.0
**Last Updated**: 2026-01-28
**Maintained By**: Netskope IPSEC/GRE Team

**Changelog**:
- v1.2.0 (2026-01-28):
  - **BREAKING CHANGE**: Updated default test parameters from 750 tunnels to 150 tunnels with 2048 endpoints per tunnel
  - Added new performance baseline for 150 tunnels with 2048 endpoints configuration
  - Updated all commands to use `-t 150 -e 2048` parameters
  - Documented expected performance numbers for new configuration
  - Baseline established from version 134.0.2.3026 test results
  - Updated test duration estimates: Total ~10-12 minutes (TCP test ~3 minutes, not 10)

- v1.1.0 (2025-01-27):
  - Updated test execution commands to use `sudo -u ansible` instead of direct ansible SSH
  - Added interactive prompt bypass with `echo yes |`
  - Documented expected test duration (~10-12 minutes for 150 tunnels)
  - Added detailed progress monitoring phases
  - Included actual performance result formats
  - Enhanced troubleshooting with real-world issues and solutions
  - Added best practices from production test run

- v1.0.0 (2025-01-27):
  - Initial skill creation
  - Basic workflow definition
  - Version verification and deployment integration
