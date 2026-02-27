# DITA Automation Validation Guide

## Overview

This guide explains how DITA skill validates and fixes generated automation scripts before delivery.

## Validation Process

### 6-Phase Validation Pipeline

```
Phase 1: Syntax Validation
    ↓
Phase 2: Dry-Run Validation
    ↓
Phase 3: Test Execution (Dry Run Mode)
    ↓
Phase 4: Execute Validation
    ↓
Phase 5: Error Analysis & Fixing
    ↓
Phase 6: Iterative Fixing Loop
```

## Phase Details

### Phase 1: Syntax Validation

**Python Scripts**:
```bash
python3 -m py_compile TC-###_test.py
pylint TC-###_test.py || true
flake8 TC-###_test.py || true
```

**Shell Scripts**:
```bash
bash -n TC-###_test.sh
shellcheck TC-###_test.sh || true
```

### Phase 2: Dry-Run Validation

**Connectivity Check**:
```bash
tsh ssh --cluster <cluster> <hostname> "echo 'Connection OK'"
```

**Command Availability**:
```bash
tsh ssh --cluster <cluster> <hostname> "which gobgp vppctl swanctl"
```

**File Path Verification**:
```bash
tsh ssh --cluster <cluster> <hostname> "ls -l /opt/ns/tenant/<tenant_id>/"
```

### Phase 3: Dry-Run Mode Support

All generated scripts include `--dry-run` flag:

**Python Example**:
```python
parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', action='store_true',
                    help='Validate script without executing')
args = parser.parse_args()

def run_remote(hostname, cluster, cmd):
    if args.dry_run:
        print(f"[DRY-RUN] Would execute: tsh ssh --cluster {cluster} {hostname} '{cmd}'")
        return "mock_output"
    else:
        # Actual execution
        ...
```

**Shell Example**:
```bash
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        *) shift ;;
    esac
done

run_remote() {
    if [ "$DRY_RUN" = true ]; then
        echo "[DRY-RUN] Would execute: tsh ssh --cluster $cluster $host '$cmd'"
    else
        tsh ssh --cluster "$cluster" "$host" "$cmd"
    fi
}
```

### Phase 4: Execute Validation

Run the script in dry-run mode:
```bash
# Python
python3 TC-001_test.py --dry-run

# Shell
bash TC-001_test.sh --dry-run
```

Capture any errors for analysis.

### Phase 5: Error Analysis & Fixing

Common errors and their fixes:

#### 1. Import Error
```
Error: ModuleNotFoundError: No module named 'xyz'

Fix: Use standard library or add try/except with graceful handling
```

#### 2. Connection Error
```
Error: Connection to host failed

Fix: Verify hostname and cluster from topology, update script
```

#### 3. Command Not Found
```
Error: gobgp: command not found

Fix: Check command from skill, use full path or correct command
```

#### 4. File Not Found
```
Error: /path/to/file: No such file

Fix: Verify actual path on host, update script with correct path
```

#### 5. Permission Denied
```
Error: Permission denied: vppctl

Fix: Add 'sudo' prefix to command
```

#### 6. Syntax Error
```
Error: SyntaxError: invalid syntax

Fix: Correct syntax (quotes, parentheses, colons, indentation)
```

### Phase 6: Iterative Fixing Loop

```
Generate Script
    ↓
Run Checks
    ↓
Errors? → YES → Analyze → Fix → Re-check
    ↓ NO
Validated ✓
```

## Validation Report Example

```markdown
## Automation Validation Report

### Script: TC-001_bgp_failover_ecgw_iad0.py

#### Validation Results:
✓ Syntax check: PASSED
✓ Dry-run execution: PASSED
✓ Host connectivity: PASSED (all hosts reachable)
✓ Command availability: PASSED (all commands found)
✓ File paths verified: PASSED

#### Issues Found & Fixed:
1. **Issue**: Missing 'sudo' for vppctl command
   **Fix**: Added 'sudo' prefix to all vppctl commands
   **Status**: FIXED

2. **Issue**: Incorrect config path
   **Fix**: Updated to /opt/ns/gregw/cfg/tenantmap/tenant3624.json
   **Status**: FIXED

#### Script Status: VALIDATED ✓

#### Execution Instructions:
# Validate without making changes
python3 TC-001_bgp_failover_ecgw_iad0.py --dry-run

# Execute actual test
python3 TC-001_bgp_failover_ecgw_iad0.py
```

## Pre-Delivery Checklist

Before delivering scripts, verify:

- [ ] **Syntax validated**: No syntax errors
- [ ] **Dry-run passed**: Script executes without runtime errors
- [ ] **Connectivity verified**: All hosts reachable via tsh
- [ ] **Commands verified**: All commands exist on target hosts
- [ ] **Paths verified**: All file/config paths correct
- [ ] **Permissions checked**: Sudo added where needed
- [ ] **Topology matched**: Uses actual hostnames/IPs
- [ ] **Skills applied**: Uses correct commands from skills
- [ ] **Error handling**: Proper error handling included
- [ ] **Cleanup included**: Resources cleaned up after execution
- [ ] **Documentation**: Clear comments and usage instructions

## Common Fix Patterns

### Fix 1: Add Sudo for VPP Commands

**Before**:
```bash
vppctl show interface
```

**After**:
```bash
sudo vppctl show interface
```

### Fix 2: Correct Command Syntax from Skill

**Before** (incorrect):
```bash
gobgp neighbor
```

**After** (from ecgw-skill):
```bash
gobgp -p 50052 neighbor
```

### Fix 3: Fix Config Path from Skill

**Before**:
```bash
/opt/ns/tenant/3624/config.json
```

**After** (from ecgw-skill):
```bash
/opt/ns/gregw/cfg/tenantmap/tenant3624.json
```

### Fix 4: Add Import Error Handling

**Before**:
```python
from trex_stl_lib.api import *
```

**After**:
```python
try:
    from trex_stl_lib.api import *
    TREX_AVAILABLE = True
except ImportError:
    print("WARNING: T-rex library not found")
    TREX_AVAILABLE = False

if not TREX_AVAILABLE:
    print("Install T-rex: pip install trex-stl-lib")
    sys.exit(1)
```

### Fix 5: Correct Hostname from Topology

**Before**:
```python
GATEWAY_HOST = "ecgw01.iad.netskope.com"  # Wrong
```

**After**:
```python
GATEWAY_HOST = "ecgw01.iad0.netskope.com"  # Correct
```

## Best Practices

1. **Always include dry-run mode** in generated scripts
2. **Validate before delivery** - never skip validation
3. **Fix iteratively** - validate after each fix
4. **Document fixes** - explain what was fixed and why
5. **Test connectivity** - verify all hosts are reachable
6. **Use actual commands** - extract from skills, don't invent
7. **Verify paths** - check file paths exist on target hosts
8. **Add error handling** - graceful failures with clear messages
9. **Include cleanup** - always clean up resources
10. **Provide clear instructions** - document how to run the script

## Tools Used for Validation

- `python3 -m py_compile` - Python syntax check
- `bash -n` - Shell script syntax check
- `pylint` / `flake8` - Python code quality (optional)
- `shellcheck` - Shell script linting (optional)
- `tsh ssh` - Remote connectivity and command testing

## Success Criteria

A script is considered validated when:

1. ✅ No syntax errors
2. ✅ Dry-run executes successfully
3. ✅ All hosts are reachable
4. ✅ All commands are available
5. ✅ All file paths are correct
6. ✅ All issues have been fixed
7. ✅ Validation report generated
8. ✅ Execution instructions provided

---

For complete details, see `SKILL.md` section: **Automation Script Validation & Self-Fixing Workflow**
