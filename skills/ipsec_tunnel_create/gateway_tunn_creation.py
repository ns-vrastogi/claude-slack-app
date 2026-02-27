import os
import json
for j in range(80000, 80100):
  d = {}
  d["tenant_id"] = str(j)
  d["tunnel_details"] = {}
  d["pop_details"] = {}
  d["pop_details"]["qa01-dp-npe"] = []
  d["pop_details"]["qa01"] = []
  for i in range(1, 200):
    tunnel = {}
    tunnel["source_peer"] = f"PrfTest_{i:04d}{j}"
    tunnel["source_ip"] = ""
    tunnel["psk"] = "your-psk-value"
    tunnel["esp"] = "aes128-sha1-sha256-sha384-sha512-modp2048-modp3072-modp4096-modp8192-ecp256-ecp384-ecp521,aes128-sha1-sha256-sha384-sha512"
    tunnel["bandwidth"] = "50"
    tunnel["rekey"] = "no"
    tunnel["reauth"] = "no"
    tunnel["nat_enabled"] = False
    tunnel["qos_enabled"] = False
    tunnel["link_id"] = 0
    tunnel["primary_pop_name"] = "qa01-dp-npe"
    tunnel["secondary_pop_name"] = "qa01"
    d["tunnel_details"][str(i)] = tunnel
    d["pop_details"]["qa01-dp-npe"].append(str(i))
    d["pop_details"]["qa01"].append(str(i))
  if not os.path.exists(f'/opt/ns/tenant/{j}/ipsecgw/'):
    print("creating directorty")
    os.makedirs(f'/opt/ns/tenant/{j}/ipsecgw/')
  with open(f'/opt/ns/tenant/{j}/ipsecgw/netskope.swanctl.json', 'w') as fp:
    print("directory alreade exists")
    json.dump(d, fp, indent=4)
