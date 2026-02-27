---
name: ecgw-skill
description: ECGW is new type of gateway which we have introduce in netskope infra, its provide direct l2 level physical connectivity between customer datacenter and netskope datacenter.
---

# ECGW Service Overview

## Architecture & Flow

### ECGW/PAS Flow
```
Client Machine → Arista Switch → Steering LB → ECGW → Proxy/CFW → Internet
```

### Key Components

1. **P2P Connections**: Physical layer 2 connectivity from customer datacenter to Netskope datacenter

2. **BGP Sessions**:
   - **Customer ↔ Arista**: Customer sends all routes to Arista for return traffic routing
   - **ECGW ↔ Arista**: Per-tenant routing within Netskope infrastructure. ECGW advertises Netskope routes to Arista, which re-advertises them to customer

3. **GRE Tunnels**: Created between Arista and ECGW (transparent to customer)

4. **Steering LB**: Load balances traffic across 3 ECGW nodes using configured VIPs

## Important Notes

- ECGW is also known as **PAS** (Private Access Service)
- ECGW is **VPP-based**, so VPP commands and vpp-skill apply here
- Traffic flows to either Proxy or CFW from ECGW
- Common configurations are in `/opt/nc/common/remote/` directory
- Tenant configs are in `/opt/ns/tenant/<tenant-id>` directory

## Hostname Conventions

### Internal POPs
- Format: `ecgw0[1-3].<pop_name>.netskope.com`
- Example: `ecgw01.iad0.netskope.com`
- Internal POPs: stg01, qa01, iad0

### Production POPs
- Format: `ecgw0[1-3].<pop_name>.skope.net`
- All POPs except stg01, qa01, iad0 are production

### Node Configuration
- Each POP has **3 ECGW nodes** (ecgw01, ecgw02, ecgw03)

## Testing Setup

### QA01 Topology (iad0 POP)

```
Client Machine → Arista Switch → Steering LB → ECGW → Proxy/CFW → Internet
```

#### Test Infrastructure

**Client Machine**:
- `pastrex01.iad0.netskope.com`

**Steering LB**:
- `pasgwstlb01.iad0.netskope.com`
- `pasgwstlb02.iad0.netskope.com`
- `pasgwstlb03.iad0.netskope.com`

**ECGW Nodes**:
- `ecgw01.iad0.netskope.com`
- `ecgw02.iad0.netskope.com`
- `ecgw03.iad0.netskope.com`

#### Testing Scope

**In Scope**:
- Client machine (pastrex01)
- ECGW nodes (ecgw01-03)
- Steering LB (for troubleshooting only)

**Out of Scope**:
- Arista switches (no access)
- CFW and Proxy services

### Production Setup

- Similar topology to QA
- Basic traffic testing only (ICMP, web traffic)
- Same commands apply

## Connectivity Expectations

### Arista Switch Connectivity
**IMPORTANT**: Arista switch IPs (e.g., 172.23.9.129, 172.23.9.10) are **NOT pingable from ECGW**. This is expected behavior and does not indicate a problem.

- Arista switches are not directly reachable via ICMP from ECGW nodes
- Communication happens through BGP sessions and GRE tunnels
- Do not attempt to ping Arista IPs as a connectivity test

### BGP Session Requirements
BGP sessions between ECGW and Arista must be in **"Established"** state for traffic to flow.

**Healthy BGP Session:**
```
Peer            AS Up/Down State       |#Received  Accepted
172.23.9.129 55256 01:23:45 Establ      |       10        10
```

**Unhealthy BGP Session (Problem):**
```
Peer            AS Up/Down State       |#Received  Accepted
172.23.9.129 55256   never Active      |        0         0
```

If BGP is in "Active" or "Idle" state, traffic will not flow through GRE tunnels.

## Common ECGW Commands

### Check BGP Status
```bash
gobgp -p 50052 neighbor
echo ""
sudo gobgp -p 50052 global rib
echo ""
```

**Expected Output:** BGP neighbors should show "Establ" (Established) state with routes received.

### Check GRE Tunnel Status
```bash
sudo vppctl show gre tunnel
```

### ECGW Configuration Location

**Path**: `/opt/ns/gregw/cfg/tenantmap/tenant<tenant_id>.json`

Example: `/opt/ns/gregw/cfg/tenantmap/tenant3624.json` for tenant 3624

**Note**: Focus on the **Express Connect** section of the configuration

### Additional Commands

All standard Linux commands work as ECGW services are hosted on Ubuntu KVM.

For VPP-specific commands, refer to the **vpp-skill**.

## Troubleshooting

### Traffic Not Flowing

1. **Check BGP Session Status First**
   ```bash
   gobgp -p 50052 neighbor
   ```
   - BGP must be in **"Establ"** (Established) state
   - If in "Active" or "Idle" state, BGP session is down - this is the primary issue to resolve
   - Check if routes are being received (`#Received` column should be > 0)

2. **Verify GRE Tunnel Configuration**
   ```bash
   sudo vppctl show gre tunnel
   ```
   - Confirm tunnels exist for the tenant
   - Note tunnel instance numbers and destination IPs

3. **Check VPP Errors**
   ```bash
   sudo vppctl show errors | grep -i gre
   ```
   - Look for "GRE input packets dropped" errors
   - High drop counts indicate GRE packet issues

4. **Verify Tenant Configuration**
   - Check tenant configuration in `/opt/ns/gregw/cfg/tenantmap/tenant<id>.json`
   - Verify express-connect circuits are configured
   - Confirm advertised routes match expected prefixes

5. **Check GRE Tunnel Traffic**
   ```bash
   sudo vppctl show interface gre<instance>
   ```
   - Monitor rx/tx packet counters
   - Counters should increment during active traffic

### Common Issues

- **BGP in "Active" State**: BGP session cannot establish. Check if gobgpd is running and network connectivity exists.
- **No GRE Tunnels on Node**: Tenant may not be configured on this specific ECGW node. Check other nodes.
- **Arista Not Pingable**: This is EXPECTED behavior. Do not treat as an error.
- **Load Balancing**: Check Steering LB VIP configuration and health checks if traffic is not reaching ECGW

## Remote Access

Use Teleport (tsh) for accessing ECGW nodes:
```bash
tsh ssh --cluster <cluster> <hostname>
```

Example:
```bash
tsh ssh --cluster iad0 ecgw01.iad0.netskope.com
```
