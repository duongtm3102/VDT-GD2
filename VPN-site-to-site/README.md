### VM1-VPC1

```bash

ip route add default via 192.168.1.173

```

![](images/Pasted%20image%2020230821102437.png)

### VPN-GW1

IP public 1 : 116.103.229.149

File `/etc/sysctl.conf`

```
net.ipv4.ip_forward = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
```

```
systcl -p
```

Cai dat strongswan

```bash
sudo apt install strongswan -y
```

Backup file config

```bash
cp /etc/ipsec.conf /etc/ipsec.conf.orig
```

Tao PSK

```
openssl rand -base64 64
```

/etc/ipsec.secrets

```bash
116.103.229.149 192.168.200.130 : PSK "secret"
```

ipsec.conf

```old
config setup
        charondebug="all"
        uniqueids=yes
conn gw1-gw2
        type=tunnel
        auto=start
        keyexchange=ikev2
        authby=secret
        left=116.103.229.149
        leftsubnet=192.168.1.0/24
        right=116.103.229.76
        rightsubnet=10.10.20.0/24
        ike=aes256-sha1-modp1024!
        esp=aes256-sha1!
        aggressive=no
        keyingtries=%forever
        ikelifetime=28800s
        lifetime=3600s
        dpddelay=30s
        dpdtimeout=120s
        dpdaction=restart
```

```bash
sudo ipsec restart
```

```bash
iptables -t nat -A POSTROUTING -s 10.10.20.0/24 -d 192.168.1.0/24 -j MASQUERADE
#check
iptables -t nat -L
```

```
# basic configuration
config setup
        charondebug="all"
        uniqueids=yes
        strictcrlpolicy=no

# connection gw1 gw2
conn gw1-gw2
	authby=secret
	left=%defaultroute
	leftid=116.103.229.149
	leftsubnet=192.168.1.0/24
	right=116.103.229.76
	rightsubnet=10.10.20.0/24
	ike=aes256-sha2_256-modp1024!
	esp=aes256-sha2_256!
	keyingtries=0
	ikelifetime=1h
	lifetime=8h
	dpddelay=30
	dpdtimeout=120
	dpdaction=restart
	auto=start
```

### VPN-GW2

IP public 1 : 116.103.229.76

/etc/ipsec.secrets

```bash
116.103.229.76 116.103.229.149 : PSK "secret"
```

ipsec.conf

```
config setup
        charondebug="all"
        uniqueids=yes
conn gw1-gw2
        type=tunnel
        auto=start
        keyexchange=ikev2
        authby=secret
        left=116.103.229.76
        leftsubnet=10.10.20.0/24
        right=116.103.229.149
        rightsubnet=192.168.1.0/24
        ike=aes256-sha1-modp1024!
        esp=aes256-sha1!
        aggressive=no
        keyingtries=%forever
        ikelifetime=28800s
        lifetime=3600s
        dpddelay=30s
        dpdtimeout=120s
        dpdaction=restart
```

```
ipsec restart
```

```bash
iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -d 10.10.20.0/24 -j MASQUERADE
```

https://sysadmins.co.za/setup-a-site-to-site-ipsec-vpn-with-strongswan-on-ubuntu/

![](images/Pasted%20image%2020230825080147.png)

## HA VPN S2S

```bash
apt-get install keepalived
```

### GW1

```bash
vrrp_sync_group G1 {
    group {
        VI_EXT
        VI_INT
    }
    notify "/usr/local/sbin/notify-ipsec.sh"
}

#External
vrrp_instance VI_EXT {
  state MASTER
  interface eth1
  virtual_router_id 50
  priority 150
  advert_int 1
  unicast_src_ip 192.168.1.173
  unicast_peer {
	192.168.1.186
  }
  authentication {
    auth_type PASS
    auth_pass mduong
  }
  virtual_ipaddress {
    116.103.227.2/23 dev eth2
  }
  nopreempt
  garp_master_delay 1
}

#Internal
vrrp_instance VI_INT {
  state MASTER
  interface eth1
  virtual_router_id 55
  priority 150
  advert_int 1
  unicast_src_ip 192.168.1.173
  unicast_peer {
	192.168.1.186
  }
  authentication {
    auth_type PASS
    auth_pass mduong
  }
  virtual_ipaddress {
    192.168.1.100/24 dev eth1
  }
  nopreempt
  garp_master_delay 1
}
```

## GW1 Backup

```bash
iptables -t nat -A POSTROUTING -s 10.10.20.0/24 -d 192.168.1.0/24 -j MASQUERADE
```

```bash
vrrp_sync_group G1 {
    group {
        VI_EXT
        VI_INT
    }
    notify "/usr/local/sbin/notify-ipsec.sh"
}

#External
vrrp_instance VI_EXT {
  state BACKUP
  interface eth1
  virtual_router_id 50
  priority 100
  advert_int 1
  unicast_src_ip 192.168.1.186
  unicast_peer {
	192.168.1.173
  }
  authentication {
    auth_type PASS
    auth_pass mduong
  }
  virtual_ipaddress {
    116.103.227.2/23 dev eth0
  }
  nopreempt
  garp_master_delay 1
}

#Internal
vrrp_instance VI_INT {
  state BACKUP
  interface eth1
  virtual_router_id 55
  priority 100
  advert_int 1
  unicast_src_ip 192.168.1.186
  unicast_peer {
	192.168.1.173
  }
  authentication {
    auth_type PASS
    auth_pass mduong
  }
  virtual_ipaddress {
    192.168.1.100/24 dev eth1
  }
  nopreempt
  garp_master_delay 1
}
```

![](images/Pasted%20image%2020230825083201.png)

```bash
# /etc/sysctl.conf
net.ipv4.ip_nonlocal_bind = 1
```

```
config setup
        charondebug="all"
        uniqueids=yes
conn gw1-gw2
        type=tunnel
        auto=start
        keyexchange=ikev2
        authby=secret
#        left=116.103.229.149
        left=116.103.227.2
        leftsubnet=192.168.1.0/24
        right=116.103.229.76
        rightsubnet=10.10.20.0/24
        ike=aes256-sha1-modp1024!
        esp=aes256-sha1!
        aggressive=no
        keyingtries=%forever
        ikelifetime=28800s
        lifetime=3600s
        dpddelay=30s
        dpdtimeout=120s
        dpdaction=restart

```

`/usr/local/sbin/notify-ipsec.sh`

```
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
```

https://serverfault.com/questions/653016/keepalived-configuration-for-vrrp
![](images/Pasted%20image%2020230825175741.png)
