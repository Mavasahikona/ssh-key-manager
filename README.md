# SSH Key Manager

A CLI tool to generate, distribute, rotate, and revoke SSH keys across a fleet of Linux servers.

## Features
- **Generate SSH Keys**: Create new SSH key pairs for users or services.
- **Distribute Keys**: Securely deploy SSH keys to multiple servers.
- **Rotate Keys**: Automatically replace old keys with new ones.
- **Revoke Keys**: Remove SSH keys from servers when they are no longer needed.

## Installation

```bash
git clone https://github.com/Mavasahikona/ssh-key-manager.git
cd ssh-key-manager
pip install -r requirements.txt
```

## Usage

```bash
python ssh_key_manager.py --help
```

## Technologies Used
- Python
- Paramiko (for SSH operations)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.