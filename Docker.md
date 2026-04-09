# How to Run Nadzoring

## Linux

### Option A: Docker (Recommended)

This is the easiest and most stable way to run Nadzoring on Linux.

```bash
# 1. Build the image
cd /path/to/nadzoring
docker build -t nadzoring:latest .

# 2. Create a convenient alias (add to ~/.bashrc or ~/.zshrc)
alias nadzoring='docker run --rm -it \
  --network host \
  --cap-add=NET_ADMIN \
  --cap-add=NET_RAW \
  nadzoring:latest'
```

After adding the alias, restart your terminal or run:

```bash
source ~/.bashrc
```

Now you can use it directly:

```bash
nadzoring --help
nadzoring dns resolve google.com
nadzoring network-base port-scan 192.168.1.0/24
nadzoring arp detect-spoofing
```

**Advantages**: Isolated environment, easy to update, no system dependency issues.

---

### Option B: Native Installation (without Docker)

```bash
# 1. Install pipx
python3 -m pip install --user -U pip pipx
python3 -m pipx ensurepath

# 2. Restart your shell or run:
source ~/.bashrc   # or ~/.zshrc

# 3. Install Nadzoring
cd /path/to/nadzoring
pipx install .

# For development (editable install):
# pipx install -e .
```

Usage:

```bash
nadzoring --help
nadzoring network-base ping 8.8.8.8
```

---

## Windows

**Recommended**: Install natively (not via WSL or Docker).

Running through WSL2 often causes networking issues (ARP, local network scanning, traceroute, etc.).

### Native Installation using pipx

```powershell
# 1. Install pipx
py -m pip install --upgrade pip pipx
py -m pipx ensurepath

# Restart PowerShell

# 2. Install Nadzoring
cd D:\nadzoring
pipx install .
```

Usage:

```powershell
nadzoring --help
nadzoring network-base ping 8.8.8.8
nadzoring dns resolve google.com
```

For development (changes reflect immediately):

```powershell
pipx install -e .
```

---

### Quick Summary

| Platform | Recommended Method       | Best For                     |
|----------|--------------------------|------------------------------|
| Linux    | Docker + alias           | Most users, servers          |
| Linux    | Native (pipx)            | Performance, development     |
| Windows  | Native (pipx)            | Best networking compatibility |

**Note**: Docker on Windows is possible but often has limitations with raw sockets and local network access.


