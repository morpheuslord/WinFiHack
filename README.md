# WinFiHack

```bash
__        ___       _____ _ _   _            _
\ \      / (_)_ __ |  ___(_) | | | __ _  ___| | __
 \ \ /\ / /| | '_ \| |_  | | |_| |/ _` |/ __| |/ /
  \ V  V / | | | | |  _| | |  _  | (_| | (__|   <
   \_/\_/  |_|_| |_|_|   |_|_| |_|\__,_|\___|_|\_\
```

WinFiHack is an recreational attempt by me to rewrite my previous project [Brute-Hacking-Framework's](https://github.com/morpheuslord/Brute-Hacking-Framework-SourceCode) main wifi hacking script that uses netsh and native windows scripts to create a wifi bruteforcer. This is in no way a fast script nor a superior way of doing the same hack but its needs no external libraries and just python and python scripts.

## Installation

The packages are minimal or nearly none 😅. The package install command is:

```bash
pip install rich pyfiglet
```

Thats it.

## Features

So listing the features:

- _Overall Features:_
  - We can use custom interfaces or non-default interfaces to run the attack.
  - Well defined way on using netsh and listing and utilizing targets.
  - Upgradeabilty
- _Code-Wise Features:_
  - Interactive menu driven system with `rich`.
  - versitality in using of interface, targets, and password files.

## How it works

So this how the bruteforcer actually works:

```mermaid
sequenceDiagram
    participant User
    participant Tool
    participant Interface
    participant Network
    participant File
    participant Attack

    User->>Tool: Provide interface (default: Wi-Fi)
    Tool->>Interface: Disconnect all active network connections
    Interface->>Network: Search for all available networks
    User->>Tool: Set target network
    User->>Tool: Input password file (default: ./wordlist/default.txt)
    Note over Tool: Ready to run the attack
    Tool->>Attack: Begin password loop
    loop For each password
        Attack->>File: Generate and store custom XML
        Attack->>Network: Attempt connection
        Network->>Attack: Verify connection (1 packet ping to Google)
        alt Ping successful
            Attack->>User: Connection established (Success)
        else Ping failed
            Attack->>User: Output failed
        end
    end
```

- _Provide Interface:_

  - The user is required to provide the network interface for the tool to use.
  - By default, the interface is set to `Wi-Fi`.

- _Search and Set Target:_

  - The user must search for and select the target network.
  - During this process, the tool performs the following sub-steps:
    - Disconnects all active network connections for the selected interface.
    - Searches for all available networks within range.

- _Input Password File:_

  - The user inputs the path to the password file.
  - The default path for the password file is `./wordlist/default.txt`.

- _Run the Attack:_

  - With the target set and the password file ready, the tool is now prepared to initiate the attack.

- _Attack Procedure:_
  - The attack involves iterating through each password in the provided file.
  - For each password, the following steps are taken:
    - A custom XML configuration for the connection attempt is generated and stored.
    - The tool attempts to connect to the target network using the generated XML and the current password.
    - To verify the success of the connection attempt, the tool performs a "1 packet ping" to Google.
    - If the ping is unsuccessful, the connection attempt is considered failed, and the tool proceeds to the next password in the list.
    - This loop continues until a successful ping response is received, indicating a successful connection attempt.

## How to run this

After installing all the packages just run `python main.py` rest is history 👍 and make sure you run this on windows cause this wont work on any other OS.

## Contributions

For those who think this can be upgraded or made effetient make sure you fork this repo slap in your correction/improvement and create a PR and if its good I will correct and merge it.
