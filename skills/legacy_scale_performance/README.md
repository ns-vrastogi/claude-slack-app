# Legacy IPSECGW Scale & Performance Testing Skill

A comprehensive Claude Code skill for conducting scale and performance regression testing on Legacy IPSECGW infrastructure at Netskope.

## Overview

This skill provides an interactive, guided workflow for executing performance tests on Legacy IPSECGW nodes, including:

- **Throughput Testing**: Single active tunnel per client pumping 1+ Gbps traffic
- **Scale Testing**: 500 idle tunnels + 32K endpoints
- **Tunnel Flap Testing**: Continuous configuration changes and tunnel stability
- **Full Regression**: Complete performance validation across all scenarios

## Features

- Step-by-step guided workflow through the entire testing process
- Automated command execution via SSH (using tsh)
- Built-in validation and verification checks
- Real-time log monitoring and error detection
- Progress tracking with todo lists
- Result collection and baseline comparison
- Troubleshooting assistance

## Installation

This skill is already installed in your Claude Code skills directory:
```
~/.claude/skills/legacy_scale_performance/
```

## Usage

### Invoking the Skill

In Claude Code, run:
```
/legacy-scale-perf
```

Or simply mention it in your conversation:
```
Help me run legacy scale performance testing
```

### What to Expect

When you invoke the skill, Claude will:

1. **Ask clarifying questions**:
   - What type of test do you want to run?
   - Which gateway nodes should be tested?
   - Which build/version is deployed?
   - Which features should be enabled (XFRM, QOS, etc.)?

2. **Guide you through each phase**:
   - Phase 1: Gateway Setup
   - Phase 2: Client Setup
   - Phase 3: Throughput Testing
   - Phase 4: Monitoring and Results
   - Phase 5: Tunnel Flap Testing (if needed)

3. **Execute commands via SSH**:
   - Uses `tsh ssh` to connect to gateway and client nodes
   - Runs configuration and validation commands
   - Shows output and validates results

4. **Track progress**:
   - Uses todo lists to track completion of each phase
   - Validates each step before proceeding
   - Provides clear status updates

5. **Help troubleshoot issues**:
   - Monitors logs for errors
   - Suggests fixes for common problems
   - Validates configurations

## Test Infrastructure

### Nodes Involved

**Gateway Nodes** (under test):
- ipsecgw01-04.c18.iad0

**Client Nodes** (traffic generation):
- prfclient01.c18.iad0 - 500 idle tunnels
- prfclient02.c18.iad0 - ~8K endpoints + 1 active tunnel
- prfclient03.c18.iad0 - ~8K endpoints + 1 active tunnel
- prfclient04.c18.iad0 - ~8K endpoints + 1 active tunnel
- prfclient05.c18.iad0 - ~8K endpoints + 1 active tunnel

**Total Scale**:
- 500 idle tunnels
- 4 active tunnels
- ~32,000 endpoints

### Access

All nodes are accessed via Teleport:
```bash
tsh ssh --cluster iad0 <hostname>
```

## Test Types

### 1. Throughput Test

Tests maximum data throughput with active traffic.

**Setup**:
- 500 idle tunnels on prfclient01
- 1 active tunnel per client (prfclient02-05)
- JMeter generates 1+ Gbps traffic per active tunnel

**Metrics Collected**:
- CPU utilization
- Memory utilization
- Network throughput (Gbps)
- Packets per second (PPS)
- JMeter response times and success rates

### 2. Scale Test

Tests gateway behavior under scale.

**Setup**:
- 500 idle tunnels
- 32K endpoints
- Baseline monitoring

**Metrics Collected**:
- Resource utilization at scale
- Tunnel establishment time
- Stability over time

### 3. Tunnel Flap Test

Tests tunnel stability under continuous changes.

**Setup**:
- 500 tunnels on prfclient01
- Continuous tunnel up/down cycles

**Metrics Collected**:
- Tunnel recovery time
- Error rates
- Resource impact during flaps

## File Structure

```
legacy_scale_performance/
├── skill.json                      # Skill metadata
├── prompt.md                       # Main skill prompt (loaded by Claude)
├── README.md                       # This file
├── commands_reference.md           # Quick command reference
├── test_results_template.md        # Template for recording results
└── validation_checklist.md         # Comprehensive validation checklist
```

## Key Files and Directories

### On Gateway Nodes

**Tunnel Configs**:
- Source: `/home/your-username/selective/netskope.swanctl.json` - Tunnel configuration file
- Destination: `/opt/ns/tenant/1530/ipsecgw/` - Where config is copied to

**Infrastructure Configs**: `/opt/nc/common/remote/`
- `cfw.conf` - CFW VIP configuration
- `proxy.conf` - NSProxy VIP configuration

**Logs**:
- `/var/log/tunsvc.log` - Tunnel service logs
- `/var/log/strongswan.log` - Strongswan logs

### On Client Nodes

**Configs**: `/etc/`
- `ipsec.conf_500Tun` - Config for 500 idle tunnels (prfclient01)
- `ipsec.secrets_500Tun` - Secrets for 500 idle tunnels
- `ipsec.conf_reg` - Config for throughput test (prfclient02-05)
- `ipsec.secrets_reg` - Secrets for throughput test

**Scripts**: `/home/seema/`
- `tunnel_bringup.py` - Brings up tunnels
- `bringup_iface.py` - Creates network interfaces/endpoints
- `interface_ip.csv` - CSV file with endpoint IPs (for JMeter)
- `test_result.jtl` - JMeter test results

**JMeter**: `/home/seema/lnp/performance-automation/tools/apache-jmeter-5.2/`

**JMeter Scripts**: `/home/seema/`
- `ipsec_script_upload_nsproxy.jmx` - Proxy upload test
- `ipsec_script_upload_download.jmx` - CFW download/upload test

## Common Commands

See [commands_reference.md](commands_reference.md) for a complete quick reference.

### Quick Start Commands

**Check if skill is working**:
```bash
# In Claude Code
/legacy-scale-perf
```

**Access a gateway node**:
```bash
tsh ssh --cluster iad0 ipsecgw01.c18.iad0
```

**Check tunnel status**:
```bash
sudo ipsec statusall | grep 1530
```

**Verify endpoints**:
```bash
ip addr | grep "10\.2" | wc -l
```

## Monitoring

### Grafana Dashboard

During the test, monitor metrics in real-time via Grafana (link provided by skill during execution).

**Key Metrics**:
- CPU utilization per node
- Memory utilization per node
- Network throughput (Gbps)
- Packets per second (PPS)
- Tunnel status

### Log Monitoring

**Gateway logs**:
```bash
tail -f /var/log/tunsvc.log
tail -f /var/log/strongswan.log
```

## Validation

Use the [validation_checklist.md](validation_checklist.md) to ensure all steps are completed correctly.

**Key validation points**:
- ✅ All gateway nodes have dummy configs applied
- ✅ All client nodes have tunnels established
- ✅ All endpoints created (~32K total)
- ✅ Connectivity verified via curl tests
- ✅ JMeter running successfully
- ✅ No errors in logs

## Recording Results

Use the [test_results_template.md](test_results_template.md) to record test results.

**Key data to record**:
- CPU utilization (average, peak)
- Memory utilization (average, peak)
- Network throughput (average, peak)
- PPS (average, peak)
- JMeter statistics (requests, success rate, response times)
- Comparison with baseline
- Any errors or issues

## Troubleshooting

### Important Notes from Test Runs

1. **Hostname Format**: Always use full hostname with `.netskope.com` suffix
   - Correct: `ipsecgw01.c18.iad0.netskope.com`
   - Incorrect: `ipsecgw01.c18.iad0`

2. **Service Management**:
   - Only stop `cfgagentv2`, NOT `cfgagentv2_health_check`
   - After copying tunnel config, services auto-reload - no need to restart

3. **prfclient01 500 Idle Tunnels**:
   - This step is **OPTIONAL** and often causes issues
   - tunnel_bringup.py may fail or cause tunnel flapping
   - Tests work fine with just the 4 active tunnels from prfclient02-05

4. **JMeter Considerations**:
   - Always use `sudo` for JMeter commands
   - Error rates of 2-4% are **expected and normal**
   - To stop: `sudo pkill -f jmeter`

5. **Endpoint Counts**:
   - Expect ~12K endpoints per client node (not 6.5K-8K)
   - Total: ~48K endpoints across prfclient02-05

6. **Throughput Monitoring**:
   - `nload` doesn't work in SSH (needs interactive terminal)
   - Use `sar -n DEV 1 5 | grep -A 1 Average` instead
   - Expected throughput: ~7-8 Gbps bidirectional at full load

### Tunnels Not Coming Up

**Check**:
- Strongswan and tunsvc logs for errors
- Verify config files copied correctly
- Ensure services restarted successfully
- Verify network connectivity to gateway

**Fix**:
```bash
# Check service status
supervisorctl status tunsvc strongswan

# Restart services
supervisorctl restart tunsvc strongswan

# Check logs
tail -100 /var/log/strongswan.log
```

### Endpoints Missing

**Check**:
```bash
ip addr | grep "10\.[2-5]" | wc -l
```

**Fix**:
```bash
sudo python3 /home/seema/bringup_iface.py
```

### JMeter Failures

**Check**:
- CSV files populated with endpoint IPs
- Tunnel connectivity (curl test)
- Old .jtl files removed

**Fix**:
```bash
# Verify CSV
cat /home/seema/interface_ip.csv | wc -l

# Test connectivity
curl -k --interface 10.2.0.2 http://10.136.8.36:2250/d/1/21bytes.txt/download

# Remove old results
rm /home/seema/test_result.jtl
```

### Low Throughput

**Check**:
- CPU/memory utilization on gateways
- Logs for errors or warnings
- Feature configuration (XFRM, QOS)
- Client-side network performance

**Fix**:
- Investigate bottlenecks in Grafana
- Check if CPU/memory exhausted
- Verify tunnel and endpoint counts

## Best Practices

1. **Verify gateway nodes are in clean state** before starting a new test (check for any active tests or processes)

2. **Verify configurations** at each step before proceeding

3. **Monitor logs** continuously during test execution

4. **Record baseline metrics** for comparison

5. **Document all issues** encountered during testing

6. **Use the validation checklist** to ensure completeness

7. **Take Grafana screenshots** for documentation

8. **Compare results** with previous baselines

## Support

For questions or issues with this skill:

1. Check the [commands_reference.md](commands_reference.md) for quick command syntax
2. Review the [validation_checklist.md](validation_checklist.md) for missing steps
3. Consult the original Confluence documentation
4. Reach out to the IPSEC/GRE team

## Updates and Maintenance

This skill is based on the procedure documented at:
https://netskope.atlassian.net/wiki/spaces/ASSGI/pages/3944055359/Steps+to+run+perf+regression+for+Legacy+IPSECGW

If the procedure changes, update the following files:
- `prompt.md` - Main workflow
- `commands_reference.md` - Command syntax
- `validation_checklist.md` - Validation steps
- `test_results_template.md` - Results format (if needed)

## Version History

- **v1.0.0** (2026-01-16): Initial release
  - Full throughput testing workflow
  - Tunnel flap testing support
  - Scale testing support
  - Interactive guidance
  - Command execution via tsh
  - Validation and monitoring

## License

Internal use only - Netskope IPSEC/GRE Team

---

**Created by**: Netskope IPSEC/GRE Team
**Maintained by**: Staff SDE - Scale & Performance Testing
**Last Updated**: 2026-01-16
