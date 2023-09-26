from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client
from neutronclient.v2_0 import client as nclient
from cinderclient import client as cclient
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
cinder = cclient.Client(3, session=sess)
servers = nova.servers.list()
networks = neutron.list_networks()
volumes = cinder.volumes.list()
# ports = neutron.list_ports(network_id='263c3ed0-6a54-47f1-b2ac-abcd64cc2ffd')
print(volumes)
# print(networks)
# print(ports)


try:
    volume1 = cinder.volumes.create(name="vol1",
                                imageRef="462d75d9-026f-404d-a344-e5f584dd5172", 
                                size = 1)
    print(volume1.id)
    volId=volume1.id
    volBootable = False
    while not volBootable:
        volInfo = cinder.volumes.get(f"{volId}")
        volBootable = False if volInfo.bootable == "false" else True
    else:
        vm1 = nova.servers.create(name="testCirros",
                        image="",
                        block_device_mapping_v2=[{'uuid': f'{volId}', 'boot_index': '0', 'source_type': 'volume', 'destination_type': 'volume'}],
                        flavor="1",
                        nics=[{"net-id": "cd907a3a-6b3a-46cb-b181-e7192fe5bfe7"}])
        print(vm1.id)

except Exception as e:
        print(f"An error occurred: {str(e)}")


# volume1 = cinder.volumes.create(name="testVol",
#                                 imageRef="462d75d9-026f-404d-a344-e5f584dd5172", 
#                                 size = 1)

# print(volume1)
# volume=
# 'block_device_mapping_v2': [{'uuid': 'ea3497f7-d2cc-4a8e-af5a-f7fb675f1ac5', 'boot_index': '0', 'source_type': 'volume', 'destination_type': 'volume'}]
# nova.servers.create(name="testPy",
# vm1 = nova.servers.create(name="testCirros",
#                     image="",
#                     block_device_mapping_v2=[{'uuid': '8c5626eb-98e1-4fa7-a978-e20823a5bde8', 'boot_index': '0', 'source_type': 'volume', 'destination_type': 'volume'}],
#                     flavor="1",
#                     nics=[{"net-id": "cd907a3a-6b3a-46cb-b181-e7192fe5bfe7"}]
#                     )
# print(vm1.id)

# cinder.volumes.delete("8c5626eb-98e1-4fa7-a978-e20823a5bde8")