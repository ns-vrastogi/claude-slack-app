import os
import re
import logging
import shlex
import subprocess
import telnetlib
import socket
import requests
import json
from datetime import datetime
from datetime import timedelta

final_testcase_summary = []


def command_execute(command):
    """
    Function to execute command and return the output
    """
    if "|" in command:
        out = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            shell=True,
        )
        res, err = out.communicate()
        return res
    else:
        cmd = shlex.split(command)
        try:
            out = subprocess.Popen(
                cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
            )
            res, err = out.communicate()
        except Exception as e:
            logging.exception("Exception %s", e)
        return res


def print_message1(message):
    """
    Function to print the message
    """
    print("\n")
    print("#############################################################")
    print("\n{}".format(message))
    print("=========================================================")


def print_message2(message1, message2):
    """
    Function to print the message
    """
    print("\n{}".format(message1))
    print("\n*********************************************************")
    print("{}".format(message2))
    print("*********************************************************")


def print_message3(message):
    """
    Function to print the message
    """
    print("\n")
    print("{}".format(message))
    print("\n#############################################################")


def testcase1_nsgregw_main_process_supervisorctl_status_check():
    print_message1("Testcase 1: nsgregw - vpp process supervisorctl status check")
    output = command_execute("sudo supervisorctl status")
    print_message2("supervisorctl status output:", output)
    pattern = re.search("vppgregw:gre-vpp\s+RUNNING", output)

    if pattern:
        print("\nResult - VPP service is in running state - PASS")
    else:
        print("\nResult - VPP service is not in running state")
        final_testcase_summary.append("Testcase 1:  nsgregw - VPP process supervisorctl status check - FAIL")
        return

    final_testcase_summary.append("Testcase 1:  nsgregw - VPP process supervisorctl status check - PASS")
    print_message3("Completed - Testcase 1: nsgregw - VPP process supervisorctl status check")


def testcase2_nsgregw_healthservice_process_supervisorctl_status_check():
    print_message1("Testcase 2: nsgregw - healthservice process supervisorctl status check")
    output = command_execute("sudo supervisorctl status")
    print_message2("supervisorctl status output:", output)
    pattern = re.search("health-service\s+RUNNING", output)

    if pattern:
        print("\nResult - health-service service is in running state -- PASS")
    else:
        print("\nResult - health-service service is not in running state -- FAIL")
        final_testcase_summary.append(
            "Testcase 2:  nsgregw - health-service  process supervisorctl status check - FAIL"
        )
        return

    final_testcase_summary.append("Testcase 2:  nsgregw - health-service process supervisorctl status check - PASS")
    print_message3("Completed - Testcase 2: nsgregw - health-service process supervisorctl status check")


def testcase3_nsgregw_cfgagentv2_process_supervisorctl_status_check():
    print_message1("Testcase 3: nsgregw - cfgagentv2 process supervisorctl status check")
    output = command_execute("sudo supervisorctl status")
    print_message2("supervisorctl status output:", output)
    pattern = re.search("cfgagentv2\s+RUNNING", output)

    if pattern:
        print("\nResult - cfgagentv2 service is in running state -- PASS")
    else:
        print("\nResult - cfgagentv2 service is not in running state -- FAIL")
        final_testcase_summary.append("Testcase 3:  nsgregw - cfgagentv2 process supervisorctl status check - FAIL")
        return

    final_testcase_summary.append("Testcase 3:  nsgregw - cfgagentv2 process supervisorctl status check - PASS")
    print_message3("Completed - Testcase 3: nsgregw - cfgagentv2 process supervisorctl status check")


def testcase4_nsgregw_loopback_interface_vip_check():
    print_message1("Testcase 4:  nsgregw - Loopback Interface VIP configuration check")
    output = command_execute("sudo ip addr show lcploop0 scope global")
    print_message2("Loopback Interface details:", output)
    pattern = re.search("inet ([\d\.]+)/32", output)
    if pattern:
        lb_vip = pattern.group(1)
        print("\nResult - LB VIP address configured in loopback interface -- PASS")
    else:
        print("\nResult - LB VIP address is not configured in loopback interface -- FAIL")
        final_testcase_summary.append("Testcase 4:  gregw - Loopback Interface VIP configuration check - FAIL")
        return

    final_testcase_summary.append("Testcase 4:  gregw - Loopback Interface VIP configuration check - PASS")
    print_message3("Completed - Testcase 4: gregw - Loopback Interface VIP configuration check")


def testcase5_nsgregw_ingress_interface_check():
    print_message1("Testcase 5:  nsgregw - Ingress interface check")
    output = command_execute("grep -i ingress-interface /opt/ns/common/remote/stsvc-interface")
    print_message2("ingress-iface check output:", output)
    pattern = r'"ingress-interface"\s*:\s*"([^"]+)"'
    output_match1 = re.search(pattern, output)

    if output_match1:
        ingress_intf = output_match1.group(1)
    else:
        print("\nResult - Error in getting ingress interface details")
        final_testcase_summary.append("Testcase 5:  nsgregw - Ingress interface check - FAIL")
        return

    output1 = command_execute(f"sudo vppctl show interface {ingress_intf} address".format(ingress_intf))
    print_message2("Ingress Interface details:", output1)
    output_match2 = re.search("L3 [\d\.]+|inet addr:[\d\.]+", output1)
    if output_match2:
        print("\nResult - Ingress interface {} IP address configured".format(ingress_intf))
    else:
        print("\nResult - Ingress interface {} no IP address configured".format(ingress_intf))
        final_testcase_summary.append("Testcase 5:  nsgregw - Ingress interface check - FAIL")
        return

    final_testcase_summary.append("Testcase 5:  nsgregw - Ingress interface check - PASS")
    print_message3("Completed - Testcase 5:  nsgregw - Ingress interface check")


def testcase6_nsgregw_ip_rule_config_check():
    print_message1("Testcase 6: nsgregw - IP rule config check")
    output = command_execute("sudo ip addr show lcploop0 scope global")
    print_message2("Loopback Interface details:", output)
    pattern = re.search("inet ([\d\.]+)/32", output)
    if pattern:
        lb_vip = pattern.group(1)
    else:
        print("\nResult - LB VIP address is not configured in loopback interface")
        final_testcase_summary.append("Testcase 6:  nsgregw - IP rule config check - FAIL")
        return

    output1 = command_execute(f"sudo vppctl show ip fib | grep -A 2 {lb_vip}")
    print_message2("IP rule show Output:", output1)
    pattern1 = f"dpo-receive: {lb_vip} on loop0"
    pattern2 = re.search(pattern1, output1)

    if pattern2:
        print("\nResult - IP rule config exists for LB VIP")
    else:
        print("\nResult - IP rule config not exist for LB VIP")
        final_testcase_summary.append("Testcase 6:  nsgregw - IP rule config check - FAIL")
        return

    final_testcase_summary.append("Testcase 6:  nsgregw - IP rule config check - PASS")
    print_message3("Completed - Testcase 6: nsgregw - IP rule config check")


def testcase7_nsgregw_vpp_version():
    print_message1("Testcase 7: nsgregw - VPP version check")
    output = command_execute("sudo vppctl show version")
    print_message2("VPP Version details:", output)
    pattern = re.search("vpp v23.02-release", output)
    if pattern:
        print("\nResult - The VPP version is correct")
        final_testcase_summary.append("Testcase 7:  nsgregw - VPP version check passed - PASS")
    else:
        print("\nResult - The VPP version has changed")
        final_testcase_summary.append("Testcase 7:  nsgregw - VPP version check failed - FAIL")
        return


def testcase8_nsgregw_plugin_check():
    print_message1("Testcase 8: nsgregw - plugin check")
    output = command_execute("sudo vppctl show plugins | grep -i 'steering\|gregw'")
    pattern = re.search("libsteering_plugin.so", output)
    pattern2 = re.search("libgregw_plugin.so", output)
    # print_message2("Plugins details:", pattern+'\n'+pattern2)
    if pattern and pattern2:
        print("\nResult - VPP and steering management Plugins are Present")
    else:
        print("\nResult - VPP Plugins are not Present")
        final_testcase_summary.append("Testcase 8:  nsgregw - VPP process plugins status check - FAIL")
        return
    final_testcase_summary.append("Testcase 8:  nsgregw - VPP plugins status check - PASS")
    print_message3("Completed - Testcase 8: nsgregw - VPP plugins check")


def testcase9_nsgregw_eventforwarder_vip_reachability_check():
    print_message1("Testcase 9: nsgregw - eventforwarder VIP reachability check")
    output1 = command_execute("cat /opt/ns/common/remote/eventforwarder")
    print_message2("eventforwarder details:", output1)
    pattern1 = re.search(".*tcp://(.*):5555", output1)
    output2 = pattern1.group(1)
    output3 = os.system("ping -c 5 " + output2)

    if output3 == 0:
        print("\nResult - EventForwarder VIP address Reachability is proper - PASS")
        final_testcase_summary.append("Testcase 9: nsgregw - eventforwarder VIP reachability check - PASS")
    else:
        print("\nResult - EventForwarder VIP address Reachability is not proper - FAIL")
        final_testcase_summary.append("Testcase 9: nsgregw - eventforwarder VIP reachability check - FAIL")

    print_message3("Completed - Testcase 9: nsgregw - eventforwarder VIP reachability check")


def testcase10_nsgregw_eventforwarder_telnet_status_check():
    print_message1("Testcase 10: nsgregw - eventforwarder telnet status check")
    output1 = command_execute("cat /opt/ns/common/remote/eventforwarder")
    print_message2("eventforwarder details:", output1)
    pattern1 = re.search(".*tcp://(.*):(\d+)", output1)
    output2 = pattern1.group(1)
    output3 = pattern1.group(2)
    telnet_status = "timed out"
    telnet = telnetlib.Telnet()
    try:
        timeout_sec = 10
        telnet.open(output2, output3, timeout_sec)
        output = telnet.read_all()
        print(output)
        telnet.close()
    except socket.error as exc:
        print(exc)
        if telnet_status in str(exc):
            print("\nResult - EventForwarder telnet status is proper - PASS")
            final_testcase_summary.append("Testcase 10: nsgregw - eventforwarder telnet status check - PASS")
        else:
            print("\nResult - EventForwarder telnet status is not proper - FAIL")
            final_testcase_summary.append("Testcase 10: nsgregw - eventforwarder telnet status check - FAIL")

    print_message3("Completed - Testcase 10: nsgregw - eventforwarder telnet status check")


def testcase11_nsgregw_probe_ip_config_check():
    print_message1("Testcase 11: nsgregw - Probe IP config check")
    output1 = command_execute("grep -i probeip /opt/ns/gregw/ns-vpp-gre.conf")
    print_message2("Probe IP config details:", output1)
    pattern = r"(probeip\s+)([\d\.]+)"
    match1 = re.search(pattern, output1, re.MULTILINE)

    if match1:
        output2 = match1.group(2)
    else:
        print("\nResult - Probe IP is not configured properly")
        final_testcase_summary.append("Testcase 11: nsgregw - Probe IP config check - FAIL")
        return

    invalid_ip = "0.0.0.0"
    if output2 == invalid_ip:
        print("\nResult - Probe IP is not valid")
        final_testcase_summary.append("Testcase 11: nsgregw - Probe IP config check - FAIL")
        return

    regex_pattern = "^([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])$"
    output3 = bool(re.match(regex_pattern, output2))
    if output3:
        print("\nResult - Probe IP is configured with proper and valid IP address")
        final_testcase_summary.append("Testcase 11: nsgregw - Probe IP config check - PASS")
    else:
        print("\nResult - Probe IP is not configured with valid IP address")
        final_testcase_summary.append("Testcase 11: nsgregw - Probe IP config check - FAIL")

    print_message3("Completed - Testcase 11: nsgregw - Probe IP config check")


def testcase12_nsgregw_pop_config_check():
    print_message1("Testcase 12: nsgregw - POP config check")
    output1 = command_execute("cat /opt/ns/common/pop")
    print_message2("POP config details:", output1)
    pattern1 = '"name":\s+"(\S+)"'
    match1 = re.search(pattern1, output1, re.MULTILINE)

    if match1:
        output2 = match1.group(1)
        print_message2("POP name is:", output2)
        print("\nResult - POP is configured properly")
        final_testcase_summary.append("Testcase 12: nsgregw - POP config check - PASS")
    else:
        print("\nResult - POP is not configured properly")
        final_testcase_summary.append("Testcase 12: nsgregw - POP config check - FAIL")

    print_message3("Completed - Testcase 12: nsgregw - POP config check")


def testcase13_nsgregw_cfw_VIP_reachability_check():
    print_message1("Testcase 13: nsgregw - CFW VIP reachability check")
    output1 = command_execute("cat /opt/ns/common/remote/stsvc-cfwsvc")
    print_message2("CFW details:", output1)
    pattern1 = re.search(r"(\d+.\d+.\d+.\d+)", output1)
    output2 = pattern1.group(1)
    output3 = os.system("ping -c 5 " + output2)

    if output3 == 0:
        print("\nResult - CFW VIP address Reachability is proper - PASS")
        final_testcase_summary.append("Testcase 13: nsgregw - CFW VIP reachability check - PASS")
    else:
        print("\nResult - EventForwarder VIP address Reachability is not proper - FAIL")
        final_testcase_summary.append("Testcase 13: nsgregw - CFW VIP reachability check - FAIL")

    print_message3("Completed - Testcase 13: nsgregw - CFW VIP reachability check")

def testcase14_nsgregw_cfw_health_check():
    print_message1("Testcase 14: nsgregw - cfw health check")
    output1 = command_execute("grep -i host /opt/ns/common/remote/stsvc-cfwsvc")
    print_message2("CFW VIP details:", output1)
    pattern = '"host":\s+"([\d\.]+)"'
    match1 = re.search(pattern, output1, re.MULTILINE)

    if match1:
        output2 = match1.group(1)
    else:
        print("\nResult - CFW VIP is not configured")
        final_testcase_summary.append("Testcase 14: nsgregw - cfw health check - FAIL")
        return

    url = "http://{}:7999/v3/health?features=all".format(output2)
    print_message2("Proxy health check URL:", url)

    try:
        resp = requests.get(url)
        data = resp.json()
    except socket.error as exc:
        print("\nException occurred when performing curl operation")
        print("\nResult - CFW health check is not proper - FAIL")
        final_testcase_summary.append("Testcase 14: nsgregw - cfw health check - FAIL")
        return

    print_message2("Curl operation response status code:", resp.status_code)
    print_message2("Advanced CFW feature status:", json.dumps(data))
    if resp.status_code == 200:
        print("\nResult - CFW health check is proper - PASS")
        final_testcase_summary.append("Testcase 14: nsgregw - cfw health check - PASS")
    else:
        print("\nResult - CFW health check is not proper - FAIL")
        final_testcase_summary.append("Testcase 14: nsgregw - cfw health check - FAIL")

    print_message3("Completed - Testcase 14: nsgregw - cfw health check")


def testcase15_nsgregw_proxy_vip_reachability_check():
    print_message1("Testcase 15: nsgregw - proxy VIP reachability check")
    output1 = command_execute("grep -i normal /opt/ns/common/remote/stsvc-nsproxy-dest -A 1")
    print_message2("Proxy VIP details:", output1)
    pattern = '"host":\s+"([\d\.]+)"'
    match1 = re.search(pattern, output1, re.MULTILINE)

    if match1:
        output2 = match1.group(1)
    else:
        print("\nResult - Proxy VIP is not configured")
        final_testcase_summary.append("Testcase 15: nsgregw - proxy VIP reachability check - FAIL")
        return

    output3 = os.system("ping -c 5 " + output2)

    if output3 == 0:
        print("\nResult - Proxy VIP address Reachability is proper - PASS")
        final_testcase_summary.append("Testcase 15: nsgregw - proxy VIP reachability check - PASS")
    else:
        print("\nResult - Proxy VIP address Reachability is not proper - FAIL")
        final_testcase_summary.append("Testcase 15: nsgregw - proxy VIP reachability check - FAIL")

    print_message3("Completed - Testcase 15: nsgregw - proxy VIP reachability check")


def testcase16_nsgregw_proxy_health_check():
    print_message1("Testcase 16: nsgregw - proxy health check")
    output1 = command_execute("grep -i normal /opt/ns/common/remote/stsvc-nsproxy-dest -A 1")
    print_message2("Proxy VIP details:", output1)
    pattern = '"host":\s+"([\d\.]+)"'
    match1 = re.search(pattern, output1, re.MULTILINE)

    if match1:
        output2 = match1.group(1)
    else:
        print("\nResult - Proxy VIP is not configured")
        final_testcase_summary.append("Testcase 16: nsgregw - proxy health check - FAIL")
        return

    url = "http://{}:8990/healthcheck".format(output2)
    print_message2("Proxy health check URL:", url)

    try:
        resp = requests.get(url)
    except socket.error as exc:
        print("\nException occurred when performing curl operation")
        print("\nResult - Proxy health check is not proper - FAIL")
        final_testcase_summary.append("Testcase 16: nsgregw - proxy health check - FAIL")
        return

    print_message2("Curl operation response status code:", resp.status_code)
    if resp.status_code == 200:
        print("\nResult - Proxy health check is proper - PASS")
        final_testcase_summary.append("Testcase 16: nsgregw - proxy health check - PASS")
    else:
        print("\nResult - Proxy health check is not proper - FAIL")
        final_testcase_summary.append("Testcase 16: nsgregw - proxy health check - FAIL")

    print_message3("Completed - Testcase 16: nsgregw - proxy health check")


def testcase17_nsgregw_tenant_directory_check():
    print_message1("Testcase 17: nsgregw - tenant directory check")
    output1 = command_execute("ls /opt/ns/tenant/ | wc -l")
    # print_message2("total tenant directories", output1)
    if os.path.exists("/opt/ns/tenant/"):
        print("\nThe tenant and directory exists")
        final_testcase_summary.append("TestCase 17: The tenant directory check - PASS")
    else:
        print("\nThe tenant directory doesn't exists")
        final_testcase_summary.append("TestCase 17: The tenant directory check - FAIL")
        return
    print_message3("Completed - TestCase 17: The tenant directory check - PASS")


def testcase18_nsgregw_startup_config_file_check():
    print_message1("Testcase 18: nsgregw - startup config check")
    output1 = command_execute("ls -l /etc/vpp/startup.conf")
    print_message2("startup config file", output1)
    output2 = command_execute("ls -l /opt/ns/gregw/ns-vpp-gre.conf")
    print_message2("ns vpp gregw config file", output2)
    if os.path.exists("/etc/vpp/startup.conf") and os.path.exists("/opt/ns/gregw/ns-vpp-gre.conf"):
        print("\n Both startup and vpp config file exists")
        final_testcase_summary.append("Testcase 18: startup config file check - PASS")
    else:
        print("\n Either startup or vpp config file is missing")
        final_testcase_summary.append("Testcase 18: startup config file check - FAIL")
    print_message3("Completed - TestCase 18: The startup config file check - PASS")


def testcase19_Check_troubleshooting_script():
    print_message1("TestCase 19: The Troubleshooting script check")
    output1 = command_execute("ls /opt/ns/gregw/scripts/")
    print_message2("Troubleshooting scripts", output1)
    if os.path.exists("/opt/ns/gregw/scripts/nsvpp_iface_counters") and os.path.exists(
        "/opt/ns/gregw/scripts/nsvpp_stats"
    ):
        print("\n Both troubleshooting file exists")
        final_testcase_summary.append("Testcase 19: troubleshoot script  check - PASS")
    else:
        print("\n The troubleshooting script is missing")
        final_testcase_summary.append("Testcase 19: troubleshoot script  check - Fail")
    print_message3("Completed - TestCase 19: The Troubleshooting script check - PASS")


def testcase20_Remote_config_file_check():
    print_message1("TestCase 20: The remote config file check")
    output1 = command_execute("ls -l /opt/ns/common/remote/")
    print_message2("Remote config files", output1)
    if (
        os.path.exists("/opt/ns/common/remote/eventforwarder")
        and os.path.exists("/opt/ns/common/remote/stsvc-nsproxy-dest")
        and os.path.exists("/opt/ns/common/remote/statsd-collector")
        and os.path.exists("/opt/ns/common/remote/statsd-collector-prod")
        and os.path.exists("/opt/ns/common/remote/stsvc-cfwetcd")
        and os.path.exists("/opt/ns/common/remote/stsvc-cfwsvc")
        and os.path.exists("/opt/ns/common/remote/stsvc-dsr")
        and os.path.exists("/opt/ns/common/remote/stsvc-interface")
    ):
        print("All the remote config files are present")
        final_testcase_summary.append("Testcase 20: Remote config file check - PASS")
    else:
        print("Some of remote config files are missing")
        final_testcase_summary.append("Testcase 20: Remote config file check - FAIL")
    print_message3("Completed - TestCase 20: Remote config file check - PASS")


def testcase21_OS_and_Kernel_Version():
    print_message1("TestCase 21: Test case to check OS and Kernel Version for IPSECGW")
    os_cmd = """lsb_release -r"""
    print("\nCommand to be executed to check the OS Version is:", os_cmd)
    os_result = (
        subprocess.run(os_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        .stdout.decode()
        .strip()
        .replace("\t", "")
    )
    key, value = os_result.split(":")
    os_output = {key.strip(): value.strip()}
    print("\n The os version is:", os_output["Release"])
    kernel_cmd = "uname -r"
    print("\nCommand to be executed to check the Kernel version is:", kernel_cmd)
    kernel_result = (
        subprocess.run(kernel_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode().strip()
    )
    print("\n The Kernel version is:", kernel_result)
    if os_output["Release"] == "20.04" and kernel_result == "5.4.0-64-generic":
        print("\nThe OS and Kernel Version Matches")
    elif os_output["Release"] == "20.04" and kernel_result == "5.15.0-139-generic":
        print("\nThe OS and Kernel Version Matches")
        final_testcase_summary.append("TestCase 21: OS and Kernel Version Check is - PASS")
    elif os_output["Release"] == "20.04" and kernel_result == "5.4.0-1048-fips":
        print("\nThe OS and Kernel Version Matches for fedramp")
        final_testcase_summary.append("TestCase 21: OS and Kernel Version Check is - PASS")
    else:
        print("\nThe OS and Kernel Version doesn't match")
        final_testcase_summary.append("TestCase 21: OS and Kernel Version Check is - FAIL")
        return
    print_message3("Completed - TestCase 21: OS and Kernel Version Check for IPSECGW - PASS")


def testcase22_Dsr_ip_reachability():
    print_message1("TestCase 22: Test case to check DSR IP reachibility for IPSECGW")
    output1 = command_execute("cat /opt/ns/common/remote/stsvc-dsr")
    print_message2("DSR IP:", output1)
    pattern = r"[\d\.]+"
    match1 = re.search(pattern, output1, re.MULTILINE)
    if match1:
        dsr_ip = match1.group()
        print_message2("\nDSR IP is ", dsr_ip)
        output3 = os.system("ping -c 5 " + dsr_ip)
        if output3 == 0:
            print("\nResult - DSR IP address Reachability is proper - PASS")
            final_testcase_summary.append("Testcase 22: nsgregw - DSR IP reachability check - PASS")
        else:
            print("\nResult - EventForwarder VIP address Reachability is not proper - FAIL")
            final_testcase_summary.append("Testcase 22: nsgregw - DSR IP reachability check - FAIL")

        print_message3("Completed - Testcase 22: nsgregw - DSR IP reachability check")


def testcase23_Jumbo_interface_check():
    print_message1("Testcase 23: nsgregw - Jumbo Interface check")
    output1 = command_execute("cat /opt/ns/common/remote/stsvc-cfwsvc")
    output2 = command_execute("cat /opt/ns/common/remote/stsvc-nsproxy-dest")
    print_message2("CFW details:", output1)
    cfw_pattern = re.search(r'("cfw-interface-ip":\s+)("\d+.\d+.\d+.\d+")', output1)
    proxy_pattern = re.search(r'("nsproxy-interface-ip":\s+)("\d+.\d+.\d+.\d+")', output2)
    cfw_ip = cfw_pattern.group(2)
    cfw_ip = cfw_ip.replace('"', "")
    proxy_ip = proxy_pattern.group(2)
    proxy_ip = proxy_ip.replace('"', "")
    if cfw_ip and proxy_ip:
        print_message2(
            f"\n CFW interface IP is {cfw_ip} and Ns_proxy interface ip is {proxy_ip}", cfw_ip + "\s" + proxy_ip
        )
        output3 = command_execute(f"ifconfig | grep -B 1 {cfw_ip}")
        output4 = command_execute(f"ifconfig | grep -B 1 {proxy_ip}")
        jumbo_cfw_pattern = re.search(r"mtu 9000", output3)
        jumbo_proxy_pattern = re.search(r"mtu 9000", output4)
        print_message2("\nCFW interface", output3)
        print_message2("\nProxy Interface", output4)
        if jumbo_cfw_pattern and jumbo_proxy_pattern:
            print("\n Results - The Jumbo Interface is configured on both proxy and CFW interface - PASS")
            final_testcase_summary.append("TestCase 23: Jumbo Interface Check - PASS")
        else:
            print("\n Results - The Jumbo interface is not configurd on either CFW or proxy interface - FAIL")
            final_testcase_summary.append("TestCase 23: Jumbo Interface Check - Fail")

    else:
        print_message2("\n Results - Enable to find either CFW interface or Proxy interface - FAIL")
        final_testcase_summary.append("TestCase 23: Jumbo Interface Check - Fail")
    print_message3("Completed - TestCase 23: Jumbo Interface Check")


def testcase24_log_file_check():
    print_message1("Testcase 24: nsgregw - Log File check")
    output1 = command_execute("ls -l /opt/ns/log/")
    print_message2("log files", output1)
    file_path = [
        "/opt/ns/log/cfgagentv2_health_check.log",
        "/opt/ns/log/nshealth.log",
        "/opt/ns/log/nsvppstsvc.log",
        "/opt/ns/log/vpp-logger.log",
        "/opt/ns/log/cfgagentv2.log",
        "/opt/ns/log/nsconfig.log",
        "/opt/ns/log/nsmetric.log",
        "/opt/ns/log/vpp.log",
    ]
    all_file_exist = True
    for path in file_path:
        if not os.path.exists(path):
            print_message2("\n Log file missing=", path)
            all_file_exist = False
    if all_file_exist:
        print("\nResult - All the log file exists - PASS")
        final_testcase_summary.append("Testcase 24: Log file check - PASS")
    else:
        print("\nResult - All the logs file are not present - FAIL")
        final_testcase_summary.append("Testcase 24: Log file check - FAIL")
    print_message3("Completed - TestCase 24: Log File Check")


def testcase25_core_file_check():
    print_message1("Testcase 25: nsgregw - core File check")
    now = datetime.now()
    time_diff = timedelta(minutes=59)
    cutoff_time = now - time_diff
    output1 = command_execute("ls -l /var/crash/")
    core_found = False
    try:
        for filename in os.listdir("/var/crash/"):
            file_path = os.path.join("/var/crash/", filename)
            # print(file_path)
            if os.path.isfile(file_path):
                try:
                    file_timestamp = os.path.getmtime(file_path)
                    mod_datetime = datetime.fromtimestamp(file_timestamp)
                    # print(mod_datetime)
                    # print(cutoff_time)
                    if mod_datetime > cutoff_time:
                        print(f"core file {filename} was created recently")
                        core_found = True
                except:
                    print(f"Couldn't get the info for file {filename}")
            else:
                core_found = False

    except Exception as e:
        print(f"An unexpected error occurred while listing directory content: {e}")
    if core_found:
        print("\nResult - Recent Core file found - FAIL")
        final_testcase_summary.append("Testcase 25: core file check - FAIL")
    else:
        print("\nResult - No Recent Core file found - PASS")
        final_testcase_summary.append("Testcase 25: core file check - PASS")
    print_message3("Completed - TestCase 25: Core File Check")


if __name__ == "__main__":
    testcase1_nsgregw_main_process_supervisorctl_status_check()
    testcase2_nsgregw_healthservice_process_supervisorctl_status_check()
    testcase3_nsgregw_cfgagentv2_process_supervisorctl_status_check()
    testcase4_nsgregw_loopback_interface_vip_check()
    testcase5_nsgregw_ingress_interface_check()
    testcase6_nsgregw_ip_rule_config_check()
    testcase7_nsgregw_vpp_version()
    testcase8_nsgregw_plugin_check()
    testcase9_nsgregw_eventforwarder_vip_reachability_check()
    testcase10_nsgregw_eventforwarder_telnet_status_check()
    testcase11_nsgregw_probe_ip_config_check()
    testcase12_nsgregw_pop_config_check()
    testcase13_nsgregw_cfw_VIP_reachability_check()
    testcase14_nsgregw_cfw_health_check()
    testcase15_nsgregw_proxy_vip_reachability_check()
    testcase16_nsgregw_proxy_health_check()
    testcase17_nsgregw_tenant_directory_check()
    testcase18_nsgregw_startup_config_file_check()
    testcase19_Check_troubleshooting_script()
    testcase20_Remote_config_file_check()
    testcase21_OS_and_Kernel_Version()
    testcase22_Dsr_ip_reachability()
    testcase23_Jumbo_interface_check()
    testcase24_log_file_check()
    testcase25_core_file_check()
    print("\n")
    print("#############################################################")
    print("\nOverall Result Summary:")
    for result in final_testcase_summary:
        print("   " + result)
    print("\n#############################################################")
