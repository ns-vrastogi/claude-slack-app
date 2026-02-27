# Performance Testing Validation Checklist

Use this checklist to ensure all steps are completed correctly during performance testing.

## Pre-Test Validation

### Gateway Nodes
- [ ] All gateway nodes verified to be in clean state (no active tests running)
- [ ] Correct build/version deployed on all nodes
- [ ] CFW VIP configuration verified (optional - usually correct)
- [ ] NSProxy VIP configuration verified (optional - usually correct)
- [ ] Required features enabled/disabled as per test plan
- [ ] **Only cfgagentv2 stopped** (not health_check)
- [ ] Tunnel config file present in `/home/your-username/selective/netskope.swanctl.json`
- [ ] **Note**: Use full hostname format: `ipsecgw01.c18.iad0.netskope.com`

### Client Nodes
- [ ] All 5 client nodes accessible via tsh
- [ ] Dummy tunnel configs present on prfclient01
- [ ] Throughput test configs present on prfclient02-05
- [ ] Python scripts available (`tunnel_bringup.py`, `bringup_iface.py`)
- [ ] JMeter installed and accessible
- [ ] JMeter scripts available

## Gateway Setup Validation

### For Each Gateway Node
- [ ] **Only cfgagentv2 stopped** (not health_check)
- [ ] Tunnel config copied with sudo: `netskope.swanctl.json` → `/opt/ns/tenant/1530/ipsecgw/`
- [ ] **Services NOT restarted** (auto-reload after config copy)
- [ ] tunsvc and strongswan services verified running: `sudo supervisorctl status tunsvc strongswan`
- [ ] No critical errors in logs (check if needed)

## Client Setup Validation

### prfclient01 (Idle Tunnels) - OPTIONAL
**⚠️ This step is optional and may cause tunnel flapping issues**
- [ ] ipsec.conf_500Tun copied to ipsec.conf
- [ ] ipsec.secrets_500Tun copied to ipsec.secrets
- [ ] strongswan client restarted
- [ ] tunnel_bringup.py executed with full path: `/home/seema/tunnel_bringup.py`
- [ ] If script fails or tunnels flap, **skip this step and proceed without idle tunnels**

### prfclient02 (Endpoints & Active Traffic)
- [ ] Endpoint count verified: `ip addr | grep "10\.2" | ... | wc -l` returns ~8000-12000
- [ ] If endpoints missing, bringup_iface.py executed
- [ ] Endpoints exported to CSV: `/home/seema/interface_ip.csv` populated
- [ ] CSV file verified (check line count and sample IPs)
- [ ] ipsec.conf_reg copied to ipsec.conf (for throughput test)
- [ ] ipsec.secrets_reg copied to ipsec.secrets (for throughput test)
- [ ] strongswan client restarted
- [ ] conn_2 tunnel brought up: `sudo ipsec up conn_2`
- [ ] Connectivity verified: `curl -k --interface 10.2.0.2 http://10.136.8.36:2250/d/1/21bytes.txt/download`
- [ ] Expected response received: "This is a test file"

### prfclient03 (Endpoints & Active Traffic)
- [ ] Endpoint count verified: `ip addr | grep "10\.3" | ... | wc -l` returns ~8000-12000
- [ ] If endpoints missing, bringup_iface.py executed
- [ ] Endpoints exported to CSV: `/home/seema/interface_ip.csv` populated
- [ ] CSV file verified (check line count and sample IPs)
- [ ] ipsec.conf_reg copied to ipsec.conf (for throughput test)
- [ ] ipsec.secrets_reg copied to ipsec.secrets (for throughput test)
- [ ] strongswan client restarted
- [ ] conn_2 tunnel brought up: `sudo ipsec up conn_2`
- [ ] Connectivity verified: `curl -k --interface 10.3.0.3 http://10.136.8.36:2250/d/1/21bytes.txt/download`
- [ ] Expected response received: "This is a test file"

### prfclient04 (Endpoints & Active Traffic)
- [ ] Endpoint count verified: `ip addr | grep "10\.4" | ... | wc -l` returns ~8000-12000
- [ ] If endpoints missing, bringup_iface.py executed
- [ ] Endpoints exported to CSV: `/home/seema/interface_ip.csv` populated
- [ ] CSV file verified (check line count and sample IPs)
- [ ] ipsec.conf_reg copied to ipsec.conf (for throughput test)
- [ ] ipsec.secrets_reg copied to ipsec.secrets (for throughput test)
- [ ] strongswan client restarted
- [ ] conn_2 tunnel brought up: `sudo ipsec up conn_2`
- [ ] Connectivity verified: `curl -k --interface 10.4.0.4 http://10.136.8.36:2250/d/1/21bytes.txt/download`
- [ ] Expected response received: "This is a test file"

### prfclient05 (Endpoints & Active Traffic)
- [ ] Endpoint count verified: `ip addr | grep "10\.5" | ... | wc -l` returns ~8000-12000
- [ ] If endpoints missing, bringup_iface.py executed
- [ ] Endpoints exported to CSV: `/home/seema/interface_ip.csv` populated
- [ ] CSV file verified (check line count and sample IPs)
- [ ] ipsec.conf_reg copied to ipsec.conf (for throughput test)
- [ ] ipsec.secrets_reg copied to ipsec.secrets (for throughput test)
- [ ] strongswan client restarted
- [ ] conn_2 tunnel brought up: `sudo ipsec up conn_2`
- [ ] Connectivity verified: `curl -k --interface 10.5.0.5 http://10.136.8.36:2250/d/1/21bytes.txt/download`
- [ ] Expected response received: "This is a test file"

## Test Execution Validation

### JMeter Setup
- [ ] Old test_result.jtl file removed
- [ ] Correct JMeter script selected (Proxy Upload / CFW Download / CFW Upload)
- [ ] JMeter script path verified
- [ ] JMeter started successfully

### During Test Monitoring
- [ ] Grafana dashboard accessible
- [ ] CPU metrics visible and updating
- [ ] Memory metrics visible and updating
- [ ] Network throughput metrics visible and updating
- [ ] PPS metrics visible and updating
- [ ] No errors appearing in gateway logs
- [ ] No tunnel flaps occurring (unless testing tunnel flap scenario)
- [ ] JMeter running without errors

## Post-Test Validation

### Results Collection
- [ ] JMeter test completed successfully
- [ ] test_result.jtl file generated
- [ ] JMeter statistics reviewed (success rate, response times, throughput)
- [ ] Grafana metrics captured (screenshots or export)
- [ ] Gateway logs reviewed for errors
- [ ] Client logs reviewed for errors

### Data Recording
- [ ] CPU utilization recorded for each gateway node
- [ ] Memory utilization recorded for each gateway node
- [ ] Network throughput recorded for each gateway node
- [ ] PPS recorded for each gateway node
- [ ] Tunnel statistics recorded (active, idle, failed)
- [ ] JMeter results recorded (total/success/failed requests, response times)
- [ ] Any errors or issues documented

### Comparison with Baseline
- [ ] Previous baseline metrics available
- [ ] Current results compared against baseline
- [ ] Regression/improvement percentages calculated
- [ ] Any significant deviations investigated
- [ ] Test results template filled out

## Cleanup (if needed)

### Gateway Nodes
- [ ] Restore original configs (if needed)
- [ ] Restart cfgagentv2 services (if needed)
- [ ] Verify normal operations restored

### Client Nodes
- [ ] Restore original configs (if needed)
- [ ] Tear down test tunnels (if needed)
- [ ] Remove test endpoints (if needed)

## Sign-off
- [ ] Test results reviewed by tester
- [ ] Test results reviewed by team lead/reviewer
- [ ] Results documented in wiki/confluence
- [ ] Action items created for any issues found
- [ ] Test marked as PASS/FAIL with appropriate justification

---

## Quick Status Check

**Total Checklist Items**: 100+
**Completed**: ____
**Percentage Complete**: ____%

**Blocking Issues**: [List any blocking issues]

**Ready to Proceed**: [YES / NO / PARTIAL]
