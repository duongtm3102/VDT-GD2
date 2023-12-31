from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client

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

servers = nova.servers.list()
print(servers)


nova.servers.create(name="testPy",
                    image="0b1a905e-d1b9-4be3-abe8-e5ad8cd45927",
                    flavor="2",
                    userdata=open("./test.sh", "r"),
                    nics=[{"net-id": "263c3ed0-6a54-47f1-b2ac-abcd64cc2ffd"}],
                    config_drive=True)