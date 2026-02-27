# Performance Test Results Template

## Test Metadata

**Date**: YYYY-MM-DD
**Tester**: [Your Name]
**Build/Version**: [e.g., develop, release-2024-01, HF-123]
**Cluster**: [e.g., iad0]
**Test Type**: [Throughput / Tunnel Flap / Scale / Full Regression]

## Gateway Nodes Tested

- [ ] ipsecgw01.c18.iad0
- [ ] ipsecgw02.c18.iad0
- [ ] ipsecgw03.c18.iad0
- [ ] ipsecgw04.c18.iad0

## Configuration

**Tenant ID**: 1530
**Tunnel Count**: 500 (idle) + 4 (active)
**Endpoint Count**: ~32,000 (8K per client node)
**Features Enabled**:
- [ ] XFRM
- [ ] QOS
- [ ] Other: __________
- [ ] None (baseline)

**CFW VIP**: __________
**NSProxy VIP**: __________

## Test Scenario

**JMeter Script Used**: [Proxy Upload / CFW Download / CFW Upload]
**Script Path**: /home/seema/ipsec_script_upload_download.jmx
**Traffic Pattern**: [Describe traffic pattern]
**Test Duration**: [Duration in minutes/hours]

## Results

### Gateway Node: ipsecgw01

**CPU Utilization**:
- Average: ____%
- Peak: ____%
- Idle: ____%

**Memory Utilization**:
- Average: ____%
- Peak: ____%
- Used: ____ GB / ____ GB

**Network Throughput**:
- Average: ____ Gbps
- Peak: ____ Gbps
- Upload: ____ Gbps
- Download: ____ Gbps

**Packets Per Second (PPS)**:
- Average: ____ PPS
- Peak: ____ PPS
- Upload: ____ PPS
- Download: ____ PPS

**Tunnel Statistics**:
- Active Tunnels: ____
- Idle Tunnels: ____
- Failed Tunnels: ____

**Errors/Issues**: [None / Describe issues]

---

### Gateway Node: ipsecgw02

**CPU Utilization**:
- Average: ____%
- Peak: ____%
- Idle: ____%

**Memory Utilization**:
- Average: ____%
- Peak: ____%
- Used: ____ GB / ____ GB

**Network Throughput**:
- Average: ____ Gbps
- Peak: ____ Gbps
- Upload: ____ Gbps
- Download: ____ Gbps

**Packets Per Second (PPS)**:
- Average: ____ PPS
- Peak: ____ PPS
- Upload: ____ PPS
- Download: ____ PPS

**Tunnel Statistics**:
- Active Tunnels: ____
- Idle Tunnels: ____
- Failed Tunnels: ____

**Errors/Issues**: [None / Describe issues]

---

### Gateway Node: ipsecgw03

**CPU Utilization**:
- Average: ____%
- Peak: ____%
- Idle: ____%

**Memory Utilization**:
- Average: ____%
- Peak: ____%
- Used: ____ GB / ____ GB

**Network Throughput**:
- Average: ____ Gbps
- Peak: ____ Gbps
- Upload: ____ Gbps
- Download: ____ Gbps

**Packets Per Second (PPS)**:
- Average: ____ PPS
- Peak: ____ PPS
- Upload: ____ PPS
- Download: ____ PPS

**Tunnel Statistics**:
- Active Tunnels: ____
- Idle Tunnels: ____
- Failed Tunnels: ____

**Errors/Issues**: [None / Describe issues]

---

### Gateway Node: ipsecgw04

**CPU Utilization**:
- Average: ____%
- Peak: ____%
- Idle: ____%

**Memory Utilization**:
- Average: ____%
- Peak: ____%
- Used: ____ GB / ____ GB

**Network Throughput**:
- Average: ____ Gbps
- Peak: ____ Gbps
- Upload: ____ Gbps
- Download: ____ Gbps

**Packets Per Second (PPS)**:
- Average: ____ PPS
- Peak: ____ PPS
- Upload: ____ PPS
- Download: ____ PPS

**Tunnel Statistics**:
- Active Tunnels: ____
- Idle Tunnels: ____
- Failed Tunnels: ____

**Errors/Issues**: [None / Describe issues]

---

## Aggregate Results

**Total Throughput**: ____ Gbps
**Total PPS**: ____ PPS
**Average CPU Across Nodes**: ____%
**Average Memory Across Nodes**: ____%
**Total Active Tunnels**: ____
**Total Idle Tunnels**: ____

## Client Node Status

### prfclient01 (500 idle tunnels)
- Tunnels Up: ____
- Status: [OK / Issues]

### prfclient02 (8K endpoints)
- Endpoints Created: ____
- Active Tunnels: ____
- Status: [OK / Issues]

### prfclient03 (8K endpoints)
- Endpoints Created: ____
- Active Tunnels: ____
- Status: [OK / Issues]

### prfclient04 (8K endpoints)
- Endpoints Created: ____
- Active Tunnels: ____
- Status: [OK / Issues]

### prfclient05 (8K endpoints)
- Endpoints Created: ____
- Active Tunnels: ____
- Status: [OK / Issues]

## JMeter Results

**Total Requests**: ____
**Successful Requests**: ____
**Failed Requests**: ____
**Success Rate**: ____%
**Average Response Time**: ____ ms
**95th Percentile Response Time**: ____ ms
**99th Percentile Response Time**: ____ ms
**Throughput**: ____ requests/sec

## Comparison with Baseline

| Metric | Current Build | Baseline | Delta | Status |
|--------|--------------|----------|-------|--------|
| CPU Avg | ____% | ____% | ____% | [✅/⚠️/❌] |
| Memory Avg | ____% | ____% | ____% | [✅/⚠️/❌] |
| Throughput | ____ Gbps | ____ Gbps | ____ Gbps | [✅/⚠️/❌] |
| PPS | ____ | ____ | ____ | [✅/⚠️/❌] |
| Response Time | ____ ms | ____ ms | ____ ms | [✅/⚠️/❌] |

**Legend**:
- ✅ = Within acceptable range (< 5% regression)
- ⚠️ = Minor regression (5-10%)
- ❌ = Significant regression (> 10%)

## Issues Encountered

1. [Issue #1 description]
   - Severity: [Low / Medium / High / Critical]
   - Resolution: [How it was resolved / Workaround]

2. [Issue #2 description]
   - Severity: [Low / Medium / High / Critical]
   - Resolution: [How it was resolved / Workaround]

## Logs and Artifacts

**Grafana Dashboard**: [Link to dashboard]
**JMeter Results**: /home/seema/test_result.jtl
**Gateway Logs**:
- tunsvc.log: [Any notable errors/warnings]
- strongswan.log: [Any notable errors/warnings]

## Observations and Notes

[Add any observations, anomalies, or notes about the test run]

## Conclusion

**Overall Status**: [PASS / PASS with Issues / FAIL]
**Recommendation**: [Approve for release / Needs investigation / Block release]

**Summary**: [Brief summary of results and any action items]

---

## Sign-off

**Tested By**: __________
**Reviewed By**: __________
**Date**: __________
