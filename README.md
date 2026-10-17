# Network SSH Tool

A beginner-friendly networking and remote-access learning project focused on understanding network diagnostics, IP configuration, connectivity testing, and Secure Shell (SSH).

## Overview

Network SSH Tool is a learning project designed to explore common networking commands and understand how SSH enables secure remote access to computers over a network.

The project starts with built-in Windows networking utilities and can be extended with Python automation and SSH functionality.

## Features

* **IP Configuration:** Inspect local network settings using `ipconfig`.
* **Connectivity Testing:** Test network reachability using `ping`.
* **DNS Lookup:** Resolve domain names using `nslookup`.
* **Network Route Tracing:** Examine network paths using `tracert`.
* **Network Connections:** Inspect connections and listening ports using `netstat`.
* **ARP Inspection:** View the local ARP cache using `arp -a`.
* **SSH Learning:** Understand secure remote connections, authentication, and SSH keys.
* **Python Integration:** Potential extension for automating networking commands.

> Note: These are the commands and learning objectives of the project. Python automation and SSH features should be implemented before describing them as built-in application features.

## Technologies Used

* Windows Command Prompt (CMD)
* PowerShell
* Git and GitHub
* Python (for planned automation)
* OpenSSH (for remote-access practice)

## Networking Commands

| Command                        | Description                                      |
| ------------------------------ | ------------------------------------------------ |
| `ipconfig`                     | Displays IP configuration                        |
| `ipconfig /all`                | Displays detailed network adapter information    |
| `ping 127.0.0.1`               | Tests the local TCP/IP networking stack          |
| `ping 8.8.8.8`                 | Tests connectivity to a public IP address        |
| `nslookup google.com`          | Queries DNS records                              |
| `tracert google.com`           | Traces the route to a destination                |
| `netstat -an`                  | Displays network endpoints and connection states |
| `arp -a`                       | Displays the ARP cache                           |
| `ssh username@host`            | Connects to a remote SSH server                  |
| `scp file.txt username@host:.` | Copies a file to a remote SSH account            |
| `sftp username@host`           | Starts an SSH file-transfer session              |

Some commands may require elevated privileges or a suitable network connection. Remote SSH commands also require an accessible SSH server and valid authentication.

## Getting Started

### Prerequisites

* A Windows computer
* Windows CMD or PowerShell
* Git installed
* Python 3 (if using Python components)
* OpenSSH Client for SSH practice
* OpenSSH Server on the target machine for incoming SSH connections

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/OneAbhik/Network_SSH_Tool.git
```

**2. Navigate to the project directory**

```bash
cd Network_SSH_Tool
```

**3. Inspect the project files**

```bash
dir
```

If a Python entry point such as `main.py` exists, follow the execution instructions documented for that file.

## Practicing SSH Locally

You can practice SSH without purchasing a separate network device by running an SSH server on your own computer.

For Windows, open PowerShell as Administrator and install the OpenSSH Server capability:

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
```

Start the service:

```powershell
Start-Service sshd
```

Check its status:

```powershell
Get-Service sshd
```

Connect to the local machine:

```bash
ssh your_username@localhost
```

Replace `your_username` with the account username on the computer hosting the SSH server.

Authentication depends on the account configuration and enabled SSH authentication methods. Your Windows Hello PIN is not necessarily your account password.

For additional configuration details, consult the official [Microsoft OpenSSH documentation](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse).

## Understanding SSH

SSH stands for **Secure Shell**. It is a protocol used to establish encrypted connections to remote systems.

Common SSH use cases include:

* Remote server administration
* Secure file transfers using SCP and SFTP
* Authentication using public and private key pairs
* Remote application deployment
* Secure tunneling and port forwarding

SSH typically uses TCP port `22`, although server administrators can configure a different port.

## Example Workflow

A basic networking investigation might follow these steps:

1. Run `ipconfig` to inspect local IP configuration.
2. Run `ping 127.0.0.1` to test the local networking stack.
3. Run `ping 8.8.8.8` to test reachability to an external IP address.
4. Run `nslookup google.com` to inspect DNS resolution.
5. Run `tracert google.com` to investigate the route to a destination.
6. Use SSH to connect to a server you are authorized to access.

A failed ping does not necessarily mean a host is offline because firewalls may block ICMP requests. Similarly, successful ping responses do not guarantee that SSH is available.

## Security Guidelines

* Only connect to systems you own or have permission to access.
* Never share or upload SSH private keys.
* Never commit passwords, API tokens, or other credentials to GitHub.
* Use SSH keys where appropriate and protect private keys with suitable permissions.
* Do not scan or probe networks without authorization.
* Review command output before sharing it publicly because it may contain internal IP addresses or other network information.

## Future Improvements

Potential enhancements include:

* A Python command-line interface
* Automated ping and DNS diagnostics
* IP address and hostname lookup utilities
* SSH connection management using Python libraries such as Paramiko
* Secure file transfer functionality
* Logging and error handling
* A menu-driven interface
* Cross-platform support for Windows and Linux

## Contributing

Contributions and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Implement and test your changes.
4. Submit a pull request describing your improvements.

## Author

**Abhik**

GitHub: [OneAbhik](https://github.com/OneAbhik)

## License

No license has been specified yet. Add a `LICENSE` file if you intend to allow others to reuse, modify, or distribute this project. Choose a license that matches your intended permissions.

---

*This project is intended for educational purposes and hands-on networking practice.*
