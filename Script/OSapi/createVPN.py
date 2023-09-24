from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client
from neutronclient.v2_0 import client as nclient
VERSION = "2.1"
AUTH_URL = "http://116.103.227.31:5000"
USERNAME = 'admin'
PASSWORD = ""
PROJECT_ID = "56ca43b653c24437ab8c2889b1237d83"
USER_DOMAIN_NAME = 'Default'
PROJECT_DOMAIN_NAME = 'Default'
PUBLIC_NETWORK_ID = "d2b875b3-88a2-4bf8-a38b-07cffdd4dbab"
IMAGE_ID = "588da1e2-3d29-4752-be29-39e56b77422b"
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

    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        

def create_VPN(privateNetworkID, vpn_info, ike_policy, ipsec_policy):
    try:
        publicNetworkID = PUBLIC_NETWORK_ID
        portPublicInfo = {'name': "VPNpublicIP",'network_id': f"{publicNetworkID}",'admin_state_up': True, 'port_security_enabled': False} 
        portPrivateInfo = {'name': "VPNprivateIP",'network_id': f"{privateNetworkID}",'admin_state_up': True, 'port_security_enabled': False}

        portPublic = neutron.create_port({'port': portPublicInfo})
        portPrivate = neutron.create_port({'port': portPrivateInfo})

        print(f"Public IP: {portPublic['port']['fixed_ips'][0]['ip_address']}")
        print(f"Private IP: {portPrivate['port']['fixed_ips'][0]['ip_address']}")

        ha_info = {
            'publicVIP': f"{portPublic['port']['fixed_ips'][0]['ip_address']}",
            'privateVIP': f"{portPrivate['port']['fixed_ips'][0]['ip_address']}",
        }
        modify_vpn_variables("vpn.sh", ha_info, vpn_info, ike_policy, ipsec_policy)
        gw = nova.servers.create(name="VPNgateway",
                    image=IMAGE_ID,
                    flavor="2",
                    userdata=open("./vpn.sh", "r"),
                    nics=[{"port-id": f"{portPublic['port']['id']}"}, {"port-id": f"{portPrivate['port']['id']}"}],
                    config_drive=True)
        print("Gateway created!\n")

        #save ID of created ports/VMs
        resourceIDs = []
        resourceIDs.append(f"PORT={portPublic['port']['id']}\n")
        resourceIDs.append(f"PORT={portPrivate['port']['id']}\n")

        resourceIDs.append(f"INSTANCE={gw.id}\n")

        with open("resourceInfo", 'w') as file:
            file.writelines(resourceIDs)

    except Exception as e:
        print(f"An error occurred: {str(e)}")        
        

def create_HAVPN(privateNetworkID, vpn_info, ike_policy, ipsec_policy):
    try: 
        #create port for 2 instance and VIP port
        publicNetworkID = PUBLIC_NETWORK_ID
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
        
        print("Network ports created!")
        print(f"Public VIP: {portPublicVIP['port']['fixed_ips'][0]['ip_address']}")
        print(f"Private VIP: {portPrivateVIP['port']['fixed_ips'][0]['ip_address']}")

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
        modify_vpn_variables("havpn.sh", ha_info_master, vpn_info, ike_policy, ipsec_policy)
        gwMaster = nova.servers.create(name="gwMaster",
                            image=IMAGE_ID,
                            flavor="2",
                            userdata=open("./havpn.sh", "r"),
                            nics=[{"port-id": f"{portPublicA['port']['id']}"}, {"port-id": f"{portPrivateA['port']['id']}"}],
                            config_drive=True)
        print("Master GW created!\n")

        #create Backup gateway
        modify_vpn_variables("havpn.sh", ha_info_backup, vpn_info, ike_policy, ipsec_policy)
        gwBackup = nova.servers.create(name="gwBackup",
                            image=IMAGE_ID,
                            flavor="2",
                            userdata=open("./havpn.sh", "r"),
                            nics=[{"port-id": f"{portPublicB['port']['id']}"}, {"port-id": f"{portPrivateB['port']['id']}"}],
                            config_drive=True)
        print("Backup GW created!\n")

        #save ID of created ports/VMs
        resourceIDs = []
        resourceIDs.append(f"PORT={portPublicVIP['port']['id']}\n")
        resourceIDs.append(f"PORT={portPublicA['port']['id']}\n")
        resourceIDs.append(f"PORT={portPublicB['port']['id']}\n")
        resourceIDs.append(f"PORT={portPrivateVIP['port']['id']}\n")
        resourceIDs.append(f"PORT={portPrivateA['port']['id']}\n")
        resourceIDs.append(f"PORT={portPrivateB['port']['id']}\n")

        resourceIDs.append(f"INSTANCE={gwMaster.id}\n")
        resourceIDs.append(f"INSTANCE={gwBackup.id}\n")

        with open("resourceInfo", 'w') as file:
            file.writelines(resourceIDs)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

        
def delete_VPN():
    try:
        instances = []
        ports = []
        with open("resourceInfo", 'r') as file:
            lines = file.readlines()

        for line in lines:
            if line.startswith('PORT='):
                port_id = line.strip().split('=')[1]
                ports.append(port_id)
            elif line.startswith('INSTANCE='):
                instance_id = line.strip().split('=')[1]
                instances.append(instance_id)

        for instance_id in instances:
            nova.servers.delete(f"{instance_id}")
            print(f"Instance {instance_id} deleted\n")

        for port_id in ports:
            neutron.delete_port(f"{port_id}")
            print(f"Port {port_id} deleted\n")

    except Exception as e:
        print(f"An error occurred: {str(e)}")    

vpn_info = {'connName': 'gw-gw',
            'leftSubnet': '192.168.10.0/24',
            'rightIP': '10.10.10.190',
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
privateNetworkID="cd907a3a-6b3a-46cb-b181-e7192fe5bfe7"
# create_HAVPN(privateNetworkID, vpn_info, ike_policy, ipsec_policy)

# create_VPN(privateNetworkID, vpn_info, ike_policy, ipsec_policy)
  
delete_VPN()