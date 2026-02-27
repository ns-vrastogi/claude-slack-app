# VPP Scale & Performance - Commands Reference

Quick reference for all commands used in VPP scale and performance testing.

## Version Check Commands

### VPP GRE Gateway
```bash
# Check current version on VPP GRE gateway
tsh ssh --cluster iad0 vppgregw01.c18.iad0.netskope.com "dpkg -l *.ns | grep ns-vpp-gregw.ns"
```

**Expected Output:**
```
ii  ns-vpp-gregw.ns    134.0.0.3398  amd64  Netskope VPP GRE Gateway
```

**Version Location:** Third column (e.g., 134.0.0.3398)

### VPP IPSEC Gateway
```bash
# Check current version on VPP IPSEC gateway
tsh ssh --cluster iad0 vppipsecgw04.c18.iad0.netskope.com "dpkg -l *.ns | grep nsipsecgw-cp.ns"
```

**Expected Output:**
```
ii  nsipsecgw-cp.ns    134.0.0.3400  amd64  Netskope VPP IPSEC Control Plane
```

**Version Location:** Third column (e.g., 134.0.0.3400)

## Deployment Commands

### Deploy to VPP GRE Gateway
```bash
# Use self-service-skill
# Example: Deploy build 134.0.0.3398 on host vppgregw01.c18.iad0.netskope.com
```

### Deploy to VPP IPSEC Gateway
```bash
# Use self-service-skill
# Example: Deploy build 134.0.0.3400 on host vppipsecgw04.c18.iad0.netskope.com
```

## Test Execution Commands

### VPP GRE Scale & Performance Test

**IMPORTANT**: Direct SSH to ansible user may fail. Use the correct method below.

**Correct One-Liner (Use This):**
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo -u ansible bash -c 'cd /home/your-username/Perf_testing/scale_performance_suite/scale_performance_automation && echo yes | python3 gre_json.py -t 750 -p'"
```

**Key components:**
- `nsgwdeployment.iad0.netskope.com` (not ansible@...)
- `sudo -u ansible bash -c '...'` - Run as ansible user
- `echo yes |` - Bypass interactive confirmation prompt
- `python3 gre_json.py -t 750 -p` - The test command

**Old Method (Do Not Use):**
```bash
# This will fail with "access denied"
tsh ssh --cluster iad0 ansible@nsgwdeployment.iad0.netskope.com "cd /home/your-username/Perf_testing/scale_performance_suite/scale_performance_automation && python3 gre_json.py -t 750 -p"
```

### VPP IPSEC Scale & Performance Test

**IMPORTANT**: Direct SSH to ansible user may fail. Use the correct method below.

**Correct One-Liner (Use This):**
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo -u ansible bash -c 'cd ~/Perf_testing/scale_performance_suite/scale_performance_automation/Ipsec_tunnel_automation && echo yes | python3 ipsec_json.py -t 750 -p'"
```

**Key components:**
- `nsgwdeployment.iad0.netskope.com` (not ansible@...)
- `sudo -u ansible bash -c '...'` - Run as ansible user
- `echo yes |` - Bypass interactive confirmation prompt
- `python3 ipsec_json.py -t 750 -p` - The test command

**Old Method (Do Not Use):**
```bash
# This will fail with "access denied"
tsh ssh --cluster iad0 ansible@nsgwdeployment.iad0.netskope.com "cd ~/Perf_testing/scale_performance_suite/scale_performance_automation/Ipsec_tunnel_automation && python3 ipsec_json.py -t 750 -p"
```

## Test Script Parameters

### Common Parameters
| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `-t` | Number of tunnels | N/A | `-t 750` |
| `-p` | Performance mode flag | Off | `-p` |

### Parameter Combinations

**Standard Scale Test (750 tunnels):**
```bash
python3 gre_json.py -t 750 -p
python3 ipsec_json.py -t 750 -p
```

**Custom Tunnel Count:**
```bash
python3 gre_json.py -t 1000 -p
python3 ipsec_json.py -t 500 -p
```

## Gateway Information

### Hostnames and FQDNs
| Gateway Type | Short Name | FQDN |
|-------------|------------|------|
| VPP GRE | vppgregw01 | vppgregw01.c18.iad0.netskope.com |
| VPP IPSEC | vppipsecgw04 | vppipsecgw04.c18.iad0.netskope.com |
| Test Host | nsgwdeployment | nsgwdeployment.iad0.netskope.com |

### Package Names
| Gateway Type | Package Name | Version Check Pattern |
|-------------|--------------|----------------------|
| VPP GRE | ns-vpp-gregw.ns | `grep ns-vpp-gregw.ns` |
| VPP IPSEC | nsipsecgw-cp.ns | `grep nsipsecgw-cp.ns` |

## Access Methods

### Teleport SSH Access
```bash
# Standard format
tsh ssh --cluster <cluster> <hostname>

# With specific user
tsh ssh --cluster <cluster> <user>@<hostname>

# Examples
tsh ssh --cluster iad0 vppgregw01.c18.iad0.netskope.com
tsh ssh --cluster iad0 ansible@nsgwdeployment.iad0.netskope.com
```

### Required Cluster
- **Cluster**: `iad0` (for all iad0 region hosts)

### Required User for Tests
- **User**: `ansible` (for test execution on nsgwdeployment)

## Script Paths

### Absolute Paths
```bash
# VPP GRE Test Script
/home/your-username/Perf_testing/scale_performance_suite/scale_performance_automation/gre_json.py

# VPP IPSEC Test Script
/home/your-username/Perf_testing/scale_performance_suite/scale_performance_automation/Ipsec_tunnel_automation/ipsec_json.py
```

### Relative Paths (from ansible user home)
```bash
# VPP IPSEC (using ~)
~/Perf_testing/scale_performance_suite/scale_performance_automation/Ipsec_tunnel_automation/ipsec_json.py
```

## Debugging Commands

### Check Gateway Connectivity
```bash
# Ping gateway
tsh ssh --cluster iad0 vppgregw01.c18.iad0.netskope.com "echo 'Connected successfully'"
tsh ssh --cluster iad0 vppipsecgw04.c18.iad0.netskope.com "echo 'Connected successfully'"
```

### Check Test Host Connectivity
```bash
# As ansible user
tsh ssh --cluster iad0 ansible@nsgwdeployment.iad0.netskope.com "whoami"
```

### Verify Script Exists
```bash
# Check GRE script
tsh ssh --cluster iad0 ansible@nsgwdeployment.iad0.netskope.com "ls -lh /home/your-username/Perf_testing/scale_performance_suite/scale_performance_automation/gre_json.py"

# Check IPSEC script
tsh ssh --cluster iad0 ansible@nsgwdeployment.iad0.netskope.com "ls -lh ~/Perf_testing/scale_performance_suite/scale_performance_automation/Ipsec_tunnel_automation/ipsec_json.py"
```

### Check Python Version
```bash
tsh ssh --cluster iad0 ansible@nsgwdeployment.iad0.netskope.com "python3 --version"
```

### Check Script Permissions
```bash
# GRE script permissions
tsh ssh --cluster iad0 ansible@nsgwdeployment.iad0.netskope.com "stat /home/your-username/Perf_testing/scale_performance_suite/scale_performance_automation/gre_json.py"

# IPSEC script permissions
tsh ssh --cluster iad0 ansible@nsgwdeployment.iad0.netskope.com "stat ~/Perf_testing/scale_performance_suite/scale_performance_automation/Ipsec_tunnel_automation/ipsec_json.py"
```

## Common Patterns

### Complete GRE Test Flow
```bash
# 1. Check version
tsh ssh --cluster iad0 vppgregw01.c18.iad0.netskope.com "dpkg -l *.ns | grep ns-vpp-gregw.ns"

# 2. Deploy if needed (via self-service-skill)
# Deploy build X.X.X.XXXX on host vppgregw01.c18.iad0.netskope.com

# 3. Verify new version
tsh ssh --cluster iad0 vppgregw01.c18.iad0.netskope.com "dpkg -l *.ns | grep ns-vpp-gregw.ns"

# 4. Run test
tsh ssh --cluster iad0 ansible@nsgwdeployment.iad0.netskope.com "cd /home/your-username/Perf_testing/scale_performance_suite/scale_performance_automation && python3 gre_json.py -t 750 -p"
```

### Complete IPSEC Test Flow
```bash
# 1. Check version
tsh ssh --cluster iad0 vppipsecgw04.c18.iad0.netskope.com "dpkg -l *.ns | grep nsipsecgw-cp.ns"

# 2. Deploy if needed (via self-service-skill)
# Deploy build X.X.X.XXXX on host vppipsecgw04.c18.iad0.netskope.com

# 3. Verify new version
tsh ssh --cluster iad0 vppipsecgw04.c18.iad0.netskope.com "dpkg -l *.ns | grep nsipsecgw-cp.ns"

# 4. Run test
tsh ssh --cluster iad0 ansible@nsgwdeployment.iad0.netskope.com "cd ~/Perf_testing/scale_performance_suite/scale_performance_automation/Ipsec_tunnel_automation && python3 ipsec_json.py -t 750 -p"
```

## Error Messages and Solutions

### "Permission denied"
**Cause:** Not running as ansible user
**Solution:** Use `ansible@nsgwdeployment.iad0.netskope.com`

### "No such file or directory"
**Cause:** Script path incorrect or script moved
**Solution:** Verify script exists with `ls -lh <script_path>`

### "dpkg: command not found"
**Cause:** Gateway doesn't have dpkg (unlikely)
**Solution:** Check if connected to correct gateway

### "Connection refused"
**Cause:** Teleport not connected or gateway down
**Solution:** Check `tsh status` and gateway health

## Quick Tips

1. **Always use FQDN** - Don't use short hostnames
2. **Always specify cluster** - Use `--cluster iad0`
3. **Use ansible user for tests** - Critical for permissions
4. **Capture full output** - Helps with debugging
5. **Wait for deployment** - Don't test during deployment
6. **Re-verify version** - Always check after deployment
7. **Use absolute paths** - Avoids path confusion

## Version Comparison Logic

```bash
# Extract version from dpkg output
current_version=$(tsh ssh --cluster iad0 <gateway> "dpkg -l *.ns | grep <package>" | awk '{print $3}')

# Compare versions
if [ "$current_version" == "$target_version" ]; then
    echo "Version matches - proceed to test"
else
    echo "Version differs - deploy first"
fi
```

---

**Last Updated:** 2025-01-27
**Maintained By:** Netskope IPSEC/GRE Team
