from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client
from neutronclient.v2_0 import client as nclient
VERSION = "2.1"
AUTH_URL = "http://116.103.226.54:35357/v3"
USERNAME = 'admin'
PASSWORD = "nZ0GYtYIjvzc3XDezQOQhUugDx6EweAOwsk9wHkF"
PROJECT_ID = "d9202c09602649de9b9d1775ac17c25e"
USER_DOMAIN_NAME = 'Default'
PROJECT_DOMAIN_NAME = 'Default'
loader = loading.get_plugin_loader('password')
auth = loader.load_from_options(auth_url=AUTH_URL,
                               username=USERNAME,
                                password=PASSWORD,
                                project_id=PROJECT_ID,
                                user_domain_name=USER_DOMAIN_NAME,
                                project_domain_name=PROJECT_DOMAIN_NAME)
sess = session.Session(auth=auth)
nova = client.Client(VERSION, session=sess)
neutron = nclient.Client(session=sess)



# function modify vpn.sh
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
        
        
        
def create_VPN(privateNetworkID, vpn_info, ike_policy, ipsec_policy):
    #create port for 2 instance and VIP port
    publicNetworkID = "263c3ed0-6a54-47f1-b2ac-abcd64cc2ffd"
    portPublicVIPInfo = {'name': "publicVIP",'network_id': f"{publicNetworkID}",'admin_state_up': True, 'port_security_enabled': False}
    portPublicAInfo = {'name': "publicA",'network_id': f"{publicNetworkID}",'admin_state_up': True, 'port_security_enabled': False}
    portPublicBInfo = {'name': "publicB",'network_id': f"{publicNetworkID}",'admin_state_up': True, 'port_security_enabled': False}
    
    portPrivateVIPInfo = {'name': "privateVIP",'network_id': f"{privateNetworkID}",'admin_state_up': True, 'port_security_enabled': False}
    portPrivateAInfo = {'name': "privateA",'network_id': f"{privateNetworkID}",'admin_state_up': True, 'port_security_enabled': False}
    portPrivateBInfo = {'name': "privateB",'network_id': f"{privateNetworkID}",'admin_state_up': True, 'port_security_enabled': False}
    
    portPublicVIP = neutron.create_port({'port': portPublicVIPInfo})
    portPublicA = neutron.create_port({'port': portPublicAInfo})
    portPublicB = neutron.create_port({'port': portPublicBInfo})
    
    portPrivateVIP = neutron.create_port({'port': portPrivateVIPInfo})
    portPrivateA = neutron.create_port({'port': portPrivateAInfo})
    portPrivateB = neutron.create_port({'port': portPrivateBInfo})
    
    ha_info_master = {
        'state': 'MASTER',
        'pass': 'abc123',
        'publicVIP': f"{portPublicVIP['port']['fixed_ips'][0]['ip_address']}",
        'privateVIP': f"{portPrivateVIP['port']['fixed_ips'][0]['ip_address']}",
        'srcIP': f"{portPrivateA['port']['fixed_ips'][0]['ip_address']}",
        'peerIP': f"{portPrivateB['port']['fixed_ips'][0]['ip_address']}"
    }
    
    ha_info_backup = {
        'state': 'BACKUP',
        'pass': 'abc123',
        'publicVIP': f"{portPublicVIP['port']['fixed_ips'][0]['ip_address']}",
        'privateVIP': f"{portPrivateVIP['port']['fixed_ips'][0]['ip_address']}",
        'srcIP': f"{portPrivateB['port']['fixed_ips'][0]['ip_address']}",
        'peerIP': f"{portPrivateA['port']['fixed_ips'][0]['ip_address']}"
    }
    
    #create Master gateway
    modify_vpn_variables("vpn.sh", ha_info_master, vpn_info, ike_policy, ipsec_policy)
    nova.servers.create(name="gwMaster",
                        image="0b1a905e-d1b9-4be3-abe8-e5ad8cd45927",
                        flavor="2",
                        userdata=open("./vpn.sh", "r"),
                        nics=[{"port-id": f"{portPublicA['port']['id']}"}, {"port-id": f"{portPrivateA['port']['id']}"}],
                        config_drive=True)
    
    #create Backup gateway
    modify_vpn_variables("vpn.sh", ha_info_backup, vpn_info, ike_policy, ipsec_policy)
    nova.servers.create(name="gwBackup",
                        image="0b1a905e-d1b9-4be3-abe8-e5ad8cd45927",
                        flavor="2",
                        userdata=open("./vpn.sh", "r"),
                        nics=[{"port-id": f"{portPublicB['port']['id']}"}, {"port-id": f"{portPrivateB['port']['id']}"}],
                        config_drive=True)
    
    
vpn_info = {'connName': 'gw-gw',
            'leftSubnet': '192.168.10.0/24',
            'rightIP': '10.0.0.82',
            'rightSubnet': '192.168.20.0/24',
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
privateNetworkID="0ff6f2ab-fe02-4042-ad22-be7013f26383"
create_VPN(privateNetworkID, vpn_info, ike_policy, ipsec_policy)