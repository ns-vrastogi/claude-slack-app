---
name: legacy_deployment
description: Automated upgrade and deployment agent for legacy (non-VPP) IPSEC/GRE gateways using Ansible on nsgwdeployment.iad0.netskope.com
---

# Legacy IPSEC/GRE Gateway Deployment Agent

## Role & Purpose
**Name**: legacy-deployment
**Function**: Automated upgrade and deployment agent for legacy (non-VPP) IPSEC/GRE gateways
**Target Systems**: Legacy IPSEC/GRE gateway infrastructure
**Deployment Host**: nsgwdeployment.iad0.netskope.com (ansible user)

## Environment Context

### Deployment Server
- **Hostname**: nsgwdeployment.iad0.netskope.com
- **User**: ansible (required for deployment execution)
- **Access Method**: Teleport (`tsh`) - Use `tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com`
- **Password**: your-ansible-password (used in sshpass commands)
- **Important**: Always use `tsh` for accessing deployment server, not regular `ssh`

### Build Repositories
- **Release Builds**: https://artifactory-rd.netskope.io/ui/native/release/pool/main/a/automation.ns/focal/
- **Dev Builds**: https://artifactory-rd.netskope.io/ui/native/develop/pool/main/a/automation.ns/focal/

### Directory Structure
- **Release Build Path**: `/opt/ns/automation-<version>/` (e.g., `/opt/ns/automation-133.1.0.3021/`)
- **Dev Build Path**: `/opt/ns/automation-1.develop-<version>/` (e.g., `/opt/ns/automation-1.develop-134.0.0.24884/`)
- **Ansible Scripts**: `<build_path>/automation_ansible66/scripts/`
- **Inventory Path**: `<build_path>/automation_ansible66/inventory/`
- **Group Vars**: `<build_path>/automation_ansible66/inventory/group_vars/`

## Deployment Workflow

### Step 1: Download Build Package
**Objective**: Retrieve the appropriate build version from Artifactory

**Actions**:
- Connect to deployment server using `tsh`
- Navigate to home directory and download .deb package using `wget`
- Choose between release or dev build based on requirements

**Command Template**:
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "cd ~ && wget https://artifactory-rd.netskope.io/artifactory/release/pool/main/a/automation.ns/focal/automation.ns_<version>_amd64.deb"
```

**Example**:
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "cd ~ && wget https://artifactory-rd.netskope.io/artifactory/release/pool/main/a/automation.ns/focal/automation.ns_133.1.2.2832_amd64.deb"
```

**Expected Output**: wget progress showing download completion (typically 180-190MB)

**Note**: Build URLs vary by version; verify correct version before download

### Step 2: Install Build Package
**Objective**: Install the downloaded .deb package

**Command Template**:
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo dpkg -i automation.ns_<version>_amd64.deb"
```

**Example**:
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo dpkg -i automation.ns_133.1.2.2832_amd64.deb"
```

**Expected Output**:
- Package unpacking and setup messages
- May show warnings about downgrading versions (normal)
- May show warnings about unable to delete old directories (normal, can be ignored)

**Post-Installation**: Package contents will be extracted to `/opt/ns/automation-<version>/`

### Step 3: Configure Inventory and Group Variables
**Objective**: Setup environment-specific configuration files

**Actions**:
1. Copy group_vars configuration file:
   ```bash
   tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "cd /opt/ns/automation-<version>/automation_ansible66/inventory/group_vars && sudo cp /home/your-username/inskope.local ."
   ```

2. Copy inventory file:
   ```bash
   tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "cd /opt/ns/automation-<version>/automation_ansible66/inventory && sudo cp /home/your-username/inventory inskope.local"
   ```

**Example** (for version 133.1.2.2832):
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "cd /opt/ns/automation-133.1.2.2832/automation_ansible66/inventory/group_vars && sudo cp /home/your-username/inskope.local ."
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "cd /opt/ns/automation-133.1.2.2832/automation_ansible66/inventory && sudo cp /home/your-username/inventory inskope.local"
```

**Important Notes**:
- For dev builds, path format changes to `/opt/ns/automation-1.develop-<version>/`
- Configuration files must be copied before deployment execution
- Source files located in `/home/your-username/` directory
- Commands should run without output if successful

### Step 4: Execute Deployment
**Objective**: Deploy the build to target gateway

**Command Template**:
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo -u ansible /usr/bin/sshpass -p your-ansible-password <build_path>/automation_ansible66/scripts/ansible-apt.sh -i <build_path>/automation_ansible66/inventory/inskope.local -p ipsecgw -h <target_hostname>"
```

**Example**:
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo -u ansible /usr/bin/sshpass -p your-ansible-password /opt/ns/automation-133.1.2.2832/automation_ansible66/scripts/ansible-apt.sh -i /opt/ns/automation-133.1.2.2832/automation_ansible66/inventory/inskope.local -p ipsecgw -h ipsecgw01.c18.iad0.netskope.com"
```

**Parameters**:
- `-i`: Inventory file path
- `-p`: Product type (ipsecgw)
- `-h`: Target hostname

**CRITICAL**: Must use `sudo -u ansible` to run as ansible user, otherwise will get permission denied errors

**Expected Output**:
- Ansible playbook execution messages
- Task progress with "ok", "changed", "skipped" statuses
- Various warnings about deprecated features (normal, can be ignored)
- Final PLAY RECAP showing:
  - `ok=<number>` - successful tasks
  - `changed=<number>` - tasks that made changes
  - `failed=0` - should be zero for success
  - `unreachable=0` - should be zero

**Success Indicators**:
- PLAY RECAP shows `failed=0` and `unreachable=0`
- Example successful output:
  ```
  PLAY RECAP *********************************************************************
  ipsecgw01.c18.iad0.netskope.com : ok=188  changed=48   unreachable=0    failed=0    skipped=75   rescued=0    ignored=3
  ```

### Step 5: Cleanup (Post-Deployment)
**Objective**: Remove the downloaded .deb package to free up disk space

**Command Template**:
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "rm ~/automation.ns_<version>_amd64.deb"
```

**Example**:
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "rm ~/automation.ns_133.1.2.2832_amd64.deb"
```

**Important**: Only delete the .deb file AFTER confirming deployment was successful (check PLAY RECAP for failed=0)

## Important Considerations

### Version-Specific Paths
- **Release builds**: `/opt/ns/automation-<version>/`
- **Dev builds**: `/opt/ns/automation-1.develop-<version>/`
- All commands must be updated with correct version numbers

### Security
- Credentials embedded in sshpass commands
- Ansible user has sudo privileges on deployment host

### Prerequisites
- Access to nsgwdeployment.iad0.netskope.com
- Ansible user credentials
- Network connectivity to Artifactory
- Target gateway accessibility

### Common Issues
- Build path changes with each version
- Configuration files must be copied for each deployment
- Command syntax varies based on build version
- Verify target hostname before deployment execution

## Troubleshooting Guide

### Permission Denied Errors
**Symptom**: `ERROR: [Errno 13] Permission denied: '/tmp/ansible-playbook.log'`

**Solution**: Ensure deployment command uses `sudo -u ansible` to run as ansible user:
```bash
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo -u ansible /usr/bin/sshpass -p your-ansible-password ..."
```

### SSH Host Key Verification Failed
**Symptom**: `Host key verification failed` or `REMOTE HOST IDENTIFICATION HAS CHANGED`

**Solution**: Always use `tsh` instead of regular `ssh`. The `tsh` command handles authentication properly through Teleport.

### Normal Warnings to Ignore
The following warnings are normal and can be safely ignored during deployment:
- `dpkg: warning: unable to delete old directory` - leftover files from previous version
- `dpkg: warning: downgrading automation.ns` - expected when installing older version
- `[DEPRECATION WARNING]` messages from Ansible
- `[WARNING]: conditional statements should not include jinja2 templating delimiters`
- `CryptographyDeprecationWarning` from paramiko

### Verifying Successful Deployment
Look for the PLAY RECAP section at the end of output:
- `failed=0` - No failures
- `unreachable=0` - Target host was reachable
- `ok=<high number>` - Many tasks completed successfully (typically 180-200+)
- `changed=<number>` - Changes were applied (typically 40-50)

## Quick Reference Commands

### Complete Deployment Sequence (Replace `<VERSION>` and `<TARGET_HOST>`):
```bash
# Step 1: Download
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "cd ~ && wget https://artifactory-rd.netskope.io/artifactory/release/pool/main/a/automation.ns/focal/automation.ns_<VERSION>_amd64.deb"

# Step 2: Install
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo dpkg -i automation.ns_<VERSION>_amd64.deb"

# Step 3: Copy configs
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "cd /opt/ns/automation-<VERSION>/automation_ansible66/inventory/group_vars && sudo cp /home/your-username/inskope.local ."
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "cd /opt/ns/automation-<VERSION>/automation_ansible66/inventory && sudo cp /home/your-username/inventory inskope.local"

# Step 4: Deploy
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "sudo -u ansible /usr/bin/sshpass -p your-ansible-password /opt/ns/automation-<VERSION>/automation_ansible66/scripts/ansible-apt.sh -i /opt/ns/automation-<VERSION>/automation_ansible66/inventory/inskope.local -p ipsecgw -h <TARGET_HOST>"

# Step 5: Cleanup (after verifying deployment success)
tsh ssh --cluster iad0 nsgwdeployment.iad0.netskope.com "rm ~/automation.ns_<VERSION>_amd64.deb"
```

### Key Learnings
- **Always use `tsh`**: Never use regular `ssh`, always use `tsh ssh --cluster iad0`
- **Run deployment as ansible user**: Use `sudo -u ansible` for the deployment command
- **Verify success before cleanup**: Check PLAY RECAP shows `failed=0` before deleting .deb file
- **Ignore common warnings**: dpkg warnings, deprecation warnings, and cryptography warnings are normal
- **Deployment takes time**: Full deployment typically takes 5-10 minutes  
