import sys
import re
import ipaddress
import platform
import subprocess

from netmiko import ConnectHandler
from netmiko.exceptions import (
    NetmikoTimeoutException, NetmikoAuthenticationException
)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QComboBox, QCheckBox,
    QTextEdit, QPushButton, QVBoxLayout, QFormLayout, QMessageBox
)

IS_WINDOWS = platform.system() == "Windows"

# ---- Remote (SSH) commands: label -> device command ----
SSH_COMMANDS = {
    "Show version": "show version",
    "Show interfaces brief": "show ip interface brief",
    "Show running-config": "show running-config",
    "Show AAA config": "show running-config | include aaa",
    "Show VLANs": "show vlan brief",
    "Show ARP table": "show ip arp",
    "Show routes": "show ip route",
}

# ---- Local commands: label -> (windows args, unix args, needs target) ----
LOCAL_COMMANDS = {
    "Ping":          (["ping", "-n", "4"], ["ping", "-c", "4"], True),
    "Traceroute":    (["tracert"],         ["traceroute"],      True),
    "NSLookup":      (["nslookup"],        ["nslookup"],        True),
    "IP config":     (["ipconfig", "/all"], ["ip", "addr"],     False),
    "ARP table":     (["arp", "-a"],       ["arp", "-a"],       False),
    "Netstat":       (["netstat", "-an"],  ["netstat", "-an"],  False),
    "Route table":   (["route", "print"],  ["ip", "route"],     False),
}

HOSTNAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.\-]*$")


def build_local_cmd(label, target):
    win_args, nix_args, needs_target = LOCAL_COMMANDS[label]
    cmd = list(win_args if IS_WINDOWS else nix_args)
    if needs_target:
        cmd.append(target)
    return cmd


def valid_target(text):
    """IP address or simple hostname (no leading '-', no spaces/symbols)."""
    try:
        ipaddress.ip_address(text)
        return True
    except ValueError:
        return bool(HOSTNAME_RE.match(text))


class SSHWorker(QThread):
    finished_ok = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, host, username, password, command):
        super().__init__()
        self.host, self.username = host, username
        self.password, self.command = password, command

    def run(self):
        device = {
            "device_type": "cisco_ios",
            "host": self.host,
            "username": self.username,
            "password": self.password,
            "timeout": 15,
        }
        try:
            with ConnectHandler(**device) as conn:
                result = conn.send_command(self.command)
            self.finished_ok.emit(result)
        except NetmikoAuthenticationException:
            self.failed.emit("Authentication failed. Check username/password.")
        except NetmikoTimeoutException:
            self.failed.emit("Connection timed out. Check IP / reachability / SSH enabled.")
        except Exception as e:
            self.failed.emit(f"Error: {e}")


class LocalWorker(QThread):
    finished_ok = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, cmd):
        super().__init__()
        self.cmd = cmd

    def run(self):
        try:
            proc = subprocess.run(
                self.cmd,
                capture_output=True,
                text=True,
                errors="replace",
                timeout=60,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            out = proc.stdout + proc.stderr
            self.finished_ok.emit(out.strip() or "(no output)")
        except subprocess.TimeoutExpired:
            self.failed.emit("Command timed out after 60s.")
        except FileNotFoundError:
            self.failed.emit(f"Command not found on this system: {self.cmd[0]}")
        except Exception as e:
            self.failed.emit(f"Error: {e}")


class SSHToolApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Command Runner")
        self.setGeometry(100, 100, 700, 580)
        self.worker = None
        self.init_ui()
        self.apply_styles()
        self.on_mode_changed()      # set initial visibility + dropdown

    def init_ui(self):
        self.ssh_check = QCheckBox("Use SSH (run on remote device)")
        self.ssh_check.setChecked(True)
        self.ssh_check.toggled.connect(self.on_mode_changed)

        self.ip_label = QLabel("IP Address:")
        self.ip_input = QLineEdit()

        self.user_label = QLabel("Username:")
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")

        self.pass_label = QLabel("Password:")
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)

        self.cmd_box = QComboBox()
        self.cmd_box.currentTextChanged.connect(self.on_command_changed)

        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.on_run)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Command output will appear here...")

        form = QFormLayout()
        form.addRow(self.ip_label, self.ip_input)
        form.addRow(self.user_label, self.user_input)
        form.addRow(self.pass_label, self.pass_input)
        form.addRow("Command:", self.cmd_box)

        layout = QVBoxLayout()
        layout.addWidget(self.ssh_check)
        layout.addLayout(form)
        layout.addWidget(self.run_btn)
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.output)
        self.setLayout(layout)

    # ---------- UI state ----------
    def on_mode_changed(self):
        ssh = self.ssh_check.isChecked()

        # show/hide creds (label + field together)
        for w in (self.user_label, self.user_input, self.pass_label, self.pass_input):
            w.setVisible(ssh)

        # swap dropdown contents
        self.cmd_box.blockSignals(True)
        self.cmd_box.clear()
        self.cmd_box.addItems(SSH_COMMANDS.keys() if ssh else LOCAL_COMMANDS.keys())
        self.cmd_box.blockSignals(False)

        self.ip_input.setPlaceholderText(
            "e.g. 192.168.1.1" if ssh else "IP or hostname, e.g. 8.8.8.8 / google.com"
        )
        self.on_command_changed()

    def on_command_changed(self):
        """Disable target box for local commands that don't need one (ipconfig etc.)."""
        if self.ssh_check.isChecked():
            self.ip_input.setEnabled(True)
            return
        label = self.cmd_box.currentText()
        needs_target = LOCAL_COMMANDS[label][2] if label in LOCAL_COMMANDS else True
        self.ip_input.setEnabled(needs_target)

    # ---------- Run ----------
    def on_run(self):
        label = self.cmd_box.currentText()
        target = self.ip_input.text().strip()

        if self.ssh_check.isChecked():
            user = self.user_input.text().strip()
            pwd = self.pass_input.text()
            try:
                ipaddress.ip_address(target)
            except ValueError:
                QMessageBox.warning(self, "Invalid IP", "Enter a valid IP address.")
                return
            if not user or not pwd:
                QMessageBox.warning(self, "Missing creds", "Enter username and password.")
                return
            self.output.setPlainText(f"Connecting to {target}...\n")
            self.worker = SSHWorker(target, user, pwd, SSH_COMMANDS[label])
        else:
            needs_target = LOCAL_COMMANDS[label][2]
            if needs_target and not valid_target(target):
                QMessageBox.warning(self, "Invalid target", "Enter a valid IP or hostname.")
                return
            cmd = build_local_cmd(label, target)
            self.output.setPlainText(f"Running: {' '.join(cmd)}\n")
            self.worker = LocalWorker(cmd)

        self.run_btn.setEnabled(False)
        self.run_btn.setText("Running...")
        self.worker.finished_ok.connect(self.output.setPlainText)
        self.worker.failed.connect(self.output.setPlainText)
        self.worker.finished.connect(self.reset_button)
        self.worker.start()

    def reset_button(self):
        self.run_btn.setEnabled(True)
        self.run_btn.setText("Run")

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget { background-color: #f4f6fa; font-size: 14px; }
            QLabel, QCheckBox { color: #2c3e50; font-weight: bold; }
            QLineEdit, QComboBox {
                background-color: white;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 6px;
            }
            QLineEdit:focus, QComboBox:focus { border-color: #3498db; }
            QLineEdit:disabled { background-color: #e5e8ec; color: #95a5a6; }
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas, 'Courier New', monospace;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
            }
            QPushButton:hover { background-color: #2176ae; }
            QPushButton:disabled { background-color: #95a5a6; }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SSHToolApp()
    window.show()
    sys.exit(app.exec_())