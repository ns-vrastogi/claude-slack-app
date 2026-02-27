# Quick Command Reference for Legacy IPSECGW Performance Testing

## Gateway Node Commands

### Access Gateway
```bash
tsh ssh --cluster iad0 ipsecgw01.c18.iad0.netskope.com
```
**Note**: Always use full hostname with `.netskope.com` suffix

### Stop Configuration Services
```bash
# Only stop cfgagentv2, not health_check
sudo supervisorctl stop cfgagentv2
```

### Apply Tunnel Config
```bash
sudo cp /home/your-username/selective/netskope.swanctl.json /opt/ns/tenant/1530/ipsecgw/
```
**Note**: Services will automatically reload. No need to restart.

### Verify Services Running
```bash
sudo supervisorctl status tunsvc strongswan
```

### Check Network Throughput
```bash
# Use sar (works in SSH)
sar -n DEV 1 5 | grep -A 1 Average

# Or use ifstat
ifstat -i bond0 1 5
```

### Monitor Logs
```bash
tail -f /var/log/tunsvc.log
tail -f /var/log/strongswan.log
```

### Check Infrastructure
```bash
cat /opt/nc/common/remote/cfw.conf
cat /opt/nc/common/remote/proxy.conf
```

## Client Node Commands

### Access Client Nodes
```bash
tsh ssh --cluster iad0 prfclient01.c18.iad0.netskope.com
tsh ssh --cluster iad0 prfclient02.c18.iad0.netskope.com
tsh ssh --cluster iad0 prfclient03.c18.iad0.netskope.com
tsh ssh --cluster iad0 prfclient04.c18.iad0.netskope.com
tsh ssh --cluster iad0 prfclient05.c18.iad0.netskope.com
```

### Setup 500 Idle Tunnels (prfclient01) - OPTIONAL
```bash
sudo cp /etc/ipsec.conf_500Tun /etc/ipsec.conf
sudo cp /etc/ipsec.secrets_500Tun /etc/ipsec.secrets
sudo ipsec restart
sudo python3 /home/seema/tunnel_bringup.py
```
**Warning**: This step is optional and may cause tunnel flapping. Can be skipped.

### Check Endpoint Count (prfclient02-05)
```bash
# On prfclient02
ip addr | grep "10\.2" | awk -F' ' '{print $2}' | awk -F'/' '{print $1}' | wc -l

# On prfclient03
ip addr | grep "10\.3" | awk -F' ' '{print $2}' | awk -F'/' '{print $1}' | wc -l

# On prfclient04
ip addr | grep "10\.4" | awk -F' ' '{print $2}' | awk -F'/' '{print $1}' | wc -l

# On prfclient05
ip addr | grep "10\.5" | awk -F' ' '{print $2}' | awk -F'/' '{print $1}' | wc -l
```

### Create Endpoints (if missing)
```bash
sudo python3 /home/seema/bringup_iface.py
```

### Export IPs to CSV (prfclient02-05)
```bash
# On prfclient02
ip addr | grep "10\.2" | awk -F' ' '{print $2}' | awk -F'/' '{print $1}' > /home/seema/interface_ip.csv

# On prfclient03
ip addr | grep "10\.3" | awk -F' ' '{print $2}' | awk -F'/' '{print $1}' > /home/seema/interface_ip.csv

# On prfclient04
ip addr | grep "10\.4" | awk -F' ' '{print $2}' | awk -F'/' '{print $1}' > /home/seema/interface_ip.csv

# On prfclient05
ip addr | grep "10\.5" | awk -F' ' '{print $2}' | awk -F'/' '{print $1}' > /home/seema/interface_ip.csv
```

### Setup Throughput Test Config (prfclient02-05)
```bash
sudo cp /etc/ipsec.conf_reg /etc/ipsec.conf
sudo cp /etc/ipsec.secrets_reg /etc/ipsec.secrets
sudo ipsec restart
```

### Bring Up Test Tunnels (prfclient02-05)
```bash
# On prfclient02
sudo ipsec up conn_2

# On prfclient03
sudo ipsec up conn_2

# On prfclient04
sudo ipsec up conn_2

# On prfclient05
sudo ipsec up conn_2
```

### Verify Connectivity (prfclient02-05)
```bash
# On prfclient02
curl -k --interface 10.2.0.2 http://10.136.8.36:2250/d/1/21bytes.txt/download

# On prfclient03
curl -k --interface 10.3.0.3 http://10.136.8.36:2250/d/1/21bytes.txt/download

# On prfclient04
curl -k --interface 10.4.0.4 http://10.136.8.36:2250/d/1/21bytes.txt/download

# On prfclient05
curl -k --interface 10.5.0.5 http://10.136.8.36:2250/d/1/21bytes.txt/download
```

Expected output: `This is a test file`

## JMeter Commands

### Run JMeter Test
```bash
# Remove old results and run test (requires sudo)
sudo rm -f /home/seema/test_result.jtl
sudo /home/seema/lnp/performance-automation/tools/apache-jmeter-5.2/bin/jmeter -n -t [SCRIPT_PATH]
```
**Note**: Error rates of 2-4% are expected and normal.

### Stop JMeter
```bash
sudo pkill -f jmeter
```

### JMeter Script Paths
```bash
# Proxy Upload
/home/seema/ipsec_script_upload_nsproxy.jmx

# CFW Download
/home/seema/ipsec_script_upload_download.jmx

# CFW Upload
/home/seema/ipsec_script_upload_download.jmx
```

## Multi-Node Command Templates

### Run on All Gateway Nodes (template)
```bash
for node in ipsecgw01 ipsecgw02 ipsecgw03 ipsecgw04; do
  echo "=== $node ==="
  tsh ssh --cluster iad0 ${node}.c18.iad0 "COMMAND_HERE"
done
```

### Run on All Client Nodes (template)
```bash
for i in {2..5}; do
  echo "=== prfclient0$i ==="
  tsh ssh --cluster iad0 prfclient0${i}.c18.iad0 "COMMAND_HERE"
done
```

## Validation Commands

### Check All Endpoints Created
```bash
# Run on each prfclient02-05, should return ~6500-8000
ip addr | grep "10\.[2-5]" | wc -l
```

### Check CSV Files Populated
```bash
cat /home/seema/interface_ip.csv | wc -l
head /home/seema/interface_ip.csv
```

### Check Tunnel Status
```bash
sudo ipsec status
sudo ipsec statusall
```

### Check Service Status
```bash
supervisorctl status
```
