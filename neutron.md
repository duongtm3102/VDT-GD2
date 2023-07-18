## Table of Contents

- [1. Giới thiệu](#1-gi%E1%BB%9Bi-thi%E1%BB%87u)
- [2. Các khái niệm](#2-c%C3%A1c-kh%C3%A1i-ni%E1%BB%87m)
	- [Provider networks](#provider-networks)
	- [Routed provider networks](#routed-provider-networks)
	- [Self-service networks](#self-service-networks)
	- [Subnets](#subnets)
	- [Subnet pools](#subnet-pools)
	- [Ports](#ports)
	- [Routers](#routers)
	- [Security groups](#security-groups)
	- [Extensions](#extensions)
	- [DHCP](#dhcp)
	- [Metadata](#metadata)
	- [Linux Bridge](#linux-bridge)
	- [Open vSwitch](#open-vswitch)
	- [L3 Agent](#l3-agent)
	- [Network namespaces](#network-namespaces)
	- [TAP device](#tap-device)
	- [Veth pair](#veth-pair)
	- [Overlay (tunnel) protocols](#overlay-tunnel-protocols)
		- [Generic routing encapsulation (GRE)](#generic-routing-encapsulation-gre)
		- [Virtual extensible local area network (VXLAN)](#virtual-extensible-local-area-network-vxlan)


# Openstack Networking - Neutron

_OpenStack Networking - Neutron là một project nhằm cung cấp "Networking-as-a-Service" giữa các interface device (ví dụ: vNICs) quản lý bởi các dịch vụ Openstack khác._

### 1. Giới thiệu

Openstack Networking cho phép tạo và quản lý các đối tượng mạng (như network, subnet và port) mà các Openstack service khác có thể sử dụng. Các plug-in có thể được sử dụng để đáp ứng với những phần mềm và thiết bị mạng khác nhau, cung cấp tính linh hoạt cho kiến trúc và triển khai Openstack.

Networking service - Neutron - cung cấp một API giúp ta định nghĩa kết nối mạng và địa chỉ trong cloud. Networking service giúp người vận hành tận dụng các công nghệ mạng khác nhau để phù hợp với mạng cloud của họ. Networking service cũng cung cấp API cho việc cấu hình và quản lý nhiều dịch vụ mạng như L3 forwarding, NAT, firewall, VPN.

Các thành phần trong Neutron:

- API Server
  - Neutron API hỗ trợ mạng Layer 2 và IP Address Management (IPAM - quản lý địa chỉ IP), cũng như một extension cho cấu trúc router Layer 3 cho phép định tuyến giữa các networks Layer 2 và các gateway ra mạng ngoài. Openstack Networking cung cấp các plug-in cho phép tương tác với nhiều công nghệ thương mại và mã nguồn mở: router, switch, virtual switch, SDN controller.
- OpenStack Networking plug-in and agents
  - Cho phép gắn/gỡ các port, tạo network hoặc subnet, cấp địa chỉ IP. Các plug-in và agent sẽ khác nhau tuỳ thuộc vào nhà cung cấp và công nghệ sử dụng trong từng cloud. Tuy nhiên tại một thời điểm chỉ có thể sử dụng 1 plug-in.
- Messaging queue
  - Chấp nhận và định tuyến các RPC request giữa các agent. Message queue được dùng trong ML2 plug-in cho RPC giữa neutron server và các neutron agent chạy trên mỗi hypervisor, trong ML2 mechanism drivers cho Open vSwitch và Linux bridge.

### 2. Các khái niệm

#### Provider networks

Provider networks cung cấp kết nối layer 2 cho các instance với tuỳ chọn hỗ trợ cho DHCP và các dịch vụ metadata. Các network này kết nối tới các network layer có sẵn tại data center, thường dùng VLAN tagging để định danh và phân biệt chúng.

Provider network cung cấp sự đơn giản, hiệu quả và tin cậy với chi phí linh hoạt. Mặc định, chỉ các quản trị viên mới có quyền tạo và sửa các provider network vì chúng yêu cầu cấu hình hạ tầng vật lý.

Provider network chỉ quản lý kết nối layer 2 cho các instance, thiếu các tính năng như các router và gán floating IP.

#### Routed provider networks

Routed provider networks cung cấp kết nối layer 3 cho các instance. Cụ thể, network này map tới nhiều layer 2 segment, mỗi segment là một provider network. Mỗi provider network được gán với một router gateway cho phép định tuyến traffic giữa chúng với nhau và với mạng ngoài.

Routed provider networks nhìn chung có hiệu suất thấp hơn provider network.

#### Self-service networks

Dạng network thường được dùng trong các project thông thường để quản lý mạng mà không cần quản trị viên. Các network này hoàn toàn là ảo và cần có các router ảo để giao tiếp với provider network và mạng bên ngoài. Self-service networks cũng cung cấp dịch vụ DHCP và metadata.

Trong đa số trường hợp, Self-service networks sử dụng các giao thức như VXLAN và GRE.

IPv4 self-service networks thường dùng dải địa chỉ private IP (RFC1918) và tương tác với provider network thông qua NAT trên các router ảo. Floating IP có thể được dùng để kết nối tới instance từ provider network. Mặt khác, IPv6 self-service networks luôn dùng dải địa chỉ IP public và giao tiếp với các provider network thông qua các router ảo bằng định tuyến tĩnh.

Self-service networks phải đi qua layer 3 agent nên nếu một node hay 1 agent bị lỗi thì có thể ảnh hưởng tới nhiều instance sử dụng chúng.

Neutron hỗ trợ các công nghệ network isolation và overlay như sau:

- **Flat**
  - Tất cả các instance đều nằm trên 1 mạng, có thể được chia sẻ với các host.
- **VLAN**

  - Cho phép người dùng tạo nhiều provider/project network sử dụng VLAN IDs (802.1Q tagged) tương ứng với VLANs trong mạng vật lý. Điều này cho phép các instance giao tiếp với nhau qua môi trường cloud. Chúng cũng có thể giao tiếp với các server, firewall và các hạ tầng mạng khác trên cùng Layer 2 VLAN.

- **GRE và VXLAN**
  - GRE và VXLAN là các giao thức đóng gói dùng để tạo các network overlay để kích hoạt và kiểm soát giao tiếp giữa các instance. Cần một router để cho phép traffic được đi ra bên ngoài GRE/VXLAN project network. Router cung cấp khả năng để kết nối tới instance trực tiếp từ mạng ngoài sử dụng floating IP.

#### Subnets

Là một khối các địa chỉ IP đã được cấu hình. Subnet được dùng để cấp phát địa chỉ IP khi các port mới được tạo trên network.

#### Subnet pools

Subnet pools dùng để ràng buộc những địa chỉ nào có thể được dùng khi tạo subnet. Khi này mỗi subnet phải nằm trong một pool được định nghĩa trước. Subnet pools cũng giúp tránh địa chỉ bị trùng lặp bởi 2 subnet trong cùng 1 pool.

#### Ports

Một Port là 1 điểm kết nối cho 1 thiết bị, như là NIC của server/mạng ảo. Port cũng mô tả cấu hình mạng liên quan như địa chỉ MAC, IP được dùng trên port đó.

#### Routers

Router cung cấp dịch vụ layer 3 ảo như định tuyến và NAT giữa mạng self-service và mạng provider hoặc giữa các mạng self-service thuộc 1 project. Neutron dùng 1 layer 3 agent để quản lý các router thông qua namespace.

#### Security groups

Cung cấp một container cho các firewall rule ảo để kiểm soát các lưu lượng ingress và egress. Security groups hoạt động ở mức port. Mỗi port có thể gắn với một hoặc nhiều security groups.
Mỗi project sẽ có 1 security groups mặc định là default. `Default` cho phép mọi egress traffic và chặn mọi ingress traffic.

#### Extensions

Neutron có khả năng mở rộng. Các Extension phục vụ 2 mục đích: giúp cung cấp tính năng mới trong API mà không cần nâng cấp phiên bản và giúp các nhà cung cấp bổ sung các chức năng phù hợp.

#### DHCP

Quản lý các địa chỉ IP cho các instance trong mạng self-service mà mạng provider. Dịch vụ DHCP trong Neutron sử dụng 1 agent quản lý các `qdhcp` namespace và dịch vụ `dnsmasq`.

#### Metadata

Dịch vụ metadata cung cấp một API cho instance lấy metadata (ví dụ: SSH key).

#### Linux Bridge

Là công nghệ cung cấp switch ảo trong hệ thống Linux.
Linux bridge sẽ tạo ra các switch layer 2 kết nối các máy ảo (VM) để các VM đó giao tiếp được với nhau và có thể kết nối được ra mạng ngoài. Linux bridge thường sử dụng kết hợp với hệ thống ảo hóa KVM-QEMU.

#### Open vSwitch

OpenvSwitch (OVS) là công nghệ switch ảo hỗ trợ SDN (Software-Defined Network), thay thế Linux bridge. OVS cung cấp chuyển mạch trong mạng ảo hỗ trợ các tiêu chuẩn Netflow, OpenFlow, sFlow. OpenvSwitch cũng được tích hợp với các switch vật lý sử dụng các tính năng lớp 2 như STP, LACP, 802.1Q VLAN tagging. OVS tunneling cũng được hỗ trợ để triển khai các mô hình network overlay như VXLAN, GRE.

#### L3 Agent

L3 agent là một phần của package openstack-neutron. Nó được xem như router layer3 chuyển hướng lưu lượng và cung cấp dịch vụ gateway cho network lớp 2. Các nodes chạy L3 agent không được cấu hình IP trực tiếp trên một card mạng mà được kết nối với mạng ngoài. Thay vì thế, sẽ có một dải địa chỉ IP từ mạng ngoài được sử dụng cho OpenStack networking. Các địa chỉ này được gán cho các routers mà cung cấp liên kết giữa mạng trong và mạng ngoài. Miền địa chỉ được lựa chọn phải đủ lớn để cung cấp địa chỉ IP duy nhất cho mỗi router khi triển khai cũng như mỗi floating IP gán cho các máy ảo.

DHCP Agent: OpenStack Networking DHCP agent chịu trách nhiệm cấp phát các địa chỉ IP cho các máy ảo chạy trên network. Nếu agent được kích hoạt và đang hoạt động khi một subnet được tạo, subnet đó mặc định sẽ được kích hoạt DHCP.
Plugin Agent: Nhiều networking plug-ins được sử dụng cho agent của chúng, bao gồm OVS và Linux bridge. Các plug-in chỉ định agent chạy trên các node đang quản lý lưu lượng mạng, bao gồm các compute node, cũng như các nodes chạy các agent

#### Network namespaces
cho phép cô lập môi trường mạng network trong một host
- Namespace phân chia việc sử dụng các khác niệm liên quan tới network như devices, địa chỉ addresses, ports, định tuyến và các quy tắc tường lửa vào trong một hộp (box) riêng biệt, chủ yếu là ảo hóa mạng trong một máy chạy một kernel duy nhất.
- Mỗi network namespaces có bản định tuyến riêng, các thiết lập iptables riêng cung cấp cơ chế NAT và lọc đối với các máy ảo thuộc namespace đó. Linux network namespaces cũng cung cấp thêm khả năng để chạy các tiến trình riêng biệt trong nội bộ mỗi namespace.
- Namespaces là tính năng của Linux kernel để cô lập và ảo hóa tài nguyên hệ thống. Network namespaces ảo hóa mạng. Trên mỗi network namespaces chứa duy nhất 1 loopback interface.  
- Mỗi network interface (physical hoặc virtual) có duy nhất 1 namespaces và có thể di chuyển giữa các namespaces.  
- Mỗi namespaces có 1 bộ địa chỉ IP, bảng routing, danh sách socket, firewall và các nguồn tài nguyên mạng riêng.  
- Khi network namespaces bị hủy, nó sẽ hủy tất cả các virtual interfaces nào bên trong nó và di chuyển bất kỳ physical interfaces nào trở lại network namespaces root.

#### TAP device
Kernel virtual network devices. Mô phỏng thiết bị link layer: truyền và nhận Ethernet frame.
TAP device gắn với user space program.
Có thể hiểu là giao diện mạng để các VM kết nối với bridge do linux bridge tạo ra

#### Veth pair
virtual Ethernet Devices. Là tunnel giữa 2 network namespaces.  Các lưu lượng tới từ một đầu veth và được đưa ra, peer tới giao diện veth còn lại.

#### Overlay (tunnel) protocols

Cơ chế giúp truyền dữ liệu giữa các mạng không tương thích với nhau (khác protocols). Nó cho phép người dùng có quyền truy cập tới các network bị chặn hoặc không an toàn.

##### Generic routing encapsulation (GRE)

Generic routing encapsulation (GRE) là giao thức chạy trên IP, sử dụng khi các giao thức truyền và payload tương thích nhưng địa chỉ payload không tương thích. Ví dụ: 1 payload nghĩ rằng nó đang chạy trên datalink layer nhưng thực ra nó đang chạy trên transport layer sử dụng giao thức datagram thông qua IP. GRE tạo kết nối private point-to-point và hoạt động bằng cách đóng gói payload.
GRE là giao thức nền tảng cho các giao thức tunnel khác nhưng GRE tunnel chỉ cung cấp xác thực yếu.

##### Virtual extensible local area network (VXLAN)

Mục đích của VXLAN là cung cấp scalable network isolation. VXLAN là " Layer 2 overlay scheme on a Layer 3 network". 
