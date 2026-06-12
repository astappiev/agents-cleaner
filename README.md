# agents-cleaner

Scan, analyze, and clean AI coding agent configuration files from your system. Supports 7+ agents across local projects and global home directories.

**Python 3.6+ · No dependencies**

## Installation

It's a single Python script — download it using any preferred method and make it executable.

Below is just a convenient one-liner to get it up and running:

```bash
curl -fsSL https://raw.githubusercontent.com/astappiev/agents-cleaner/main/agents-cleaner.py \
  -o ~/.local/bin/agents-cleaner && chmod +x ~/.local/bin/agents-cleaner
```

> Make sure ~/.local/bin is in your PATH (it is by default on most modern Linux distros and macOS). If not, add export PATH="$HOME/.local/bin:$PATH" to your shell profile.

## Quick Start

```bash
agents-cleaner              # Scan current directory
agents-cleaner /some/path   # Scan a specific directory
agents-cleaner --purge      # Remove all agent files
```

## Common Use-Cases

### 1. You've tried different tools and don't use them anymore
Clean up tools you've abandoned while keeping your preferred one:
```bash
agents-cleaner --purge --keep-claude    # Keep only Claude Code, remove Cursor, Copilot, etc.
agents-cleaner --purge-cursor           # Remove just Cursor from everywhere
```

### 2. You want a fresh start (remove bloated environment)
Wipe all AI agent configurations and start clean:
```bash
agents-cleaner --purge                  # Remove all local and global agent files
agents-cleaner --purge-local            # Keep global, remove only local project files
agents-cleaner --purge-global           # Keep local, remove only global configs
```

### 3. Audit another user's environment
Override `HOME` to resolve both global paths (`~/.claude`, etc.) and local paths (`~/work/.claude`, etc.) for that user:
```bash
HOME=/home/user2 agents-cleaner         # Scan user2's global configs
HOME=/home/user2 agents-cleaner ~/work  # Also scan /home/user2/work for local files
```

> On Windows, use `USERPROFILE` instead of `HOME`.

## Commands

| Command               | Effect                                                           |
| --------------------- | ---------------------------------------------------------------- |
| `agents-cleaner`      | Scan current directory and display found agent files             |
| `agents-cleaner PATH` | Scan PATH for local agent files (global paths always scanned)    |
| `--purge`             | Delete all agent files (local and global)                        |
| `--purge-local`       | Delete only local agent files                                    |
| `--purge-global`      | Delete only global agent files                                   |
| `--purge-{agent}`     | Delete specific agent (e.g., `--purge-claude`, `--purge-cursor`) |
| `--keep-{agent}`      | Protect agent during purge (e.g., `--keep-claude`)               |
| `--keep-global`       | Protect all global files during purge                            |

## How It Works

Scans for agent config files in:
- **Local**: The specified path (or current directory) and its subdirectories
- **Global**: Home directory patterns (`~/.claude`, `~/.cursor`, etc.) resolved via `$HOME`

Safe by default — scanning never deletes. Only `--purge` flags modify files.

## License

MIT
