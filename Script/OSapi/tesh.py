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


def modify_vpn_variables(file_path, new_vpn_conn_name, new_vpn_left_ip):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        modified_lines = []
        for line in lines:
            if line.startswith("VPN_CONN_NAME="):
                modified_lines.append(f'VPN_CONN_NAME="{new_vpn_conn_name}"\n')
            elif line.startswith("VPN_LEFT_IP="):
                modified_lines.append(f'VPN_LEFT_IP="{new_vpn_left_ip}"\n')
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
new_vpn_conn_name = "new-gw1-gw2"
new_vpn_left_ip = "192.168.1.100"

modify_vpn_variables(file_path, new_vpn_conn_name, new_vpn_left_ip)

