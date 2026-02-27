# Polaris Skill

**Name**: polaris
**Description**: Internal tool for managing VMs, IP address allocation, DNS records, and VLAN configuration in Netskope infrastructure.

## Purpose
This skill provides operations for:
- VM management (list, lookup, stop)
- IP address reservation and allocation
- DNS record management (create, list, delete)
- KVM host operations

---

## Prerequisites & Authentication

### Access Polaris Tools
```bash
tsh ssh --cluster sje011 polaris-tools-1.sje011.netskope.com
```

### Set Environment Variables
After logging in, authenticate with:
```bash
source /etc/polaris/qe-env
```

---

## Operations

### 1. IP Address Management

**IMPORTANT**: Always prefer VIP allocation method over manual DNS record creation. Manual DNS registration should only be used as a last resort.

#### Allocate VIP (Virtual IP) - **RECOMMENDED METHOD**
**Purpose**: Allocate a new virtual IP address on a specific VLAN (This is the preferred and recommended method)

**Command Pattern**:
```bash
polaris-image --allocate-vip --vip-fqdn <fqdn> --vlan-num <vlan-number> --pop-name <pop>
```

**Examples**:
```bash
# Example 1: Allocate VIP for test client
polaris-image --allocate-vip --vip-fqdn vishal.tclient.iad0.netskope.com --vlan-num 584 --pop-name iad0

# Example 2: Allocate VIP for IPSEC gateway on VLAN 678
polaris-image --allocate-vip --vip-fqdn scale.perf.ipsecgw.legacy.vlan678.iad0.netskope.com --vlan-num 678 --pop-name iad0

# Example 3: Allocate VIP for VPP GRE gateway on VLAN 700
polaris-image --allocate-vip --vip-fqdn vppgregw01.c18.vlan700.iad0.netskope.com --vlan-num 700 --pop-name iad0
```

**Success Output**:
```
2025-08-25 13:53:24,102 INFO 680 IP Allocation success: scale.perf.ipsecgw.legacy.vlan678.iad0.netskope.com 10.111.96.146 255.255.255.0 (10.111.96.146/24)	[polaris-image:allocate_vip]
```
The output shows: `<fqdn> <ip> <netmask> (<cidr>)`

**IMPORTANT - FQDN Format Rules**:
- General format: `<hostname>.<cluster>.<component>.vlan<number>.<pop>.netskope.com`
- For VLAN-specific hosts: `<hostname>.<cluster>.vlan<number>.<pop>.netskope.com`
- **AVOID**: Do NOT include the POP name twice (e.g., `vppgregw01.c18.iad0.vlan700.iad0.netskope.com` is WRONG)
- **CORRECT**: `vppgregw01.c18.vlan700.iad0.netskope.com` (only one `iad0`)

**IP Allocation Behavior**:
- VIP allocation automatically assigns an IP from the VLAN's IP pool
- The assigned IP may come from any subnet within the VLAN's CIDR block (e.g., VLAN 700 uses a /21 CIDR that spans multiple /24 subnets like 10.136.133.0/24, 10.136.134.0/24, etc.)
- You do NOT need to manually specify an IP address - the system selects an available one

#### Check Free IPs on a Subnet
**Purpose**: Find available IP addresses in a specific subnet (useful for understanding VLAN IP usage)

**Command Pattern**:
```bash
polaris dns2 record a list --zone <zone> | grep <subnet>
```

**Example**:
```bash
# Check available IPs in 10.136.133.x subnet
polaris dns2 record a list --zone iad0.netskope.com | grep 10.136.133.

# Check available IPs in 10.136.57.x subnet
polaris dns2 record a list --zone iad0.netskope.com | grep 10.136.57.
```

#### Find VLAN for a Subnet
**Purpose**: Determine which VLAN a subnet belongs to by analyzing hostname patterns

**Command Pattern**:
```bash
polaris dns2 record a list --zone <zone> | grep '<subnet>' | grep -iE 'vlan|vl[0-9]|bond[0-9]'
```

**Example**:
```bash
# Find VLAN for subnet 10.136.133.0/24
polaris dns2 record a list --zone iad0.netskope.com | grep '10\.136\.133\.' | grep -iE 'vlan|vl[0-9]|bond[0-9]' | head -20

# The output will show hostnames like:
# vppsteeringlb01.vlan700.c18.iad0.netskope.com    A    10.136.133.126
# This indicates subnet 10.136.133.0/24 belongs to VLAN 700
```

**Common VLAN to Subnet Mappings (iad0)**:
- VLAN 700: 10.136.133.0/21 (includes .133, .134, .135, etc.)
- VLAN 678: 10.111.96.0/24
- VLAN 584: Various subnets
- VLAN 592: 10.136.57.0/24

#### Register IP in DNS - **USE AS LAST RESORT ONLY**
**Purpose**: Manually create a DNS A record for a specific IP address

**⚠️ WARNING**: This method is NOT RECOMMENDED and should only be used as a last resort. Always try the VIP allocation method first.

**Command Pattern**:
```bash
polaris dns2 record a create --zone <zone> <fqdn> <ip-address>
```

**Example**:
```bash
polaris dns2 record a create --zone iad0.netskope.com vishal.gregw2-vlan592.iad0.netskope.com 10.136.57.245
```

**When to use this method**:
- Only when VIP allocation is not possible or not supported
- As an absolute last resort for special cases
- After consulting with infrastructure team

#### Delete IP Address
**Purpose**: Remove IP allocation and DNS records (use when IP was created by mistake or no longer needed)

**Command Pattern**:
```bash
# Delete from IPAM
polaris ipam prefix delete <ip-address>

# Delete DNS A record
polaris dns record a delete --zone <zone> <fqdn> <ip-address>
```

**Examples**:
```bash
# Delete IP from IPAM
polaris ipam prefix delete 10.111.96.146

# Delete corresponding DNS record
polaris dns record a delete --zone iad0.netskope.com scale.perf.ipsecgw.legacy.vlan678.iad0.netskope.com 10.111.96.146
```

---

### 2. VM Management

#### Create New VM

**Purpose**: Bring up new VMs for various purposes (gateways, clients, TRex, etc.)

**IMPORTANT - Deployment Methods**:
- **VPP-based VMs** (VPP IPSEC/GRE/ECGW gateways, VPP clients): Use YAML file method
- **Legacy VMs** (Legacy IPSEC/GRE gateways, TRex, regular clients, dummy CFW): Use direct command method

**VM Types and Resource Specifications**:
| VM Type | CPU Cores | Memory | Deployment Method |
|---------|-----------|--------|-------------------|
| Legacy IPSEC Gateway | 16 | 32GB | Direct Command |
| Legacy GRE Gateway | 16 | 32GB | Direct Command |
| TRex VM | 16 | 32GB | Direct Command |
| Client VM | 8 | 8GB | Direct Command |
| Dummy CFW | 8 | 8GB | Direct Command |
| VPP IPSEC Gateway | 8 | 8GB | YAML File |
| VPP GRE Gateway | 8 | 8GB | YAML File |
| VPP ECGW Gateway | 8 | 8GB | YAML File |
| VPP Client | 8 | 8GB | YAML File |

**Available KVM Hosts**: kvmdevperf16 to kvmdevperf20 in iad0
- `kvmdevperf16.iad0.netskope.com`
- `kvmdevperf17.iad0.netskope.com`
- `kvmdevperf18.iad0.netskope.com`
- `kvmdevperf19.iad0.netskope.com`
- `kvmdevperf20.iad0.netskope.com`

**Note**: If resources are not available on one KVM, try the next available KVM host.

##### Method 1: Direct Command (Legacy Gateways, TRex, Regular Clients)

**Command Pattern**:
```bash
polaris image vm create sriov \
  --kvm <kvm-hostname> \
  --pop <pop-name> \
  --name <vm-name> \
  --fqdn <fqdn> \
  --vlan-num <vlan-number> \
  --cpus <cpu-count> \
  --memory <memory-in-gb> \
  --image ubuntu20
```

**Examples**:
```bash
# Create Legacy GRE Gateway (16 cores, 32GB)
polaris image vm create sriov \
  --kvm kvmdevperf16.iad0.netskope.com \
  --pop iad0 \
  --name vishal.gregw2 \
  --fqdn vishal.gregw2.iad0.netskope.com \
  --vlan-num 700 \
  --cpus 16 \
  --memory 32 \
  --image ubuntu20

# Create TRex VM (16 cores, 32GB)
polaris image vm create sriov \
  --kvm kvmdevperf17.iad0.netskope.com \
  --pop iad0 \
  --name vpptrex02 \
  --fqdn vpptrex02.iad0.netskope.com \
  --vlan-num 700 \
  --cpus 16 \
  --memory 32 \
  --image ubuntu20

# Create Client VM (8 cores, 8GB)
polaris image vm create sriov \
  --kvm kvmdevperf18.iad0.netskope.com \
  --pop iad0 \
  --name test.client01 \
  --fqdn test.client01.iad0.netskope.com \
  --vlan-num 584 \
  --cpus 8 \
  --memory 8 \
  --image ubuntu20
```

##### Method 2: YAML File (VPP-based Gateways and Clients)

**Steps**:
1. Create a YAML configuration file with VM specifications
2. Transfer the YAML file to polaris-tools server
3. Execute `polaris image vm create-from-yaml <yaml-file>`

**YAML Template** (vpp_deploy.yml):
```yaml
allowDuplicateHostnames: null
autostart: true
base_image: ubuntu20
cpus: 8
disableMemballoon: null
diskGiB: 100
disks: []
existing_disks: []
fqdn: <vm-fqdn>
kvm_criteria: []
kvm_hostname: <kvm-hostname>
memoryKiB: 8388608  # 8GB
name: <vm-name>
native_vlan: 800
network_config:
  interfaces:
  - type: sriov
    vlan: <vlan-number>
  - dns: none
    ip_address: none
    name: egw
    num_vfs: 2
    skip_config: true
    type: sriov
    vlan: 584
    vlan_tagged: false
override_domain: iad0.netskope.com
pop_name: iad0
```

**Command Pattern**:
```bash
polaris image vm create-from-yaml <yaml-file>
```

**Example Workflow**:
```bash
# 1. Create YAML file with appropriate values
# 2. Copy to polaris-tools (if not already there)
# 3. Execute creation
polaris image vm create-from-yaml vpp_ipsec_gw.yml
```

**YAML Configuration Values**:
- `cpus`: 8 (for all VPP-based VMs)
- `memoryKiB`: 8388608 (8GB for all VPP-based VMs)
- `diskGiB`: 100 (default)
- `base_image`: ubuntu20
- `fqdn`: Full qualified domain name (e.g., vppipsecgw01.iad0.netskope.com)
- `name`: Short name without domain (e.g., vppipsecgw01.iad0)
- `kvm_hostname`: One of kvmdevperf16-20.iad0.netskope.com
- `vlan`: Primary VLAN number (e.g., 700, 584, 592)

#### List All KVM Hosts
**Purpose**: Get a list of all available KVM hypervisor hosts

**Command Pattern**:
```bash
polaris image kvm list
```

#### Lookup VM/Device Information
**Purpose**: Find which KVM host a VM is running on, along with guest details

**Command Pattern**:
```bash
polaris image device_lookup <hostname>
```

**Examples**:
```bash
# Lookup TREX VM location
polaris image device_lookup vpptrex01.iad0.netskope.com

# Find specific device via DNS query
polaris dns2 record a list --zone iad0.netskope.com | grep 'steeringlb01'
```

#### Stop a VM
**Purpose**: Gracefully stop a virtual machine running on a specific KVM host

**Command Pattern**:
```bash
polaris image vm stop --kvm <kvm-hostname> --guest <guest-name>
```

**Examples**:
```bash
# Stop VPP gateway VM
polaris image vm stop --kvm kvmdevperf08.iad0.netskope.com --guest vppigw02.c18

# Stop VPP GRE TREX VM
polaris image vm stop --kvm kvmdevperf10.iad0.netskope.com --guest vppgretrex01.c18.iad0
```

**Note**: Guest name is typically the short hostname without domain (e.g., `vppigw02.c18` instead of `vppigw02.c18.iad0.netskope.com`)

---

## Common Workflows

### Workflow 1: Create New VM (Automated Process)

**User provides**: Hostname and VM type

**System automatically**:
- Selects CPU and memory based on VM type
- Chooses deployment method (direct command vs YAML)
- Selects available KVM host (kvmdevperf16-20)
- Retries on different KVM if resources unavailable

**Decision Tree**:
```
Is VM type VPP-based? (VPP IPSEC/GRE/ECGW gateway, VPP client)
├─ YES: Use YAML file method
│   ├─ Create YAML with 8 CPUs, 8GB memory
│   ├─ Transfer to polaris-tools
│   └─ Execute: polaris image vm create-from-yaml
│
└─ NO: Use direct command method
    ├─ Is it Legacy IPSEC/GRE gateway or TRex?
    │   └─ YES: Use 16 CPUs, 32GB memory
    └─ Is it Client VM or Dummy CFW?
        └─ YES: Use 8 CPUs, 8GB memory
```

**Example - Create VPP IPSEC Gateway**:
1. User provides: "vppipsecgw05.iad0.netskope.com" and "VPP IPSEC Gateway"
2. System automatically:
   - Detects VPP-based VM → Use YAML method
   - Sets: 8 CPUs, 8GB memory
   - Creates YAML with appropriate configuration
   - Selects KVM: kvmdevperf16.iad0.netskope.com (or next available)
   - Executes: `polaris image vm create-from-yaml vpp_ipsec_gw.yml`

**Example - Create Legacy GRE Gateway**:
1. User provides: "legacy.gregw05.iad0.netskope.com" and "Legacy GRE Gateway"
2. System automatically:
   - Detects Legacy VM → Use direct command method
   - Sets: 16 CPUs, 32GB memory
   - Selects KVM: kvmdevperf17.iad0.netskope.com (or next available)
   - Executes direct command with appropriate parameters

**Example - Create TRex VM**:
1. User provides: "vpptrex05.iad0.netskope.com" and "TRex VM"
2. System automatically:
   - Detects TRex VM → Use direct command method
   - Sets: 16 CPUs, 32GB memory
   - Executes creation command

**Example - Create Client VM**:
1. User provides: "testclient02.iad0.netskope.com" and "Client VM"
2. System automatically:
   - Detects Client VM → Use direct command method
   - Sets: 8 CPUs, 8GB memory
   - Executes creation command

### Workflow 2: Allocate VIP for New Service - **RECOMMENDED**
This is the primary and recommended method for IP allocation.

1. Verify the FQDN format is correct (no duplicate POP names):
   - ✅ CORRECT: `hostname.cluster.vlan<num>.<pop>.netskope.com`
   - ❌ WRONG: `hostname.cluster.<pop>.vlan<num>.<pop>.netskope.com`
2. Use `polaris-image --allocate-vip` with appropriate parameters:
   ```bash
   polaris-image --allocate-vip --vip-fqdn <service-fqdn> --vlan-num <vlan> --pop-name <pop>
   ```
3. Verify success message with allocated IP details (ignore DNS timeout warnings if allocation succeeds)
4. Use the allocated IP/FQDN for service configuration

### Workflow 3: Manual IP Reservation - **LAST RESORT ONLY**
⚠️ Use this workflow only when VIP allocation is not possible or not supported.

1. Check for free IPs in the target subnet:
   ```bash
   polaris dns2 record a list --zone iad0.netskope.com | grep <subnet>
   ```
2. Choose an available IP from the output
3. Register the IP in DNS (only as last resort):
   ```bash
   polaris dns2 record a create --zone iad0.netskope.com <fqdn> <ip>
   ```

### Workflow 4: Clean Up Unused Resources
1. Delete IP from IPAM:
   ```bash
   polaris ipam prefix delete <ip>
   ```
2. Delete DNS record:
   ```bash
   polaris dns record a delete --zone iad0.netskope.com <fqdn> <ip>
   ```

---

## Important Notes

- **IP Allocation Preference**: ALWAYS use `polaris-image --allocate-vip` method for IP allocation. Manual DNS record creation (`polaris dns2 record a create`) should ONLY be used as a last resort when VIP allocation is not possible
- **Authentication**: Always run `source /etc/polaris/qe-env` after logging into polaris-tools
- **POP Names**: Common POPs include `iad0`, `sje011`, etc. - use the appropriate POP for your infrastructure
- **VLAN Numbers**: Ensure VLAN numbers match your network topology (e.g., 584, 592, 678, 700)
- **DNS Zones**: Most operations use `iad0.netskope.com` but verify the correct zone for your environment
- **FQDN Format Rules**:
  - Standard format: `<hostname>.<cluster>.vlan<number>.<pop>.netskope.com`
  - **CRITICAL**: Do NOT duplicate the POP name in the FQDN
  - Examples:
    - ✅ CORRECT: `vppgregw01.c18.vlan700.iad0.netskope.com`
    - ❌ WRONG: `vppgregw01.c18.iad0.vlan700.iad0.netskope.com` (duplicate iad0)
- **Automatic IP Pool Assignment**: VIP allocation assigns IPs from the VLAN's entire CIDR block, which may span multiple /24 subnets. The assigned IP may differ from the specific subnet you checked for availability.
- **VM Creation Guidelines**:
  - Always ask user for VM type before creation (Legacy IPSEC/GRE gateway, VPP IPSEC/GRE/ECGW gateway, TRex, Client, VPP Client, Dummy CFW)
  - User only needs to provide hostname and VM type - CPU/memory are automatically selected
  - **VPP-based VMs** (VPP IPSEC/GRE/ECGW, VPP Client): Use YAML file method with 8 CPUs, 8GB memory
  - **Legacy VMs** (Legacy IPSEC/GRE): Use direct command with 16 CPUs, 32GB memory
  - **TRex VMs**: Use direct command with 16 CPUs, 32GB memory
  - **Client/CFW VMs**: Use direct command with 8 CPUs, 8GB memory
  - Prefer KVM hosts: kvmdevperf16-20.iad0.netskope.com
  - If resources unavailable on one KVM, automatically try the next available KVM
  - Default image: ubuntu20
  - Default disk: 100GB

---

## Troubleshooting

### Common Errors and Solutions

#### Error: "DNS Zone not found" or "http_code: 400"
**Cause**: Incorrect FQDN format, usually duplicate POP name in the hostname

**Example of WRONG format**:
```bash
# WRONG - has 'iad0' twice
polaris-image --allocate-vip --vip-fqdn vppgregw01.c18.iad0.vlan700.iad0.netskope.com --vlan-num 700 --pop-name iad0
```

**Solution**: Remove the duplicate POP name
```bash
# CORRECT - only one 'iad0'
polaris-image --allocate-vip --vip-fqdn vppgregw01.c18.vlan700.iad0.netskope.com --vlan-num 700 --pop-name iad0
```

#### Error: "DNS operation timed out"
**Cause**: Temporary DNS timeout - this is usually a transient error and can be ignored if the operation succeeds

**Solution**:
- Check if the operation succeeded despite the timeout error
- Look for "IP Allocation success" message in the output
- The timeout error often appears but doesn't prevent successful allocation

#### VIP Allocated from Different Subnet Than Expected
**Behavior**: When checking free IPs in 10.136.133.0/24, the VIP allocation assigns an IP from 10.136.134.0/24

**Explanation**: This is NORMAL behavior
- VLANs use larger CIDR blocks (e.g., /21) that span multiple /24 subnets
- The VIP allocation system automatically selects from any available subnet within the VLAN's CIDR range
- Example: VLAN 700 uses 10.136.133.0/21, which includes:
  - 10.136.133.0/24
  - 10.136.134.0/24
  - 10.136.135.0/24
  - And more...

**Action**: No action needed - the allocated IP is correct and will work properly

#### VM Creation - Insufficient Resources on KVM
**Cause**: Selected KVM host does not have sufficient CPU/memory resources

**Solution**:
- Try the next available KVM host from kvmdevperf16-20
- Example sequence:
  1. Try kvmdevperf16.iad0.netskope.com
  2. If fails, try kvmdevperf17.iad0.netskope.com
  3. Continue through kvmdevperf18, 19, 20 until successful

#### VM Creation - Wrong Deployment Method
**Error**: Using direct command for VPP-based VM or YAML for legacy VM

**Solution**: Always use the correct method based on VM type
- **VPP-based** (VPP IPSEC/GRE/ECGW, VPP Client) → YAML file method
- **Legacy** (Legacy IPSEC/GRE, TRex, Client, CFW) → Direct command method

---

## Keywords for Auto-Invocation
When users mention these operations, consider using this skill:
- **IP Allocation**: IP allocation, reserve IP, allocate VIP, allocate IP on VLAN, find free IP
- **DNS Management**: DNS record creation, register hostname, create DNS record, delete DNS
- **VM Creation**: create VM, bring up VM, deploy VM, new VM, provision VM, create gateway, create client, create TRex
- **VM Management**: stop VM, find VM, VM lookup, device lookup, which KVM
- **KVM Operations**: KVM host lookup, list KVM hosts, available KVM
- **VLAN Operations**: find VLAN for subnet, which VLAN, subnet belongs to
- **General Polaris**: polaris operations, use polaris, polaris tool
