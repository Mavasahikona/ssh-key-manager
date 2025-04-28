import argparse
import os
import paramiko
from typing import List

class SSHKeyManager:
    """
    A CLI tool to manage SSH keys across a fleet of Linux servers.
    """

    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def generate_key(self, key_path: str = "id_rsa") -> None:
        """
        Generate a new SSH key pair.

        Args:
            key_path (str): Path to save the key pair. Defaults to "id_rsa".
        """
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(key_path)
        with open(f"{key_path}.pub", "w") as pub_key_file:
            pub_key_file.write(f"{key.get_name()} {key.get_base64()}")
        print(f"SSH key pair generated at {key_path} and {key_path}.pub")

    def distribute_key(self, servers: List[str], username: str, key_path: str, password: str = None) -> None:
        """
        Distribute the public key to a list of servers.

        Args:
            servers (List[str]): List of server IPs or hostnames.
            username (str): Username for SSH login.
            key_path (str): Path to the public key.
            password (str, optional): Password for SSH login. Defaults to None.
        """
        with open(key_path, "r") as pub_key_file:
            pub_key = pub_key_file.read().strip()

        for server in servers:
            try:
                self.ssh.connect(server, username=username, password=password)
                stdin, stdout, stderr = self.ssh.exec_command(f"mkdir -p ~/.ssh && echo '{pub_key}' >> ~/.ssh/authorized_keys")
                print(f"Key distributed to {server}")
            except Exception as e:
                print(f"Failed to distribute key to {server}: {e}")
            finally:
                self.ssh.close()

    def rotate_key(self, servers: List[str], username: str, old_key_path: str, new_key_path: str, password: str = None) -> None:
        """
        Rotate an old SSH key with a new one on a list of servers.

        Args:
            servers (List[str]): List of server IPs or hostnames.
            username (str): Username for SSH login.
            old_key_path (str): Path to the old public key.
            new_key_path (str): Path to the new public key.
            password (str, optional): Password for SSH login. Defaults to None.
        """
        with open(old_key_path, "r") as old_key_file:
            old_key = old_key_file.read().strip()
        with open(new_key_path, "r") as new_key_file:
            new_key = new_key_file.read().strip()

        for server in servers:
            try:
                self.ssh.connect(server, username=username, password=password)
                stdin, stdout, stderr = self.ssh.exec_command(f"sed -i 's|{old_key}|{new_key}|g' ~/.ssh/authorized_keys")
                print(f"Key rotated on {server}")
            except Exception as e:
                print(f"Failed to rotate key on {server}: {e}")
            finally:
                self.ssh.close()

    def revoke_key(self, servers: List[str], username: str, key_path: str, password: str = None) -> None:
        """
        Revoke an SSH key from a list of servers.

        Args:
            servers (List[str]): List of server IPs or hostnames.
            username (str): Username for SSH login.
            key_path (str): Path to the public key to revoke.
            password (str, optional): Password for SSH login. Defaults to None.
        """
        with open(key_path, "r") as pub_key_file:
            pub_key = pub_key_file.read().strip()

        for server in servers:
            try:
                self.ssh.connect(server, username=username, password=password)
                stdin, stdout, stderr = self.ssh.exec_command(f"sed -i '/{pub_key}/d' ~/.ssh/authorized_keys")
                print(f"Key revoked from {server}")
            except Exception as e:
                print(f"Failed to revoke key from {server}: {e}")
            finally:
                self.ssh.close()

def main():
    parser = argparse.ArgumentParser(description="SSH Key Manager CLI Tool")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate Key
    generate_parser = subparsers.add_parser("generate", help="Generate a new SSH key pair")
    generate_parser.add_argument("--key-path", default="id_rsa", help="Path to save the key pair")

    # Distribute Key
    distribute_parser = subparsers.add_parser("distribute", help="Distribute a public key to servers")
    distribute_parser.add_argument("--servers", nargs="+", required=True, help="List of server IPs or hostnames")
    distribute_parser.add_argument("--username", required=True, help="Username for SSH login")
    distribute_parser.add_argument("--key-path", required=True, help="Path to the public key")
    distribute_parser.add_argument("--password", help="Password for SSH login")

    # Rotate Key
    rotate_parser = subparsers.add_parser("rotate", help="Rotate an old SSH key with a new one")
    rotate_parser.add_argument("--servers", nargs="+", required=True, help="List of server IPs or hostnames")
    rotate_parser.add_argument("--username", required=True, help="Username for SSH login")
    rotate_parser.add_argument("--old-key-path", required=True, help="Path to the old public key")
    rotate_parser.add_argument("--new-key-path", required=True, help="Path to the new public key")
    rotate_parser.add_argument("--password", help="Password for SSH login")

    # Revoke Key
    revoke_parser = subparsers.add_parser("revoke", help="Revoke an SSH key from servers")
    revoke_parser.add_argument("--servers", nargs="+", required=True, help="List of server IPs or hostnames")
    revoke_parser.add_argument("--username", required=True, help="Username for SSH login")
    revoke_parser.add_argument("--key-path", required=True, help="Path to the public key to revoke")
    revoke_parser.add_argument("--password", help="Password for SSH login")

    args = parser.parse_args()
    manager = SSHKeyManager()

    if args.command == "generate":
        manager.generate_key(args.key_path)
    elif args.command == "distribute":
        manager.distribute_key(args.servers, args.username, args.key_path, args.password)
    elif args.command == "rotate":
        manager.rotate_key(args.servers, args.username, args.old_key_path, args.new_key_path, args.password)
    elif args.command == "revoke":
        manager.revoke_key(args.servers, args.username, args.key_path, args.password)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()