# Topology Finder Skill

## Overview
This skill discovers and maps network topology from client machines to the internet through Netskope infrastructure (IPSEC/GRE/ECGW gateways). It creates a detailed network diagram showing all devices, interfaces, and IP addresses for troubleshooting and testing purposes.

## Access Methods
- **Primary**: Use `tsh ssh --cluster <cluster> <hostname>` to access devices
- **Fallback**: Use ansible user via MCP SSH server if tsh fails

## Topology Types

### 1. IPSEC Gateway
- Standard IPSEC tunnel-based connectivity using IKE/ESP protocols
- VPP Config location: `/opt/ns/ipsecgw/ns-vpp-ipsec.conf`
- IKE interface binding: `/opt/ns/ipsec/netskope.plugin.strongswan.conf` (defines which interface accepts IKE requests)

#### Client Types:
**Legacy Clients**:
- Config files: `/etc/ipsec.conf` and `/etc/ipsec.secrets`
- Status check: Use `strongswan ipsec` commands

**VPP-based Clients**:
- Config location: `/opt/ns/tenant/6666/ipsecgw/`
- Status check: Use `strongswan ipsec` commands
- Data path: Similar to ECGW VPP setup

#### Gateway Configuration:
- Tenant config: `/opt/ns/tenant/<tenant-id>/ipsecgw/`
- Status check: Use `swanctl` generic commands (NOT ipsec commands)
- VPP interfaces: Each tunnel creates an `ipip` interface
  - Check with: `sudo vppctl show interface`

#### Naming Conventions:
- **VPP gateways**: Typically start with keyword "vpp" (e.g., `vppipsecgw01`, `vppipsecgw02`)
- **QA setup**: No defined naming scheme

#### IKE Request Handling:
- **VPP systems**: Always accept IKE requests on loop interface VIP (shared VIP on `lcploop0`)
- **Client side**: Can be any interface
  - Check `local_addrs` in config files:
    - `netskope.stsvc.default.swanctl.conf` OR
    - `netskope.default.swanctl.conf`
  - This shows which IP the gateway will accept IKE requests on

#### Key Discovery Commands:
- **Gateway tunnel status**: `swanctl --list-sas`
- **VPP interfaces**: `sudo vppctl show interface` (shows ipip tunnel interfaces)
- **Client tunnel status**: `ipsec status` or `ipsec statusall`

#### Topology Diagram Requirements:
- **IMPORTANT**: Always show subnet information for IPSEC topologies
  - Local subnet (client-side network ranges)
  - Remote subnet (gateway/Netskope-side network ranges)
  - Document subnets from tunnel configuration files

#### IPSEC Tenant-Specific Data:
**IMPORTANT**: When mapping IPSEC topology, only show information for the specific tenant:
- If gateway tenant is 3624, fetch and display only tenant 3624 configuration from gateway
- Show only the IPSEC tunnel(s) associated with that tenant
- Focus on the specific tenant's config in `/opt/ns/tenant/<tenant-id>/ipsecgw/`
- Filter out other tenant information

### 2. GRE Gateway
- GRE tunnel-based connectivity
- Config location: `/opt/ns/gregw/ns-vpp-gre.conf`

### 3. ECGW/PAS Gateway
- Physical Layer 2 connectivity from customer datacenter to Netskope datacenter
- Config location: `/opt/ns/pasgw/ns-vpp-pas.conf`

## Common Network Flow

All topology types follow this basic flow:

```
Client → [Steering LB (optional)] → Gateway (IPSEC/GRE/ECGW) → Proxy/CFW → Internet
```

**Exception for ECGW**:
```
Client → Arista Switch → Steering LB → ECGW Gateway → Proxy/CFW → Internet
```

## Key Information to Collect

### For Each Device:
1. **Hostname** and management IP
2. **Network interfaces** (name, IP address, subnet)
3. **Data path interfaces** (separate from management)
4. **Routes** and routing configuration
5. **Tenant information** (from `/opt/ns/tenant/<tenant-id>`)

### For Client Machines (ECGW Topology):
1. **BGP Next-Hop Information**:
   - Run `ip route show` to display routing table
   - Identify next-hop IPs (shown as `via <ip_address>`)
   - These next-hops point to Arista switch interfaces
   - Document the BGP peer relationship between client and Arista
   - This helps identify which Arista switches are configured in the topology
2. **Data Path Interface**:
   - Identify VLAN interface used for data path (e.g., bond0.207)
   - Document IP address and subnet

### For VPP-Based Gateways:
1. **VPP Configuration File**:
   - IPSEC: `/opt/ns/ipsecgw/ns-vpp-ipsec.conf`
   - GRE: `/opt/ns/gregw/ns-vpp-gre.conf`
   - ECGW/PAS: `/opt/ns/pasgw/ns-vpp-pas.conf`

2. **DSR Routes**: Return traffic routes from CFW/Proxy (bypasses Steering LB)

### For IPSEC Gateways (Additional):
1. **IKE Interface Configuration**:
   - Check `/opt/ns/ipsec/netskope.plugin.strongswan.conf` for interface bindings
   - Identify which interface accepts IKE requests (typically VIP on lcploop0)

2. **Tunnel Configuration**:
   - Gateway: `/opt/ns/tenant/<tenant-id>/ipsecgw/`
   - Look for `netskope.stsvc.default.swanctl.conf` or `netskope.default.swanctl.conf`
   - Extract `local_addrs` (gateway IKE endpoint)
   - Extract `remote_addrs` (client IKE endpoint)
   - Extract `local_ts` (local traffic selectors/subnets)
   - Extract `remote_ts` (remote traffic selectors/subnets)

3. **Tunnel Status**:
   - Gateway: `swanctl --list-sas` (shows active Security Associations)
   - Gateway VPP: `sudo vppctl show interface` (shows ipip interfaces per tunnel)
   - Client (legacy): `ipsec status` or `ipsec statusall`
   - Client (VPP): Same as above

4. **Subnet Information** (Critical for IPSEC):
   - **Local subnet**: Network ranges on Netskope/gateway side
   - **Remote subnet**: Network ranges on client side
   - These define which traffic flows through the tunnel
   - Must be included in all IPSEC topology diagrams

### For Steering LB:
- **Purpose**: Load balances traffic across multiple gateway nodes
- **Method**: Uses VIP (Virtual IP) for traffic distribution
- **Backend Nodes**: List of gateway nodes being load balanced

### VIP Configuration:
- **Single shared VIP per service**: Each service (ECGW, IPSEC, GRE) has a single VIP that is SHARED across all gateway nodes
- **Location**: The SAME VIP is configured on the `lcploop0` interface on ALL gateway nodes in the cluster
- **Direction**: Steering LB → VIP → Gateway nodes (source IP-based load balancing)
- **Discovery**: To find the VIP, check the `lcploop0` interface configuration on any gateway node - all will have the same IP
- **Example**: For ECGW, all 3 nodes (ecgw01, ecgw02, ecgw03) have the SAME VIP: `192.168.64.1`
- **Load Balancing**: Source IP-based load balancing at Steering LB layer distributes traffic to one of the gateway nodes
- **Usage**:
  - All gateway nodes listen on the same shared VIP
  - Steering LB uses source IP hash to distribute traffic to one of the nodes
  - Gateway nodes use the shared VIP as source when connecting to Proxy/CFW
  - Gateway nodes use the shared VIP as source for tunnels (GRE/IPSEC)
  - Provides high availability - if one node fails, LB redirects to remaining nodes

### For Proxy/CFW Connections:
- **CFW Details**: Check `/opt/ns/common/remote/stsvc-cfwsvc`
  - Source IP from gateway
  - CFW destination information

- **Proxy Details**: Check `/opt/ns/common/remote/nsipsecgw-stsvc-nsproxy-dest`
  - Focus on "normal" proxy configuration only
  - Source IP from gateway

### Management vs Data Path:
- All devices have a **management interface** (Linux-level, default route)
- Management interface is **NOT used for data path** in most cases
- Identify and document data path interfaces separately

## ECGW-Specific Information

### Architecture Components:

1. **P2P Connections**: Physical Layer 2 connectivity from customer datacenter to Netskope datacenter

2. **BGP Sessions**:
   - **Customer ↔ Arista**: Customer advertises all routes to Arista for return traffic
   - **ECGW ↔ Arista**: Per-tenant routing within Netskope. ECGW advertises Netskope routes to Arista, which re-advertises to customer
   - **BGP Next-Hop Discovery**: Check BGP routes on client machine to identify Arista switch IPs
     - Command: `ip route` or `ip route show` on client machine
     - Look for next-hop IPs in routing table (e.g., `via <arista_ip>`)
     - These next-hop IPs are the Arista switch interfaces connected to the client
     - Example: If client route shows `via 169.254.27.0`, this is the Arista switch's BGP peer IP
     - This helps identify which Arista switches are in the topology

3. **GRE Tunnels**: Created between Arista and ECGW (transparent to customer)

4. **Steering LB**: Load balances traffic across 3 ECGW nodes using configured VIPs

### ECGW Naming Conventions:

**Internal POPs**:
- Format: `ecgw0[1-3].<pop_name>.netskope.com`
- Example: `ecgw01.iad0.netskope.com`
- Internal POPs: stg01, qa01, iad0

**Production POPs**:
- Format: `ecgw0[1-3].<pop_name>.skope.net`
- All POPs except stg01, qa01, iad0 are production

### ECGW Node Configuration:
- Each POP has **3 ECGW nodes**: ecgw01, ecgw02, ecgw03
- All GRE tunnels are present on all ECGW nodes

### ECGW Tenant-Specific Data:
**IMPORTANT**: When mapping ECGW topology, only show information for the specific tenant:
- If client is tenant 3624, fetch and display only tenant 3624 configuration from ECGW
- Show only the GRE tunnel(s) associated with that tenant
- Filter out other tenant information

## Discovery Workflow

1. **Identify the starting device** (hostname provided by user)
2. **Access the device** using tsh or ansible
3. **Determine gateway type** (IPSEC/GRE/ECGW) by checking directories
4. **Collect device information**:
   - Network interfaces and IPs
   - VPP configuration (if VPP-based)
   - Tenant configuration
   - Routes and DSR routes
5. **Trace upstream/downstream**:
   - Find Steering LB (if present)
   - Identify connected Proxy/CFW nodes
   - For ECGW: find Arista switches and BGP peers
   - For IPSEC: find client machines and tunnel endpoints
6. **For IPSEC Topologies - Additional Steps**:
   - Check IKE interface binding (`/opt/ns/ipsec/netskope.plugin.strongswan.conf`)
   - Get tunnel configuration from `/opt/ns/tenant/<tenant-id>/ipsecgw/`
   - Run `swanctl --list-sas` to verify active tunnels
   - Check `sudo vppctl show interface` for ipip interfaces
   - Extract subnet information (local_ts and remote_ts)
   - Document both IKE endpoints (local_addrs and remote_addrs)
   - If client access is available, check client config and status
7. **Map complete topology** following the network flow
8. **Generate diagram** with all collected information

## Output Format

Create a clear network diagram showing:
- Device hostnames and management IPs
- Data path interfaces with IPs
- Connections between devices with interface details
- VIPs and load balancing information
- Tenant ID and associated configuration
- BGP sessions (for ECGW)
- GRE tunnels (for ECGW)
- **IPSEC-specific information**:
  - IKE endpoints (local_addrs and remote_addrs)
  - Local subnets (local_ts / traffic selectors)
  - Remote subnets (remote_ts / traffic selectors)
  - Tunnel status (UP/DOWN)
  - VPP ipip interface names
  - IKE interface binding (which interface accepts IKE)

Format the diagram in a way that's easy to understand for troubleshooting and testing purposes by an AI Agent.

## Notes

- Focus on data path interfaces, not management interfaces
- Document any exceptions or unusual configurations found
- Verify tenant-specific filtering for ECGW and IPSEC topologies
- For IPSEC: Always include subnet information in diagrams (critical for tunnel traffic flow understanding)
- For IPSEC: Use `swanctl` commands on gateways, `ipsec` commands on clients
- For VPP-based systems: Check both swanctl status and VPP interface status
- GRE-specific details will be provided separately when needed 
