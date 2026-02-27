# Sumo Logic Skill

## Name
`sumo_logic`

## Description
This skill fetches logs from Sumo Logic server, performs root cause analysis, and generates diagrams based on the analysis. It specializes in analyzing IPSEC/GRE gateway logs to troubleshoot tunnel issues, flaps, and customer-specific events.

## Prerequisites
- Access to Sumo Logic MCP server
- MCP server `sumologic` must be configured

## MCP Server Integration
**REQUIRED**: This skill uses the `sumologic` MCP server. All queries must be executed through the MCP server.

Use `ToolSearch` to find and load: `mcp__sumologic__search_sumologic`

## Log Files and Their Purpose

### 1. StrongSwan Log (`/opt/ns/log/strongswan.log`)
**Purpose**: Contains all IPSEC-related events
**Use Cases**:
- Tunnel up/down events
- Tunnel flaps
- Connection establishment/deletion
- IPSEC SA events

**Source Categories**:
- `_sourcecategory=*ipsecgw*`
- `_index=nsipsecgregw`

### 2. GRE Gateway Log (`/opt/ns/log/nsgregw.log`) - Legacy GRE Gateway
**Purpose**: Contains GRE tunnel-related events and resource status (equivalent to strongswan.log for IPSEC)
**Use Cases**:
- GRE tunnel up/down events
- GRE tunnel status changes
- Resource status changes
- Gateway health events
- Connection establishment/deletion

**Source Categories**:
- `_sourcecategory=*gregw*` or `_sourcecategory=*gre*`
- `_index=nsipsecgregw`

**Query Example**:
```
((_sourcecategory=*gregw*) AND (_sourceName=/opt/ns/log/nsgregw.log) AND (_sourceHost=nsgregw01.nrt3.nskope.net) AND "tenant-18548")
```

### 3. TunSvc Log (`/opt/ns/log/tunsvc.log`) - Legacy IPSEC & GRE Gateways
**Purpose**: Tunnel Service log - manages tunnel lifecycle and operations
**Use Cases**:
- Tunnel creation and deletion
- Tunnel state transitions
- Service-level tunnel operations
- Tunnel configuration changes
- Connection management events

**Query Example**:
```
# For IPSEC gateways
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/tunsvc.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND "tenant-18548")

# For GRE gateways
((_sourcecategory=*gregw*) AND (_sourceName=/opt/ns/log/tunsvc.log) AND (_sourceHost=nsgregw01.nrt3.nskope.net) AND "tenant-18548")
```

### 4. Monitor Log (`/opt/ns/log/ipsecmonitor.log`) - Legacy IPSEC & GRE Gateways
**Purpose**: Monitors tunnel health and connectivity (works for both IPSEC and GRE tunnels)
**Use Cases**:
- Health check failures
- Tunnel monitoring events
- Keepalive failures
- Gateway connectivity issues
- Tunnel health status changes

**Query Example**:
```
# For IPSEC gateways
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/ipsecmonitor.log) AND (_sourceHost=ipsecgw*.nyc4.nskope.net) AND ("health check" OR "keepalive"))

# For GRE gateways
((_sourcecategory=*gregw*) AND (_sourceName=/opt/ns/log/ipsecmonitor.log) AND (_sourceHost=nsgregw*.nrt3.nskope.net) AND ("health check" OR "keepalive"))
```

### 5. Config Watcher Log (`/opt/ns/log/cfgwatcher.log`) - Legacy IPSEC & GRE Gateways
**Purpose**: Watches for configuration file changes and triggers reloads
**Use Cases**:
- Configuration file modifications detected
- Config reload events
- File system watch errors
- Configuration synchronization issues
- Tenant config updates

**Query Example**:
```
# For IPSEC gateways
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/cfgwatcher.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND ("config" OR "reload"))

# For GRE gateways
((_sourcecategory=*gregw*) AND (_sourceName=/opt/ns/log/cfgwatcher.log) AND (_sourceHost=nsgregw01.nrt3.nskope.net) AND ("config" OR "reload"))
```

### 6. Config Agent v2 Log (`/opt/ns/log/cfgagentv2.log`) - Legacy IPSEC & GRE Gateways
**Purpose**: Configuration agent that manages gateway and tenant configurations
**Use Cases**:
- Tenant configuration push/pull
- Configuration validation errors
- API communication with control plane
- Configuration deployment status
- Tenant provisioning/deprovisioning events

**Query Example**:
```
# For IPSEC gateways
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/cfgagentv2.log) AND (_sourceHost=ipsecgw*.nyc4.nskope.net) AND ("tenant-18548" OR "config push"))

# For GRE gateways
((_sourcecategory=*gregw*) AND (_sourceName=/opt/ns/log/cfgagentv2.log) AND (_sourceHost=nsgregw*.nrt3.nskope.net) AND ("tenant-18548" OR "config push"))
```

### 7. NS Health Log (`/opt/ns/log/nshealth.log`) - VPP IPSEC & GRE Gateways
**Purpose**: Health check and monitoring service for VPP-based gateways
**Use Cases**:
- VPP process health monitoring
- Service health status
- Health check failures and recovery
- Component health status
- Gateway readiness checks

**Query Example**:
```
# For VPP IPSEC gateways
((_sourcecategory=*vppipsecgw*) AND (_sourceName=/opt/ns/log/nshealth.log) AND (_sourceHost=vppipsecgw*.iad0.netskope.com) AND ("health" OR "status"))

# For VPP GRE gateways
((_sourcecategory=*vppgregw*) AND (_sourceName=/opt/ns/log/nshealth.log) AND (_sourceHost=vppgregw*.iad0.netskope.com) AND ("health" OR "status"))
```

### 8. NS VPP ST Svc Log (`/opt/ns/log/nsvppstsvc.log`) - VPP IPSEC & GRE Gateways
**Purpose**: VPP Statistics Service - collects and reports VPP statistics
**Use Cases**:
- VPP performance metrics
- Traffic statistics
- Interface statistics
- Packet processing stats
- Resource utilization metrics

**Query Example**:
```
# For VPP IPSEC gateways
((_sourcecategory=*vppipsecgw*) AND (_sourceName=/opt/ns/log/nsvppstsvc.log) AND (_sourceHost=vppipsecgw*.iad0.netskope.com) AND ("stats" OR "metrics"))

# For VPP GRE gateways
((_sourcecategory=*vppgregw*) AND (_sourceName=/opt/ns/log/nsvppstsvc.log) AND (_sourceHost=vppgregw*.iad0.netskope.com) AND ("stats" OR "metrics"))
```

### 9. VPP Log (`/opt/ns/log/vpp.log`) - VPP IPSEC & GRE Gateways
**Purpose**: Core VPP (Vector Packet Processing) logs - low-level packet processing events
**Use Cases**:
- VPP core events
- Packet processing errors
- Interface events
- Plugin operations
- VPP crashes or restarts
- Tunnel setup at VPP level
- Crypto operations

**Query Example**:
```
# For VPP IPSEC gateways
((_sourcecategory=*vppipsecgw*) AND (_sourceName=/opt/ns/log/vpp.log) AND (_sourceHost=vppipsecgw*.iad0.netskope.com) AND ("error" OR "tunnel"))

# For VPP GRE gateways
((_sourcecategory=*vppgregw*) AND (_sourceName=/opt/ns/log/vpp.log) AND (_sourceHost=vppgregw*.iad0.netskope.com) AND ("error" OR "tunnel"))
```

### 10. NS Metric Log (`/opt/ns/log/nsmetric.log`) - VPP IPSEC & GRE Gateways
**Purpose**: Metrics collection and reporting service for VPP gateways
**Use Cases**:
- Gateway metrics export
- Performance monitoring data
- Telemetry collection
- Metric push/pull operations
- Monitoring system integration

**Query Example**:
```
# For VPP IPSEC gateways
((_sourcecategory=*vppipsecgw*) AND (_sourceName=/opt/ns/log/nsmetric.log) AND (_sourceHost=vppipsecgw*.iad0.netskope.com) AND ("metric" OR "export"))

# For VPP GRE gateways
((_sourcecategory=*vppgregw*) AND (_sourceName=/opt/ns/log/nsmetric.log) AND (_sourceHost=vppgregw*.iad0.netskope.com) AND ("metric" OR "export"))
```

## Gateway Type Identification

### Legacy IPSEC Gateways
- **Hostname Pattern**: `ipsecgw[0-9]+.<pop>.nskope.net` (e.g., `ipsecgw01.nyc4.nskope.net`)
- **Available Logs**:
  - `/opt/ns/log/strongswan.log` - IPSEC protocol events (IPSEC-specific)
  - `/opt/ns/log/tunsvc.log` - Tunnel service operations
  - `/opt/ns/log/ipsecmonitor.log` - Health monitoring
  - `/opt/ns/log/cfgwatcher.log` - Config file watching
  - `/opt/ns/log/cfgagentv2.log` - Configuration management

### Legacy GRE Gateways
- **Hostname Pattern**: `nsgregw[0-9]+.<pop>.nskope.net` (e.g., `nsgregw01.nrt3.nskope.net`)
- **Available Logs**:
  - `/opt/ns/log/nsgregw.log` - GRE tunnel events (GRE-specific, equivalent to strongswan.log)
  - `/opt/ns/log/tunsvc.log` - Tunnel service operations (same as IPSEC)
  - `/opt/ns/log/ipsecmonitor.log` - Health monitoring (same as IPSEC)
  - `/opt/ns/log/cfgwatcher.log` - Config file watching (same as IPSEC)
  - `/opt/ns/log/cfgagentv2.log` - Configuration management (same as IPSEC)

**Key Difference**: Legacy GRE gateways use `nsgregw.log` instead of `strongswan.log` for tunnel protocol events. All other log files are identical between IPSEC and GRE gateways.

### VPP IPSEC Gateways
- **Hostname Pattern**: `vppipsecgw[0-9]+.*` (e.g., `vppipsecgw04.c18.iad0.netskope.com`, `vppipsecgw01.iad0.netskope.com`)
- **Source Category**: `_sourcecategory=*vppipsecgw*`
- **Available Logs**:
  - `/opt/ns/log/nshealth.log` - Health monitoring service
  - `/opt/ns/log/nsvppstsvc.log` - VPP statistics service
  - `/opt/ns/log/vpp.log` - Core VPP packet processing logs
  - `/opt/ns/log/nsmetric.log` - Metrics collection service
  - **Note**: VPP gateways do NOT have strongswan.log, tunsvc.log, ipsecmonitor.log, cfgwatcher.log, or cfgagentv2.log

### VPP GRE Gateways
- **Hostname Pattern**: `vppgregw[0-9]+.*` (e.g., `vppgregw01.c18.iad0.netskope.com`, `vppgregw01.iad0.netskope.com`)
- **Source Category**: `_sourcecategory=*vppgregw*` or `_sourcecategory=*vppgre*`
- **Available Logs**:
  - `/opt/ns/log/nshealth.log` - Health monitoring service
  - `/opt/ns/log/nsvppstsvc.log` - VPP statistics service
  - `/opt/ns/log/vpp.log` - Core VPP packet processing logs
  - `/opt/ns/log/nsmetric.log` - Metrics collection service
  - **Note**: VPP gateways do NOT have nsgregw.log, tunsvc.log, ipsecmonitor.log, cfgwatcher.log, or cfgagentv2.log

**Key Differences Summary**:
1. **Legacy IPSEC vs Legacy GRE**: Only tunnel protocol log differs (strongswan.log vs nsgregw.log). All other logs (tunsvc, ipsecmonitor, cfgwatcher, cfgagentv2) are identical.
2. **Legacy vs VPP**: Completely different log structure:
   - Legacy: strongswan/nsgregw.log, tunsvc.log, ipsecmonitor.log, cfgwatcher.log, cfgagentv2.log
   - VPP: nshealth.log, nsvppstsvc.log, vpp.log, nsmetric.log
3. **VPP IPSEC vs VPP GRE**: Same log files for both VPP gateway types.

## POP-wide Search Strategy

**IMPORTANT**: All POPs contain 4 gateway type combinations:
1. Legacy IPSEC gateways (`ipsecgw[0-9]+.<pop>.nskope.net`)
2. Legacy GRE gateways (`nsgregw[0-9]+.<pop>.nskope.net`)
3. VPP IPSEC gateways (`vppipsecgw[0-9]+.*.<pop>.*`)
4. VPP GRE gateways (`vppgregw[0-9]+.*.<pop>.*`)

**Search Rule**: Unless a specific hostname is mentioned, queries should search **ALL gateway types** (both Legacy and VPP) for the requested protocol (IPSEC or GRE) in that POP.

### Example Search Patterns by Request Type

**User Request**: "Count IPSEC flaps on nyc4 in last hour" (no specific hostname mentioned)
- **Action**: Search **BOTH** Legacy IPSEC AND VPP IPSEC gateways in nyc4
- **Query**:
```
# Search across both Legacy and VPP IPSEC gateways
((_sourcecategory=*ipsecgw* OR _sourcecategory=*vppipsecgw*) AND (_sourceHost=*nyc4*) AND ...)
```

**User Request**: "Check GRE gateway issues on mil1" (no specific hostname mentioned)
- **Action**: Search **BOTH** Legacy GRE AND VPP GRE gateways in mil1
- **Query**:
```
# Search across both Legacy and VPP GRE gateways
((_sourcecategory=*gregw* OR _sourcecategory=*vppgregw*) AND (_sourceHost=*mil1*) AND ...)
```

**User Request**: "Analyze logs on ipsecgw01.nyc4.nskope.net" (specific hostname mentioned)
- **Action**: Search **ONLY** that specific Legacy IPSEC gateway
- **Query**: Use specific hostname in query

## Quick Reference: Log Files Summary

### Legacy Gateway Log Files

| Log File | Gateway Type | Primary Purpose | Common Use Cases |
|----------|--------------|-----------------|------------------|
| `strongswan.log` | Legacy IPSEC | IPSEC protocol events | Tunnel up/down, SA events, authentication issues |
| `nsgregw.log` | Legacy GRE | GRE tunnel events | GRE tunnel up/down, resource status, connection events |
| `tunsvc.log` | Legacy IPSEC & GRE | Tunnel service operations | Tunnel lifecycle, creation/deletion tracking |
| `ipsecmonitor.log` | Legacy IPSEC & GRE | Health monitoring | Health check failures, keepalive issues, connectivity problems |
| `cfgwatcher.log` | Legacy IPSEC & GRE | Config file watching | Config reload events, file change detection |
| `cfgagentv2.log` | Legacy IPSEC & GRE | Config management | Tenant provisioning, config push/pull, API errors |

### VPP Gateway Log Files

| Log File | Gateway Type | Primary Purpose | Common Use Cases |
|----------|--------------|-----------------|------------------|
| `nshealth.log` | VPP IPSEC & GRE | Health monitoring service | Service health, component status, readiness checks |
| `nsvppstsvc.log` | VPP IPSEC & GRE | VPP statistics service | Performance metrics, traffic stats, interface stats |
| `vpp.log` | VPP IPSEC & GRE | Core VPP processing | Packet processing, tunnel events, crypto ops, VPP errors |
| `nsmetric.log` | VPP IPSEC & GRE | Metrics collection | Telemetry, monitoring data export |

**Troubleshooting Decision Tree**:

### For Legacy Gateways:
1. **Tunnel flapping?**
   - Legacy IPSEC → Start with `strongswan.log`
   - Legacy GRE → Start with `nsgregw.log`
2. **Tunnel not created?** → Check `tunsvc.log` then `cfgagentv2.log`
3. **Health check issues?** → Check `ipsecmonitor.log`
4. **Config not applied?** → Check `cfgagentv2.log` → `cfgwatcher.log` → `tunsvc.log`
5. **Gateway-wide issue?** → Query all logs for error patterns

### For VPP Gateways:
1. **Tunnel flapping?** → Check `vpp.log` for tunnel events and errors
2. **VPP process issues?** → Check `nshealth.log` for service health
3. **Performance problems?** → Check `nsvppstsvc.log` for statistics and `nsmetric.log` for metrics
4. **Packet processing errors?** → Check `vpp.log` for VPP core errors
5. **Gateway-wide issue?** → Query all VPP logs for error patterns

### General Troubleshooting:
- **Unknown gateway type?** → Search across ALL gateway types (Legacy + VPP) in the POP
- **POP-wide analysis?** → Query both Legacy and VPP gateways unless specific type is mentioned

## Query Patterns

### Pattern 1: IPSEC Gateway Logs (Specific Host)
```
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/strongswan.log) AND (_sourceHost=<hostname>) AND "<keywords>")
```

**Example**:
```
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/strongswan.log) AND (_sourceHost=ipsecgw07.nyc4.nskope.net) AND "down" or "delete")
```

### Pattern 2: Legacy IPSEC Gateway Logs (All Hosts in POP)
```
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/strongswan.log) AND (_sourceHost=*.<pop>.nskope.net) AND "<keywords>")
```

**Example** (all Legacy IPSEC gateways in nyc4):
```
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/strongswan.log) AND (_sourceHost=*.nyc4.nskope.net) AND "down")
```

### Pattern 2a: ALL IPSEC Gateways in POP (Legacy + VPP) - RECOMMENDED
**Use this when no specific hostname is mentioned and request is for IPSEC gateways in a POP**

```
((_sourcecategory=*ipsecgw* OR _sourcecategory=*vppipsecgw*) AND (_sourceHost=*<pop>*) AND "<keywords>")
```

**Example** (all IPSEC gateways - both Legacy and VPP - in nyc4):
```
# Search Legacy strongswan.log AND VPP vpp.log for tunnel down events
((_sourcecategory=*ipsecgw* OR _sourcecategory=*vppipsecgw*) AND (_sourceHost=*nyc4*) AND ("Tunnel is Down" OR "tunnel down" OR "down"))
```

**Note**: This pattern searches across different log files automatically based on gateway type:
- Legacy IPSEC: searches strongswan.log, tunsvc.log, etc.
- VPP IPSEC: searches vpp.log, nshealth.log, etc.

### Pattern 3: Legacy GRE Gateway - Tunnel Protocol Logs
Query GRE tunnel-specific events (equivalent to strongswan.log for IPSEC):

```
((_sourcecategory=*gregw* OR _sourcecategory=*gre*) AND (_sourceName=/opt/ns/log/nsgregw.log) AND (_sourceHost=<hostname>) AND "<keywords>")
```

**Alternative using index**:
```
((_index=nsipsecgregw) AND (_sourcename=/opt/ns/log/nsgregw.log) AND (_sourcehost=<hostname>) AND "<keywords>")
```

**Example** (GRE tunnel down events):
```
((_sourcecategory=*gregw*) AND (_sourceName=/opt/ns/log/nsgregw.log) AND (_sourceHost=nsgregw0*.nrt3.nskope.net) AND ("resource_status" AND "11264") or ("DOWN" AND "11264"))
```

**Note**: For other log files on Legacy GRE gateways (tunsvc.log, ipsecmonitor.log, cfgwatcher.log, cfgagentv2.log), use the same patterns as IPSEC gateways but with GRE hostname pattern and source category.

### Pattern 3a: ALL GRE Gateways in POP (Legacy + VPP) - RECOMMENDED
**Use this when no specific hostname is mentioned and request is for GRE gateways in a POP**

```
((_sourcecategory=*gregw* OR _sourcecategory=*vppgregw*) AND (_sourceHost=*<pop>*) AND "<keywords>")
```

**Example** (all GRE gateways - both Legacy and VPP - in nrt3):
```
# Search Legacy nsgregw.log AND VPP vpp.log for tunnel events
((_sourcecategory=*gregw* OR _sourcecategory=*vppgregw*) AND (_sourceHost=*nrt3*) AND ("DOWN" OR "resource_status" OR "tunnel"))
```

**Note**: This pattern searches across different log files automatically based on gateway type:
- Legacy GRE: searches nsgregw.log, tunsvc.log, etc.
- VPP GRE: searches vpp.log, nshealth.log, etc.

### Pattern 4: VPP Gateway - VPP Core Log
Query VPP packet processing and tunnel events (works for both VPP IPSEC and VPP GRE):

```
# For VPP IPSEC gateways
((_sourcecategory=*vppipsecgw*) AND (_sourceName=/opt/ns/log/vpp.log) AND (_sourceHost=<hostname>) AND "<keywords>")

# For VPP GRE gateways
((_sourcecategory=*vppgregw*) AND (_sourceName=/opt/ns/log/vpp.log) AND (_sourceHost=<hostname>) AND "<keywords>")
```

**Example** (VPP tunnel errors):
```
# VPP IPSEC - tunnel errors
((_sourcecategory=*vppipsecgw*) AND (_sourceName=/opt/ns/log/vpp.log) AND (_sourceHost=vppipsecgw*.iad0*) AND ("tunnel" OR "error" OR "drop"))

# VPP GRE - tunnel errors
((_sourcecategory=*vppgregw*) AND (_sourceName=/opt/ns/log/vpp.log) AND (_sourceHost=vppgregw*.iad0*) AND ("tunnel" OR "error" OR "drop"))
```

### Pattern 5: VPP Gateway - Health and Metrics
Query VPP health monitoring and metrics:

```
# Health monitoring
((_sourcecategory=*vpp*) AND (_sourceName=/opt/ns/log/nshealth.log) AND (_sourceHost=<hostname>) AND "<keywords>")

# Statistics service
((_sourcecategory=*vpp*) AND (_sourceName=/opt/ns/log/nsvppstsvc.log) AND (_sourceHost=<hostname>) AND "<keywords>")

# Metrics collection
((_sourcecategory=*vpp*) AND (_sourceName=/opt/ns/log/nsmetric.log) AND (_sourceHost=<hostname>) AND "<keywords>")
```

**Example** (VPP health check failures):
```
((_sourcecategory=*vppipsecgw*) AND (_sourceName=/opt/ns/log/nshealth.log) AND (_sourceHost=*nyc4*) AND ("failed" OR "unhealthy" OR "error"))
```

### Pattern 6: Tenant-Specific Queries
**IMPORTANT**: For tenant-specific queries, always provide comprehensive analysis including:
- Total flap count
- Breakdown by gateway (which nodes had flaps)
- Breakdown by POP
- Breakdown by flap reason (DPD, HC, duplicate tunnel, etc.)

**Query Strategy**:
1. Query ALL gateway types (Legacy + VPP) unless specific hostname is mentioned
2. Get all tunnel events (down/up/delete)
3. Correlate with other log files (ipsecmonitor.log, cfgagentv2.log) for context
4. Categorize by reason
5. Present structured summary

**Query Template** (searches all gateway types in all POPs):
```
((_sourcecategory=*ipsecgw* OR _sourcecategory=*vppipsecgw* OR _sourcecategory=*gregw* OR _sourcecategory=*vppgregw*) AND "tenant-<tenant_id>")
```

**Example 1** (tenant 11264 - all gateways, all POPs):
```
((_sourcecategory=*ipsecgw* OR _sourcecategory=*vppipsecgw*) AND "tenant-11264" AND ("Tunnel is Down" OR "Tunnel is Up" OR "delete" OR "established"))
```

**Example 2** (tenant 11264 - specific POP):
```
((_sourcecategory=*ipsecgw* OR _sourcecategory=*vppipsecgw*) AND (_sourceHost=*nyc4*) AND "tenant-11264" AND ("Tunnel is Down" OR "Tunnel is Up"))
```

**Example 3** (tenant 11264 - specific gateway):
```
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/strongswan.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND "tenant-11264")
```

**Multi-Log Query for Context** (get reason details):
```
# Main tunnel events
((_sourcecategory=*ipsecgw* OR _sourcecategory=*vppipsecgw*) AND "tenant-11264")

# Health check context (Legacy gateways only)
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/ipsecmonitor.log) AND "tenant-11264")

# Config change context (Legacy gateways only)
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/cfgagentv2.log) AND "tenant-11264")

# VPP health context (VPP gateways only)
((_sourcecategory=*vppipsecgw* OR _sourcecategory=*vppgregw*) AND (_sourceName=/opt/ns/log/nshealth.log) AND "tenant-11264")
```

### Pattern 7: Legacy Gateway - TunSvc Log (IPSEC & GRE)
Query tunnel service operations and lifecycle events (works for both IPSEC and GRE gateways):

```
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/tunsvc.log) AND (_sourceHost=<hostname>) AND "<keywords>")
```

**Example** (tenant tunnel creation/deletion):
```
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/tunsvc.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND "tenant-18548" AND ("create" OR "delete"))
```

### Pattern 8: Legacy Gateway - Monitor Log (IPSEC & GRE)
Query health check and monitoring events (works for both IPSEC and GRE gateways):

```
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/ipsecmonitor.log) AND (_sourceHost=<hostname>) AND "<keywords>")
```

**Example** (health check failures):
```
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/ipsecmonitor.log) AND (_sourceHost=*.nyc4.nskope.net) AND ("health check failed" OR "keepalive failure"))
```

### Pattern 9: Legacy Gateway - Config Watcher Log (IPSEC & GRE)
Query configuration change detection events (works for both IPSEC and GRE gateways):

```
# For IPSEC gateways
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/cfgwatcher.log) AND (_sourceHost=<hostname>) AND "<keywords>")

# For GRE gateways
((_sourcecategory=*gregw*) AND (_sourceName=/opt/ns/log/cfgwatcher.log) AND (_sourceHost=<hostname>) AND "<keywords>")
```

**Example** (config reload events):
```
# IPSEC
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/cfgwatcher.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND ("config reload" OR "file modified"))

# GRE
((_sourcecategory=*gregw*) AND (_sourceName=/opt/ns/log/cfgwatcher.log) AND (_sourceHost=nsgregw01.nrt3.nskope.net) AND ("config reload" OR "file modified"))
```

### Pattern 10: Legacy Gateway - Config Agent v2 Log (IPSEC & GRE)
Query configuration management and tenant provisioning events (works for both IPSEC and GRE gateways):

```
# For IPSEC gateways
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/cfgagentv2.log) AND (_sourceHost=<hostname>) AND "<keywords>")

# For GRE gateways
((_sourcecategory=*gregw*) AND (_sourceName=/opt/ns/log/cfgagentv2.log) AND (_sourceHost=<hostname>) AND "<keywords>")
```

**Example** (tenant config push):
```
# IPSEC
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/cfgagentv2.log) AND (_sourceHost=*.nyc4.nskope.net) AND "tenant-18548" AND ("config push" OR "provision"))

# GRE
((_sourcecategory=*gregw*) AND (_sourceName=/opt/ns/log/cfgagentv2.log) AND (_sourceHost=*.nrt3.nskope.net) AND "tenant-18548" AND ("config push" OR "provision"))
```

### Pattern 11: Multi-Log Correlation (Legacy IPSEC & GRE Gateways)
Query across multiple log files for comprehensive analysis (works for both IPSEC and GRE gateways):

```
# For IPSEC gateways
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/strongswan.log OR _sourceName=/opt/ns/log/tunsvc.log OR _sourceName=/opt/ns/log/ipsecmonitor.log OR _sourceName=/opt/ns/log/cfgagentv2.log) AND (_sourceHost=<hostname>) AND "tenant-<tenant_id>")

# For GRE gateways
((_sourcecategory=*gregw*) AND (_sourceName=/opt/ns/log/nsgregw.log OR _sourceName=/opt/ns/log/tunsvc.log OR _sourceName=/opt/ns/log/ipsecmonitor.log OR _sourceName=/opt/ns/log/cfgagentv2.log) AND (_sourceHost=<hostname>) AND "tenant-<tenant_id>")
```

**Example** (all tenant events across logs):
```
# IPSEC - comprehensive tenant analysis
((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/strongswan.log OR _sourceName=/opt/ns/log/tunsvc.log OR _sourceName=/opt/ns/log/cfgagentv2.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND "tenant-18548")

# GRE - comprehensive tenant analysis
((_sourcecategory=*gregw*) AND (_sourceName=/opt/ns/log/nsgregw.log OR _sourceName=/opt/ns/log/tunsvc.log OR _sourceName=/opt/ns/log/cfgagentv2.log) AND (_sourceHost=nsgregw01.nrt3.nskope.net) AND "tenant-18548")
```

## Log Format Understanding

### StrongSwan Log Line Format
```
2026-02-14 16:16:36 55[TNC] <tenant-18548-37746|39567> 893027:../libs/strongswan-nstunsvc/src/NsTunSvcListener.c:03696 Tunnel is Down for connection: tenant-18548-37746 peer-id: 372.NE_6_6a80b9a8 peer-ip: 74.67.17.200 interface: xfrm4680, tunc4680, vrfx4680, vrft4680
```

**Key Fields**:
- **Timestamp**: `2026-02-14 16:16:36`
- **Tenant ID**: `tenant-18548-37746`
- **Event**: `Tunnel is Down`
- **Connection Name**: `tenant-18548-37746`
- **Peer ID**: `372.NE_6_6a80b9a8`
- **Peer IP**: `74.67.17.200`
- **Interfaces**: `xfrm4680, tunc4680, vrfx4680, vrft4680`

## Flap Reason Categorization

**CRITICAL**: When analyzing tenant flaps, always categorize by reason using log message patterns.

### Identifying Flap Reasons from Log Messages

| Flap Reason | Log Message Patterns | Keywords to Search |
|-------------|---------------------|-------------------|
| **DPD Timeout** | "DPD timeout", "Dead Peer Detection", "DPD sequence", "peer timeout" | `"DPD"`, `"Dead Peer"`, `"timeout"` |
| **HC Down (Health Check)** | "health check failed", "HC failed", "keepalive failed", "no response from peer" | `"health check"`, `"HC"`, `"keepalive"` |
| **New Tunnel from Same Peer** | "already exists", "duplicate connection", "replacing connection", "tunnel exists for peer" | `"already exists"`, `"duplicate"`, `"replacing"` |
| **Peer Unreachable** | "peer unreachable", "no route to host", "connection refused", "network unreachable" | `"unreachable"`, `"no route"`, `"refused"` |
| **Authentication Failure** | "authentication failed", "auth failed", "PSK mismatch", "invalid credentials", "IKE_AUTH failed" | `"auth"`, `"authentication"`, `"PSK"`, `"credentials"` |
| **SA Establishment Failure** | "CHILD_SA failed", "IKE_SA failed", "SA establishment failed", "no proposal chosen" | `"CHILD_SA"`, `"IKE_SA"`, `"proposal"` |
| **Configuration Reload** | "config reload", "configuration changed", "reloading connection", "config update" | `"reload"`, `"configuration"`, `"config"` |
| **Gateway Restart** | "gateway restart", "service restart", "strongswan restart", "daemon restarted" | `"restart"`, `"restarted"`, `"daemon"` |
| **Peer Initiated Disconnect** | "delete message received", "peer requested delete", "peer closed connection" | `"delete message"`, `"peer requested"`, `"peer closed"` |
| **Interface Down** | "interface down", "link down", "no carrier", "interface error" | `"interface down"`, `"link down"`, `"carrier"` |

### Query Strategy for Flap Categorization

To properly categorize flaps, query all log messages for the tenant and look for these patterns:

**Query 1: Get all tunnel events**
```javascript
query: "((_sourcecategory=*ipsecgw* OR _sourcecategory=*vppipsecgw*) AND \"tenant-<ID>\" AND (\"Tunnel is Down\" OR \"Tunnel is Up\" OR \"delete\" OR \"established\"))"
```

**Query 2: Get context around down events (with context lines)**
```javascript
query: "((_sourcecategory=*ipsecgw* OR _sourcecategory=*vppipsecgw*) AND \"tenant-<ID>\" AND \"Tunnel is Down\")"
// Check lines before and after the "Tunnel is Down" event for reason
```

**Query 3: Check related logs for more context**
```javascript
// Check ipsecmonitor.log for HC failures
query: "((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/ipsecmonitor.log) AND \"tenant-<ID>\" AND (\"health check\" OR \"keepalive\"))"

// Check cfgagentv2.log for config changes
query: "((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/cfgagentv2.log) AND \"tenant-<ID>\" AND (\"config\" OR \"reload\"))"
```

### Example Log Analysis for Categorization

**Example 1: DPD Timeout**
```
2026-02-14 16:16:35 55[TNC] <tenant-11264-12345|67890> DPD timeout detected for peer 74.67.17.200
2026-02-14 16:16:36 55[TNC] <tenant-11264-12345|67890> Tunnel is Down for connection: tenant-11264-12345
```
**Reason**: DPD Timeout

**Example 2: Health Check Failure**
```
2026-02-14 16:16:35 ipsecmonitor: health check failed for tenant-11264, no response from peer
2026-02-14 16:16:36 55[TNC] <tenant-11264-12345|67890> Tunnel is Down for connection: tenant-11264-12345
```
**Reason**: HC Down

**Example 3: Duplicate Tunnel**
```
2026-02-14 16:16:35 55[TNC] <tenant-11264-12345|67890> connection already exists for peer 74.67.17.200, replacing
2026-02-14 16:16:36 55[TNC] <tenant-11264-12345|67890> Tunnel is Down for connection: tenant-11264-12345
2026-02-14 16:16:37 55[TNC] <tenant-11264-12345|67891> Tunnel is Up for connection: tenant-11264-12345
```
**Reason**: New tunnel from same peer

### Automated Categorization Logic

When processing log events:
1. Extract timestamp, gateway hostname, POP, event type
2. Look for reason keywords in the log message
3. If "Tunnel is Down" event:
   - Check surrounding log lines (within 5 seconds before)
   - Search for reason patterns in order of priority
   - Assign to first matching category
4. If no clear reason found, mark as "Unknown/Other"
5. Count occurrences per category
6. Calculate percentages

## Common Use Cases

### Use Case 1: Tunnel Flap Analysis
**User Request**: "How many times did tenant 11264's tunnel flap in the last hour?"

**IMPORTANT - Required Output Format**:
When analyzing tenant-specific flaps, **ALWAYS** provide:

1. **Total Flap Count**: Overall number of flaps
2. **Flaps by Gateway**: Show which nodes/gateways had flaps
3. **Flaps by POP**: Breakdown per data center
4. **Flaps by Reason**: Categorize flaps by root cause with counts:
   - DPD timeout (Dead Peer Detection)
   - HC down (Health Check failure)
   - New tunnel from same peer (duplicate connection)
   - Peer unreachable
   - Authentication failure
   - SA establishment failure
   - Configuration reload
   - Gateway restart
   - Unknown/Other

**Example Output Format**:
```
Total Flaps: 20

Breakdown by Gateway:
- ipsecgw01.nyc4.nskope.net: 12 flaps
- ipsecgw03.mil1.nskope.net: 8 flaps

Breakdown by POP:
- nyc4: 12 flaps
- mil1: 8 flaps

Breakdown by Reason:
- DPD timeout: 10 flaps (50%)
- HC down (Health Check failure): 5 flaps (25%)
- New tunnel from same peer: 3 flaps (15%)
- Peer unreachable: 2 flaps (10%)
```

**Steps**:
1. Query for all events (up/down/delete) for the tenant across all gateways
2. Parse log messages to identify flap reasons
3. Group flaps by gateway/hostname
4. Group flaps by POP
5. Categorize flaps by reason (DPD, HC, duplicate tunnel, etc.)
6. Calculate counts and percentages
7. Provide structured summary as shown above

### Use Case 2: Gateway Health Check
**User Request**: "Check ipsecgw07.nyc4 for any errors in the last 24 hours"

**Steps**:
1. Query strongswan.log for error keywords
2. Look for "down", "delete", "failed", "error" keywords
3. Summarize findings

### Use Case 3: POP-wide Analysis
**User Request**: "Are there any issues in nyc4 POP?"

**Steps**:
1. Query all gateways in nyc4 POP using wildcard (*.nyc4.nskope.net)
2. Search for error patterns
3. Identify affected tenants and gateways

### Use Case 4: Root Cause Analysis
**User Request**: "Why is tenant 18548's tunnel unstable?"

**Steps**:
1. Fetch all events for tenant-18548
2. Analyze timeline of up/down events
3. Look for patterns (peer IP changes, interface issues, etc.)
4. Generate timeline diagram
5. Provide root cause summary

### Use Case 5: Configuration Issue Troubleshooting (Legacy IPSEC)
**User Request**: "Tenant 18548 tunnel not coming up after configuration push"

**Steps**:
1. Query `cfgagentv2.log` for config push events for tenant-18548
2. Query `cfgwatcher.log` for config reload events
3. Query `tunsvc.log` for tunnel creation attempts
4. Query `strongswan.log` for tunnel establishment failures
5. Correlate timestamps to identify if config was applied correctly

**Queries**:
```javascript
// Step 1: Check config push
query: "((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/cfgagentv2.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND \"tenant-18548\")"

// Step 2: Check config reload
query: "((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/cfgwatcher.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND \"reload\")"

// Step 3: Check tunnel creation
query: "((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/tunsvc.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND \"tenant-18548\" AND \"create\")"

// Step 4: Check tunnel establishment
query: "((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/strongswan.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND \"tenant-18548\")"
```

### Use Case 6: Health Check Monitoring (Legacy IPSEC)
**User Request**: "Check if gateway ipsecgw03.mil1 is performing health checks correctly"

**Steps**:
1. Query `ipsecmonitor.log` for health check events
2. Look for health check failures or keepalive timeouts
3. Identify affected tunnels/tenants
4. Check if failures correlate with tunnel down events in strongswan.log

**Queries**:
```javascript
// Step 1: Health check events
query: "((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/ipsecmonitor.log) AND (_sourceHost=ipsecgw03.mil1.nskope.net) AND (\"health check\" OR \"keepalive\"))"

// Step 2: Correlate with tunnel events
query: "((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/strongswan.log) AND (_sourceHost=ipsecgw03.mil1.nskope.net) AND \"Tunnel is Down\")"
```

### Use Case 7: Tenant Provisioning/Deprovisioning Analysis (Legacy IPSEC)
**User Request**: "Track tenant 11264 provisioning lifecycle"

**Steps**:
1. Query `cfgagentv2.log` for tenant provision/deprovision events
2. Query `tunsvc.log` for tunnel creation/deletion
3. Query `cfgwatcher.log` for configuration changes
4. Build timeline of provisioning events

**Queries**:
```javascript
// Comprehensive provisioning view
query: "((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/cfgagentv2.log OR _sourceName=/opt/ns/log/tunsvc.log OR _sourceName=/opt/ns/log/cfgwatcher.log) AND \"tenant-11264\" AND (\"provision\" OR \"create\" OR \"delete\" OR \"deprovision\"))"
```

### Use Case 8: Gateway-wide Issue Detection (Legacy IPSEC)
**User Request**: "Are there any systemic issues on ipsecgw01.nyc4?"

**Steps**:
1. Query all log files for error patterns
2. Check for:
   - Multiple tunnel failures (strongswan.log)
   - Health check failures (ipsecmonitor.log)
   - Config agent errors (cfgagentv2.log)
   - Service crashes or restarts (tunsvc.log)
3. Identify common patterns or timing

**Queries**:
```javascript
// Multi-log error detection
query: "((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/*.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND (\"error\" OR \"failed\" OR \"crash\" OR \"restart\" OR \"timeout\"))"
```

### Use Case 9: RCA Document (PowerPoint) Generation
**User Request**: "Prepare RCA document for tenant 18548 tunnel flaps" or "Create RCA PPT for IPSEC issues"

**Purpose**: Generate a comprehensive Root Cause Analysis document in PowerPoint format with event analysis, graphs, and visualizations.

**Required Information to Collect**:
Before generating the RCA document, **ALWAYS ask the user** for the following information:
1. **Customer Name** (Required) - e.g., "Acme Corporation"
2. **Tenant ID** (Required if not already provided) - e.g., "18548"
3. **Gateway/Hostname** (Optional if POP-wide analysis)
4. **Time Period** (Required) - e.g., "last 24 hours", "Feb 14 10:00 AM to Feb 15 2:00 PM"
5. **Issue Type** (Required) - e.g., "Tunnel Flaps", "Connectivity Issues", "Health Check Failures"
6. **POP Name** (if gateway not specified) - e.g., "nyc4", "mil1"
7. **Severity Level** (Optional) - e.g., "Critical", "High", "Medium"
8. **Ticket/Case Number** (Optional) - e.g., "INC00123456"

**Steps**:
1. **Collect Required Information**:
   - Use AskUserQuestion tool to gather customer name and other missing details
   - Validate all required fields are provided

2. **Data Collection Phase**:
   - Query all relevant logs for the specified time period
   - Collect tunnel up/down events
   - Gather error events and their frequencies
   - Identify different types of flaps/issues

3. **Analysis Phase**:
   - Count total flap occurrences
   - Categorize flaps by type:
     - Authentication failures
     - Peer unreachable
     - Configuration issues
     - Health check failures
     - DPD (Dead Peer Detection) timeouts
     - SA (Security Association) failures
   - Calculate statistics (frequency, duration, MTTR)
   - Identify patterns (time-based, peer-based, interface-based)

4. **PPT Generation Phase**:
   - Create PowerPoint presentation using python-pptx library
   - Include all sections listed below

**PPT Structure and Content**:

**Slide 1: Title Slide**
- Title: "Root Cause Analysis - [Issue Type]"
- Customer Name
- Tenant ID
- Date Range
- POP/Gateway
- Prepared Date
- Netskope Logo (if available)

**Slide 2: Executive Summary**
- Brief overview of the issue
- Impact statement
- Number of incidents
- Total downtime
- Resolution status

**Slide 3: Timeline Overview**
- Graphical timeline of all events
- Visual representation showing:
  - Tunnel down events (red markers)
  - Tunnel up events (green markers)
  - Duration of outages
- X-axis: Time, Y-axis: Tunnel status

**Slide 4: Flap Statistics**
- Table showing:
  - Total number of flaps
  - Average flap duration
  - Longest outage duration
  - Shortest outage duration
  - Mean Time To Recover (MTTR)
  - Affected connections/peers

**Slide 5: Flap Type Distribution (Bar Chart)**
- Bar chart showing count of each flap type:
  - Authentication failures
  - DPD timeouts
  - Peer unreachable
  - Configuration issues
  - Health check failures
  - SA establishment failures
  - Other errors
- X-axis: Flap Type, Y-axis: Count

**Slide 6: Flap Type Distribution (Pie Chart)**
- Pie chart showing percentage distribution of flap types
- Different colors for each category
- Include percentages and counts

**Slide 7: Hourly Flap Distribution**
- Line graph showing flaps per hour
- Identify peak hours
- X-axis: Hour of day, Y-axis: Number of flaps

**Slide 8: Event Details Table**
- Detailed table with columns:
  - Timestamp
  - Event Type (Up/Down)
  - Duration
  - Peer IP
  - Interface
  - Reason/Error Message
  - Connection ID

**Slide 9: Root Cause Analysis**
- Primary root cause identified
- Contributing factors
- Evidence from logs
- Technical details
- Correlated events

**Slide 10: Peer Analysis (if multiple peers)**
- Table or chart showing flaps per peer IP
- Identify problematic peer connections
- Geographical analysis if applicable

**Slide 11: Configuration Analysis**
- Relevant configuration changes detected
- Config push events from cfgagentv2.log
- Config reload events from cfgwatcher.log
- Correlation with flap events

**Slide 12: Health Check Analysis**
- Health check failure statistics
- Correlation with tunnel flaps
- Keepalive timeout events
- Graph showing health check status over time

**Slide 13: Impact Assessment**
- Services affected
- User impact
- Business impact
- SLA compliance status

**Slide 14: Recommendations**
- Immediate actions taken
- Preventive measures
- Configuration recommendations
- Monitoring improvements
- Follow-up actions

**Slide 15: Appendix - Log Samples**
- Key log excerpts showing:
  - First flap occurrence
  - Pattern examples
  - Error messages
  - Recovery events

**Implementation Requirements**:

1. **Python Libraries Needed**:
   ```bash
   pip install python-pptx matplotlib pandas numpy
   ```

2. **Graph Generation**:
   - Use matplotlib for creating charts
   - Export as PNG images
   - Embed in PPT slides
   - Use Netskope brand colors if available:
     - Primary: #00B4A0 (Teal)
     - Secondary: #1E3A8A (Navy Blue)
     - Alert Red: #DC2626
     - Success Green: #10B981
     - Warning Orange: #F59E0B

3. **Data Processing**:
   - Parse log lines to extract structured data
   - Group events by type
   - Calculate statistics
   - Generate time-series data

**Example Queries for RCA**:

```javascript
// Step 1: All tunnel events for tenant
query: "((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/strongswan.log) AND (_sourceHost=ipsecgw*.nyc4.nskope.net) AND \"tenant-18548\")"

// Step 2: Configuration changes
query: "((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/cfgagentv2.log OR _sourceName=/opt/ns/log/cfgwatcher.log) AND (_sourceHost=ipsecgw*.nyc4.nskope.net) AND \"tenant-18548\")"

// Step 3: Health check events
query: "((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/ipsecmonitor.log) AND (_sourceHost=ipsecgw*.nyc4.nskope.net) AND \"tenant-18548\")"

// Step 4: Tunnel service events
query: "((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/tunsvc.log) AND (_sourceHost=ipsecgw*.nyc4.nskope.net) AND \"tenant-18548\")"
```

**Python Script Template for PPT Generation**:

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
import matplotlib.pyplot as plt
from datetime import datetime

def create_rca_ppt(customer_name, tenant_id, time_period, events_data, statistics, analysis):
    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    # Slide 1: Title Slide
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]

    title.text = "Root Cause Analysis - IPSEC Tunnel Flaps"
    subtitle.text = f"Customer: {customer_name}\nTenant ID: {tenant_id}\nPeriod: {time_period}\nDate: {datetime.now().strftime('%Y-%m-%d')}"

    # Slide 2: Executive Summary
    # ... (implementation continues)

    # Slide 5: Bar Chart for Flap Types
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    title = slide.shapes.title
    title.text = "Flap Type Distribution"

    # Generate bar chart using matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))
    flap_types = list(statistics['flap_types'].keys())
    counts = list(statistics['flap_types'].values())
    colors = ['#DC2626', '#F59E0B', '#10B981', '#00B4A0', '#1E3A8A']

    ax.bar(flap_types, counts, color=colors[:len(flap_types)])
    ax.set_xlabel('Flap Type')
    ax.set_ylabel('Count')
    ax.set_title('Distribution of Tunnel Flap Types')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save and embed chart
    chart_path = '/tmp/flap_types_chart.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    slide.shapes.add_picture(chart_path, Inches(1), Inches(2), width=Inches(8))
    plt.close()

    # Continue with other slides...

    return prs

# Save presentation
prs.save(f'/tmp/RCA_{customer_name}_{tenant_id}_{datetime.now().strftime("%Y%m%d")}.pptx')
```

**Output Files**:
- PowerPoint file: `RCA_[CustomerName]_[TenantID]_[Date].pptx`
- Supporting charts (PNG): Generated in /tmp and embedded in PPT
- Optional: PDF export of the presentation

**Workflow Summary**:
1. User requests RCA document
2. Ask for customer name and other required details
3. Query all relevant logs using Sumo Logic
4. Parse and analyze log data
5. Calculate statistics and categorize events
6. Generate charts using matplotlib
7. Create PowerPoint presentation with all slides
8. Save and provide download link to user

**Important Notes**:
- Always ask for customer name before generating RCA document
- Use professional formatting and brand colors
- Include clear visualizations and graphs
- Provide actionable recommendations
- Ensure all timestamps are in user's timezone
- Include log evidence for root cause claims
- Make the presentation executive-ready

## Expected Output Format

**CRITICAL**: When analyzing tenant-specific logs, ALWAYS provide comprehensive breakdown.

### Standard Tenant Analysis Output

When analyzing logs for a specific tenant, provide:

1. **Executive Summary**: Brief overview of findings

2. **Total Flap Count**: Overall number of tunnel flaps detected

3. **Breakdown by Gateway**: List which gateways/nodes experienced flaps
   ```
   Example:
   - ipsecgw01.nyc4.nskope.net: 12 flaps
   - ipsecgw03.mil1.nskope.net: 8 flaps
   - vppipsecgw02.c18.iad0.netskope.com: 5 flaps
   ```

4. **Breakdown by POP**: Group flaps by data center location
   ```
   Example:
   - nyc4: 12 flaps
   - mil1: 8 flaps
   - iad0: 5 flaps
   ```

5. **Breakdown by Flap Reason**: Categorize flaps by root cause with counts and percentages
   ```
   Example:
   Total: 25 flaps
   - DPD timeout: 10 flaps (40%)
   - HC down (Health Check failure): 5 flaps (20%)
   - New tunnel from same peer: 4 flaps (16%)
   - Peer unreachable: 3 flaps (12%)
   - Authentication failure: 2 flaps (8%)
   - Unknown/Other: 1 flap (4%)
   ```

6. **Timeline**: When events occurred (chronological list with timestamps)

7. **Root Cause Analysis**: Detailed analysis of why events happened
   - Primary reason identified
   - Contributing factors
   - Evidence from logs

8. **Recommendations**: Actionable steps to resolve issues
   - Immediate actions
   - Long-term fixes
   - Monitoring suggestions

9. **Detailed Event Log** (optional): Table with timestamp, gateway, POP, event type, reason

10. **Diagram** (optional): Visual representation of events timeline

### Output Format Template

```markdown
## Tenant <ID> Flap Analysis

### Summary
[Brief overview of the situation]

### Total Flaps: <count>

### Breakdown by Gateway
| Gateway | Flaps | Percentage |
|---------|-------|------------|
| gateway1 | X | XX% |
| gateway2 | Y | YY% |

### Breakdown by POP
| POP | Flaps | Percentage |
|-----|-------|------------|
| pop1 | X | XX% |
| pop2 | Y | YY% |

### Breakdown by Reason
| Reason | Count | Percentage |
|--------|-------|------------|
| DPD timeout | X | XX% |
| HC down | Y | YY% |
| New tunnel from same peer | Z | ZZ% |
| [Other reasons...] | ... | ...% |

### Timeline
[Chronological list of events with timestamps]

### Root Cause Analysis
[Detailed analysis]

### Recommendations
[Actionable recommendations]
```

### When NOT to Provide Detailed Breakdown

Only provide simplified output when:
- User explicitly asks for a quick summary
- Query is NOT tenant-specific (e.g., general POP health check)
- No flaps detected (just report "no flaps found")

For all tenant-specific flap queries, the detailed breakdown is REQUIRED.

## Query Construction Rules

1. **Hostname Format**:
   - Specific host: `ipsecgw07.nyc4.nskope.net`
   - All hosts in POP: `*.nyc4.nskope.net`
   - All hosts with pattern: `ipsecgw*.nyc4.nskope.net`

2. **Tenant ID Format**:
   - Always use: `tenant-<ID>` (e.g., `tenant-11264`)

3. **Keywords by Log File**:

   **strongswan.log (IPSEC Protocol Events)**:
   - Tunnel down: `"Tunnel is Down"` or `"down"`
   - Tunnel up: `"Tunnel is Up"` or `"established"`
   - Deletion: `"delete"` or `"deleted"`
   - SA events: `"CHILD_SA"` or `"IKE_SA"`
   - Authentication: `"authentication"` or `"auth failed"`
   - Connection: `"connection"` or `"peer"`

   **tunsvc.log (Tunnel Service - Legacy IPSEC)**:
   - Tunnel creation: `"create tunnel"` or `"tunnel created"`
   - Tunnel deletion: `"delete tunnel"` or `"tunnel deleted"`
   - Service operations: `"start"` or `"stop"` or `"restart"`
   - State transitions: `"state change"` or `"transition"`
   - Configuration: `"config"` or `"configure"`

   **ipsecmonitor.log (Health Monitoring - Legacy IPSEC)**:
   - Health checks: `"health check"` or `"HC"`
   - Keepalive: `"keepalive"` or `"KA"`
   - Failures: `"failed"` or `"timeout"` or `"unreachable"`
   - Recovery: `"recovered"` or `"up"`
   - Connectivity: `"ping"` or `"reachable"`

   **cfgwatcher.log (Config File Watching - Legacy IPSEC)**:
   - File changes: `"modified"` or `"changed"` or `"updated"`
   - Reload: `"reload"` or `"restart"`
   - Detection: `"detected"` or `"watch"`
   - Errors: `"error"` or `"failed to reload"`

   **cfgagentv2.log (Config Management - Legacy IPSEC)**:
   - Config push: `"config push"` or `"push config"`
   - Config pull: `"config pull"` or `"pull config"`
   - Provisioning: `"provision"` or `"add tenant"`
   - Deprovisioning: `"deprovision"` or `"remove tenant"`
   - Validation: `"validate"` or `"validation error"`
   - API calls: `"API"` or `"control plane"`
   - Sync: `"sync"` or `"synchronize"`

   **nsgregw.log (GRE Gateway)**:
   - Resource status: `"resource_status"` or `"status"`
   - Tunnel events: `"UP"` or `"DOWN"`
   - Gateway health: `"health"` or `"alive"`

   **Common Error Keywords (All Logs)**:
   - `"error"` or `"ERROR"`
   - `"failed"` or `"failure"`
   - `"timeout"` or `"timed out"`
   - `"crash"` or `"crashed"`
   - `"exception"` or `"fatal"`

4. **Time Range**:
   - **CRITICAL**: Must use ISO 8601 format with timezone
   - Format: `YYYY-MM-DDTHH:mm:ss+TZ` (e.g., `2026-02-14T21:39:56+05:30`)
   - Cannot use relative formats like `-30m`, `-1h` - these will fail
   - Use moment.js format or calculate timestamps programmatically

## Timestamp Handling (IMPORTANT)

### Required Format
Sumo Logic API requires timestamps in ISO 8601 format with timezone offset:
```
2026-02-14T21:39:56+05:30
```

### Calculating Timestamps

**Using Node.js** (in MCP server or command line):
```javascript
const moment = require('moment');
const to = moment();
const from = moment().subtract(30, 'minutes');

console.log('from:', from.format());  // 2026-02-14T21:39:56+05:30
console.log('to:', to.format());      // 2026-02-14T22:09:56+05:30
```

**Common Time Ranges**:
- Last 30 minutes: `moment().subtract(30, 'minutes').format()`
- Last 1 hour: `moment().subtract(1, 'hour').format()`
- Last 24 hours: `moment().subtract(24, 'hours').format()`
- Last 1 day: `moment().subtract(1, 'day').format()`

**IMPORTANT**:
- Do NOT use formats like `-30m`, `-1h`, `now` - these are invalid
- Always provide both `from` and `to` parameters
- The MCP server uses Asia/Hong_Kong timezone internally

### Example Query with Timestamps
```javascript
mcp__sumologic__search_sumologic({
  query: "((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/strongswan.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND \"tenant-18548\")",
  from: "2026-02-14T21:39:56+05:30",
  to: "2026-02-14T22:09:56+05:30"
})
```

## Log Response Structure

### Response Format
The MCP server returns logs in this structure:
```json
{
  "messages": [
    {
      "map": {
        "_raw": "{\"log\":\"<actual log line>\"}",
        "_sourcehost": "ipsecgw01.nyc4.nskope.net",
        "_sourcename": "/opt/ns/log/strongswan.log",
        "_messagetime": "1771086240000",
        "datacenter": "nyc4",
        "pop": "US-NYC4",
        ...
      }
    }
  ]
}
```

### Key Fields in Response
- **_raw**: Contains the actual log line as JSON string (needs parsing)
- **_sourcehost**: Hostname of the gateway
- **_sourcename**: Log file path
- **_messagetime**: Unix timestamp in milliseconds
- **datacenter**: POP name (e.g., "nyc4")
- **pop**: Full POP identifier (e.g., "US-NYC4")

### PII Masking
**IMPORTANT**: The MCP server automatically masks sensitive information:
- Phone numbers → `[PHONE REDACTED]`
- IP addresses (in some contexts) → `[ADDRESS REDACTED]`
- Tenant IDs in connection names may be partially redacted

When analyzing logs, be aware that:
- Tenant IDs might appear as `tenant-[PHONE REDACTED]`
- Some numeric values might be redacted
- Peer IPs and interface names are usually preserved

### Parsing Log Data
The `_raw` field contains JSON with the actual log line:
```json
"_raw": "{\"log\":\"2026-02-14 16:16:36 55[TNC] <tenant-18548-37746|39567> ... Tunnel is Down for connection: tenant-18548-37746 peer-id: 372.NE_6_6a80b9a8 peer-ip: 74.67.17.200 interface: xfrm4680...\"}"
```

To extract the log line:
1. Parse the `_raw` JSON string
2. Extract the `log` field
3. Parse the StrongSwan log format

## Error Handling

If query fails:
1. Verify MCP server `sumologic` is available
2. Check query syntax
3. Verify hostname/POP name format
4. Ensure time range is specified

## Practical Examples

### Example 1: Tenant Tunnel Flaps (Last 30 Minutes)

**Step 1**: Calculate timestamps
```bash
cd ~/mcp-sumologic
node -e "const moment = require('moment'); console.log('from:', moment().subtract(30, 'minutes').format()); console.log('to:', moment().format());"
```

**Step 2**: Query for tunnel down events
```javascript
mcp__sumologic__search_sumologic({
  query: "((_sourcecategory=*ipsecgw* ) AND (_sourceName=/opt/ns/log/strongswan.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND \"tenant-18548\")",
  from: "2026-02-14T21:39:56+05:30",
  to: "2026-02-14T22:09:56+05:30"
})
```

**Step 3**: Query for tunnel up events
```javascript
mcp__sumologic__search_sumologic({
  query: "((_sourcecategory=*ipsecgw* ) AND (_sourceName=/opt/ns/log/strongswan.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND \"tenant-18548\" AND (\"Tunnel is Up\" OR \"established\"))",
  from: "2026-02-14T21:39:56+05:30",
  to: "2026-02-14T22:09:56+05:30"
})
```

### Example 2: All Activity for a Gateway (Last 1 Hour)
```javascript
mcp__sumologic__search_sumologic({
  query: "((_sourcecategory=*ipsecgw* ) AND (_sourceName=/opt/ns/log/strongswan.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND NOT half-open)",
  from: moment().subtract(1, 'hour').format(),
  to: moment().format()
})
```

### Example 3: Multiple Tenants in POP
```javascript
mcp__sumologic__search_sumologic({
  query: "((_sourcecategory=*ipsecgw* ) AND (_sourceName=/opt/ns/log/strongswan.log) AND (_sourceHost=*.nyc4.nskope.net) AND (\"tenant-18548\" OR \"tenant-11264\"))",
  from: moment().subtract(30, 'minutes').format(),
  to: moment().format()
})
```

## Workflow for Tunnel Flap Analysis

1. **Load the Sumo Logic MCP tool**:
   ```
   ToolSearch → select:mcp__sumologic__search_sumologic
   ```

2. **Calculate timestamps** (if needed):
   ```bash
   cd ~/mcp-sumologic && node -e "const moment = require('moment'); console.log(moment().subtract(30, 'minutes').format(), moment().format());"
   ```

3. **Query for tunnel down events** using tenant ID and hostname

4. **Query for tunnel up events** to identify recovery

5. **Analyze the results**:
   - Count up/down events
   - Extract peer IPs and interface names
   - Identify patterns (multiple sites, timing, etc.)
   - Look for error messages

6. **Generate report** with:
   - Summary of findings
   - Timeline table
   - Root cause analysis
   - Recommendations

## Troubleshooting

### Issue: Empty Results `{ "messages": [] }`

**Possible Causes**:
1. **Invalid timestamp format** - Must use ISO 8601 with timezone
2. **No logs in time range** - Expand the time window
3. **Wrong hostname format** - Check exact hostname spelling
4. **Authentication issue** - Verify MCP server credentials

**Solution**:
- Check MCP server logs for actual errors (after updating client.ts to throw errors)
- Verify timestamp format matches: `YYYY-MM-DDTHH:mm:ss+TZ`
- Test with working query first: `"((_sourcecategory=*ipsecgw*) AND (_sourceName=/opt/ns/log/strongswan.log) AND (_sourceHost=ipsecgw01.nyc4.nskope.net) AND NOT half-open)"`

### Issue: MCP Server Not Connected

**Check**:
```bash
# Verify server is in config
cat ~/.claude/config.json | grep -A 10 "sumologic"

# Check credentials
cat ~/mcp-sumologic/.env

# Test MCP server manually
cd ~/mcp-sumologic
node --experimental-specifier-resolution=node dist/index.js
```

**Fix**: Restart Claude Code to reload MCP server

## Notes

- **Gateway Numbering**: Gateways are numbered sequentially (ipsecgw01, ipsecgw02, etc.)
- **Wildcard Usage**: Use `*` to match multiple hosts when POP name is given
- **Case Sensitivity**: Log searches are case-sensitive, use exact keyword matching
- **Multiple Keywords**: Use OR/AND operators for multiple conditions
- **MCP Server Location**: `~/mcp-sumologic/`
- **Config Files**:
  - `~/.claude/config.json` - MCP server registration and credentials
  - `~/mcp-sumologic/.env` - Development environment variables
- **Timezone**: MCP server uses Asia/Hong_Kong timezone by default
