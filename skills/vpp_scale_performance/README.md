# VPP Scale & Performance Testing Skill

Automated scale and performance testing workflow for VPP-based IPSEC and GRE gateways.

## Overview

This skill automates the complete testing workflow for VPP gateways including:
- ✅ Version verification on target gateway
- ✅ Automated deployment (only if version differs)
- ✅ Test execution with proper parameters
- ✅ Result reporting with full metrics

## Supported Gateways

| Gateway Type | Hostname | Package Name |
|-------------|----------|--------------|
| VPP GRE | vppgregw01.c18.iad0.netskope.com | ns-vpp-gregw.ns |
| VPP IPSEC | vppipsecgw04.c18.iad0.netskope.com | nsipsecgw-cp.ns |

## Quick Start

### Basic Usage

```
run vpp gre scale and performance on version 134.0.0.3398
```

```
run vpp ipsec scale and performance on version 134.0.0.3400
```

### What Happens

1. **Version Check**: Checks current version on gateway
2. **Smart Deployment**: Only deploys if version differs (uses self-service-skill)
3. **Test Execution**: Runs 750 tunnel scale test with performance metrics
4. **Results**: Displays complete test results

## Test Configuration

### Default Parameters
- **Tunnels**: 750
- **Mode**: Performance (`-p` flag)
- **Test Host**: nsgwdeployment.iad0.netskope.com
- **Test User**: ansible (required)

### Test Scripts

**GRE Test:**
```bash
/home/your-username/Perf_testing/scale_performance_suite/scale_performance_automation/gre_json.py
```

**IPSEC Test:**
```bash
~/Perf_testing/scale_performance_suite/scale_performance_automation/Ipsec_tunnel_automation/ipsec_json.py
```

## Workflow

```
┌─────────────────┐
│  User Request   │
│  (with version) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check Current   │
│ Version         │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │Version │
    │Match?  │
    └───┬────┘
        │
   No   │   Yes
   ┌────┴────┐
   ▼         ▼
┌──────┐  ┌──────┐
│Deploy│  │ Skip │
│ via  │  │Deploy│
│Self- │  └──┬───┘
│Service│    │
└──┬───┘    │
   │        │
   ▼        │
┌──────┐   │
│Verify│   │
│New   │   │
│Version│  │
└──┬───┘   │
   │        │
   └────┬───┘
        │
        ▼
┌─────────────────┐
│  Run Scale &    │
│  Performance    │
│  Test (750      │
│  tunnels)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Display Final   │
│ Results         │
└─────────────────┘
```

## Example Interactions

### Scenario 1: Version Matches (No Deployment Needed)

**User**: "run vpp gre scale and performance on version 134.0.0.3398"

**Assistant**:
- Checks version on vppgregw01.c18.iad0.netskope.com
- Finds version 134.0.0.3398 already running
- Skips deployment
- Runs test directly
- Shows results

### Scenario 2: Version Differs (Deployment Required)

**User**: "run vpp ipsec scale and performance on version 134.0.0.3400"

**Assistant**:
- Checks version on vppipsecgw04.c18.iad0.netskope.com
- Finds different version (e.g., 134.0.0.3390)
- Deploys version 134.0.0.3400 using self-service-skill
- Re-verifies new version
- Runs test
- Shows results

## Command Reference

### Manual Version Check

**VPP GRE:**
```bash
tsh ssh --cluster iad0 vppgregw01.c18.iad0.netskope.com "dpkg -l *.ns | grep ns-vpp-gregw.ns"
```

**VPP IPSEC:**
```bash
tsh ssh --cluster iad0 vppipsecgw04.c18.iad0.netskope.com "dpkg -l *.ns | grep nsipsecgw-cp.ns"
```

### Manual Test Execution

**IMPORTANT**: Direct SSH to ansible user may fail. Use sudo method instead.

**GRE Test (CORRECT METHOD):**
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo -u ansible bash -c 'cd /home/your-username/Perf_testing/scale_performance_suite/scale_performance_automation && echo yes | python3 gre_json.py -t 750 -p'"
```

**IPSEC Test (CORRECT METHOD):**
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo -u ansible bash -c 'cd ~/Perf_testing/scale_performance_suite/scale_performance_automation/Ipsec_tunnel_automation && echo yes | python3 ipsec_json.py -t 750 -p'"
```

**Key differences from old method:**
- Use `nsgwdeployment.iad0.netskope.com` instead of `ansible@nsgwdeployment...`
- Use `sudo -u ansible bash -c '...'` to run as ansible user
- Add `echo yes |` to bypass interactive prompts

## Dependencies

### Required Skills
- **self-service-skill**: Used for automated deployment when version differs

### Required Tools
- **tsh**: Teleport SSH client for remote access
- **python3**: Python 3.x for running test scripts
- **dpkg**: Debian package manager for version checking

### Required Access
- SSH access to gateway hosts via Teleport
- SSH access to test execution host (nsgwdeployment) as ansible user
- Jenkins access (via self-service-skill) for deployments

## Important Notes

⚠️ **Critical Requirements:**
- Test scripts MUST run as `ansible` user
- Always use full hostname (FQDN)
- Always specify `--cluster iad0` for tsh
- Do NOT modify script paths or parameters
- Wait for deployment completion before testing

📊 **Test Metrics:**
- Tunnel establishment success rate
- Throughput (Gbps)
- Latency measurements
- Packet loss statistics
- Overall test status

⏱️ **Expected Duration:**
- Version check: ~5 seconds
- Deployment (if needed): ~5-10 minutes
- Test execution: ~15-20 minutes (actual, not 30-60)
  - Tunnel setup: ~2 minutes
  - UDP tests: ~5 minutes
  - TCP test: ~10 minutes
  - Post-validation: ~1 minute
- Total without deployment: ~15-20 minutes
- Total with deployment: ~20-30 minutes

## Troubleshooting

### Common Issues

**Issue**: "access denied to ansible connecting to nsgwdeployment"
**Fix**: Don't use direct SSH to ansible user. Use: `sudo -u ansible bash -c '...'`
```bash
# WRONG
tsh ssh --cluster iad0 ansible@nsgwdeployment.iad0.netskope.com

# CORRECT
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo -u ansible bash -c '...'"
```

**Issue**: Test prompts "Do you want to continue anyway? (yes/no):"
**Fix**: Add `echo yes |` before python command to bypass interactive prompt

**Issue**: "Permission denied: new_client.conf"
**Fix**: Files are owned by ansible user - always run as ansible user

**Issue**: Test appears to hang at "restarting CFW to load new nat config"
**Fix**: Normal behavior - CFW restart takes 30-60 seconds, test continues automatically

**Issue**: "unable to click total PPS" messages
**Fix**: Not an error - transient metrics collection issue, final results collected successfully

**Issue**: Gateway not responding after deployment
**Fix**: Wait for health checks to complete (~5-10 min)

**Issue**: Version check fails
**Fix**: Verify gateway hostname and tsh connectivity

## File Structure

```
~/.claude/skills/vpp_scale_performance/
├── SKILL.md           # Main skill definition and workflow
├── skill.json         # Skill metadata
├── README.md          # This file
└── claude.md          # Legacy skill file (deprecated)
```

## Version History

- **v1.0.0** (2025-01-27): Initial release
  - Version verification
  - Automated deployment integration
  - GRE and IPSEC test support
  - Result reporting

## Contributing

This skill is maintained by the Netskope IPSEC/GRE Team. For updates or issues, contact the team.

## License

Internal use only - Netskope Inc.
