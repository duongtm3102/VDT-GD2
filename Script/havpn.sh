#!/bin/bash

HA_STATE="MASTER"
HA_PASS="abc123"
HA_PUBLIC_VIP="10.0.0.62"
HA_PRIVATE_VIP="192.168.10.85"
HA_SRC_IP="192.168.10.174"
HA_PEER_IP="192.168.10.253"
HA_PEER_INTERFACE=$(ip route get $HA_PEER_IP | sed -nr 's/.*dev ([^\ ]+).*/\1/p')
HA_PUBLIC_INTERFACE=$(ip route get $HA_PUBLIC_VIP | sed -nr 's/.*dev ([^\ ]+).*/\1/p')
HA_PRIVATE_INTERFACE=$(ip route get $HA_PRIVATE_VIP | sed -nr 's/.*dev ([^\ ]+).*/\1/p')

VPN_CONN_NAME="gw1-gw2"
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

# install keepalived
apt-get install keepalived -y

cat <<EOF > /etc/keepalived/keepalived.conf
vrrp_sync_group G1 {
    group {
        VI_EXT
        VI_INT
    }
    notify "/usr/local/sbin/notify-ipsec.sh"
}

#External
vrrp_instance VI_EXT {
  state $HA_STATE
  interface $HA_PEER_INTERFACE
  virtual_router_id 50
  priority 150
  advert_int 1
  unicast_src_ip $HA_SRC_IP
  unicast_peer {
	$HA_PEER_IP
  }
  authentication {
    auth_type PASS
    auth_pass $HA_PASS
  }
  virtual_ipaddress {
    $HA_PUBLIC_VIP dev $HA_PUBLIC_INTERFACE
  }
  nopreempt
  garp_master_delay 1
}

#Internal
vrrp_instance VI_INT {
  state $HA_STATE
  interface $HA_PEER_INTERFACE
  virtual_router_id 55
  advert_int 1
  unicast_src_ip $HA_SRC_IP
  unicast_peer {
	$HA_PEER_IP
  }
  authentication {
    auth_type PASS
    auth_pass $HA_PASS
  }
  virtual_ipaddress {
    $HA_PRIVATE_VIP dev $HA_PRIVATE_INTERFACE
  }
  nopreempt  
  garp_master_delay 1
}
EOF

cat <<\EOF > /usr/local/sbin/notify-ipsec.sh
#!/bin/bash
TYPE=$1
NAME=$2
STATE=$3
case $STATE in
        "MASTER") /usr/sbin/ipsec restart
				  exit 0	
                  ;;
        "BACKUP") /usr/sbin/ipsec stop
				  exit 0
                  ;;
        "FAULT")  /usr/sbin/ipsec stop
                  exit 0
                  ;;
        *)        /usr/bin/logger "ipsec unknown state"
                  exit 1
                  ;;
esac
EOF

systemctl restart keepalived.service


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
        ikelifetime=$IKE_LIFETIME\s
        lifetime=$IPSEC_LIFETIME\s
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