# VPP Command Reference

## Interface Commands

### Show interface addresses
```bash
sudo vppctl show int address
```
Displays IP addresses assigned to all VPP interfaces.

### Show hardware interfaces
```bash
sudo vppctl show hardware-interfaces
```
Shows detailed hardware interface information including link status, speed, and statistics.

## Routing Commands

### Show IP routing table
```bash
sudo vppctl show ip table
```
Displays the VPP IP routing table with all configured routes.

### Show IP FIB (Forwarding Information Base)
```bash
sudo vppctl show ip fib
```
Shows the forwarding information base with route details.

Example - search for specific route:
```bash
sudo vppctl show ip fib | grep -A 4 20.2.0.10
```

### Add IP route
```bash
sudo vppctl ip route add <destination> via <gateway> <interface>
```
Example:
```bash
sudo vppctl ip route add 20.2.0.10/32 via 20.2.0.5 BondEthernet0.676
```

### Delete IP route
```bash
sudo vppctl ip route del <destination> via <gateway>
```
Example:
```bash
sudo vppctl ip route del 20.2.0.10/32 via 29.2.0.1
```

## Error/Debugging Commands

### Show all errors
```bash
sudo vppctl show errors
```
Displays all VPP error counters.

### Show only actual errors (filter out "no error")
```bash
sudo vppctl show errors | grep -i error | grep -v "no error"
```
Filters the error output to show only non-zero error counts.

## Node and Buffer Commands

### Show node information
```bash
sudo vppctl show node
```
Displays information about VPP graph nodes.

### Show buffer usage
```bash
sudo vppctl show buffers
```
Shows buffer allocation and usage statistics.

### Show runtime statistics
```bash
sudo vppctl show runtime
```
Displays runtime statistics for all nodes including CPU cycles and packet processing.

## Service-Specific Commands (STSVC)

### Show tunnel details
```bash
sudo vppctl show stsvc tunnel_details
```
Displays detailed information about all service tunnels.

### Show tunnel details for specific tenant
```bash
sudo vppctl show stsvc tunnel_details tenantid <tenant_id>
```
Example:
```bash
sudo vppctl show stsvc tunnel_details tenantid 6666
```

### Show tunnel endpoints for specific tenant
```bash
sudo vppctl show stsvc tunnel_details tenantid <tenant_id> | grep endpoint
```
Example:
```bash
sudo vppctl show stsvc tunnel_details tenantid 6666 | grep endpoint
```

### Show global service statistics
```bash
sudo vppctl show stsvc stats global
```
Displays global statistics for the STSVC service.

### Show service summary
```bash
sudo vppctl show stsvc summary
```
Shows a summary of the service status and configuration.

## IPsec Service Commands

### Show IPsec service stats per thread
```bash
sudo vppctl show ipsecstsvc stats thread <thread_id>
```
Shows IPsec service statistics for a specific worker thread.

Example - check forward traffic on all threads:
```bash
sudo vppctl show ipsecstsvc stats thread 0 |grep recv_node_traffic_to_fwd;\
sudo vppctl show ipsecstsvc stats thread 1 |grep recv_node_traffic_to_fwd;\
sudo vppctl show ipsecstsvc stats thread 2 |grep recv_node_traffic_to_fwd;\
sudo vppctl show ipsecstsvc stats thread 3 |grep recv_node_traffic_to_fwd;\
sudo vppctl show ipsecstsvc stats thread 4 |grep recv_node_traffic_to_fwd;\
sudo vppctl show ipsecstsvc stats thread 5 |grep recv_node_traffic_to_fwd;
```

Example - check reverse traffic on all threads:
```bash
sudo vppctl show ipsecstsvc stats thread 0 |grep recv_node_traffic_to_rev;\
sudo vppctl show ipsecstsvc stats thread 1 |grep recv_node_traffic_to_rev;\
sudo vppctl show ipsecstsvc stats thread 2 |grep recv_node_traffic_to_rev;\
sudo vppctl show ipsecstsvc stats thread 3 |grep recv_node_traffic_to_rev;\
sudo vppctl show ipsecstsvc stats thread 4 |grep recv_node_traffic_to_rev;\
sudo vppctl show ipsecstsvc stats thread 5 |grep recv_node_traffic_to_rev;
```

## Load Balancing (NSLB) Commands

### Show load balancer distribution
```bash
sudo vppctl nslb show-distribution
```
Displays the load balancer's traffic distribution configuration.

### Show load balancer services
```bash
sudo vppctl nslb show-service
```
Shows configured load balancer services and their backends.

## Packet Trace Commands

### Clear trace buffer
```bash
sudo vppctl clear trace
```
Clears the packet trace buffer.

### Add packet trace
```bash
sudo vppctl trace add dpdk-input <count>
```
Captures packets for tracing. Example:
```bash
sudo vppctl trace add dpdk-input 100000
```

### Show packet trace
```bash
sudo vppctl show trace
```
Displays captured packet traces.

### Show trace with max count
```bash
sudo vppctl show trace max <count>
```
Example - save trace to file:
```bash
sudo vppctl -s /run/vpp/cli.sock show trace max 100000 > /tmp/test2
```

### Set trace filter
```bash
sudo vppctl classify filter trace mask hex {src_mask} match hex {src_mask_filter}
```
Sets up packet classification filters for selective tracing.

### Enable filtered trace
```bash
sudo vppctl trace add dpdk-input <count> filter
```
Example:
```bash
sudo vppctl trace add dpdk-input 10000 filter
```

### Delete trace filter
```bash
sudo vppctl classify table delete table 0
```
Removes the classification filter table.

## Statistics Commands

### Get VPP statistics
```bash
sudo vpp_get_stats dump
```
Dumps all VPP statistics counters.

### Get worker thread utilization
```bash
sudo vpp_get_stats dump | grep -i "NSIPSECGW\|STSVC" | grep -i recv_node_traffic_to_fwd; \
sleep 60; \
sudo vpp_get_stats dump | grep -i "NSIPSECGW\|STSVC" | grep -i recv_node_traffic_to_fwd;
```
Captures statistics at two points in time to measure worker thread traffic processing.

## Feature Control Commands

### Disable log emission
```bash
ns_steering features disable_log_emit 1
```
Disables log emission in the steering service to reduce logging overhead.

## VPP Service Management (Supervisorctl)

### Show service status
```bash
sudo supervisorctl status
```
Shows status of all supervised services including VPP.

### Show specific service status
```bash
sudo supervisorctl status steeringlb:vpp
```
Shows status of a specific service.

### Restart VPP service
```bash
sudo supervisorctl restart steeringlb:vpp
```
Restarts the VPP service.

### Stop VPP service
```bash
sudo supervisorctl stop steeringlb:vpp
```
Stops the VPP service.

### Start VPP init service
```bash
sudo supervisorctl start steeringlb:init
```
Starts the VPP initialization service.

### Restart all services
```bash
sudo supervisorctl restart all
```
Restarts all supervised services.

### Stop specific services
```bash
sudo supervisorctl stop cfgagentv2 cfgagentv2_health_check cfgwatcher health-service
```
Stops multiple specified services.

## Direct VPP Startup

### Start VPP directly with config
```bash
sudo /usr/bin/vpp -c /etc/vpp/startup.conf
```
Starts VPP directly using the startup configuration file.

### Restart VPP with updated config
```bash
sudo vpp restart
```
Restarts VPP service (alternative method).

## Configuration Files

### VPP startup configuration
```
/etc/vpp/startup.conf
```
Main VPP startup configuration file.

### Interface configuration
```
/etc/vpp/nat.conf
```
Network interface configuration for VPP.

### VPP logs
```
/opt/ns/log/vpp.log
/opt/ns/log/nsvpp.log
/var/log/syslog
```
VPP log file locations.

### SteeringLB logs
```
/var/log/steeringlbhealthmonitor_stdout.log
/var/log/steeringlbhealthmonitor.log
/var/log/steeringlb_stdout.log
```
SteeringLB service log files.

## Plugin Management

### Replace plugin SO files
```bash
cd /home/your-username/testing_plugins
sudo cp libsteering_plugin.so /usr/lib/ipsec/plugins/libsteering_plugin.so
sudo cp libipsecgw_plugin.so /usr/lib/ipsec/plugins/libipsecgw_plugin.so
```
Updates VPP plugin shared objects for testing.

### Revert plugin SO files
```bash
cd /home/your-username/testing_plugins
sudo cp libsteering_plugin.so_org /usr/lib/ipsec/plugins/libsteering_plugin.so
sudo cp libipsecgw_plugin.so_org /usr/lib/ipsec/plugins/libipsecgw_plugin.so
```
Reverts plugins to original versions. 
