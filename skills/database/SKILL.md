name: Database
Description: This is to skill to find all the avaiable resources for our testing, including client machine both qa and production, our gateway ECGW/IPSEC/GRE and all our tenant which we use for our testing, this skill also responsbile for reserving the device is somebody wants. 

Device types
client.txt will have all the clients machines. 
gateway.txt will have all gateway which inlcudes, legacy gre/ipsec and vpp ipsec/gre gateway. 

Reservation: 
If somebody ask to reserve the deviec, give one of the devices. Please note if user ask for client then give from client.txt only and if users ask for some gatewaythen give it from dut.txt. The name of the gateway will define the type of gateway for example all vpp gatewat will have keyword so if somebody ask for vpp ipsec gateway then give any available device which has both vpp and ipsec keywork in host name for example, vppipsecgw01.c18.iad0.netskope.com. Similary if somebody asks for legacy gre gateway then find a deviec with gre keywork in hostame but it should not have vpp keyworkd for example nsgregw01.c18.iad0.netskope.com. example of legacy ipsec gateway ipsecgw01.iad0.netskope.com 

If somebody ask for both gateway and client then first find the gateway then find from which client that gateway ingress and vip is reachable and assign the clientaccodingly.(this is for future since you right now you don't have access to device to check this)


Production tenant. 
Used in PDV
https://apigw-gre-ipsec-dfw3-1.goskope.com/
API for above tenant 
your-api-token

QA Tenant
Personel use. 
https://your-username.qa.boomskope.com
API for above tenant
your-api-token

Clients
prod clients
your-prod-client.compute-1.amazonaws.com
