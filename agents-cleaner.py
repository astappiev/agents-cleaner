#!/usr/bin/env python3

import argparse
import os
import glob
import shutil

# ==========================================
# CONFIGURATION: Agent File Map
# ==========================================
# Add or modify agents here. The script will automatically
# generate --keep-<agent> and --purge-<agent> flags for each entry.
AGENT_MAP = {
    "dotagents": {
        "name": "Standard Agent Config (.agents)",
        "executables": [],
        "local": [".agents", "AGENTS.md"],
        "global": ["~/.agents"],
    },
    "claude": {
        "name": "Claude Code",
        "executables": ["claude", "~/.local/bin/claude", "~/.nvm/versions/node/*/bin/claude", " ~/.local/share/fnm/node-versions/*/installation/bin/claude"],
        "local": ["CLAUDE.md", ".claude", ".claude.json"],
        "global": ["~/.claude", "~/.claude.json"],
    },
    "codex": {
        "name": "OpenAI Codex",
        "executables": ["codex", "~/.local/bin/codex", "~/.nvm/versions/node/*/bin/codex", "~/.local/share/fnm/node-versions/*/installation/bin/codex"],
        "local": ["CODEX.md", ".codex", ".codex/config.toml"],
        "global": ["~/.codex", "~/.codex/config.toml"],
    },
    "pi": {
        "name": "Pi",
        "executables": ["pi", "~/.local/bin/pi", "~/.nvm/versions/node/*/bin/pi", "~/.local/share/fnm/node-versions/*/installation/bin/pi"],
        "local": [".pi", ".pi/settings.json"],
        "global": ["~/.pi", "~/.pi/agent/settings.json"],
    },
    "copilot": {
        "name": "GitHub Copilot",
        "executables": ["gh", "~/.local/bin/gh"],
        "local": [".github/copilot-instructions.md", "copilot.json", ".github/instructions"],
        "global": ["~/.copilot"],
    },
    "gemini": {
        "name": "Google Gemini",
        "executables": ["gemini", "~/.local/bin/gemini", "~/.local/share/pnpm/nodejs/*/bin/gemini"],
        "local": ["GEMINI.md", ".gemini/settings.json"],
        "global": [".gemini/settings.json", "/etc/gemini-cli/system-defaults.json"],
    },
    "cursor": {
        "name": "Cursor",
        "executables": ["cursor", "~/.local/bin/cursor", "~/.cursor-server"],
        "local": [".cursorrules", ".cursorignore", ".cursor"],
        "global": ["~/.cursor"],
    },
    "windsurf": {
        "name": "Windsurf",
        "executables": ["windsurf", "~/.local/bin/windsurf"],
        "local": [".windsurfrules", ".windsurf"],
        "global": [],
    },
    "opencode": {
        "name": "OpenCode",
        "executables": ["opencode", "~/.local/bin/opencode"],
        "local": ["opencode.json", "opencode.jsonc", ".opencode"],
        "global": ["~/.config/opencode"],
    },
    "antigravity-cli": {
        "name": "Antigravity CLI",
        "executables": ["agy", "~/.local/bin/agy"],
        "local": [],
        "global": ["~/.gemini/antigravity-cli", "~/.gemini/antigravity-cli/settings.json"],
    },
    "antigravity-ide": {
        "name": "Antigravity IDE",
        "executables": ["~/.antigravity-ide-server", "~/.antigravity-server"],
        "local": [".antigravity"],
        "global": ["~/.gemini/antigravity-ide", "~/.config/antigravity"],
    },
}


def find_executables(metadata):
    """Returns a list of detected executable paths for an agent."""
    found = []
    seen = set()
    for entry in metadata.get("executables", []):
        candidates = []
        if not entry.startswith("~") and "/" not in entry and "\\" not in entry:
            resolved = shutil.which(entry)
            if resolved:
                candidates.append(resolved)
        else:
            for match in glob.glob(os.path.expanduser(entry)):
                if os.path.exists(match):
                    candidates.append(match)
        for path in candidates:
            real = os.path.realpath(path)
            if real not in seen:
                seen.add(real)
                found.append(path)
    return found


def find_files(search_global=False, base_path=None):
    """Scans the directory and optionally global paths for agent files."""
    found_data = {}
    search_root = os.path.abspath(base_path) if base_path else os.getcwd()

    if base_path and not os.path.exists(search_root):
        return found_data

    for agent, metadata in AGENT_MAP.items():
        local_matches = []
        global_matches = []
        executable_matches = []

        # Detect installed executables
        executable_matches = find_executables(metadata)

        # Scan Local Paths
        for pattern in metadata["local"]:
            full_pattern = os.path.join(search_root, pattern)
            for match in glob.glob(full_pattern, recursive=True):
                if os.path.exists(match):
                    local_matches.append(match)

        # Scan Global Paths
        if search_global:
            for pattern in metadata["global"]:
                expanded = os.path.expanduser(pattern)
                for match in glob.glob(expanded):
                    if os.path.exists(match):
                        global_matches.append(match)

        if executable_matches or local_matches or global_matches:
            found_data[agent] = {
                "executables": executable_matches,
                "local_files": local_matches,
                "global_files": global_matches,
                "metadata": metadata,
            }

    return found_data


def delete_path(path):
    """Safely deletes a file or directory."""
    try:
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        print(f"✅ Deleted: {path}")
    except Exception as e:
        print(f"❌ Failed to delete {path}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Analyze, detect, and clean AI coding agent configuration files.", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("path", nargs="?", default=None, metavar="PATH", help="Directory to scan for local agent files (default: current directory)")
    parser.add_argument("--purge", action="store_true", help="Remove all found files (both local and global, unless overridden by a keep flag)")
    parser.add_argument("--purge-local", action="store_true", help="Remove all local agent files")
    parser.add_argument("--purge-global", action="store_true", help="Remove all global agent files")
    parser.add_argument("--keep-global", action="store_true", help="Keep all global agent files (overrides --purge)")

    # Dynamically generate agent-specific flags
    for agent in AGENT_MAP.keys():
        parser.add_argument(f"--purge-{agent}", action="store_true", help=f"Purge files specifically for {agent}")
        parser.add_argument(f"--keep-{agent}", action="store_true", help=f"Keep files for {agent} (overrides --purge)")

    args = parser.parse_args()

    # Step 1: Scan for files - always search global
    scan_path = os.path.expanduser(args.path) if args.path else None
    agents_present = find_files(search_global=True, base_path=scan_path)

    # Step 2: Display findings
    if not agents_present:
        print("✨ Clean! No coding agent footprints detected.")
        return 0

    print("🔍 Found agent files:")
    for agent, data in agents_present.items():
        print(f"  [{agent}] {data['metadata']['name']}")
        for f in data["executables"]:
            print(f"    🤖 {f}")
        for f in data["global_files"]:
            print(f"    🌐 {f}")
        for f in data["local_files"]:
            print(f"    📄 {f}")

    # Step 3: Determine deletions based on user inputs
    # Use a set to avoid duplicates when multiple purge flags overlap
    files_to_delete = set()

    for agent, data in agents_present.items():
        keep_agent = getattr(args, f"keep_{agent.replace('-', '_')}")
        if keep_agent:
            continue

        purge_specific = getattr(args, f"purge_{agent.replace('-', '_')}")

        if args.purge or purge_specific:
            for f in data["local_files"]:
                files_to_delete.add(f)
            if not args.keep_global:
                for f in data["global_files"]:
                    files_to_delete.add(f)

        if args.purge_local:
            for f in data["local_files"]:
                files_to_delete.add(f)

        if args.purge_global and not args.keep_global:
            for f in data["global_files"]:
                files_to_delete.add(f)

    # Step 4: Execute deletion or inform user about how to proceed
    if files_to_delete:
        print("\n🗑️  Executing deletion...")
        for f in sorted(files_to_delete):
            delete_path(f)
        print("\nCleanup complete.")
    else:
        if args.purge or args.purge_local or args.purge_global or any(getattr(args, f"purge_{a.replace('-', '_')}") for a in AGENT_MAP):
            print("\nℹ️  No files were deleted (your --keep flags protected them).")
        else:
            print("\nℹ️  Run with --purge, --purge-local, --purge-global, or --purge-<agent> to remove these files.")

    return 0


if __name__ == "__main__":
    exit(main())
