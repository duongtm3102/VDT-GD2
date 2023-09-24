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
servers = nova.servers.list()
networks = neutron.list_networks()
# ports = neutron.list_ports(network_id='263c3ed0-6a54-47f1-b2ac-abcd64cc2ffd')
print(servers)
# print(networks)
# print(ports)
nova.servers.create(name="testPy",
                    image="3ebbfd02-969c-4e48-b995-d7e4058b9db2",
                    flavor="2",
                    nics=[{"net-id": "d2b875b3-88a2-4bf8-a38b-07cffdd4dbab"}])

# vm1 = nova.servers.create(name="testCirros",
#                     image="efde7b43-0c4e-4c95-b53e-6fe5b9e9eb2e",
#                     flavor="1",
#                     nics=[{"net-id": "0ff6f2ab-fe02-4042-ad22-be7013f26383"}]
#                     )
# print(vm1.id)

# vm1del=nova.servers.delete("522617f6-c353-4917-92b5-b2f0476756bb")
# print(vm1del)

# port = {'name': "port5",'network_id': "263c3ed0-6a54-47f1-b2ac-abcd64cc2ffd",'admin_state_up': True, 'port_security_enabled': False}
# out = neutron.create_port({'port':port})
# print(out['port']['id'])
# print(out['port']['fixed_ips'][0]['ip_address'])

# portInfo = 'port4'
# outInfo = neutron.show_port(f'?name={portInfo}')
# print(outInfo['ports'][0]['id'])
# port = {'id': "da908eb4-d2f7-4393-958b-9287fb28962c"}
# delPort = neutron.delete_port("da908eb4-d2f7-4393-958b-9287fb28962c")
# print(delPort)