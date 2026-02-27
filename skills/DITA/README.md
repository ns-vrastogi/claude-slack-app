# DITA Skill

**Dynamic and Intelligent Test Case & Automation Assistant**

## Overview

DITA is a comprehensive test generation skill that creates high-coverage test plans and topology-aware automation for Netskope's VPP/CNI-based networking features.

## Key Capabilities

1. **Topology-Aware Test Generation**
   - Accepts or discovers network topology diagrams
   - Generates automation scripts with actual device hostnames and IPs
   - Adapts to specific gateway types (ECGW, IPSEC, GRE, Legacy)

2. **Multi-Skill Integration**
   - Automatically consults relevant skills for feature-specific context
   - Extracts actual commands and configuration paths
   - Applies best practices from domain-specific skills

3. **Comprehensive Test Coverage**
   - Functional, negative, boundary testing
   - Performance, scalability, resiliency
   - Security, chaos engineering, concurrency
   - Upgrade/rollback scenarios

4. **Automation-Ready Artifacts**
   - Python (pytest-style) test scripts with dry-run support
   - Shell scripts with error handling
   - T-rex/CyPerf performance profiles
   - Manual test procedures with CLI commands

5. **Automated Validation & Self-Fixing** ⭐ NEW
   - Validates generated scripts for syntax errors
   - Runs dry-run mode to catch runtime issues
   - Verifies connectivity to all hosts
   - Checks command availability and file paths
   - Automatically fixes common issues
   - Provides detailed validation reports
   - Iterates until all issues are resolved

## Skill Integration Matrix

| Feature Type | Primary Skills | Secondary Skills |
|-------------|---------------|------------------|
| ECGW | ecgw-skill, vpp-skill | topology-finder-skill |
| IPSEC | vpp-skill, topology-finder-skill | - |
| GRE | vpp-skill | topology-finder-skill |
| Performance (VPP) | vpp_scale_performance, vpp-skill | ecgw-skill (if ECGW) |
| Performance (Legacy) | legacy_scale_performance | - |
| Topology Unknown | topology-finder-skill | (then route to above) |

## Usage

```bash
# Example: Generate test cases for ECGW BGP failover
"Generate test cases for ECGW BGP failover feature"
→ DITA will:
  1. Identify feature type (ECGW)
  2. Read ecgw-skill + vpp-skill
  3. Discover/validate topology
  4. Generate topology-aware test cases with actual commands
```

## Input Requirements

- **Feature description or design document**
- **Topology diagram** (or will auto-discover using topology-finder-skill)
  - Device hostnames
  - IP addresses and interfaces
  - Gateway types and tenant IDs
- **Test scope** (functional, performance, etc.)

## Output Structure

1. **Summary**: Feature scope, risks, skills consulted
2. **Test Plan Overview**: Coverage matrix, risk ranking
3. **Detailed Test Cases**: With topology mapping and automation code
4. **Runnable Automation**: Python/Shell scripts with actual device details

## Workflow

```
User Request
    ↓
Identify Feature Type (ECGW/IPSEC/GRE/Legacy)
    ↓
Consult Relevant Skills (read skill files)
    ↓
Obtain/Discover Topology (use topology-finder-skill if needed)
    ↓
Extract Commands & Config Paths (from skills)
    ↓
Generate Topology-Aware Test Cases & Automation (with dry-run support)
    ↓
VALIDATE SCRIPTS ⭐
├─ Run syntax checks
├─ Execute dry-run mode
├─ Verify connectivity
├─ Check commands & paths
└─ Fix issues if found
    ↓
Iterate Until All Issues Resolved
    ↓
Generate Validation Report
    ↓
Deliver VALIDATED Scripts ✓
```

## Test Categories

- Edge & Corner Cases
- Negative & Fault Injection
- Performance & Scalability
- Security & Hardening
- Upgrade/Rollback
- Chaos Engineering

## Automation Tools

- **CLI**: kubectl, vppctl, gobgp, swanctl, ip, tc, tcpdump
- **Performance**: T-rex, CyPerf, BPS, iperf3, Jmeter
- **Stress**: stress-ng, chaos-mesh, fio
- **Remote Access**: tsh ssh (Teleport)

## Quality Standards

- Multi-run determinism
- Idempotent setup/teardown
- Resource cleanup verification
- Temporal correctness
- RFC and vendor standard compliance

## Files

- `SKILL.md` - Complete skill definition with templates and workflows
- `README.md` - This overview document

---

For detailed instructions, templates, and examples, see `SKILL.md`.
