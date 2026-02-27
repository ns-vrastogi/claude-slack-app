# ECGW Functional Test Automation

Automated test suite for ECGW functional testing on QA01 topology with Tenant 3624.

## Overview

This script automates the first 9 test cases from `ECGS_Functional_final.csv`:

1. **Test 1**: Web traffic forwarding test (CFW)
2. **Test 2**: Non-web traffic forwarding test (Proxy)
3. **Test 3**: Multiple tunnel traffic forwarding test
4. **Test 4**: Custom port traffic (SKIPPED as requested)
5. **Test 5**: All service validation
6. **Test 6**: Health Check - Status 200
7. **Test 7**: Health Check - Status 503 (CFW failure)
8. **Test 8**: Health Check - Status 503 (Proxy failure)
9. **Test 9**: Tunnel status on all ECGW

## Prerequisites

### System Requirements

- Python 3.7 or higher
- SSH access to QA01 infrastructure
- Passwordless SSH authentication configured for `ansible` user
- Access to the following hosts:
  - `pastrex01.iad0.netskope.com` (client machine)
  - `ecgw01.iad0.netskope.com` (ECGW node 1)
  - `ecgw02.iad0.netskope.com` (ECGW node 2)
  - `ecgw03.iad0.netskope.com` (ECGW node 3)

### Python Dependencies

Install required Python packages:

```bash
pip install urllib3
```

Or using a requirements file:

```bash
pip install -r requirements.txt
```

**requirements.txt**:
```
urllib3>=1.26.0
```

**Note**: The script uses the system's native SSH client (via subprocess) instead of paramiko, which ensures proper integration with ssh-agent and encrypted SSH keys.

### SSH Configuration

Ensure passwordless SSH access is configured for the `ansible` user:

```bash
# Test connectivity
ssh ansible@pastrex01.iad0.netskope.com "echo 'Connection OK'"
ssh ansible@ecgw01.iad0.netskope.com "echo 'Connection OK'"
ssh ansible@ecgw02.iad0.netskope.com "echo 'Connection OK'"
ssh ansible@ecgw03.iad0.netskope.com "echo 'Connection OK'"
```

## Installation

1. **Clone or download the script**:
   ```bash
   cd ~/.claude/skills/DITA/
   chmod +x ecgw_automation.py
   ```

2. **Install dependencies**:
   ```bash
   pip install paramiko urllib3
   ```

3. **Verify SSH access**:
   ```bash
   # Should connect without password prompt
   ssh ansible@pastrex01.iad0.netskope.com
   ```

## Usage

### Basic Execution

Run all tests sequentially:

```bash
python3 ecgw_automation.py
```

### Expected Output

The script will:
1. Display a header with test environment information
2. Execute each test case sequentially
3. Show real-time progress with colored output
4. Display a detailed summary at the end
5. Save results to a JSON file

**Example Output**:
```
================================================================================
           ECGW Functional Test Automation - QA01 Tenant 3624
================================================================================

Test Environment:
  Tenant ID: 3624
  Client: pastrex01.iad0.netskope.com
  ECGW Nodes: ecgw01.iad0.netskope.com, ecgw02.iad0.netskope.com, ecgw03.iad0.netskope.com
  CFW: 10.111.96.6:7777
  Proxy: 10.111.59.221:7777

================================================================================
                  [Test #1] Web Traffic Forwarding Test
--------------------------------------------------------------------------------

✓ Connected to pastrex01.iad0.netskope.com
✓ Connected to ecgw01.iad0.netskope.com

Checking which ECGW node has active traffic on gre156...
✓ Found active traffic on ecgw01.iad0.netskope.com: RX=1234, TX=5678

Sending ICMP traffic to 8.8.8.8...
✓ Test PASSED: Traffic forwarded successfully

...
```

### Test Results

#### Console Output
- **Green (✓)**: Test passed
- **Red (✗)**: Test failed
- **Yellow (⚠)**: Test error
- **Cyan (○)**: Test skipped

#### JSON Output
Results are automatically saved to:
```
ecgw_test_results_YYYYMMDD_HHMMSS.json
```

**JSON Structure**:
```json
{
  "timestamp": "2026-01-28T10:30:00.123456",
  "topology": { ... },
  "summary": {
    "total": 8,
    "passed": 7,
    "failed": 1,
    "errors": 0,
    "skipped": 0
  },
  "tests": [
    {
      "test_id": 1,
      "test_name": "Traffic Forwarding - Web traffic forwarding test",
      "status": "PASS",
      "duration": "5.23s",
      "error_message": null,
      "details": [...]
    },
    ...
  ]
}
```

## Test Details

### Test 1: Web Traffic Forwarding
- **Method**: Sends ICMP ping to `8.8.8.8` (CFW test destination)
- **Validation**: Checks GRE tunnel counter increase on active ECGW node
- **Duration**: ~10 seconds

### Test 2: Non-Web Traffic Forwarding
- **Method**: Downloads test file via wget (proxy path)
- **Validation**: Checks GRE tunnel counter increase
- **Duration**: ~15 seconds

### Test 3: Multiple Tunnel Traffic Forwarding
- **Method**: Tests traffic through both gre156 and gre157
- **Validation**: Verifies traffic goes through correct tunnel
- **Duration**: ~20 seconds

### Test 5: All Service Validation
- **Method**: Runs `supervisorctl status` on all 3 ECGW nodes
- **Validation**: Ensures all services are in RUNNING state
- **Duration**: ~5 seconds per node

### Test 6: Health Check Status 200
- **Method**: Curls CFW (port 8999) and Proxy (port 8990) health endpoints
- **Validation**: Both should return HTTP 200
- **Duration**: ~5 seconds

### Test 7: Health Check Status 503 (CFW Failure)
- **Method**: Blocks CFW health check port with iptables, waits, then removes rule
- **Validation**: Health check should fail (503 or timeout) while blocked
- **Duration**: ~30 seconds (includes cleanup)
- **Note**: Automatically cleans up iptables rules

### Test 8: Health Check Status 503 (Proxy Failure)
- **Method**: Blocks Proxy health check port with iptables, waits, then removes rule
- **Validation**: Health check should fail (503 or timeout) while blocked
- **Duration**: ~30 seconds (includes cleanup)
- **Note**: Automatically cleans up iptables rules

### Test 9: Tunnel Status on All ECGW
- **Method**: Runs `sudo vppctl show gre tunnel` on all ECGW nodes
- **Validation**: Verifies gre156 and gre157 exist on all nodes
- **Duration**: ~10 seconds

## Troubleshooting

### SSH Connection Issues

**Problem**: `Failed to connect to <hostname>` or `Private key file is encrypted`

**Solutions**:
1. Verify SSH key is loaded in ssh-agent:
   ```bash
   ssh-add -l
   ```
   If empty, add your key:
   ```bash
   ssh-add ~/.ssh/id_rsa
   ```

2. Test manual connection:
   ```bash
   ssh -v ansible@pastrex01.iad0.netskope.com
   ```
   If this works but the script doesn't, ensure ssh-agent is running:
   ```bash
   eval $(ssh-agent)
   ssh-add
   ```

3. Check SSH config (~/.ssh/config):
   ```
   Host *.netskope.com
       User ansible
       IdentityFile ~/.ssh/id_rsa
   ```

**Note**: The script now uses the system's native SSH client, which properly supports ssh-agent and encrypted keys. If manual SSH works, the script should work too.

### Permission Issues

**Problem**: `Permission denied` errors

**Solutions**:
1. Verify ansible user has sudo access:
   ```bash
   ssh ansible@ecgw01.iad0.netskope.com "sudo -l"
   ```

2. Check if passwordless sudo is configured:
   ```bash
   ssh ansible@ecgw01.iad0.netskope.com "sudo vppctl show version"
   ```

### VPP Command Issues

**Problem**: `vppctl` commands fail or timeout

**Solutions**:
1. Verify VPP is running:
   ```bash
   ssh ansible@ecgw01.iad0.netskope.com "sudo systemctl status vpp"
   ```

2. Check VPP socket permissions:
   ```bash
   ssh ansible@ecgw01.iad0.netskope.com "ls -la /run/vpp/cli.sock"
   ```

### Health Check Issues

**Problem**: Health checks return unexpected status codes

**Solutions**:
1. Verify network connectivity:
   ```bash
   ssh ansible@ecgw01.iad0.netskope.com "ping -c 3 10.111.96.6"
   ssh ansible@ecgw01.iad0.netskope.com "ping -c 3 10.111.59.221"
   ```

2. Test health check manually:
   ```bash
   ssh ansible@ecgw01.iad0.netskope.com "curl -v http://10.111.96.6:8999/health"
   ssh ansible@ecgw01.iad0.netskope.com "curl -v http://10.111.59.221:8990/health"
   ```

### Test Failures

**Problem**: Tests fail unexpectedly

**Solutions**:
1. Run tests individually by commenting out other tests in `run_all_tests()`
2. Increase timeout values in the script
3. Check if services are running:
   ```bash
   ssh ansible@ecgw01.iad0.netskope.com "sudo supervisorctl status"
   ```

## Script Architecture

### Class Structure

```
ECGWTestAutomation
├── TOPOLOGY (dict) - Environment configuration
├── __init__()
├── run_all_tests() - Main test orchestrator
├── test_01_web_traffic_forwarding()
├── test_02_non_web_traffic_forwarding()
├── test_03_multiple_tunnel_traffic_forwarding()
├── test_05_all_service_validation()
├── test_06_health_check_status_200()
├── test_07_health_check_status_503_cfw_failure()
├── test_08_health_check_status_503_proxy_failure()
├── test_09_tunnel_status_all_ecgw()
├── get_ssh_client() - SSH connection manager
├── get_gre_tunnel_counters() - VPP counter extraction
├── find_active_ecgw_node() - Active node discovery
├── print_summary() - Results reporting
└── save_results_json() - JSON export

SSHClient
├── connect() - Establish SSH connection
├── execute_command() - Run remote command
└── close() - Close connection

TestResult
├── start() - Mark test as started
├── pass_test() - Mark test as passed
├── fail_test() - Mark test as failed
├── error_test() - Mark test as errored
└── duration() - Calculate test duration
```

### Key Features

- **Automatic SSH connection pooling**: Reuses connections across tests
- **Colored terminal output**: Easy visual feedback
- **Detailed logging**: Every step is logged with context
- **Error handling**: Graceful failure with cleanup
- **JSON export**: Machine-readable results
- **Modular design**: Easy to add new tests

## Extending the Script

### Adding a New Test

1. **Create a test method**:
   ```python
   def test_10_my_new_test(self) -> TestResult:
       """Test Case 10: My new test"""
       result = TestResult(10, "My New Test")
       result.start()

       self.print_test_header(10, "My New Test")

       try:
           # Test implementation
           client = self.get_ssh_client(self.TOPOLOGY["client_machine"])
           # ... test logic ...

           result.pass_test("Test passed successfully")
       except Exception as e:
           result.error_test(f"Test execution error: {str(e)}")

       return result
   ```

2. **Add to test list**:
   ```python
   def run_all_tests(self):
       test_cases = [
           # ... existing tests ...
           self.test_10_my_new_test,
       ]
   ```

### Customizing Topology

Edit the `TOPOLOGY` dictionary in the `ECGWTestAutomation` class:

```python
TOPOLOGY = {
    "tenant_id": 3624,  # Change tenant ID
    "client_machine": "pastrex01.iad0.netskope.com",
    "ecgw_nodes": [
        "ecgw01.iad0.netskope.com",
        "ecgw02.iad0.netskope.com",
        "ecgw03.iad0.netskope.com"
    ],
    # ... customize other parameters ...
}
```

## Best Practices

1. **Run in non-production environment first**: Always test in QA before production
2. **Monitor resource usage**: Tests generate traffic and may impact other services
3. **Sequential execution**: Tests run one by one to avoid interference
4. **Automatic cleanup**: Destructive tests (iptables) clean up automatically
5. **Error recovery**: Script handles errors gracefully and continues

## Known Limitations

1. **Custom port traffic (Test 4)**: Not implemented as requested
2. **Arista switch access**: No direct access, tested via GRE tunnels
3. **CFW/Proxy services**: Cannot directly control these services
4. **Single topology**: Hardcoded for QA01 Tenant 3624
5. **Health check simulation**: Uses iptables blocking instead of actual service failure

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review test logs and JSON output
3. Manually verify SSH access and VPP commands
4. Consult the ECGW skill documentation: `~/.claude/skills/ecgw-skill/`

## Version History

- **v1.0** (2026-01-28): Initial release with 8 automated test cases (1-3, 5-9)
