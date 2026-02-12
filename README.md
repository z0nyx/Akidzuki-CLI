# Akidzuki-CLI

Terminal SSH connection manager. Store your SSH connections, connect quickly, manage servers from one place. Works like Termius but in your terminal.

**Author:** [z0nyx](https://github.com/z0nyx)  
**Repository:** [https://github.com/z0nyx/Akidzuki-CLI](https://github.com/z0nyx/Akidzuki-CLI)

## Features

- ✅ **Connection Management** - Add, edit, delete SSH connections
- ✅ **Keyboard Navigation** - Navigate with arrow keys, no mouse needed
- ✅ **Search & Filter** - Find connections fast (Press `F`)
- ✅ **Grouping** - Keep production, staging, personal separate
- ✅ **Favorites** - Star frequently used connections (Press `*` or `V`)
- ✅ **Recent Connections** - Jump back to servers you just used
- ✅ **Connection Testing** - Check if a server is reachable (Press `T`)
- ✅ **Sorting** - Order by name, host, last used, or group
- ✅ **Secure Password Storage** - Uses your system keyring, not plaintext
- ✅ **SSH Key Support** - Bring your own .pem or id_rsa
- ✅ **Interactive SSH Sessions** - Full terminal access, jump back with Ctrl+B
- ✅ **Keep-Alive** - No more dropped sessions during lunch
- ✅ **SSH Config Format** - Compatible with OpenSSH, no lock-in
- ✅ **Export/Import** - Move connections between machines (JSON, SSH config)
- ✅ **CLI Commands** - Script it, pipe it, automate it
- ✅ **Logging** - Know what broke and when
- ✅ **Beautiful TUI** - Actually readable, not just green text on black

## How It Works

Add a connection, it writes to `.ssh_config` — same format OpenSSH uses. Passwords? Those go to your system's secure storage: Windows Credential Store, macOS Keychain, or Linux Secret Service. Everything else lives in config files right in your working directory. No hidden folders, no surprises.

### Data Storage

**SSH Connections** live in:
- **Default:** `.ssh_config` in whatever directory you're in
- **Format:** Standard SSH config. You could cat it and use it with OpenSSH directly
- **Custom:** Change the path in settings if you want it elsewhere

**Application Settings** live in:
- **Default:** `.ssh_cli_settings.json` in your current directory
- **What's inside:** Config path, log settings, timeouts, whether you like colors

**Passwords** live in:
- **Windows:** Credential Manager
- **macOS:** Keychain
- **Linux:** Secret Service API or KWallet

## Installation

### Quick Install

#### Windows

1. Grab the repo
2. Open Command Prompt or PowerShell in the folder
3. Run:
```bash
install.bat
```

This will:
- Check if Python exists
- Install the thing and its dependencies
- Add `akidzuki` to your PATH automatically
- Tell you if it worked

#### Linux / macOS

1. Clone or download
2. Open terminal in the folder
3. Make it executable and run:
```bash
chmod +x install.sh
./install.sh
```

This will:
- Check for Python 3
- Install the package
- Add `akidzuki` to your PATH (via `.bashrc`, `.zshrc`, or `.profile`)
- Verify it's working

### Manual Install

#### Prerequisites

- Python 3.8 or newer
- pip

#### Step 1: Get the Code

```bash
git clone https://github.com/z0nyx/Akidzuki-CLI.git
cd Akidzuki-CLI
```

#### Step 2: Install

**Option A: Editable (you're gonna change stuff)**
```bash
pip install -e .
```

**Option B: Regular (just want it to work)**
```bash
pip install .
```

#### Step 3: Check It

```bash
akidzuki
```

**If it's not found:**
- **Windows:** Look in `%USERPROFILE%\AppData\Roaming\Python\Python3XX\Scripts`
- **Linux/macOS:** Check `~/.local/bin` or just add it to PATH

### Dev Setup

1. Clone:
```bash
git clone https://github.com/z0nyx/Akidzuki-CLI.git
cd Akidzuki-CLI
```

2. Virtual environment:
```bash
python -m venv venv
```

3. Activate:
   - **Windows:** `venv\Scripts\activate`
   - **Linux/macOS:** `source venv/bin/activate`

4. Dependencies:
```bash
pip install -r requirements.txt
```

5. Run:
```bash
python main.py
```

or

```bash
python -m akidzuki_cli.main
```

## Usage

### Main Menu

Just type:
```bash
akidzuki
```
<div align="center">
  <img src="https://media.discordapp.net/attachments/1396120664682922097/1463588313356308595/image.png?ex=698f6156&is=698e0fd6&hm=58ee143adffb796e7ac4bdaf34704370defe419996bfb18313e3131c0d7b73bc&=&format=webp&quality=lossless&width=1376&height=361" alt="Akidzuki-CLI">
</div>

#### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **↑/↓** | Move around |
| **Enter** | Connect |
| **A** | New connection |
| **E** | Edit this one |
| **D** | Delete this one |
| **T** | Ping test |
| **F** | Search |
| **S** | Sort differently |
| **G** | Show only this group |
| *** / V** | Star it / Show only favorites |
| **I** | Connection details |
| **R** | Refresh list |
| **?** | Help screen |
| **Q / ESC** | Exit |

### During SSH Session

- **Ctrl+B** - Back to menu (session stays open)
- **Ctrl+C** - Disconnect and return

### CLI Commands

For when you don't want the menu:

```bash
# List everything
python -m akidzuki_cli.cli list [--sort name|host|last_used|group]

# Test a connection
python -m akidzuki_cli.cli test <connection_name>

# Connect directly
python -m akidzuki_cli.cli connect <connection_name>
```

### Adding a Connection

It'll ask for:

- **Connection Name** (required) - Whatever you want to call it
- **Host** (required) - IP or domain
- **HostName** (optional) - If different from the display name
- **Username** (default: root) - Who you're logging in as
- **Port** (default: 22) - SSH port
- **Password** (optional) - Goes straight to your keyring
- **Identity File** (optional) - Path to your private key
- **Group** (optional) - dev, prod, homelab, whatever
- **Favorite** (optional) - Star it now or later

## Configuration

### Connection Storage

Connections land in `.ssh_config` (unless you change it). Looks like this:

```
Host server1
  HostName 192.168.1.100
  User root
  Port 22
  IdentityFile ~/.ssh/id_rsa
  # Group: production
  # Favorite: true
  # LastUsed: 2026-01-21T18:32:00
  # CreatedAt: 2026-01-20T10:15:30
```

### Application Settings

Settings go in `.ssh_cli_settings.json`:

```json
{
  "config_path": ".ssh_config",
  "log_file": "ssh_cli.log",
  "log_level": "INFO",
  "ssh_timeout": 10,
  "test_timeout": 5,
  "keepalive_interval": 30,
  "show_colors": true,
  "sort_by": "name",
  "default_group": null,
  "recent_limit": 5
}
```

**What they do:**
- `config_path` - Where your servers are stored
- `log_file` - Where logs go
- `log_level` - How chatty the logs should be
- `ssh_timeout` - How long to wait before giving up
- `test_timeout` - Same but for ping tests
- `keepalive_interval` - How often to ping idle sessions
- `show_colors` - Some people hate colors, weirdly
- `sort_by` - Default sorting preference
- `default_group` - Pre-fill this group for new servers
- `recent_limit` - How many recent servers to remember

### Moving Your Storage

Edit `.ssh_cli_settings.json` and change `config_path`:

```json
{
  "config_path": "/home/you/ssh/servers.txt"
}
```

## Export/Import

Available through `akidzuki_cli.utils.export_import`:

- `export_to_json()` - Save everything as JSON
- `import_from_json()` - Load from JSON
- `export_to_ssh_config()` - Plain SSH config format
- `import_from_ssh_config()` - Import from existing SSH config

## Security

### Passwords

No plaintext passwords. Ever. They go straight to:
- **Windows:** Credential Manager
- **macOS:** Keychain
- **Linux:** Secret Service / KWallet

Your OS encrypts them, not this script.

### SSH Keys

Prefer keys? Just drop the path to your private key. Works with both password and key auth.

## Requirements

- Python 3.8+
- paramiko >= 3.0.0
- rich >= 13.0.0  
- keyring >= 24.0.0
- cryptography >= 41.0.0
- pyyaml >= 6.0.0

## Project Structure

```
Akidzuki-CLI/
├── akidzuki_cli/              # The actual code
│   ├── config/           # Reading/writing configs
│   ├── models/           # What a connection looks like
│   ├── services/         # The logic
│   ├── ssh/              # Actually connecting
│   ├── ui/               # The terminal UI
│   ├── utils/            # Helpers, logs, export/import
│   ├── cli.py            # Command line interface
│   ├── main.py           # Entry point for the UI
│   └── settings.py       # Settings management
├── main.py               # Launch script
├── requirements.txt      # Dependencies
├── setup.py              # Old school setup
├── pyproject.toml        # New school setup
├── install.bat           # Windows installer
├── install.sh            # *nix installer
└── README.md             # This file
```

## Troubleshooting

### "akidzuki: command not found"

**Windows:**
1. Check `%USERPROFILE%\AppData\Roaming\Python\Python3XX\Scripts`
2. Restart your terminal
3. Run `install.bat` again

**Linux/macOS:**
1. Check `~/.local/bin`
2. Add it to PATH or restart terminal
3. `source ~/.bashrc` (or `.zshrc`)

### Won't Connect

- Double-check username/password
- Is SSH actually running on the server?
- Firewalls? Corporate VPN?
- Hit `T` to test before you waste time

### Import Errors

- `pip install -r requirements.txt` again
- `python --version` — need 3.8+
- Did you activate your venv?

## Contributing

Found a bug? Want a feature? PRs welcome.

## Support

- **GitHub Issues:** [https://github.com/z0nyx/Akidzuki-CLI/issues](https://github.com/z0nyx/Akidzuki-CLI/issues)
- **Author:** [@z0nyx](https://github.com/z0nyx)
