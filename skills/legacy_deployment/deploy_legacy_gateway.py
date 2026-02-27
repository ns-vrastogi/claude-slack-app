#!/usr/bin/env python3
"""
Legacy IPSEC/GRE Gateway Deployment Script

This script automates the deployment of release builds to legacy (non-VPP) IPSEC/GRE gateways.
It executes the complete deployment workflow including download, install, configure, deploy, and cleanup.

Usage:
    python3 deploy_legacy_gateway.py <build_version> <hostname>

Example:
    python3 deploy_legacy_gateway.py 134.0.0.3394 ipsecgw01.c18.iad0.netskope.com
"""

import sys
import subprocess
import argparse
import time
from typing import Tuple


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


class LegacyGatewayDeployer:
    """Handles deployment of builds to legacy IPSEC/GRE gateways"""

    DEPLOYMENT_HOST = "nsgwdeployment.iad0.netskope.com"
    CLUSTER = "iad0"
    ARTIFACTORY_BASE_URL = "https://artifactory-rd.netskope.io/artifactory/release/pool/main/a/automation.ns/focal"
    ANSIBLE_USER = "ansible"
    ANSIBLE_PASSWORD = "your-ansible-password"

    def __init__(self, build_version: str, target_hostname: str):
        self.build_version = build_version
        self.target_hostname = target_hostname
        self.build_path = f"/opt/ns/automation-{build_version}"
        self.deb_filename = f"automation.ns_{build_version}_amd64.deb"

    def print_step(self, step_num: int, message: str):
        """Print a step header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}=== Step {step_num}: {message} ==={Colors.ENDC}")

    def print_success(self, message: str):
        """Print success message"""
        print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

    def print_error(self, message: str):
        """Print error message"""
        print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

    def print_warning(self, message: str):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

    def print_info(self, message: str):
        """Print info message"""
        print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")

    def run_ssh_command(self, command: str, timeout: int = 300) -> Tuple[int, str, str]:
        """Execute command via tsh ssh"""
        full_cmd = f'tsh ssh --cluster {self.CLUSTER} {self.DEPLOYMENT_HOST} "{command}"'

        try:
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -1, "", str(e)

    def step1_download_build(self) -> bool:
        """Download build package from Artifactory"""
        self.print_step(1, "Downloading Build Package")

        download_url = f"{self.ARTIFACTORY_BASE_URL}/{self.deb_filename}"
        command = f"cd ~ && wget {download_url}"

        self.print_info(f"Downloading {self.deb_filename}...")
        returncode, stdout, stderr = self.run_ssh_command(command, timeout=600)

        if returncode == 0 and "saved" in stdout:
            self.print_success(f"Build package downloaded successfully")
            return True
        else:
            self.print_error(f"Failed to download build package")
            if stderr:
                print(f"Error: {stderr}")
            return False

    def step2_install_build(self) -> bool:
        """Install the downloaded .deb package"""
        self.print_step(2, "Installing Build Package")

        command = f"sudo dpkg -i {self.deb_filename}"

        self.print_info(f"Installing package...")
        returncode, stdout, stderr = self.run_ssh_command(command, timeout=300)

        if returncode == 0 or "Setting up automation.ns" in stdout:
            self.print_success("Build package installed successfully")
            self.print_warning("Ignoring normal dpkg warnings about old directories")
            return True
        else:
            self.print_error("Failed to install build package")
            if stderr:
                print(f"Error: {stderr}")
            return False

    def step3_copy_config_files(self) -> bool:
        """Copy configuration files (group_vars and inventory)"""
        self.print_step(3, "Copying Configuration Files")

        # Copy group_vars
        self.print_info("Copying group_vars configuration...")
        command1 = f"cd {self.build_path}/automation_ansible66/inventory/group_vars && sudo cp /home/your-username/inskope.local ."
        returncode1, _, stderr1 = self.run_ssh_command(command1)

        if returncode1 != 0:
            self.print_error("Failed to copy group_vars configuration")
            if stderr1:
                print(f"Error: {stderr1}")
            return False

        self.print_success("group_vars configuration copied")

        # Copy inventory
        self.print_info("Copying inventory configuration...")
        command2 = f"cd {self.build_path}/automation_ansible66/inventory && sudo cp /home/your-username/inventory inskope.local"
        returncode2, _, stderr2 = self.run_ssh_command(command2)

        if returncode2 != 0:
            self.print_error("Failed to copy inventory configuration")
            if stderr2:
                print(f"Error: {stderr2}")
            return False

        self.print_success("inventory configuration copied")
        return True

    def step4_execute_deployment(self) -> bool:
        """Execute the Ansible deployment"""
        self.print_step(4, "Executing Deployment")

        ansible_script = f"{self.build_path}/automation_ansible66/scripts/ansible-apt.sh"
        inventory_path = f"{self.build_path}/automation_ansible66/inventory/inskope.local"

        command = (
            f"sudo -u {self.ANSIBLE_USER} /usr/bin/sshpass -p {self.ANSIBLE_PASSWORD} "
            f"{ansible_script} -i {inventory_path} -p ipsecgw -h {self.target_hostname}"
        )

        self.print_info(f"Deploying to {self.target_hostname}...")
        self.print_warning("This may take several minutes...")

        returncode, stdout, stderr = self.run_ssh_command(command, timeout=900)

        # Check for PLAY RECAP in output
        if "PLAY RECAP" in stdout:
            # Extract the recap line
            recap_lines = [line for line in stdout.split('\n') if self.target_hostname in line and 'ok=' in line]
            if recap_lines:
                recap = recap_lines[0]
                print(f"\n{Colors.BOLD}PLAY RECAP:{Colors.ENDC}")
                print(recap)

                # Check for failures
                if "failed=0" in recap and "unreachable=0" in recap:
                    self.print_success("Deployment completed successfully!")
                    return True
                else:
                    self.print_error("Deployment completed with errors")
                    return False

        self.print_error("Deployment failed - could not find PLAY RECAP")
        if stderr:
            print(f"Error: {stderr}")
        return False

    def step5_cleanup(self) -> bool:
        """Remove the downloaded .deb file"""
        self.print_step(5, "Cleanup")

        command = f"rm ~/{self.deb_filename}"

        self.print_info("Removing downloaded .deb file...")
        returncode, _, stderr = self.run_ssh_command(command)

        if returncode == 0:
            self.print_success("Cleanup completed")
            return True
        else:
            self.print_warning("Cleanup failed, but deployment was successful")
            if stderr:
                print(f"Error: {stderr}")
            return True  # Don't fail the entire deployment for cleanup issues

    def deploy(self) -> bool:
        """Execute the complete deployment workflow"""
        print(f"\n{Colors.BOLD}{Colors.HEADER}╔════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}║   Legacy IPSEC/GRE Gateway Deployment                     ║{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}╚════════════════════════════════════════════════════════════╝{Colors.ENDC}")

        print(f"\n{Colors.BOLD}Build Version:{Colors.ENDC} {self.build_version}")
        print(f"{Colors.BOLD}Target Host:{Colors.ENDC} {self.target_hostname}")
        print(f"{Colors.BOLD}Deployment Server:{Colors.ENDC} {self.DEPLOYMENT_HOST}")

        start_time = time.time()

        # Execute deployment steps
        steps = [
            (self.step1_download_build, "Download failed"),
            (self.step2_install_build, "Installation failed"),
            (self.step3_copy_config_files, "Configuration failed"),
            (self.step4_execute_deployment, "Deployment failed"),
            (self.step5_cleanup, "Cleanup failed (non-critical)")
        ]

        for i, (step_func, error_msg) in enumerate(steps, 1):
            if not step_func():
                self.print_error(f"\n{error_msg}")
                if i < 5:  # Don't fail on cleanup
                    return False

        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)

        print(f"\n{Colors.OKGREEN}{Colors.BOLD}╔════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}║   Deployment Completed Successfully!                      ║{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}╚════════════════════════════════════════════════════════════╝{Colors.ENDC}")
        print(f"\n{Colors.BOLD}Time elapsed:{Colors.ENDC} {minutes}m {seconds}s")
        print(f"\n{Colors.OKGREEN}✓ {self.target_hostname} is now running build {self.build_version}{Colors.ENDC}\n")

        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Deploy release builds to legacy IPSEC/GRE gateways',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s 134.0.0.3394 ipsecgw01.c18.iad0.netskope.com
  %(prog)s 133.1.2.2832 ipsecgw02.c18.iad0.netskope.com

Prerequisites:
  - tsh CLI must be installed and configured
  - Access to nsgwdeployment.iad0.netskope.com
  - Valid credentials for Teleport authentication
        """
    )

    parser.add_argument('build_version', help='Build version to deploy (e.g., 134.0.0.3394)')
    parser.add_argument('hostname', help='Target gateway hostname (e.g., ipsecgw01.c18.iad0.netskope.com)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')

    args = parser.parse_args()

    if args.dry_run:
        print(f"\n{Colors.WARNING}DRY RUN MODE{Colors.ENDC}")
        print(f"Would deploy build {args.build_version} to {args.hostname}")
        return 0

    # Create deployer and execute
    deployer = LegacyGatewayDeployer(args.build_version, args.hostname)

    try:
        success = deployer.deploy()
        return 0 if success else 1
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Deployment interrupted by user{Colors.ENDC}")
        return 130
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
