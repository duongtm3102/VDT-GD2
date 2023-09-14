# import fileinput

# def modify_vpn_conn_name_and_left_ip(file_path, vpn_conn_name, vpn_left_ip):
#     for line in fileinput.input(file_path, inplace=True):
#         if line.startswith('VPN_CONN_NAME='):
#             print(f'VPN_CONN_NAME="{vpn_conn_name}"')
#         elif line.startswith('VPN_LEFT_IP='):
#             print(f'VPN_LEFT_IP="{vpn_left_ip}"')
#         else:
#             print(line.rstrip())

# modify_vpn_conn_name_and_left_ip('test.sh', 'new-gw1-gw2', '192.168.10.1')


def modify_vpn_variables(file_path, ha_info, vpn_info, ike_policy, ipsec_policy):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        modified_lines = []
        for line in lines:
            if line.startswith("HA_STATE="):
                modified_lines.append(f'HA_STATE="{ha_info["state"]}"\n')
            elif line.startswith("HA_PASS="):
                modified_lines.append(f'HA_PASS="{ha_info["pass"]}"\n')
            elif line.startswith("HA_PUBLIC_VIP="):
                modified_lines.append(f'HA_PUBLIC_VIP="{ha_info["publicVIP"]}"\n')
            elif line.startswith("HA_PRIVATE_VIP="):
                modified_lines.append(f'HA_PRIVATE_VIP="{ha_info["privateVIP"]}"\n')
            elif line.startswith("HA_SRC_IP="):
                modified_lines.append(f'HA_SRC_IP="{ha_info["srcIP"]}"\n')
            elif line.startswith("HA_PEER_IP="):
                modified_lines.append(f'HA_PEER_IP="{ha_info["peerIP"]}"\n')
            elif line.startswith("VPN_CONN_NAME="):
                modified_lines.append(f'VPN_CONN_NAME="{vpn_info["connName"]}"\n')
            elif line.startswith("VPN_LEFT_SUBNET="):
                modified_lines.append(f'VPN_LEFT_SUBNET="{vpn_info["leftSubnet"]}"\n')
            elif line.startswith("VPN_RIGHT_IP="):
                modified_lines.append(f'VPN_RIGHT_IP="{vpn_info["rightIP"]}"\n')
            elif line.startswith("VPN_RIGHT_SUBNET="):
                modified_lines.append(f'VPN_RIGHT_SUBNET="{vpn_info["rightSubnet"]}"\n')
            elif line.startswith("VPN_PSK="):
                modified_lines.append(f'VPN_PSK="{vpn_info["psk"]}"\n')
            elif line.startswith("IKE_VERSION="):
                modified_lines.append(f'IKE_VERSION="{ike_policy["version"]}"\n')
            elif line.startswith("IKE_ENCRYPTION="):
                modified_lines.append(f'IKE_ENCRYPTION="{ike_policy["encryption"]}"\n')
            elif line.startswith("IKE_AUTHENTICATION="):
                modified_lines.append(f'IKE_AUTHENTICATION="{ike_policy["authentication"]}"\n')                                                                
            elif line.startswith("IKE_DHGROUP="):
                modified_lines.append(f'IKE_DHGROUP="{ike_policy["dhgroup"]}"\n') 
            elif line.startswith("IKE_LIFETIME="):
                modified_lines.append(f'IKE_LIFETIME="{ike_policy["lifetime"]}"\n') 
            elif line.startswith("IPSEC_ENCRYPTION="):
                modified_lines.append(f'IPSEC_ENCRYPTION="{ipsec_policy["encryption"]}"\n') 
            elif line.startswith("IPSEC_AUTHENTICATION="):
                modified_lines.append(f'IPSEC_AUTHENTICATION="{ipsec_policy["authentication"]}"\n') 
            elif line.startswith("IPSEC_PROTOCOL="):
                modified_lines.append(f'IPSEC_PROTOCOL="{ipsec_policy["protocol"]}"\n')
            elif line.startswith("IPSEC_LIFETIME="):
                modified_lines.append(f'IPSEC_LIFETIME="{ipsec_policy["lifetime"]}"\n')                 
            else:
                modified_lines.append(line)

        with open(file_path, 'w') as file:
            file.writelines(modified_lines)

        print(f"Modified {file_path} successfully.")
    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Sử dụng hàm để thay đổi giá trị của biến
file_path = "test.sh"

ha_info = {'state': 'MASTER',
           'pass': 'abc123',
           'publicVIP': '10.0.0.62',
           'privateVIP': '192.168.10.160',
           'srcIP': '192.168.10.170',
           'peerIP': '192.168.10.180'
}
vpn_info = {'connName': 'gw-gw',
            'leftSubnet': '192.168.20.0/24',
            'rightIP': '10.0.0.100',
            'rightSubnet': '192.168.30.0/24',
            'psk': "4PXq1pNugWnXtFR3UYNHOXjM1xp6nJFDyP9ghAeuFe9oLOzRSL7fhX4XmUZn9QJPPfaHUP9McEKZPSxEnDoJGQ=="
}
ike_policy = {'version': 'ikev2',
              'encryption': 'aes256',
              'authentication': 'sha1',
              'dhgroup': 'modp1024',
              'lifetime': '28800'    
}
ipsec_policy = {'encryption': 'aes256',
                'authentication': 'sha1',
                'protocol': 'esp',
                'lifetime': '3600' 
    
}
modify_vpn_variables(file_path, ha_info, vpn_info, ike_policy, ipsec_policy)

