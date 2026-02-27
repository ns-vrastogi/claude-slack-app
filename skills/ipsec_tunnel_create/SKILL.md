# IPsec Tunnel Creation Skill

## Metadata
- **Name**: ipsec_tunnel_create
- **Description**: Automates creation of IPsec tunnels between Linux clients (Ubuntu/StrongSwan) and Netskope IPsec gateways (VPP-based or Legacy)
- **Version**: 1.0

## Trigger Keywords
This skill should be invoked when the user requests:
- "create ipsec tunnel"
- "bring up ipsec tunnel"
- "configure ipsec tunnel"
- "load ipsec config"
- "load config on ipsec"
- "load ipsec gateway with [N] tunnels/connections"

## Reference Files
- **Client List**: `client.txt` - Available Ubuntu clients with StrongSwan
- **Gateway List**: `dut.txt` - Available Netskope IPsec gateways (VPP and Legacy)
- **Config Generator**: `gateway_tunn_creation.py` - Reference script for netskope gateway config generation

## Prerequisites and Pre-Checks

### 1. Gateway Type Detection
- **VPP Gateway**: Hostname contains "vpp" (e.g., `vppipsecgw01.c18.iad0.netskope.com`)
- **Legacy Gateway**: Hostname without "vpp" (e.g., `ipsecgw01.c18.iad0.netskope.com`)

### 2. Version-Specific Gateway Selection
If user specifies a build/version:
1. Check all gateways in `dut.txt` to find which gateway is running that version
2. If no gateway found with that version:
   - For VPP gateways: Use `self-service-skill` to deploy/upgrade
   - For Legacy gateways: Use `legacy_deployment` skill to deploy/upgrade

### 3. Network Reachability Check
Before configuration:
- Verify Netskope IPsec gateway is reachable from the selected client
- Check routing and identify the correct interface to use as `leftid` in client config
- Any client from `client.txt` can be used if gateway is reachable

---

## Configuration Steps

### Part 1: Client-Side Configuration (Ubuntu/StrongSwan)

**Location**: `/etc/ipsec.conf` and `/etc/ipsec.secrets` on client

#### ipsec.conf Parameters
```
leftid: ai_claude_<random_number>
```
- Must be unique for each tunnel
- Format: `ai_claude_<random_number>` (e.g., `ai_claude_12345`)
- Must match Netskope gateway's `source_peer` value
- For multiple tunnels, increment the random number for each tunnel

```
rightid: <gateway_ingress_ip>
```
- IP address of Netskope gateway's ingress interface/VIP
- Find in: `netskope.plugin.strongswan.conf` on gateway

#### ipsec.secrets Parameters
```
<leftid> : PSK "<preshared_key>"
```
- **leftid**: Same as configured in ipsec.conf
- **preshared_key**: `ai_generated_key_<random_number>` (can be same for all tunnels)

### Part 2: Netskope Gateway Configuration

**Gateway Config Location**: `/opt/ns/tenant/<tenant-id>/ipsecgw/netskope.swanctl.json`
**Example**: `/opt/ns/tenant/3624/ipsecgw/netskope.swanctl.json`

#### Configuration Structure
```json
{
  "tenant_id": "<tenant_id>",
  "tunnel_details": {
    "<tunnel_number>": {
      "source_peer": "ai_claude_<random_number>",
      "source_ip": "",
      "psk": "ai_generated_key_<random_number>",
      "esp": "aes128-sha1-sha256-sha384-sha512-modp2048-modp3072-modp4096-modp8192-ecp256-ecp384-ecp521,aes128-sha1-sha256-sha384-sha512",
      "bandwidth": "50",
      "rekey": "no",
      "reauth": "no",
      "nat_enabled": false,
      "qos_enabled": false,
      "link_id": 0,
      "primary_pop_name": "qa01-dp-npe",
      "secondary_pop_name": "qa01"
    }
  },
  "pop_details": {
    "qa01-dp-npe": ["<tunnel_number>"],
    "qa01": ["<tunnel_number>"]
  }
}
```

#### Key Parameters
- **tunnel_number**: Unique tunnel ID (must be different for each tunnel)
- **source_peer**: Must match client's `leftid` (e.g., `ai_claude_12345`)
- **psk**: Must match client's preshared key (base64 encoded: `your-psk-value` = default)
- **pop_details**: All tunnel numbers must be listed under current POP (`qa01-dp-npe`) to be loaded

#### Config Service Auto-Generation
After modifying `netskope.swanctl.json`, the config service automatically generates:
- `netskope.dp.plugin.strongswan.conf`
- `netskope.dp.swanctl.secrets`
- `netskope.dp.swanctl.conf`
- `netskope.plugin.strongswan.conf`
- `netskope.swanctl.conf`
- `netskope.swanctl.secrets`

---

## Use Cases

### Use Case 1: Create Single/Multiple Tunnels
**User Request**: "Create [N] IPsec tunnels between client and gateway"

**Steps**:
1. Select client from `client.txt` and gateway from `dut.txt`
2. Verify network reachability
3. For each tunnel (1 to N):
   - Generate unique `leftid`: `ai_claude_<base_number + i>`
   - Configure client ipsec.conf with unique leftid and gateway rightid
   - Configure client ipsec.secrets with leftid and PSK
   - Add tunnel to gateway's `netskope.swanctl.json` with matching source_peer
   - Add tunnel number to pop_details list
4. Restart IPsec services on both sides

### Use Case 2: Load Gateway with N Connections
**User Request**: "Load ipsec gateway with 20,000 connections"

**Reference**: Use `gateway_tunn_creation.py` script

**Logic**:
- Total tenants: 100 (tenant IDs: 80000-80099)
- Connections per tenant: N / 100
- For 20,000 connections: 100 tenants × 200 tunnels each

**Steps**:
1. Modify script's range: `for i in range(1, 200)` → adjust 200 based on (N / 100)
2. Generate configs for tenant range: `for j in range(80000, 80100)`
3. Each tunnel gets:
   - Unique source_peer: `PrfTest_{tunnel_id:04d}{tenant_id}`
   - PSK: `your-psk-value`
4. Create directory structure: `/opt/ns/tenant/<tenant_id>/ipsecgw/`
5. Write `netskope.swanctl.json` for each tenant
6. Config service automatically loads all tunnels listed in pop_details

### Use Case 3: Version-Specific Tunnel Creation
**User Request**: "Create tunnel on gateway running version 134.0.0.3391"

**Steps**:
1. Query all gateways in `dut.txt` for running version
2. If found: Use that gateway
3. If not found:
   - Select suitable gateway
   - Determine type (VPP or Legacy)
   - Deploy version using appropriate skill:
     - VPP: `self-service-skill`
     - Legacy: `legacy_deployment`
4. Proceed with tunnel creation

---

## Important Notes

### Tenant and Tunnel Numbering
- Available tenants: 80000-80099 (100 total)
- Keep tenants same, adjust tunnels per tenant for scaling
- Tunnel numbers must be unique within a tenant
- All tunnel numbers must be listed in `pop_details["qa01-dp-npe"]` to be loaded

### Gateway Ingress Interface
- Find ingress interface IP in: `netskope.plugin.strongswan.conf` on gateway
- This IP becomes the `rightid` in client config

### PSK Encoding
- Default PSK: `your-psk-value` (base64 encoded)
- Can use custom PSK: `ai_generated_key_<random_number>`

### Multiple Tunnel Uniqueness
- Each tunnel requires unique `leftid` on client
- Each tunnel requires unique `source_peer` on gateway
- Each tunnel requires unique `tunnel_number` in netskope.swanctl.json
- leftid must match source_peer
- PSK can be same for all tunnels

---

## Execution Checklist

- [ ] Identify gateway type (VPP vs Legacy)
- [ ] Verify/deploy correct version if specified
- [ ] Check network reachability from client to gateway
- [ ] Find gateway ingress interface IP
- [ ] Generate unique identifiers for each tunnel
- [ ] Configure client ipsec.conf and ipsec.secrets
- [ ] Configure gateway netskope.swanctl.json
- [ ] Add tunnel numbers to pop_details list
- [ ] Restart ipsec service on client: `systemctl restart strongswan`
- [ ] Verify config service generated files on gateway
- [ ] Test tunnel connectivity

---

## Example: Single Tunnel Creation

**Client**: prfclient01.c18.iad0.netskope.com
**Gateway**: vppipsecgw01.c18.iad0.netskope.com
**Gateway Ingress IP**: 10.136.133.10
**Tenant**: 80000
**Tunnel Number**: 1

### Client Config
```conf
# /etc/ipsec.conf
conn tunnel1
    leftid=ai_claude_12345
    rightid=10.136.133.10
    ...
```

```secrets
# /etc/ipsec.secrets
ai_claude_12345 : PSK "ai_generated_key_001"
```

### Gateway Config
```json
{
  "tenant_id": "80000",
  "tunnel_details": {
    "1": {
      "source_peer": "ai_claude_12345",
      "psk": "ai_generated_key_001",
      ...
    }
  },
  "pop_details": {
    "qa01-dp-npe": ["1"]
  }
}
```
