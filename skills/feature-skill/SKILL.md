name: feature-skill
description: This is skill to understand the features like health-check, ctap, qos and httpad over ipsec, gre and ecgw. 

First, we will descripe the health check feature. 
Its the functionality through which all the gateway keep track of status of downsteadm services proxy and cfw. 
these gateawy send the curl request over a port and ip of cfw and proxy mentiond in "/opt/ns/commont/remote/"
the command to check the healtcheck on all legacy gateway is nswatson.sh -p 3215 -c 'show stats http-healthcheck-utility' and on vpp based gateway is gw-cli healthchecksvc show runtime status
. In case of proxy we are only concern about the normal proxy health check. 
