#!/bin/bash

HA_PUBLIC_VIP="10.0.0.43"
HA_PRIVATE_VIP="192.168.10.135"

VPN_CONN_NAME="gw-gw"
VPN_LEFT_IP=$HA_PUBLIC_VIP
VPN_LEFT_SUBNET="192.168.10.0/24"
VPN_RIGHT_IP="10.0.0.82"
VPN_RIGHT_SUBNET="192.168.20.0/24"
VPN_PSK="4PXq1pNugWnXtFR3UYNHOXjM1xp6nJFDyP9ghAeuFe9oLOzRSL7fhX4XmUZn9QJPPfaHUP9McEKZPSxEnDoJGQ=="

IKE_VERSION="ikev2"
IKE_ENCRYPTION="aes256"
IKE_AUTHENTICATION="sha1"
IKE_DHGROUP="modp1024"
IKE_LIFETIME="28800"

IPSEC_ENCRYPTION="aes256"
IPSEC_AUTHENTICATION="sha1"
IPSEC_PROTOCOL="esp"
IPSEC_LIFETIME="3600"


#allow port forwarding
cat <<EOF > /etc/sysctl.conf 
net.ipv4.ip_forward = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
EOF

sysctl -p

#install strongswan
apt install strongswan -y

# save old ipsec config
cp /etc/ipsec.conf /etc/ipsec.conf.orig

# new ipsec config
cat <<EOF > /etc/ipsec.conf
config setup
        charondebug="all"
        uniqueids=yes
conn $VPN_CONN_NAME
        type=tunnel
        auto=start
        keyexchange=$IKE_VERSION
        authby=secret
        left=$VPN_LEFT_IP
        leftsubnet=$VPN_LEFT_SUBNET
        right=$VPN_RIGHT_IP
        rightsubnet=$VPN_RIGHT_SUBNET 
        ike=$IKE_ENCRYPTION-$IKE_AUTHENTICATION-$IKE_DHGROUP!
        $IPSEC_PROTOCOL=$IPSEC_ENCRYPTION-$IPSEC_AUTHENTICATION!
        aggressive=no
        keyingtries=%forever
        ikelifetime=${IKE_LIFETIME}s
        lifetime=${IPSEC_LIFETIME}s
        dpddelay=30s
        dpdtimeout=120s
        dpdaction=restart

EOF

cat <<EOF >> /etc/ipsec.secrets
$VPN_LEFT_IP $VPN_RIGHT_IP : PSK "$VPN_PSK"

EOF

#restart ipsec tunnel
ipsec restart
#add firewall rule
iptables -t nat -A POSTROUTING -s $VPN_RIGHT_SUBNET -d $VPN_LEFT_SUBNET -j MASQUERADE