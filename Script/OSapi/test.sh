#!/bin/bash

VPN_CONN_NAME="new-gw1-gw2"
VPN_LEFT_IP="192.168.1.100"
VPN_LEFT_SUBNET="192.168.10.0/24"
VPN_RIGHT_IP="10.0.0.82"
VPN_RIGHT_SUBNET="192.168.20.0/24"
VPN_PSK="4PXq1pNugWnXtFR3UYNHOXjM1xp6nJFDyP9ghAeuFe9oLOzRSL7fhX4XmUZn9QJPPfaHUP9McEKZPSxEnDoJGQ=="

#allow port forwarding
cat <<EOF > /etc/sysctl.conf 
net.ipv4.ip_forward = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
EOF

cat <<EOF > /etc/sysctl.conf.test
net.ipv4.ip_forward = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
EOF