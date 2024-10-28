from netmiko import ConnectHandler
from log import authLog
from functions import failedDevices, logInCSV, filterFilename

import traceback
import os

postValidationCommands = [
    'show interface description',
    'show ip int br',
    'show sdwan control local-properties',
    'show sdwan control connections',
    'show sdwan bfd sessions',
    'show endpoint-tracker',
    'show ip sla statistics',
    'show ip sla summary',
    'show interfaces',
    'show cdp neighbors'
]

shHostname = "show run | i hostname"

def postValidation(validIPs, username, netDevice, shCommand):
    # This function is to take a show run
    
    for validDeviceIP in validIPs:
        try:
            validDeviceIP = validDeviceIP.strip()
            currentNetDevice = {
                'device_type': 'cisco_xe',
                'ip': validDeviceIP,
                'username': username,
                'password': netDevice['password'],
                'secret': netDevice['secret'],
                'global_delay_factor': 2.0,
                'timeout': 120,
                'session_log': 'Outputs/netmikoLog.txt',
                'verbose': True,
                'session_log_file_mode': 'append'
            }

            print(f"INFO: Connecting to device {validDeviceIP}...")
            authLog.info(f"Connecting to device {validDeviceIP}")
            with ConnectHandler(**currentNetDevice) as sshAccess:
                try:
                    authLog.info(f"Connected to device: {validDeviceIP}")
                    sshAccess.enable()
                    shHostnameOut = sshAccess.send_command(shHostname)
                    authLog.info(f"User {username} successfully found the hostname {shHostnameOut} for device: {validDeviceIP}")
                    shHostnameOut = shHostnameOut.split(' ')[1]
                    shHostnameOut = shHostnameOut + "#"

                    authLog.info(f"Running the following commands: {postValidationCommands}")
                    print(f"INFO: Running command:{postValidationCommands}, on device {validDeviceIP}")
                    postValidationCommandsOut = sshAccess.send_config_set(postValidationCommands)
                    authLog.info(f"Automation successfully run the command: {postValidationCommands} on device: {validDeviceIP}")
                    authLog.info(f"{shHostnameOut}{postValidationCommands}\n{postValidationCommandsOut}")
                    print(f"INFO: Command successfully executed\n{shHostnameOut}{postValidationCommands}\n{postValidationCommandsOut}")

                    filename = filterFilename('Post Validation Commands')
                    authLog.info(f"This is the filename:{filename}")

                    with open(f"Outputs/{filename} for device {validDeviceIP}.txt", "a") as file:
                        file.write(f"User {username} connected to device IP {validDeviceIP}\n\n")
                        file.write(f"{shHostnameOut}\n{postValidationCommands}\n{postValidationCommandsOut}")
                        authLog.info(f"File:{file} successfully created")

                    print("INFO: Outputs and files successfully created.")
                    print("INFO: For any erros or logs please check authLog.txt in logs")

                except Exception as error:
                    print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
                    authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}")
                    authLog.error(traceback.format_exc(),"\n")
                    failedDevices(username,validDeviceIP,error)
                    
        except Exception as error:
            print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
            authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}")
            authLog.error(traceback.format_exc(),"\n")
            failedDevices(username,validDeviceIP,error)   