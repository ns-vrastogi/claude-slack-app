# QA01 ECGW Topology - Tenant 3624
## Network Architecture Diagram

```
                                    INTERNET
                                        |
                    +-------------------+-------------------+
                    |                                       |
              CFW Service                            Proxy Service
           10.111.96.6:7777                      10.111.59.221:7777
           HC: 8999                              HC: 8990
                    |                                       |
                    +-------------------+-------------------+
                                        |
                            ECGW Gateway Layer (VPP-Based)
                    All 3 nodes share same VIP: 192.168.64.1
                    +-------------------+-------------------+
                    |                   |                   |
                ecgw01              ecgw02              ecgw03
         Mgmt: 10.136.134.100  Mgmt: 10.136.134.101  Mgmt: 10.136.134.102
         loop0: 192.168.64.1   loop0: 192.168.64.1   loop0: 192.168.64.1
         (shared VIP)          (shared VIP)          (shared VIP)
                    |                   |                   |
                    +-------------------+-------------------+
                                        |
                         VIP: 192.168.64.1 (on lcploop0)
                   Steering LB balances to ECGW (by source IP)
                                        |
                            Steering LB Layer (Source IP-based Load Balancing)
                    +-------------------+-------------------+
                    |                   |                   |
              pasgwstlb01          pasgwstlb02         pasgwstlb03
            10.111.96.135        10.111.96.136       10.111.96.137
                    |                   |                   |
                    +-------------------+-------------------+
                                        |
                            Arista Switch Layer (BGP Peers)
                    +-------------------+-------------------+
                    |                                       |
             Arista Switch 1                        Arista Switch 2
             172.23.9.129                           172.23.9.10
           (BGP AS 55256)                         (BGP AS 55256)
           GRE: 172.23.8.129                      GRE: 172.23.8.2
                    |                                       |
                    +-------------------+-------------------+
                                        |
                                  Client Machine
                               pastrex01.iad0
                         Mgmt: 10.136.134.107/21
                         Data: 169.254.27.1/31 (bond0.207)
```

---

## VIP Configuration

**ECGW Service VIP: 192.168.64.1 (Shared Across All Nodes)**

- **Location:** Configured on the `lcploop0` interface (VPP loop0) on ALL ECGW gateways
- **Shared Configuration:** All 3 ECGW nodes (ecgw01, ecgw02, ecgw03) have the SAME VIP: 192.168.64.1
- **Purpose:** Single shared VIP for the ECGW service cluster
- **Direction:** Steering LB → VIP 192.168.64.1 → ECGW nodes (load balanced by source IP)
- **Load Balancing Method:** Source IP-based load balancing at Steering LB layer
- **Usage:**
  - All ECGW nodes listen on the same VIP: 192.168.64.1
  - Steering LB distributes traffic based on source IP to one of the 3 ECGW nodes
  - ECGW nodes use this shared VIP as source for GRE tunnels and connections to Proxy/CFW
  - This provides high availability - if one node fails, traffic automatically goes to remaining nodes

---

## Component Details

### 1. Client Machine: pastrex01.iad0.netskope.com

**Management Interface:**
- Interface: bond0.700
- IP Address: 10.136.134.107/21
- Gateway: 10.136.128.1

**Data Path Interface (to Arista):**
- Interface: bond0.207 (VLAN 207)
- IP Address: 169.254.27.1/31
- BGP Peer: 169.254.27.0 (Arista connection)

**Routing:**
- Default: via 10.136.128.1 (management)
- 8.8.8.8: via 169.254.27.0 (data path via Arista)
- 5.161.7.195: via 169.254.27.0 (data path via Arista)

---

### 2. Arista Switch Layer (No Direct Access)

**Arista Switch 1:**
- IP: 172.23.9.129
- BGP AS: 55256
- Role: BGP peer with ECGW, forwards tenant routes
- GRE Endpoint: 172.23.8.129 (tunnel to ECGW)
- Connected Circuit: ms-circuit-01

**Arista Switch 2:**
- IP: 172.23.9.10
- BGP AS: 55256
- Role: BGP peer with ECGW, forwards tenant routes
- GRE Endpoint: 172.23.8.2 (tunnel to ECGW)
- Connected Circuit: ms-circuit-02

**BGP Configuration:**
- Receives routes from Customer (pastrex01)
- Advertises routes to ECGW via BGP
- Creates GRE tunnels to ECGW nodes

**Tenant 3624 Advertised Routes:**
- 8.8.8.8/32 (Next-hop: 172.23.9.129 and 172.23.9.10)
- 172.16.5.129/32 (Next-hop: 172.23.9.129 and 172.23.9.10)

---

### 3. Steering LB Layer

**pasgwstlb01.iad0.netskope.com:**
- Management IP: 10.136.134.97
- Data Path IP (VLAN 678): 10.111.96.135/24
- Role: Load balances traffic to ECGW nodes using VIP

**pasgwstlb02.iad0.netskope.com:**
- Management IP: 10.136.134.98 (estimated)
- Data Path IP (VLAN 678): 10.111.96.136/24 (estimated)

**pasgwstlb03.iad0.netskope.com:**
- Management IP: 10.136.134.99 (estimated)
- Data Path IP (VLAN 678): 10.111.96.137/24 (estimated)

**Backend Nodes:**
- ecgw01.iad0.netskope.com
- ecgw02.iad0.netskope.com
- ecgw03.iad0.netskope.com

---

### 4. ECGW Gateway Layer (VPP-Based)

#### ecgw01.iad0.netskope.com

**Management Interface:**
- Interface: bond0.700
- IP: 10.136.134.100/21

**Data Path Interfaces (Linux CP):**
- lcpbond0.678 (to CFW): 10.111.96.128/24
- lcpbond0.677 (to Proxy): 10.111.59.224/24
- tap0 (to Arista): 172.23.9.1/24

**VPP Interfaces:**
- BondEthernet0.678: 10.111.96.128/24 (CFW path)
- BondEthernet0.677: 10.111.59.224/24 (Proxy path)
- loop0: 192.168.64.1/32 (Shared VIP - same on all ECGW nodes)
  - Used as GRE tunnel source
  - Used as source IP for Proxy/CFW connections
  - Receives traffic from Steering LB
  - Check with: `ip addr show lcploop0` or `sudo vppctl show interface addr loop0`

**BGP Configuration:**
- BGP Neighbors:
  - 172.23.9.10 (AS 55256) - Established
  - 172.23.9.129 (AS 55256) - Established
- BGP Routes Learned: 0 (routes advertised to ECGW, not learned)

**GRE Tunnels (Tenant 3624 Specific):**
1. **gre156**:
   - Source: 192.168.64.1
   - Destination: 172.23.8.129 (Arista Switch 1)
   - Status: UP
   - Circuit: ms-circuit-01

2. **gre157**:
   - Source: 192.168.64.1
   - Destination: 172.23.8.2 (Arista Switch 2)
   - Status: UP
   - Circuit: ms-circuit-02

**Other GRE Tunnels (Other Tenants - Not Detailed):**
- gre150, gre151, gre152, gre153, gre154, gre155 (up to 8 total tunnels)

#### ecgw02.iad0.netskope.com
- Similar configuration to ecgw01
- Loop0: 192.168.64.1/32 (Shared VIP - same as ecgw01 and ecgw03)
- Same GRE tunnel destinations for tenant 3624

#### ecgw03.iad0.netskope.com
- Similar configuration to ecgw01
- Loop0: 192.168.64.1/32 (Shared VIP - same as ecgw01 and ecgw02)
- Same GRE tunnel destinations for tenant 3624

---

### 5. Proxy/CFW Layer

**CFW Service:**
- Host: 10.111.96.6
- Port: 7777
- Health Check Port: 8999
- Interface IP on ECGW: 10.111.96.128 (VLAN 678)
- Role: Cloud Firewall service, processes tenant traffic

**Proxy Service (Normal):**
- Host: 10.111.59.221
- Port: 7777
- Health Check Port: 8990
- Interface IP on ECGW: 10.111.59.224 (VLAN 677)
- Role: Web proxy service, processes tenant traffic

---

## Tenant 3624 Specific Configuration

**Tenant Information:**
- Tenant Name: Netskope
- Tenant ID: d7b4d8d3dacaa57e9a8b1e101c996243
- Tenant ID Number: 3624
- Home POP: qa01-mp-npe (ID: 0xDA0B)
- Connected POP: qa01-dp-npe

**Express Connect Circuits:**

1. **Circuit ms-circuit-01:**
   - VLAN ID: 200
   - Site Name: ms-config-replica-vishal
   - Probe IP: 172.23.9.1
   - GRE Source IP: 172.23.8.129
   - Next-Hop: 172.23.9.129 (Arista Switch 1)
   - Advertised Routes:
     - 8.8.8.8/32
     - 172.16.5.129/32

2. **Circuit ms-circuit-02:**
   - VLAN ID: 200
   - Site Name: ms-config-replica-vishal
   - Probe IP: 172.23.9.1
   - GRE Source IP: 172.23.8.2
   - Next-Hop: 172.23.9.10 (Arista Switch 2)
   - Advertised Routes:
     - 8.8.8.8/32
     - 172.16.5.129/32

---

## Traffic Flow for Tenant 3624

### Outbound Traffic (Client → Internet):

```
1. pastrex01 (169.254.27.1)
   ↓ [BGP/L2 connection to Arista]
2. Arista Switch 1/2 (172.23.9.129 or 172.23.9.10)
   ↓ [GRE tunnel: 172.23.8.129 or 172.23.8.2 → 192.168.64.1 (ECGW VIP)]
3. Steering LB (10.111.96.135/136/137)
   ↓ [Source IP-based load balancing to VIP 192.168.64.1 → one of 3 ECGW nodes]
4. ECGW (ecgw01/02/03 - all have same VIP 192.168.64.1)
   ↓ [VPP routing using VIP 192.168.64.1 as source]
5. CFW (10.111.96.6) OR Proxy (10.111.59.221)
   ↓ [Sees traffic from 192.168.64.1, processed and forwarded]
6. Internet
```

### Return Traffic (Internet → Client):

```
1. Internet
   ↓
2. CFW/Proxy (10.111.96.6 or 10.111.59.221)
   ↓ [DSR - Direct Server Return, bypasses Steering LB]
3. ECGW (VIP 192.168.64.1 - stateful connection to same node that handled outbound)
   ↓ [GRE tunnel: 192.168.64.1 → 172.23.8.129 or 172.23.8.2]
4. Arista Switch 1/2 (172.23.9.129 or 172.23.9.10)
   ↓ [BGP routing back to customer]
5. pastrex01 (169.254.27.1)
```

---

## Key Observations

1. **VIP Architecture:** Single shared VIP (192.168.64.1) across all ECGW nodes
   - All 3 ECGW nodes (ecgw01, ecgw02, ecgw03) have the SAME VIP: 192.168.64.1 on lcploop0
   - Steering LB uses source IP-based load balancing to distribute traffic to one of the 3 nodes
   - ECGW nodes use this shared VIP (192.168.64.1) as source for Proxy/CFW connections
   - GRE tunnel source uses the shared VIP (192.168.64.1)
   - Provides high availability - if one node fails, LB redirects to remaining nodes
2. **Redundancy:** Two circuits (ms-circuit-01 and ms-circuit-02) provide redundancy with two Arista switches
3. **Load Balancing:** Steering LB distributes traffic across 3 ECGW nodes
4. **GRE Tunnels:** All ECGW nodes have GRE tunnels to both Arista switches for tenant 3624
5. **BGP Routing:** Arista switches maintain BGP sessions with ECGW for dynamic route advertisement
6. **VPP Processing:** ECGW uses VPP for high-performance packet processing
7. **DSR Return Path:** Return traffic bypasses Steering LB using Direct Server Return
8. **Health Checks:** Both CFW and Proxy have dedicated health check ports for monitoring
9. **VLAN Separation:**
   - VLAN 678: CFW traffic path
   - VLAN 677: Proxy traffic path
   - VLAN 200: Customer circuit VLAN

---

## Access Information

**Cluster:** iad0

**Accessible Nodes:**
- `tsh ssh --cluster iad0 pastrex01.iad0.netskope.com`
- `tsh ssh --cluster iad0 ecgw01.iad0.netskope.com`
- `tsh ssh --cluster iad0 ecgw02.iad0.netskope.com`
- `tsh ssh --cluster iad0 ecgw03.iad0.netskope.com`
- `tsh ssh --cluster iad0 pasgwstlb01.iad0.netskope.com`
- `tsh ssh --cluster iad0 pasgwstlb02.iad0.netskope.com`
- `tsh ssh --cluster iad0 pasgwstlb03.iad0.netskope.com`

**Not Accessible:**
- Arista Switches (172.23.9.129, 172.23.9.10)
- CFW Service (10.111.96.6)
- Proxy Service (10.111.59.221)

---

## Configuration Files

**ECGW (all nodes):**
- Tenant Config: `/opt/ns/gregw/cfg/tenantmap/tenant3624.json`
- VPP Config: `/opt/ns/pasgw/ns-vpp-pas.conf`
- CFW Config: `/opt/ns/common/remote/stsvc-cfwsvc`
- Proxy Config: `/opt/ns/common/remote/stsvc-nsproxy-dest`

**Verify VIP Configuration:**
```bash
# Check VIP on Linux CP interface
ip addr show lcploop0

# Check VIP on VPP interface
sudo vppctl show interface addr loop0
```

---

**Generated:** 2026-01-07
**Cluster:** iad0
**Tenant:** 3624 (Netskope)
