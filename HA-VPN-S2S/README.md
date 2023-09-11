# HA VPN Site to Site

- [1. Giới thiệu](#1-gi%E1%BB%9Bi-thi%E1%BB%87u)
	- [1.1. IPSec và VPN](#11-ipsec-v%C3%A0-vpn)
		- [IPSec là gì?](#ipsec-l%C3%A0-g%C3%AC)
		- [VPN, IPSec VPN là gì?](#vpn-ipsec-vpn-l%C3%A0-g%C3%AC)
	- [1.2. Strongswan](#12-strongswan)
- [2. Thực hành](#2-th%E1%BB%B1c-h%C3%A0nh)
	- [2.1. Mô hình](#21-m%C3%B4-h%C3%ACnh)
		- [IPSec Tunnel](#ipsec-tunnel)
		- [HA Gateway](#ha-gateway)
	- [2.2. Triển khai](#22-tri%E1%BB%83n-khai)
		- [2.2.1. HA Gateway 1](#221-ha-gateway-1)
		- [2.2.2. IPSec Tunnel](#222-ipsec-tunnel)
			- [Trên các `Gateway`](#tr%C3%AAn-c%C3%A1c-gateway)
			- [Trên Gateway1 ( thực hiện trên cả Master và Slave)](#tr%C3%AAn-gateway1--th%E1%BB%B1c-hi%E1%BB%87n-tr%C3%AAn-c%E1%BA%A3-master-v%C3%A0-slave)
			- [Trên Gateway 2](#tr%C3%AAn-gateway-2)
			- [Trên VM1 - VPC1](#tr%C3%AAn-vm1---vpc1)
			- [Trên VM2 VPC2](#tr%C3%AAn-vm2-vpc2)
		- [2.2.3. Test](#223-test)



## 1. Giới thiệu

### 1.1. IPSec và VPN 

#### IPSec là gì?

**IPsec** là một nhóm giao thức được sử dụng cùng nhau để thiết lập các kết nối được mã hóa giữa các thiết bị. Nó giúp bảo mật dữ liệu được gửi qua public network. Nhóm giao thức này này thường được sử dụng để thiết lập `VPN`. Nó hoạt động bằng cách mã hóa IP packet cùng với việc xác thực nguồn của các packet.

Trong thuật ngữ “IPsec”, “IP” là viết tắt của “Internet Protocol” và “sec” là “security”. Internet Protocol là một routing protocol chính được sử dụng trên Internet. Nó chỉ định nơi dữ liệu sẽ đi bằng địa chỉ IP. Nhóm giao thức này an toàn vì nó thêm mã hóa và xác thực vào quá trình này.

#### VPN, IPSec VPN là gì?

Virtual private network (VPN) là một kết nối được mã hóa giữa hai hoặc nhiều máy tính. Kết nối VPN diễn ra qua các public network, nhưng dữ liệu trao đổi qua VPN vẫn là riêng tư vì nó được mã hóa.

VPN giúp bạn có thể truy cập và trao đổi dữ liệu bí mật một cách an toàn qua cơ sở hạ tầng shared network. Ví dụ, khi nhân viên làm việc từ xa thay vì ở văn phòng, họ thường sử dụng VPN để truy cập các file và app của công ty.

Nhiều VPN sử dụng IPsec protocol để thiết lập và chạy các kết nối được mã hóa. 


[Tham khảo 1](https://www.cloudflare.com/learning/network-layer/what-is-ipsec/#:~:text=IPsec%20tunnel%20mode%20is%20used,addition%20to%20the%20packet%20payload.)

[Tham khảo 2](https://vietnix.vn/ipsec-la-gi/)

[Đọc thêm](https://networklessons.com/cisco/ccie-routing-switching/ipsec-internet-protocol-security)


### 1.2. Strongswan 

StrongSwan là một phần mềm mã nguồn mở cung cấp dịch vụ VPN (Virtual Private Network) dựa trên các giao thức mạng bảo mật tiêu chuẩn như IPsec (Internet Protocol Security) và IKEv2 (Internet Key Exchange version 2). Nó cho phép tạo ra các kết nối bảo mật qua mạng công cộng, cho phép truyền dữ liệu an toàn giữa các mạng và thiết bị khác nhau.

### 1.3. Keepalived

Keepalived là một phần mềm định tuyến, được viết bằng ngôn ngữ C. Chương trình keepalived cho phép nhiều máy tính cùng chia sẻ một địa chỉ IP ảo với nhau theo mô hình Active – Passive (ta có thể cấu hình thêm một chút để chuyển thành mô hình Active – Active).

Khi người dùng cần truy cập vào dịch vụ, người dùng chỉ cần truy cập vào địa chỉ IP ảo dùng chung này thay vì phải truy cập vào những địa chỉ IP thật của các thiết bị kia.

Một số đặc điểm của phần mềm Keepalived:

- Keepalived không đảm bảo tính ổn định của dịch vụ chạy trên máy chủ, nó chỉ đảm bảo rằng sẽ luôn có ít nhất một máy chủ chịu trách nhiệm cho IP dùng chung khi có sự cố xảy ra.
- Keepalived thường được dùng để dựng các hệ thống HA (High Availability) dùng nhiều router/firewall/server để đảm bảo hệ thống được hoạt động liên tục.
- Keepalived dùng giao thức _**VRRP (Virtual Router Redundancy Protocol)**_ để liên lạc giữa các thiết bị trong nhóm.

Các router vật lý sử dụng chung VIP phải liên lạc với nhau bằng địa chỉ multicast _**224.0.0.18**_ bằng giao thức VRRP. Các router vật lý sẽ có độ ưu tiên (priority) trong khoảng từ 1 – 254, và router có độ ưu tiên cao nhất sẽ thành Master, các router còn lại sẽ thành các Slave/Backup, hoạt động ở chế độ chờ.

Các router/server vật lý dùng chung VIP sẽ có 2 trạng thái là **MASTER/ACTIVE** và **BACKUP/SLAVE**. Cơ chế failover được xử lý bởi giao thức VRRP, khi khởi động dịch vụ, toàn bộ các server dùng chung VIP sẽ gia nhập vào một nhóm multicast. Nhóm multicast này dùng để gởi/nhận các gói tin quảng bá VRRP. Các router sẽ quảng bá độ ưu tiên (priority) của mình, server với độ ưu tiên cao nhất sẽ được chọn làm MASTER. Một khi nhóm đã có 1 MASTER thì MASTER này sẽ chịu trách nhiệm gởi các gói tin quảng bá VRRP định kỳ cho nhóm multicast.

Nếu vì một sự cố gì đó mà các server BACKUP không nhận được các gói tin quảng bá từ MASTER trong một khoảng thời gian nhất định thì cả nhóm sẽ bầu ra một MASTER mới. MASTER mới này sẽ tiếp quản địa chỉ VIP của nhóm và gởi các gói tin ARP báo là nó đang giữ địa chỉ VIP này. Khi MASTER cũ hoạt động bình thường trở lại thì router này có thể lại trở thành MASTER hoặc trở thành BACKUP tùy theo cấu hình độ ưu tiên của các router.
## 2. Thực hành

Tạo IPSec tunnel giữa 2 VPC `192.168.1.0/24` và `10.10.20.0/24` đảm bảo HA phía `Gateway 1`.

### 2.1. Mô hình
#### IPSec Tunnel

- `VPC 1`: 192.168.1.0/24
- `Gateway 1`: 
	- Public IP: 116.103.227.2 (virtual IP)
	- Private IP: 192.168.1.100 (virtual IP)

- `VPC 2`: 10.10.20.0/24
- `Gateway 2`:
	- Public IP: 116.103.229.76
	- Private IP: 10.10.20.204

`IPSec Tunnel` được tạo giữa 2 đầu Public IP của các Gateway.

![](images/model%20(1).png)

#### HA Gateway

Để đảm bảo HA phía Gateway 1, em sử dụng 2 VM là  `Master` và `Slave` chạy `Keepalived`. 
Mặc định các IP `116.103.227.2` và `192.168.1.100` được gắn vào `Master` để thiết lập `IPSec tunnel`.

Khi `Master` down, các IP trên sẽ được gán qua `Slave` và IPSec tunnel tự động được thiết lập lại.
 ![](images/model%20(2).png)

### 2.2. Triển khai

#### 2.2.1. HA Gateway 1

Trên `Master` và `Slave`, cài đặt Keepalived.

```bash
apt-get install keepalived
```

Trên `Master`, config file `/etc/keepalived/keepalived.conf`

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
  virtual_router_id 150
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
 
**Giải thích:**

- `vrrp_sync_group` : Nhóm các VRRP instance được đồng bộ, khi trạng thái 1 thành viên thay đổi, script `notify-ipsec.sh` sẽ được thực thi.
- `vrrp_instance` : các định nghĩa, cấu hình 1 keepalived instance.
- `state` : trạng thái ban đầu
- `interface` : chỉ định interface cho giao tiếp VRRP giữa các server.
- `virtual_router_id` : ID cho mỗi instance, ID này phải giống nhau trên các server (cùng vrrp instance).
- `priority` : độ ưu tiên cao hơn sẽ làm Master.
- `unicast_src_ip`: IP của máy nguồn.
- `unicast_peer`: IP của (các) máy *đối tác*.
- `authentication` : Cách xác thực.
- `virtual_ipaddress` : VIP và interface gán VIP.
- `nopreempt`: Khi `Master` up lại thì `Slave` vẫn sẽ giữ VIP( thay vì mặc định là chuyển lại cho `Master`).
- `garp_master_delay` : thời gian giữa các gói tin GARP (Gratuitous ARP) được gửi từ router MASTER.
	- *Note* : https://serverfault.com/questions/653016/keepalived-configuration-for-vrrp
	- ![](images/Pasted%20image%2020230825175741.png)


Trên `Slave`, config file `/etc/keepalived/keepalived.conf`

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


File `/usr/local/sbin/notify-ipsec.sh` dùng để bật/tắt IPSec process mỗi khi state keepalived thay đổi.
```bash
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

Khởi động lại service.

```bash
systemctl restart keepalived.service
```

Kiểm tra trên `Master`, ta thấy các IP đã được gán:
![](images/Pasted%20image%2020230828105602.png)

Stop keepalived trên `Master`, các IP sẽ được gán cho `Slave`:

![](images/Pasted%20image%2020230828105457.png)

#### 2.2.2. IPSec Tunnel


##### Trên các `Gateway`

**Allow address pair:**

Các VM có chức năng Port Security nên cần phải **Allow address pair** IP của VPC 2 trên interface private IP của VM Gateway 1 (và ngược lại)

**Cho phép IP forwarding:**

File `/etc/sysctl.conf`

```
net.ipv4.ip_forward = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
```

- Cấu hình đầu tiên cho phép chức năng chuyển tiếp gói tin IP giữa các giao diện mạng. GW giờ có chức năng như 1 router.
- Cấu hình 2 để GW không chấp nhận gói tin chuyển hướng.
- Cấu hình 3 để GW không gửi gói tin chuyển hướng tới máy khác.

```
systcl -p
```
![](images/Pasted%20image%2020230828110235.png)

**Cài đặt Strongswan**

```bash
apt install strongswan -y
```

**Backup file config**

```bash
cp /etc/ipsec.conf /etc/ipsec.conf.orig
```

**Tạo PSK dùng cho 2 phía**

```
openssl rand -base64 64
```


##### Trên Gateway1 ( thực hiện trên cả Master và Slave)

File `/etc/ipsec.conf`

```bash
config setup
        charondebug="all"
        uniqueids=yes
conn gw1-gw2
        type=tunnel
        auto=start
        keyexchange=ikev2
        authby=secret
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

**Giải thích:**
- **config setup** specifies general configuration information for IPSec which applies to all connections.
- **charondebug = “all”** defines how much Charon debugging output should be logged.
- **uniqueids = yes** states whether a particular participant ID should be kept unique.
- **conn gw1-gw2** is the connection name.
- **type=tunnel** is the type of connection.
- **auto=start** allows the connection to start by default.
- **keyexchange=ikev2** is the Internet key exchange version.
- **authby=secret** authenticated with secret.
- **left=116.103.227.2** is the public IP address of server A.
- **leftsubnet=192.168.1.0/24** is the subnet/private IP of server A.
- **right=116.103.229.76** is the public IP address of server B/remote server.
- **rightsubnet=10.10.20.0/24** is the subnet/private IP of server B.
- **ike=aes256-sha1-modp1024** is the type of encryption when the Internet key exchange.
- **ikelifetime=28800s** is the time before the re-authentication of keys.
- **esp=aes256-sha1!** is the encapsulation security suite of protocols.
- **aggressive** states whether to use Aggressive or Main Mode.
- **keyingtries** states the number of attempts that should be made to negotiate a connection.
- **lifetime** defines how long a particular instance of a connection should last, from successful negotiation to expiry.
- **dpddelay** specifies the time interval with which exchanges are sent to the peer.
- **dpdtimeout** specifies the timeout interval to delete connections in case of inactivity.
- **dpdaction** states how to use the Dead Peer Detection(DPD) protocol to manage the connection.

File `/etc/ipsec.secrets`

```bash
116.103.227.2 116.103.229.76 : PSK "key đã tạo ở trên"
```

Khởi động lại `ipsec` để nhận config:

```bash
ipsec restart
```

Thiết lập `firewall rule` :

```bash
iptables -t nat -A POSTROUTING -s 10.10.20.0/24 -d 192.168.1.0/24 -j MASQUERADE
```

##### Trên Gateway 2

File `/etc/ipsec.conf`

```bash
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
        right=116.103.227.2
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

File `/etc/ipsec.secrets`

```bash
116.103.229.76 116.103.227.2 : PSK "key đã tạo ở trên"
```

Khởi động lại `ipsec` để nhận config:

```bash
ipsec restart
```

Thiết lập `firewall rule` :

```bash
iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -d 10.10.20.0/24 -j MASQUERADE
```

##### Trên VM1 - VPC1

`IP`: 192.168.1.220

**Trỏ `default gateway` đến `192.168.1.100`**

File `/etc/netplan/01-netcfg.yaml`:
```bash
##
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: yes
    eth1:
      dhcp4: yes
      routes:
      - to: default
        via: 192.168.1.100
    eth2:
      dhcp4: yes
    eth3:
      dhcp4: yes
    eth4:
      dhcp4: yes
```

```bash
netplan apply
```

Kiểm tra route trên VM1:
![](images/Pasted%20image%2020230828111652.png)

##### Trên VM2 VPC2
`IP` : 10.10.20.15

**Trỏ `default gateway` đến `10.10.20.204`**

File `/etc/netplan/01-netcfg.yaml`:
```bash
##
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: yes
      routes:
       - to: default
         via: 10.10.20.204
    eth1:
      dhcp4: yes
    eth2:
      dhcp4: yes
    eth3:
      dhcp4: yes
    eth4:
      dhcp4: yes
```

```bash
netplan apply
```

Kiểm tra route trên VM2:
![](images/Pasted%20image%2020230828112227.png)

#### 2.2.3. Test
**Ping giữa 2 VM thuộc 2 VPC**

![](images/Pasted%20image%2020230828112635.png)

Có thể thấy 2 máy đã ping được với nhau.


**Test HA Gateway**

Thực hiện stop/start `keepalived` trên `Master` để IPSec Tunnel thiết lập lại. Trong lúc đó tiến hành ping giữa VM 1 và VM 2
![](images/Pasted%20image%2020230828112919.png)

![](images/Pasted%20image%2020230828112938.png)
**->** Mỗi lần IPSec Tunnel được thiết lập lại sẽ bị drop 2-3 gói tin.

## Note todo
- Đọc thêm về IPSec
- Hiểu properties trong các config.
- Tìm các cách tối ưu



https://sysadmins.co.za/setup-a-site-to-site-ipsec-vpn-with-strongswan-on-ubuntu/


