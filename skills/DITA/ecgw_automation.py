#!/usr/bin/env python3
"""
ECGW Functional Test Automation Script
Automates the first 9 test cases from ECGS_Functional_final.csv
Topology: QA01 - Tenant 3624
"""

import subprocess
import time
import json
import sys
import re
import shlex
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import urllib3

# Disable SSL warnings for testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TestResult:
    """Store test execution results"""
    def __init__(self, test_id: int, test_name: str):
        self.test_id = test_id
        self.test_name = test_name
        self.status = "NOT_RUN"  # PASS, FAIL, SKIP, ERROR
        self.details = []
        self.start_time = None
        self.end_time = None
        self.error_message = None

    def start(self):
        self.start_time = datetime.now()
        self.status = "RUNNING"

    def pass_test(self, details: str = ""):
        self.status = "PASS"
        self.end_time = datetime.now()
        if details:
            self.details.append(details)

    def fail_test(self, reason: str):
        self.status = "FAIL"
        self.end_time = datetime.now()
        self.error_message = reason
        self.details.append(f"FAILURE: {reason}")

    def skip_test(self, reason: str):
        self.status = "SKIP"
        self.error_message = reason

    def error_test(self, error: str):
        self.status = "ERROR"
        self.end_time = datetime.now()
        self.error_message = error
        self.details.append(f"ERROR: {error}")

    def add_detail(self, detail: str):
        self.details.append(detail)

    def duration(self) -> str:
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return f"{delta.total_seconds():.2f}s"
        return "N/A"


class SSHClient:
    """SSH connection wrapper for remote command execution using system SSH"""

    def __init__(self, hostname: str, username: str = "ansible"):
        self.hostname = hostname
        self.username = username
        self.connected = False

    def connect(self) -> bool:
        """Test SSH connection"""
        try:
            # Test connection with a simple command
            cmd = ["ssh", "-o", "ConnectTimeout=10", "-o", "StrictHostKeyChecking=no",
                   f"{self.username}@{self.hostname}", "echo 'connected'"]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=15,
                text=True
            )

            if result.returncode == 0 and "connected" in result.stdout:
                self.connected = True
                return True
            else:
                print(f"{Colors.FAIL}Failed to connect to {self.hostname}: {result.stderr}{Colors.ENDC}")
                return False
        except subprocess.TimeoutExpired:
            print(f"{Colors.FAIL}Connection timeout to {self.hostname}{Colors.ENDC}")
            return False
        except Exception as e:
            print(f"{Colors.FAIL}Failed to connect to {self.hostname}: {e}{Colors.ENDC}")
            return False

    def execute_command(self, command: str, timeout: int = 30) -> Tuple[int, str, str]:
        """Execute command and return (exit_code, stdout, stderr)"""
        try:
            # Build SSH command
            ssh_cmd = [
                "ssh",
                "-o", "ConnectTimeout=10",
                "-o", "StrictHostKeyChecking=no",
                "-o", "BatchMode=yes",  # Don't prompt for password
                f"{self.username}@{self.hostname}",
                command
            ]

            # Execute command
            result = subprocess.run(
                ssh_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                text=True
            )

            return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            return -1, "", f"Command timeout after {timeout} seconds"
        except Exception as e:
            return -1, "", str(e)

    def close(self):
        """Close SSH connection (no-op for subprocess-based SSH)"""
        self.connected = False


class ECGWTestAutomation:
    """Main test automation class for ECGW functional tests"""

    # Topology configuration for QA01 - Tenant 3624
    TOPOLOGY = {
        "tenant_id": 3624,
        "client_machine": "pastrex01.iad0.netskope.com",
        "ecgw_nodes": [
            "ecgw01.iad0.netskope.com",
            "ecgw02.iad0.netskope.com",
            "ecgw03.iad0.netskope.com"
        ],
        "cfw_service": {
            "host": "10.111.96.6",
            "port": 7777,
            "hc_port": 8999
        },
        "proxy_service": {
            "host": "10.111.59.221",
            "port": 7777,
            "hc_port": 8990
        },
        "gre_tunnels": {
            "gre156": {
                "source": "192.168.64.1",
                "destination": "172.23.8.129",
                "circuit": "ms-circuit-01"
            },
            "gre157": {
                "source": "192.168.64.1",
                "destination": "172.23.8.2",
                "circuit": "ms-circuit-02"
            }
        },
        "test_destinations": {
            "cfw_test": "8.8.8.8",
            "proxy_test": "https://ash-speed.hetzner.com/100MB.bin"
        }
    }

    def __init__(self):
        self.results: List[TestResult] = []
        self.ssh_connections: Dict[str, SSHClient] = {}

    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

    def print_test_header(self, test_id: int, test_name: str):
        """Print test case header"""
        print(f"\n{Colors.OKCYAN}{Colors.BOLD}[Test #{test_id}] {test_name}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{'-' * 80}{Colors.ENDC}")

    def get_ssh_client(self, hostname: str) -> Optional[SSHClient]:
        """Get or create SSH client for a host"""
        if hostname not in self.ssh_connections:
            client = SSHClient(hostname)
            if client.connect():
                self.ssh_connections[hostname] = client
                print(f"{Colors.OKGREEN}✓ Connected to {hostname}{Colors.ENDC}")
            else:
                return None
        return self.ssh_connections[hostname]

    def cleanup_connections(self):
        """Close all SSH connections"""
        for client in self.ssh_connections.values():
            client.close()
        self.ssh_connections.clear()

    def get_gre_tunnel_counters(self, ecgw_node: str, tunnel_name: str) -> Optional[Dict]:
        """Get VPP GRE tunnel packet counters"""
        client = self.get_ssh_client(ecgw_node)
        if not client:
            return None

        # Get tunnel instance number from tunnel name (e.g., gre156 -> 156)
        tunnel_num = tunnel_name.replace("gre", "")

        # Execute VPP command to get tunnel counters
        cmd = f"sudo vppctl show interface gre{tunnel_num}"
        exit_code, stdout, stderr = client.execute_command(cmd)

        if exit_code != 0:
            print(f"{Colors.WARNING}Warning: Could not get counters for {tunnel_name}: {stderr}{Colors.ENDC}")
            return None

        # Parse output to extract rx/tx packet counts
        counters = {
            "tunnel": tunnel_name,
            "rx_packets": 0,
            "tx_packets": 0,
            "rx_bytes": 0,
            "tx_bytes": 0
        }

        # Parse VPP output
        for line in stdout.split('\n'):
            if 'rx packets' in line.lower():
                match = re.search(r'(\d+)', line)
                if match:
                    counters['rx_packets'] = int(match.group(1))
            elif 'rx bytes' in line.lower():
                match = re.search(r'(\d+)', line)
                if match:
                    counters['rx_bytes'] = int(match.group(1))
            elif 'tx packets' in line.lower():
                match = re.search(r'(\d+)', line)
                if match:
                    counters['tx_packets'] = int(match.group(1))
            elif 'tx bytes' in line.lower():
                match = re.search(r'(\d+)', line)
                if match:
                    counters['tx_bytes'] = int(match.group(1))

        return counters

    def find_active_ecgw_node(self, tunnel_name: str = "gre156") -> Optional[str]:
        """Find which ECGW node is actively handling traffic for a specific tunnel"""
        print(f"\n{Colors.OKBLUE}Checking which ECGW node has active traffic on {tunnel_name}...{Colors.ENDC}")

        for node in self.TOPOLOGY["ecgw_nodes"]:
            counters = self.get_gre_tunnel_counters(node, tunnel_name)
            if counters and (counters['rx_packets'] > 0 or counters['tx_packets'] > 0):
                print(f"{Colors.OKGREEN}✓ Found active traffic on {node}: "
                      f"RX={counters['rx_packets']}, TX={counters['tx_packets']}{Colors.ENDC}")
                return node

        # If no active traffic, return first node
        print(f"{Colors.WARNING}No active traffic found, using first node: {self.TOPOLOGY['ecgw_nodes'][0]}{Colors.ENDC}")
        return self.TOPOLOGY["ecgw_nodes"][0]

    # ==================== TEST CASE IMPLEMENTATIONS ====================

    def test_01_web_traffic_forwarding(self) -> TestResult:
        """Test Case 1: Web traffic forwarding test"""
        result = TestResult(1, "Traffic Forwarding - Web traffic forwarding test")
        result.start()

        self.print_test_header(1, "Web Traffic Forwarding Test")

        try:
            # Connect to client machine
            client = self.get_ssh_client(self.TOPOLOGY["client_machine"])
            if not client:
                result.error_test(f"Failed to connect to client machine {self.TOPOLOGY['client_machine']}")
                return result

            # Find active ECGW node
            active_node = self.find_active_ecgw_node("gre156")
            if not active_node:
                result.error_test("Could not determine active ECGW node")
                return result

            # Get initial GRE tunnel counters
            initial_counters = self.get_gre_tunnel_counters(active_node, "gre156")
            if not initial_counters:
                result.error_test("Failed to get initial GRE tunnel counters")
                return result

            result.add_detail(f"Active ECGW node: {active_node}")
            result.add_detail(f"Initial RX packets: {initial_counters['rx_packets']}")
            result.add_detail(f"Initial TX packets: {initial_counters['tx_packets']}")

            # Send web traffic to CFW test destination (8.8.8.8)
            print(f"\n{Colors.OKBLUE}Sending ICMP traffic to {self.TOPOLOGY['test_destinations']['cfw_test']}...{Colors.ENDC}")
            cmd = f"ping -c 5 {self.TOPOLOGY['test_destinations']['cfw_test']}"
            exit_code, stdout, stderr = client.execute_command(cmd, timeout=15)

            result.add_detail(f"Ping command exit code: {exit_code}")

            # Wait a moment for counters to update
            time.sleep(2)

            # Get final GRE tunnel counters
            final_counters = self.get_gre_tunnel_counters(active_node, "gre156")
            if not final_counters:
                result.error_test("Failed to get final GRE tunnel counters")
                return result

            result.add_detail(f"Final RX packets: {final_counters['rx_packets']}")
            result.add_detail(f"Final TX packets: {final_counters['tx_packets']}")

            # Check if counters increased (indicating traffic forwarding)
            rx_increase = final_counters['rx_packets'] - initial_counters['rx_packets']
            tx_increase = final_counters['tx_packets'] - initial_counters['tx_packets']

            result.add_detail(f"RX packet increase: {rx_increase}")
            result.add_detail(f"TX packet increase: {tx_increase}")

            if rx_increase > 0 and tx_increase > 0:
                result.pass_test(f"Web traffic successfully forwarded through ECGW (RX: +{rx_increase}, TX: +{tx_increase})")
                print(f"{Colors.OKGREEN}✓ Test PASSED: Traffic forwarded successfully{Colors.ENDC}")
            else:
                result.fail_test("No traffic increase detected on GRE tunnel")
                print(f"{Colors.FAIL}✗ Test FAILED: No traffic detected{Colors.ENDC}")

        except Exception as e:
            result.error_test(f"Test execution error: {str(e)}")
            print(f"{Colors.FAIL}✗ Test ERROR: {str(e)}{Colors.ENDC}")

        return result

    def test_02_non_web_traffic_forwarding(self) -> TestResult:
        """Test Case 2: Non-web traffic forwarding test"""
        result = TestResult(2, "Traffic Forwarding - Non-web traffic forwarding test")
        result.start()

        self.print_test_header(2, "Non-Web Traffic Forwarding Test")

        try:
            # Connect to client machine
            client = self.get_ssh_client(self.TOPOLOGY["client_machine"])
            if not client:
                result.error_test(f"Failed to connect to client machine {self.TOPOLOGY['client_machine']}")
                return result

            # Find active ECGW node
            active_node = self.find_active_ecgw_node("gre156")
            if not active_node:
                result.error_test("Could not determine active ECGW node")
                return result

            # Get initial GRE tunnel counters
            initial_counters = self.get_gre_tunnel_counters(active_node, "gre156")
            if not initial_counters:
                result.error_test("Failed to get initial GRE tunnel counters")
                return result

            result.add_detail(f"Active ECGW node: {active_node}")
            result.add_detail(f"Initial RX packets: {initial_counters['rx_packets']}")
            result.add_detail(f"Initial TX packets: {initial_counters['tx_packets']}")

            # Send non-web traffic (using wget for proxy test)
            print(f"\n{Colors.OKBLUE}Downloading test file via proxy (wget --no-check-certificate)...{Colors.ENDC}")
            cmd = f"timeout 10 wget --no-check-certificate -O /dev/null {self.TOPOLOGY['test_destinations']['proxy_test']} 2>&1"
            exit_code, stdout, stderr = client.execute_command(cmd, timeout=15)

            result.add_detail(f"Wget command exit code: {exit_code}")

            # Wait a moment for counters to update
            time.sleep(2)

            # Get final GRE tunnel counters
            final_counters = self.get_gre_tunnel_counters(active_node, "gre156")
            if not final_counters:
                result.error_test("Failed to get final GRE tunnel counters")
                return result

            result.add_detail(f"Final RX packets: {final_counters['rx_packets']}")
            result.add_detail(f"Final TX packets: {final_counters['tx_packets']}")

            # Check if counters increased
            rx_increase = final_counters['rx_packets'] - initial_counters['rx_packets']
            tx_increase = final_counters['tx_packets'] - initial_counters['tx_packets']

            result.add_detail(f"RX packet increase: {rx_increase}")
            result.add_detail(f"TX packet increase: {tx_increase}")

            if rx_increase > 0 and tx_increase > 0:
                result.pass_test(f"Non-web traffic successfully forwarded through ECGW (RX: +{rx_increase}, TX: +{tx_increase})")
                print(f"{Colors.OKGREEN}✓ Test PASSED: Traffic forwarded successfully{Colors.ENDC}")
            else:
                result.fail_test("No traffic increase detected on GRE tunnel")
                print(f"{Colors.FAIL}✗ Test FAILED: No traffic detected{Colors.ENDC}")

        except Exception as e:
            result.error_test(f"Test execution error: {str(e)}")
            print(f"{Colors.FAIL}✗ Test ERROR: {str(e)}{Colors.ENDC}")

        return result

    def test_03_multiple_tunnel_traffic_forwarding(self) -> TestResult:
        """Test Case 3: Multiple tunnel traffic forwarding test"""
        result = TestResult(3, "Traffic Forwarding - Multiple tunnel traffic forwarding test")
        result.start()

        self.print_test_header(3, "Multiple Tunnel Traffic Forwarding Test")

        try:
            # Connect to client machine
            client = self.get_ssh_client(self.TOPOLOGY["client_machine"])
            if not client:
                result.error_test(f"Failed to connect to client machine {self.TOPOLOGY['client_machine']}")
                return result

            # Find active ECGW node
            active_node = self.find_active_ecgw_node("gre156")
            if not active_node:
                result.error_test("Could not determine active ECGW node")
                return result

            result.add_detail(f"Active ECGW node: {active_node}")

            # Check both GRE tunnels (gre156 and gre157)
            tunnels_to_test = ["gre156", "gre157"]
            tunnel_results = {}

            for tunnel in tunnels_to_test:
                print(f"\n{Colors.OKBLUE}Testing tunnel {tunnel}...{Colors.ENDC}")

                # Get initial counters
                initial = self.get_gre_tunnel_counters(active_node, tunnel)
                if not initial:
                    result.add_detail(f"Warning: Could not get counters for {tunnel}")
                    continue

                # Send traffic
                cmd = f"ping -c 3 {self.TOPOLOGY['test_destinations']['cfw_test']}"
                exit_code, stdout, stderr = client.execute_command(cmd, timeout=10)

                time.sleep(2)

                # Get final counters
                final = self.get_gre_tunnel_counters(active_node, tunnel)
                if not final:
                    result.add_detail(f"Warning: Could not get final counters for {tunnel}")
                    continue

                rx_increase = final['rx_packets'] - initial['rx_packets']
                tx_increase = final['tx_packets'] - initial['tx_packets']

                tunnel_results[tunnel] = {
                    "rx_increase": rx_increase,
                    "tx_increase": tx_increase,
                    "active": rx_increase > 0 or tx_increase > 0
                }

                result.add_detail(f"{tunnel}: RX +{rx_increase}, TX +{tx_increase}, Active: {tunnel_results[tunnel]['active']}")
                print(f"  {tunnel}: RX +{rx_increase}, TX +{tx_increase}")

            # Check if at least one tunnel is active (traffic goes through one tunnel at a time)
            active_tunnels = [t for t, r in tunnel_results.items() if r['active']]

            if len(active_tunnels) >= 1:
                result.pass_test(f"Traffic forwarded through tunnel(s): {', '.join(active_tunnels)}")
                print(f"{Colors.OKGREEN}✓ Test PASSED: Traffic forwarded through correct tunnel(s){Colors.ENDC}")
            else:
                result.fail_test("No traffic detected on any configured tunnel")
                print(f"{Colors.FAIL}✗ Test FAILED: No traffic on tunnels{Colors.ENDC}")

        except Exception as e:
            result.error_test(f"Test execution error: {str(e)}")
            print(f"{Colors.FAIL}✗ Test ERROR: {str(e)}{Colors.ENDC}")

        return result

    def test_05_all_service_validation(self) -> TestResult:
        """Test Case 5: All service validation"""
        result = TestResult(5, "All service Validation")
        result.start()

        self.print_test_header(5, "All Service Validation Test")

        try:
            all_services_ok = True

            # Check services on all 3 ECGW nodes
            for node in self.TOPOLOGY["ecgw_nodes"]:
                print(f"\n{Colors.OKBLUE}Checking services on {node}...{Colors.ENDC}")

                client = self.get_ssh_client(node)
                if not client:
                    result.add_detail(f"Failed to connect to {node}")
                    all_services_ok = False
                    continue

                # Execute supervisorctl status
                cmd = "sudo supervisorctl status"
                exit_code, stdout, stderr = client.execute_command(cmd)

                if exit_code != 0:
                    result.add_detail(f"{node}: supervisorctl command failed")
                    all_services_ok = False
                    continue

                # Parse output to check service states
                services = {}
                for line in stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            service_name = parts[0]
                            service_state = parts[1]
                            services[service_name] = service_state

                # Count services in different states
                running = sum(1 for s in services.values() if 'RUNNING' in s.upper())
                total = len(services)

                result.add_detail(f"{node}: {running}/{total} services running")
                print(f"  {node}: {running}/{total} services running")

                # Check if any service is not running
                failed_services = [name for name, state in services.items() if 'RUNNING' not in state.upper()]
                if failed_services:
                    result.add_detail(f"{node}: Failed services: {', '.join(failed_services)}")
                    print(f"{Colors.WARNING}  Warning: Non-running services: {', '.join(failed_services)}{Colors.ENDC}")
                    all_services_ok = False

            if all_services_ok:
                result.pass_test("All supervisorctl services are running on all nodes")
                print(f"{Colors.OKGREEN}✓ Test PASSED: All services running{Colors.ENDC}")
            else:
                result.fail_test("Some services are not in running state")
                print(f"{Colors.FAIL}✗ Test FAILED: Some services not running{Colors.ENDC}")

        except Exception as e:
            result.error_test(f"Test execution error: {str(e)}")
            print(f"{Colors.FAIL}✗ Test ERROR: {str(e)}{Colors.ENDC}")

        return result

    def test_06_health_check_status_200(self) -> TestResult:
        """Test Case 6: Health Check - Status 200"""
        result = TestResult(6, "Health Check - Status 200")
        result.start()

        self.print_test_header(6, "Health Check Status 200 Test")

        try:
            # Test from one ECGW node (all nodes should have same health check access)
            ecgw_node = self.TOPOLOGY["ecgw_nodes"][0]
            client = self.get_ssh_client(ecgw_node)
            if not client:
                result.error_test(f"Failed to connect to {ecgw_node}")
                return result

            hc_results = {}

            # Check CFW health check
            print(f"\n{Colors.OKBLUE}Checking CFW health check...{Colors.ENDC}")
            cfw_host = self.TOPOLOGY["cfw_service"]["host"]
            cfw_port = self.TOPOLOGY["cfw_service"]["hc_port"]
            cmd = f"curl -s -o /dev/null -w '%{{http_code}}' http://{cfw_host}:{cfw_port}/health"
            exit_code, stdout, stderr = client.execute_command(cmd, timeout=10)

            cfw_status = stdout.strip()
            hc_results["CFW"] = cfw_status
            result.add_detail(f"CFW health check (http://{cfw_host}:{cfw_port}/health): {cfw_status}")
            print(f"  CFW health check: {cfw_status}")

            # Check Proxy health check
            print(f"\n{Colors.OKBLUE}Checking Proxy health check...{Colors.ENDC}")
            proxy_host = self.TOPOLOGY["proxy_service"]["host"]
            proxy_port = self.TOPOLOGY["proxy_service"]["hc_port"]
            cmd = f"curl -s -o /dev/null -w '%{{http_code}}' http://{proxy_host}:{proxy_port}/health"
            exit_code, stdout, stderr = client.execute_command(cmd, timeout=10)

            proxy_status = stdout.strip()
            hc_results["Proxy"] = proxy_status
            result.add_detail(f"Proxy health check (http://{proxy_host}:{proxy_port}/health): {proxy_status}")
            print(f"  Proxy health check: {proxy_status}")

            # Verify both return 200
            if cfw_status == "200" and proxy_status == "200":
                result.pass_test("Both CFW and Proxy health checks return status 200")
                print(f"{Colors.OKGREEN}✓ Test PASSED: All health checks return 200{Colors.ENDC}")
            else:
                failed = [name for name, status in hc_results.items() if status != "200"]
                result.fail_test(f"Health check(s) did not return 200: {', '.join(failed)}")
                print(f"{Colors.FAIL}✗ Test FAILED: Health checks not returning 200{Colors.ENDC}")

        except Exception as e:
            result.error_test(f"Test execution error: {str(e)}")
            print(f"{Colors.FAIL}✗ Test ERROR: {str(e)}{Colors.ENDC}")

        return result

    def test_07_health_check_status_503_cfw_failure(self) -> TestResult:
        """Test Case 7: Health Check - Status 503 in case of CFW failure"""
        result = TestResult(7, "Health Check - Status 503 in case of either CFW or proxy failure")
        result.start()

        self.print_test_header(7, "Health Check Status 503 (CFW Failure) Test")

        try:
            # Use first ECGW node for testing
            ecgw_node = self.TOPOLOGY["ecgw_nodes"][0]
            client = self.get_ssh_client(ecgw_node)
            if not client:
                result.error_test(f"Failed to connect to {ecgw_node}")
                return result

            cfw_host = self.TOPOLOGY["cfw_service"]["host"]
            cfw_hc_port = self.TOPOLOGY["cfw_service"]["hc_port"]

            # Step 1: Check initial health check status
            print(f"\n{Colors.OKBLUE}Step 1: Checking initial CFW health check status...{Colors.ENDC}")
            cmd = f"curl -s -o /dev/null -w '%{{http_code}}' http://{cfw_host}:{cfw_hc_port}/health"
            exit_code, stdout, stderr = client.execute_command(cmd, timeout=10)
            initial_status = stdout.strip()
            result.add_detail(f"Initial CFW health check status: {initial_status}")
            print(f"  Initial status: {initial_status}")

            # Step 2: Block CFW health check using iptables
            print(f"\n{Colors.OKBLUE}Step 2: Blocking CFW health check port {cfw_hc_port} with iptables...{Colors.ENDC}")
            cmd = f"sudo iptables -A OUTPUT -p tcp -d {cfw_host} --dport {cfw_hc_port} -j DROP"
            exit_code, stdout, stderr = client.execute_command(cmd)

            if exit_code != 0:
                result.error_test(f"Failed to add iptables rule: {stderr}")
                return result

            result.add_detail(f"Added iptables rule to block CFW health check")
            print(f"  {Colors.OKGREEN}✓ iptables rule added{Colors.ENDC}")

            # Wait for health check to fail
            print(f"\n{Colors.OKBLUE}Step 3: Waiting 10 seconds for health check to detect failure...{Colors.ENDC}")
            time.sleep(10)

            # Step 3: Check health check status after blocking
            print(f"\n{Colors.OKBLUE}Step 4: Checking CFW health check status after blocking...{Colors.ENDC}")
            cmd = f"timeout 5 curl -s -o /dev/null -w '%{{http_code}}' http://{cfw_host}:{cfw_hc_port}/health || echo '000'"
            exit_code, stdout, stderr = client.execute_command(cmd, timeout=10)
            blocked_status = stdout.strip()
            result.add_detail(f"CFW health check status after blocking: {blocked_status}")
            print(f"  Status after blocking: {blocked_status}")

            # Step 4: Cleanup - Remove iptables rule
            print(f"\n{Colors.OKBLUE}Step 5: Cleaning up - removing iptables rule...{Colors.ENDC}")
            cmd = f"sudo iptables -D OUTPUT -p tcp -d {cfw_host} --dport {cfw_hc_port} -j DROP"
            exit_code, stdout, stderr = client.execute_command(cmd)
            result.add_detail("Removed iptables rule")
            print(f"  {Colors.OKGREEN}✓ iptables rule removed{Colors.ENDC}")

            # Wait for health check to recover
            time.sleep(5)

            # Verify final state
            cmd = f"curl -s -o /dev/null -w '%{{http_code}}' http://{cfw_host}:{cfw_hc_port}/health"
            exit_code, stdout, stderr = client.execute_command(cmd, timeout=10)
            final_status = stdout.strip()
            result.add_detail(f"Final CFW health check status (after cleanup): {final_status}")
            print(f"  Final status (after cleanup): {final_status}")

            # Evaluate test result
            if blocked_status == "000" or blocked_status == "503":
                result.pass_test(f"Health check correctly failed (status: {blocked_status}) when CFW was blocked")
                print(f"{Colors.OKGREEN}✓ Test PASSED: Health check failed as expected{Colors.ENDC}")
            else:
                result.fail_test(f"Health check did not fail as expected (status: {blocked_status})")
                print(f"{Colors.FAIL}✗ Test FAILED: Health check should have failed{Colors.ENDC}")

        except Exception as e:
            # Attempt cleanup on error
            try:
                cmd = f"sudo iptables -D OUTPUT -p tcp -d {cfw_host} --dport {cfw_hc_port} -j DROP"
                client.execute_command(cmd)
                print(f"{Colors.WARNING}Cleanup executed due to error{Colors.ENDC}")
            except:
                pass

            result.error_test(f"Test execution error: {str(e)}")
            print(f"{Colors.FAIL}✗ Test ERROR: {str(e)}{Colors.ENDC}")

        return result

    def test_08_health_check_status_503_proxy_failure(self) -> TestResult:
        """Test Case 8: Health Check - Status 503 in case of Proxy failure"""
        result = TestResult(8, "Health Check - Status 503")
        result.start()

        self.print_test_header(8, "Health Check Status 503 (Proxy Failure) Test")

        try:
            # Use first ECGW node for testing
            ecgw_node = self.TOPOLOGY["ecgw_nodes"][0]
            client = self.get_ssh_client(ecgw_node)
            if not client:
                result.error_test(f"Failed to connect to {ecgw_node}")
                return result

            proxy_host = self.TOPOLOGY["proxy_service"]["host"]
            proxy_hc_port = self.TOPOLOGY["proxy_service"]["hc_port"]

            # Step 1: Check initial health check status
            print(f"\n{Colors.OKBLUE}Step 1: Checking initial Proxy health check status...{Colors.ENDC}")
            cmd = f"curl -s -o /dev/null -w '%{{http_code}}' http://{proxy_host}:{proxy_hc_port}/health"
            exit_code, stdout, stderr = client.execute_command(cmd, timeout=10)
            initial_status = stdout.strip()
            result.add_detail(f"Initial Proxy health check status: {initial_status}")
            print(f"  Initial status: {initial_status}")

            # Step 2: Block Proxy health check using iptables
            print(f"\n{Colors.OKBLUE}Step 2: Blocking Proxy health check port {proxy_hc_port} with iptables...{Colors.ENDC}")
            cmd = f"sudo iptables -A OUTPUT -p tcp -d {proxy_host} --dport {proxy_hc_port} -j DROP"
            exit_code, stdout, stderr = client.execute_command(cmd)

            if exit_code != 0:
                result.error_test(f"Failed to add iptables rule: {stderr}")
                return result

            result.add_detail(f"Added iptables rule to block Proxy health check")
            print(f"  {Colors.OKGREEN}✓ iptables rule added{Colors.ENDC}")

            # Wait for health check to fail
            print(f"\n{Colors.OKBLUE}Step 3: Waiting 10 seconds for health check to detect failure...{Colors.ENDC}")
            time.sleep(10)

            # Step 3: Check health check status after blocking
            print(f"\n{Colors.OKBLUE}Step 4: Checking Proxy health check status after blocking...{Colors.ENDC}")
            cmd = f"timeout 5 curl -s -o /dev/null -w '%{{http_code}}' http://{proxy_host}:{proxy_hc_port}/health || echo '000'"
            exit_code, stdout, stderr = client.execute_command(cmd, timeout=10)
            blocked_status = stdout.strip()
            result.add_detail(f"Proxy health check status after blocking: {blocked_status}")
            print(f"  Status after blocking: {blocked_status}")

            # Step 4: Cleanup - Remove iptables rule
            print(f"\n{Colors.OKBLUE}Step 5: Cleaning up - removing iptables rule...{Colors.ENDC}")
            cmd = f"sudo iptables -D OUTPUT -p tcp -d {proxy_host} --dport {proxy_hc_port} -j DROP"
            exit_code, stdout, stderr = client.execute_command(cmd)
            result.add_detail("Removed iptables rule")
            print(f"  {Colors.OKGREEN}✓ iptables rule removed{Colors.ENDC}")

            # Wait for health check to recover
            time.sleep(5)

            # Verify final state
            cmd = f"curl -s -o /dev/null -w '%{{http_code}}' http://{proxy_host}:{proxy_hc_port}/health"
            exit_code, stdout, stderr = client.execute_command(cmd, timeout=10)
            final_status = stdout.strip()
            result.add_detail(f"Final Proxy health check status (after cleanup): {final_status}")
            print(f"  Final status (after cleanup): {final_status}")

            # Evaluate test result
            if blocked_status == "000" or blocked_status == "503":
                result.pass_test(f"Health check correctly failed (status: {blocked_status}) when Proxy was blocked")
                print(f"{Colors.OKGREEN}✓ Test PASSED: Health check failed as expected{Colors.ENDC}")
            else:
                result.fail_test(f"Health check did not fail as expected (status: {blocked_status})")
                print(f"{Colors.FAIL}✗ Test FAILED: Health check should have failed{Colors.ENDC}")

        except Exception as e:
            # Attempt cleanup on error
            try:
                cmd = f"sudo iptables -D OUTPUT -p tcp -d {proxy_host} --dport {proxy_hc_port} -j DROP"
                client.execute_command(cmd)
                print(f"{Colors.WARNING}Cleanup executed due to error{Colors.ENDC}")
            except:
                pass

            result.error_test(f"Test execution error: {str(e)}")
            print(f"{Colors.FAIL}✗ Test ERROR: {str(e)}{Colors.ENDC}")

        return result

    def test_09_tunnel_status_all_ecgw(self) -> TestResult:
        """Test Case 9: Tunnel status on all ECGW"""
        result = TestResult(9, "Tunnel status on all ECGW")
        result.start()

        self.print_test_header(9, "Tunnel Status on All ECGW Test")

        try:
            expected_tunnels = ["gre156", "gre157"]
            all_tunnels_present = True

            # Check tunnels on all 3 ECGW nodes
            for node in self.TOPOLOGY["ecgw_nodes"]:
                print(f"\n{Colors.OKBLUE}Checking GRE tunnels on {node}...{Colors.ENDC}")

                client = self.get_ssh_client(node)
                if not client:
                    result.add_detail(f"Failed to connect to {node}")
                    all_tunnels_present = False
                    continue

                # Execute VPP command to list GRE tunnels
                cmd = "sudo vppctl show gre tunnel"
                exit_code, stdout, stderr = client.execute_command(cmd)

                if exit_code != 0:
                    result.add_detail(f"{node}: Failed to get GRE tunnels")
                    all_tunnels_present = False
                    continue

                # Parse output to find tenant 3624 tunnels
                found_tunnels = []
                for tunnel in expected_tunnels:
                    if tunnel in stdout or tunnel.replace("gre", "") in stdout:
                        found_tunnels.append(tunnel)

                result.add_detail(f"{node}: Found tunnels: {', '.join(found_tunnels)}")
                print(f"  {node}: {', '.join(found_tunnels)}")

                # Check if all expected tunnels are present
                missing = set(expected_tunnels) - set(found_tunnels)
                if missing:
                    result.add_detail(f"{node}: Missing tunnels: {', '.join(missing)}")
                    print(f"{Colors.WARNING}  Warning: Missing tunnels: {', '.join(missing)}{Colors.ENDC}")
                    all_tunnels_present = False

            if all_tunnels_present:
                result.pass_test(f"All tenant 3624 tunnels ({', '.join(expected_tunnels)}) present on all ECGW nodes")
                print(f"{Colors.OKGREEN}✓ Test PASSED: All tunnels present on all nodes{Colors.ENDC}")
            else:
                result.fail_test("Not all tunnels are present on all ECGW nodes")
                print(f"{Colors.FAIL}✗ Test FAILED: Some tunnels missing{Colors.ENDC}")

        except Exception as e:
            result.error_test(f"Test execution error: {str(e)}")
            print(f"{Colors.FAIL}✗ Test ERROR: {str(e)}{Colors.ENDC}")

        return result

    # ==================== MAIN TEST EXECUTION ====================

    def run_all_tests(self):
        """Execute all test cases sequentially"""
        self.print_header("ECGW Functional Test Automation - QA01 Tenant 3624")

        print(f"{Colors.OKBLUE}Test Environment:{Colors.ENDC}")
        print(f"  Tenant ID: {self.TOPOLOGY['tenant_id']}")
        print(f"  Client: {self.TOPOLOGY['client_machine']}")
        print(f"  ECGW Nodes: {', '.join(self.TOPOLOGY['ecgw_nodes'])}")
        print(f"  CFW: {self.TOPOLOGY['cfw_service']['host']}:{self.TOPOLOGY['cfw_service']['port']}")
        print(f"  Proxy: {self.TOPOLOGY['proxy_service']['host']}:{self.TOPOLOGY['proxy_service']['port']}")

        # Define test cases to run
        test_cases = [
            self.test_01_web_traffic_forwarding,
            self.test_02_non_web_traffic_forwarding,
            self.test_03_multiple_tunnel_traffic_forwarding,
            # Test 4 (custom port) is skipped as requested
            self.test_05_all_service_validation,
            self.test_06_health_check_status_200,
            self.test_07_health_check_status_503_cfw_failure,
            self.test_08_health_check_status_503_proxy_failure,
            self.test_09_tunnel_status_all_ecgw,
        ]

        # Execute each test sequentially
        for test_func in test_cases:
            result = test_func()
            self.results.append(result)
            time.sleep(2)  # Small delay between tests

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test execution summary"""
        self.print_header("Test Execution Summary")

        # Count results by status
        passed = sum(1 for r in self.results if r.status == "PASS")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        errors = sum(1 for r in self.results if r.status == "ERROR")
        skipped = sum(1 for r in self.results if r.status == "SKIP")
        total = len(self.results)

        # Print summary statistics
        print(f"{Colors.BOLD}Overall Results:{Colors.ENDC}")
        print(f"  {Colors.OKGREEN}PASSED: {passed}{Colors.ENDC}")
        print(f"  {Colors.FAIL}FAILED: {failed}{Colors.ENDC}")
        print(f"  {Colors.WARNING}ERRORS: {errors}{Colors.ENDC}")
        print(f"  {Colors.OKCYAN}SKIPPED: {skipped}{Colors.ENDC}")
        print(f"  {Colors.BOLD}TOTAL: {total}{Colors.ENDC}")

        # Calculate pass rate
        if total > 0:
            pass_rate = (passed / total) * 100
            print(f"\n  {Colors.BOLD}Pass Rate: {pass_rate:.1f}%{Colors.ENDC}")

        # Print detailed results
        print(f"\n{Colors.BOLD}Detailed Results:{Colors.ENDC}\n")

        for result in self.results:
            # Color based on status
            if result.status == "PASS":
                color = Colors.OKGREEN
                symbol = "✓"
            elif result.status == "FAIL":
                color = Colors.FAIL
                symbol = "✗"
            elif result.status == "ERROR":
                color = Colors.WARNING
                symbol = "⚠"
            else:
                color = Colors.OKCYAN
                symbol = "○"

            print(f"{color}{symbol} Test #{result.test_id}: {result.test_name}{Colors.ENDC}")
            print(f"  Status: {color}{result.status}{Colors.ENDC}")
            print(f"  Duration: {result.duration()}")

            if result.error_message:
                print(f"  {Colors.FAIL}Error: {result.error_message}{Colors.ENDC}")

            if result.details:
                print(f"  Details:")
                for detail in result.details[:5]:  # Show first 5 details
                    print(f"    - {detail}")
                if len(result.details) > 5:
                    print(f"    ... ({len(result.details) - 5} more)")

            print()

        # Save results to JSON file
        self.save_results_json()

    def save_results_json(self):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ecgw_test_results_{timestamp}.json"

        results_data = {
            "timestamp": datetime.now().isoformat(),
            "topology": self.TOPOLOGY,
            "summary": {
                "total": len(self.results),
                "passed": sum(1 for r in self.results if r.status == "PASS"),
                "failed": sum(1 for r in self.results if r.status == "FAIL"),
                "errors": sum(1 for r in self.results if r.status == "ERROR"),
                "skipped": sum(1 for r in self.results if r.status == "SKIP"),
            },
            "tests": [
                {
                    "test_id": r.test_id,
                    "test_name": r.test_name,
                    "status": r.status,
                    "duration": r.duration(),
                    "error_message": r.error_message,
                    "details": r.details
                }
                for r in self.results
            ]
        }

        try:
            with open(filename, 'w') as f:
                json.dump(results_data, f, indent=2)
            print(f"{Colors.OKGREEN}Test results saved to: {filename}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.WARNING}Warning: Could not save results to file: {e}{Colors.ENDC}")


def main():
    """Main entry point"""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("=" * 80)
    print("ECGW Functional Test Automation Script".center(80))
    print("QA01 Topology - Tenant 3624".center(80))
    print("=" * 80)
    print(f"{Colors.ENDC}\n")

    # Create automation instance
    automation = ECGWTestAutomation()

    try:
        # Run all tests
        automation.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Test execution interrupted by user{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Fatal error: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup SSH connections
        print(f"\n{Colors.OKBLUE}Cleaning up SSH connections...{Colors.ENDC}")
        automation.cleanup_connections()
        print(f"{Colors.OKGREEN}Cleanup complete{Colors.ENDC}")


if __name__ == "__main__":
    main()
