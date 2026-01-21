# Akidzuki-CLI

Terminal SSH connection manager. Store your SSH connections, connect quickly, manage servers from one place. Works like Termius but in your terminal.

**Author:** [z0nyx](https://github.com/z0nyx)  
**Repository:** [https://github.com/z0nyx/Akidzuki-CLI](https://github.com/z0nyx/Akidzuki-CLI)

## Features

- ✅ **Connection Management** - Add, edit, and delete SSH connections
- ✅ **Keyboard Navigation** - Navigate connections with arrow keys
- ✅ **Search & Filter** - Quickly find connections (Press `F`)
- ✅ **Grouping** - Organize connections by groups
- ✅ **Favorites** - Mark frequently used connections (Press `*` or `V`)
- ✅ **Recent Connections** - Track and access recently used connections
- ✅ **Connection Testing** - Test connections before connecting (Press `T`)
- ✅ **Sorting** - Sort by name, host, last used date, or group
- ✅ **Secure Password Storage** - Passwords stored via system keyring
- ✅ **SSH Key Support** - Use SSH keys for authentication
- ✅ **Interactive SSH Sessions** - Full terminal access with return-to-menu (Ctrl+B)
- ✅ **Keep-Alive** - Maintain long-running sessions
- ✅ **SSH Config Format** - Compatible with standard SSH config files
- ✅ **Export/Import** - Export/import connections (JSON, SSH config)
- ✅ **CLI Commands** - Command-line interface for quick access
- ✅ **Logging** - Comprehensive operation logging
- ✅ **Beautiful TUI** - Rich terminal UI with colors and formatting

## How It Works

When you add a connection, it saves to `.ssh_config` file (standard SSH config format). Passwords go to your system's secure storage - Windows Credential Store, macOS Keychain, or Linux Secret Service. Everything else is stored in config files in your working directory.

### Data Storage

**SSH Connections** are saved in:
- **Default location:** `.ssh_config` in the current working directory
- **Format:** Standard SSH config format (compatible with OpenSSH)
- **Customizable:** Can be changed via settings file

**Application Settings** are saved in:
- **Default location:** `.ssh_cli_settings.json` in the current working directory
- **Contains:** Config path, log settings, timeouts, display preferences

**Passwords** are stored in:
- **Windows:** Windows Credential Store
- **macOS:** Keychain
- **Linux:** Secret Service API or KWallet

## Installation

### Quick Installation

#### Windows

1. Download or clone the repository
2. Open Command Prompt or PowerShell in the project directory
3. Run:
```bash
install.bat
```

The installer will:
- Check for Python installation
- Install the package and dependencies
- Add the `akidzuki` command to your PATH automatically
- Verify the installation

#### Linux / macOS

1. Download or clone the repository
2. Open terminal in the project directory
3. Make the installer executable and run:
```bash
chmod +x install.sh
./install.sh
```

The installer will:
- Check for Python 3 installation
- Install the package and dependencies
- Add the `akidzuki` command to your PATH (via `.bashrc`, `.zshrc`, or `.profile`)
- Verify the installation

### Manual Installation

#### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

#### Step 1: Clone or Download

```bash
git clone https://github.com/z0nyx/Akidzuki-CLI.git
cd Akidzuki-CLI
```

#### Step 2: Install the Package

**Option A: Editable installation (recommended for development)**
```bash
pip install -e .
```

**Option B: Regular installation**
```bash
pip install .
```

#### Step 3: Verify Installation

After installation, you should be able to run:
```bash
akidzuki
```

**Note:** If the `akidzuki` command is not found:
- **Windows:** The Scripts directory may not be in PATH. Check `%USERPROFILE%\AppData\Roaming\Python\Python3XX\Scripts`
- **Linux/macOS:** The bin directory may not be in PATH. Check `~/.local/bin` or add it manually

### Development Installation

For development purposes:

1. Clone the repository:
```bash
git clone https://github.com/z0nyx/Akidzuki-CLI.git
cd Akidzuki-CLI
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - **Windows:** `venv\Scripts\activate`
   - **Linux/macOS:** `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python main.py
```

or

```bash
python -m ssh_cli.main
```

## Usage

### Main Menu

Launch the application:
```bash
akidzuki
```

#### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **↑/↓** | Navigate connections |
| **Enter** | Connect to selected connection |
| **A** | Add new connection |
| **E** | Edit selected connection |
| **D** | Delete selected connection |
| **T** | Test connection |
| **F** | Search/Filter connections |
| **S** | Change sort order |
| **G** | Filter by group |
| *** / V** | Toggle favorite / Show favorites only |
| **I** | Show connection info |
| **R** | Refresh list |
| **?** | Show help |
| **Q / ESC** | Quit |

### During SSH Session

- **Ctrl+B** - Return to main menu (keeps connection alive)
- **Ctrl+C** - Disconnect and return to menu

### CLI Commands

For command-line usage:

```bash
# List all connections
python -m ssh_cli.cli list [--sort name|host|last_used|group]

# Test a connection
python -m ssh_cli.cli test <connection_name>

# Connect to a server
python -m ssh_cli.cli connect <connection_name>
```

### Adding a Connection

When adding a new connection, you'll be prompted for:

- **Connection Name** (required) - A friendly name for the connection
- **Host** (required) - IP address or hostname
- **HostName** (optional) - Actual hostname (defaults to Host)
- **Username** (default: root) - SSH username
- **Port** (default: 22) - SSH port
- **Password** (optional) - Stored securely in system keyring
- **Identity File** (optional) - Path to SSH private key
- **Group** (optional) - Group for organization
- **Favorite** (optional) - Mark as favorite

## Configuration

### Connection Storage

Connections are stored in `.ssh_config` file (by default in the current working directory) in standard SSH config format:

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

Settings are stored in `.ssh_cli_settings.json` (by default in the current working directory):

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

**Settings explained:**
- `config_path` - Path to SSH config file
- `log_file` - Path to log file
- `log_level` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `ssh_timeout` - SSH connection timeout (seconds)
- `test_timeout` - Connection test timeout (seconds)
- `keepalive_interval` - Keep-alive interval (seconds)
- `show_colors` - Enable colors in interface
- `sort_by` - Default sort order
- `default_group` - Default group for new connections
- `recent_limit` - Number of recent connections to display

### Changing Storage Location

To change where connections are stored, edit `.ssh_cli_settings.json` and modify the `config_path` value:

```json
{
  "config_path": "/path/to/your/ssh_config"
}
```

## Export/Import

Export and import functionality is available through the `ssh_cli.utils.export_import` module:

- `export_to_json()` - Export connections to JSON format
- `import_from_json()` - Import connections from JSON
- `export_to_ssh_config()` - Export to SSH config format
- `import_from_ssh_config()` - Import from SSH config

## Security

### Password Storage

Passwords are stored securely using your system's credential manager:

- **Windows:** Windows Credential Store
- **macOS:** Keychain
- **Linux:** Secret Service API or KWallet

Passwords are never stored in plain text files. They are encrypted by your operating system's secure storage.

### SSH Keys

You can use SSH keys instead of passwords for authentication. Simply provide the path to your private key file when adding or editing a connection.

## Requirements

- Python 3.8 or higher
- paramiko >= 3.0.0
- rich >= 13.0.0
- keyring >= 24.0.0
- cryptography >= 41.0.0
- pyyaml >= 6.0.0

## Project Structure

```
Akidzuki-CLI/
├── ssh_cli/              # Main package
│   ├── config/           # Configuration management
│   ├── models/           # Data models
│   ├── services/         # Business logic (service layer)
│   ├── ssh/              # SSH client and sessions
│   ├── ui/               # User interface
│   ├── utils/            # Utilities (validation, logging, export/import)
│   ├── cli.py            # CLI commands
│   ├── main.py           # GUI entry point
│   └── settings.py       # Settings management
├── main.py               # Launch script
├── requirements.txt      # Dependencies
├── setup.py              # Package setup
├── pyproject.toml        # Modern package configuration
├── install.bat           # Windows installer
├── install.sh            # Linux/macOS installer
└── README.md             # Documentation
```

## Troubleshooting

### Command Not Found

If `akidzuki` command is not found after installation:

**Windows:**
1. Check if Scripts directory is in PATH: `%USERPROFILE%\AppData\Roaming\Python\Python3XX\Scripts`
2. Restart your terminal/command prompt
3. Or run the installer again: `install.bat`

**Linux/macOS:**
1. Check if bin directory is in PATH: `~/.local/bin`
2. Add to PATH manually or restart terminal
3. Or run: `source ~/.bashrc` (or `.zshrc`)

### Connection Issues

- Verify SSH credentials are correct
- Check if SSH service is running on the target server
- Ensure firewall allows SSH connections
- Test connection using the built-in test feature (Press `T`)

### Import Errors

If you encounter import errors:
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)
- Verify virtual environment is activated (if using one)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or contributions, please visit:
- **GitHub:** [https://github.com/z0nyx/Akidzuki-CLI](https://github.com/z0nyx/Akidzuki-CLI)
- **Author:** [z0nyx](https://github.com/z0nyx)
