#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP CHECKER - Advanced Android Termux Network Utility
Developer: KSURitam
Version: 1.0.0
Platform: Android Termux (ARM64)

A lightweight, professional terminal-based network utility
for detecting LAN IPs, Minecraft Direct Connect addresses,
and analyzing IP information.
"""

import os
import sys
import re
import json
import time
import socket
import shutil
import subprocess
import ipaddress
import urllib.request
import urllib.error
from pathlib import Path

# ============================================================
# CONSTANTS & CONFIG
# ============================================================
APP_NAME = "IP CHECKER"
APP_SUBTITLE = "ADVANCED NETWORK & MINECRAFT LAN IP UTILITY"
DEVELOPER = "KSURitam"
VERSION = "1.0.0"

CONFIG_DIR = Path.home() / ".ip_checker"
CONFIG_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history.json"

# ANSI Colors
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    # Lemon Yellow
    LEMON = "\033[38;5;226m"
    YELLOW = "\033[93m"
    # Green
    GREEN = "\033[92m"
    BRIGHT_GREEN = "\033[38;5;46m"
    # Info
    WHITE = "\033[97m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    # Error
    RED = "\033[91m"
    # UI
    BG_DARK = "\033[48;5;236m"

# Fallback if terminal doesn't support colors
if not sys.stdout.isatty() or os.environ.get("NO_COLOR"):
    for attr in dir(C):
        if not attr.startswith("_"):
            setattr(C, attr, "")

DEFAULT_CONFIG = {
    "scan_duration": 60,
    "scan_interval": 2,
    "auto_refresh": False,
    "repeated_scanning": True,
    "network_role": "AUTO",  # AUTO / HOTSPOT HOST / CONNECTED CLIENT
    "public_ip_lookup": True,
    "hotspot_detection": True,
    "local_ip_detection": True,
    "theme": "LEMON_GREEN",
    "animation": True,
    "layout": "FULL",  # FULL / COMPACT
    "lookup_history": False,
    "confirm_public_lookup": True,
}

# ============================================================
# UTILITIES
# ============================================================
def term_width():
    try:
        return shutil.get_terminal_size((80, 24)).columns
    except Exception:
        return 80

def clear():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))

def center(text, width=None, pad=" "):
    w = width or term_width()
    # Strip ANSI for length calculation
    visible = re.sub(r"\033\[[0-9;]*m", "", text)
    length = len(visible)
    if length >= w:
        return text
    left = (w - length) // 2
    return pad * left + text

def line(char="─", color=None):
    w = term_width()
    c = color or C.DIM
    return f"{c}{char * w}{C.RESET}"

def hr():
    print(f"{C.YELLOW}{'═' * term_width()}{C.RESET}")

def label(key, value, key_color=None, val_color=None):
    kc = key_color or C.CYAN
    vc = val_color or C.WHITE
    print(f"  {kc}{key:<22}{C.RESET} {vc}{value}{C.RESET}")

def box_title(title, color=None):
    c = color or C.LEMON
    w = term_width()
    inner = w - 4
    print(f"{c}┌{'─' * inner}┐{C.RESET}")
    print(f"{c}│{C.RESET} {C.BOLD}{C.WHITE}{title.ljust(inner - 1)}{C.RESET} {c}│{C.RESET}")
    print(f"{c}└{'─' * inner}┘{C.RESET}")

def pause(msg="Press ENTER to continue..."):
    try:
        input(f"\n{C.DIM}{msg}{C.RESET}")
    except (KeyboardInterrupt, EOFError):
        pass

# ============================================================
# BANNER
# ============================================================
BANNER = r"""
  ██╗██████╗      ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
  ██║██╔══██╗    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
  ██║██████╔╝    ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
  ██║██╔═══╝     ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
  ██║██║         ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
  ╚═╝╚═╝          ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
"""

def show_banner(compact=False):
    """Display the main IP CHECKER banner."""
    if compact:
        print(f"{C.LEMON}{C.BOLD}")
        print(center("╔═══════════════════════════════════════════╗"))
        print(center("║      IP  CHECKER   v1.0.0                ║"))
        print(center("║   Advanced Network & Minecraft LAN IP    ║"))
        print(center(f"║         Developer: {DEVELOPER:<20}  ║"))
        print(center("╚═══════════════════════════════════════════╝"))
        print(f"{C.RESET}")
        return

    width = term_width()
    print()
    # Choose banner size based on terminal width
    if width >= 80:
        for row in BANNER.strip("\n").split("\n"):
            print(f"{C.LEMON}{C.BOLD}{center(row)}{C.RESET}")
    else:
        # Small fallback banner
        art = [
            "██╗██████╗     ██████╗██╗  ██╗",
            "██║██╔══██╗   ██╔════╝██║  ██║",
            "██║██████╔╝   ██║     ███████║",
            "██║██╔═══╝    ██║     ██╔══██║",
            "██║██║        ╚██████╗██║  ██║",
            "╚═╝╚═╝         ╚═════╝╚═╝  ╚═╝",
        ]
        for row in art:
            print(f"{C.LEMON}{C.BOLD}{center(row)}{C.RESET}")

    print()
    print(f"{C.BRIGHT_GREEN}{C.BOLD}{center(APP_SUBTITLE)}{C.RESET}")
    print(f"{C.WHITE}{C.DIM}{center(f'Developer: {DEVELOPER}   |   v{VERSION}')}{C.RESET}")
    print()

# ============================================================
# CONFIG
# ============================================================
def load_config():
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
            cfg = dict(DEFAULT_CONFIG)
            cfg.update(data)
            return cfg
    except Exception:
        pass
    return dict(DEFAULT_CONFIG)

def save_config(cfg):
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
        return True
    except Exception as e:
        print(f"{C.RED}Failed to save config: {e}{C.RESET}")
        return False

# ============================================================
# COMMAND RUNNER
# ============================================================
def run_cmd(cmd, timeout=4):
    """Run shell command, return stdout or empty string."""
    try:
        r = subprocess.run(
            cmd, shell=isinstance(cmd, str),
            capture_output=True, text=True, timeout=timeout
        )
        return r.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return ""

def cmd_exists(name):
    return shutil.which(name) is not None

# ============================================================
# NETWORK DETECTION ENGINE
# ============================================================
def list_interfaces():
    """Return dict: {ifname: {'state','mtu','mac'}}"""
    ifaces = {}
    try:
        base = "/sys/class/net"
        if os.path.isdir(base):
            for name in os.listdir(base):
                info = {"state": "unknown", "mtu": "?", "mac": "?"}
                try:
                    with open(f"{base}/{name}/operstate") as f:
                        info["state"] = f.read().strip()
                except Exception:
                    pass
                try:
                    with open(f"{base}/{name}/mtu") as f:
                        info["mtu"] = f.read().strip()
                except Exception:
                    pass
                try:
                    with open(f"{base}/{name}/address") as f:
                        info["mac"] = f.read().strip()
                except Exception:
                    pass
                ifaces[name] = info
    except Exception:
        pass
    return ifaces

def get_ip_addr_json():
    """Parse `ip -j addr` if available, else fallback to text."""
    out = run_cmd(["ip", "-j", "addr"])
    if out:
        try:
            return json.loads(out)
        except Exception:
            pass
    # Fallback parse from `ip addr`
    text = run_cmd(["ip", "addr"])
    return parse_ip_addr_text(text)

def parse_ip_addr_text(text):
    """Parse `ip addr` text output into similar structure."""
    result = []
    cur = None
    for line in text.splitlines():
        m = re.match(r"^\d+:\s+([^:]+):\s+<([^>]*)>.*\s+state\s+(\S+)", line)
        if m:
            if cur:
                result.append(cur)
            cur = {"ifname": m.group(1), "flags": m.group(2).split(","),
                   "operstate": m.group(3), "addr_info": []}
            continue
        if cur is None:
            continue
        m2 = re.match(r"^\s+inet6?\s+(\S+)", line)
        if m2:
            fam = "inet6" if "inet6" in line else "inet"
            cur["addr_info"].append({"family": fam, "local": m2.group(1)})
    if cur:
        result.append(cur)
    return result

def get_interfaces_with_ips():
    """Return list of dicts: ifname, flags, state, addrs (v4/v6)."""
    data = get_ip_addr_json()
    ifaces = []
    for d in data:
        ifname = d.get("ifname", "?")
        flags = d.get("flags", [])
        state = d.get("operstate", "UNKNOWN")
        v4, v6 = [], []
        for a in d.get("addr_info", []):
            fam = a.get("family", "")
            local = a.get("local", "")
            if fam == "inet" and local:
                v4.append(local)
            elif fam == "inet6" and local:
                # Skip link-local only if no other
                v6.append(local)
        ifaces.append({
            "ifname": ifname,
            "flags": flags,
            "state": state,
            "ipv4": v4,
            "ipv6": v6,
        })
    return ifaces

def classify_interface(name, flags):
    """Classify interface role based on name patterns and flags."""
    n = name.lower()
    if n == "lo":
        return "LOOPBACK"
    if n.startswith("rmnet") or "ccmni" in n or "pdp" in n:
        return "MOBILE"
    if n.startswith("ap") or "softap" in n or "swlan" in n or "wlan1" in n:
        return "HOTSPOT"
    if n.startswith("wlan") or "wifi" in n or "p2p" in n:
        return "WIFI"
    if n.startswith("eth") or "usb" in n or "rndis" in n:
        return "USB_ETHERNET"
    if n.startswith("tun") or n.startswith("tap"):
        return "VPN"
    if n.startswith("dummy"):
        return "DUMMY"
    return "OTHER"

def get_routes():
    """Return list of default routes with gateway."""
    out = run_cmd(["ip", "-j", "route"])
    routes = []
    if out:
        try:
            for r in json.loads(out):
                routes.append(r)
            return routes
        except Exception:
            pass
    # Fallback text
    text = run_cmd(["ip", "route"])
    for line in text.splitlines():
        parts = line.split()
        if parts and parts[0] == "default":
            gw = ""
            if "via" in parts:
                try:
                    gw = parts[parts.index("via") + 1]
                except Exception:
                    pass
            dev = ""
            if "dev" in parts:
                try:
                    dev = parts[parts.index("dev") + 1]
                except Exception:
                    pass
            routes.append({"dst": "default", "gateway": gw, "dev": dev})
    return routes

def get_default_gateway():
    for r in get_routes():
        if r.get("dst") == "default" and r.get("gateway"):
            return r["gateway"], r.get("dev", "")
    # Fallback to /proc/net/route
    try:
        with open("/proc/net/route") as f:
            for line in f.readlines()[1:]:
                parts = line.split()
                if len(parts) >= 3 and parts[1] == "00000000":
                    gw_hex = parts[2]
                    dev = parts[0]
                    # Convert hex LE to dotted
                    b = bytes.fromhex(gw_hex)
                    gw = ".".join(str(x) for x in reversed(b))
                    return gw, dev
    except Exception:
        pass
    return "", ""

def get_active_interface():
    """Return the interface that has the default route."""
    _, dev = get_default_gateway()
    if dev:
        return dev
    # Fallback: first non-lo iface with IPv4 up
    for i in get_interfaces_with_ips():
        if i["ifname"] != "lo" and i["ipv4"]:
            return i["ifname"]
    return ""

def get_public_ip(timeout=5):
    """Get public IP via HTTPS. Returns (ip, error)."""
    services = [
        ("https://api.ipify.org", "text"),
        ("https://ifconfig.me/ip", "text"),
        ("https://ipinfo.io/ip", "text"),
    ]
    for url, _ in services:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "IPChecker/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read().decode().strip()
                try:
                    ipaddress.ip_address(data)
                    return data, None
                except ValueError:
                    continue
        except urllib.error.URLError as e:
            last_err = f"Network error: {e.reason}"
        except Exception as e:
            last_err = str(e)
    return None, last_err if 'last_err' in dir() else "All services failed"

def get_neigh(ip):
    """Get MAC for IP from neighbor cache if present."""
    out = run_cmd(["ip", "neigh"])
    for line in out.splitlines():
        parts = line.split()
        if parts and parts[0] == ip:
            mac = ""
            state = ""
            dev = ""
            if "lladdr" in parts:
                try:
                    mac = parts[parts.index("lladdr") + 1]
                except Exception:
                    pass
            if "dev" in parts:
                try:
                    dev = parts[parts.index("dev") + 1]
                except Exception:
                    pass
            if len(parts) > 1:
                state = parts[-1]
            return {"mac": mac, "state": state, "dev": dev}
    return None

# ============================================================
# ROLE DETECTION
# ============================================================
def determine_network_role(cfg, ifaces, gateway_dev):
    """
    Determine this device's role: HOTSPOT_HOST / CONNECTED_CLIENT / UNKNOWN.
    """
    if cfg.get("network_role") != "AUTO":
        return cfg["network_role"]

    role = "UNKNOWN"
    # If any interface is flagged HOTSPOT and has IPv4 → likely host
    for i in ifaces:
        cls = classify_interface(i["ifname"], i["flags"])
        if cls == "HOTSPOT" and i["ipv4"] and i["state"].lower() == "up":
            role = "HOTSPOT HOST"
            break
    # If active default route is via wlan* with a gateway → connected client
    if role == "UNKNOWN" and gateway_dev:
        cls = classify_interface(gateway_dev, [])
        if cls == "WIFI" and get_default_gateway()[0]:
            role = "CONNECTED CLIENT"
    return role

def get_lan_ip(cfg, ifaces, role):
    """
    Return (ip, interface, status) for the LAN IP relevant to Minecraft hosting.
    """
    if not ifaces:
        return None, None, "UNVERIFIED"

    if role == "HOTSPOT HOST":
        for i in ifaces:
            if classify_interface(i["ifname"], i["flags"]) == "HOTSPOT" and i["ipv4"]:
                return i["ipv4"][0], i["ifname"], "VERIFIED"
        return None, None, "UNVERIFIED"

    if role == "CONNECTED CLIENT":
        # Prefer wlan with IPv4
        for i in ifaces:
            cls = classify_interface(i["ifname"], i["flags"])
            if cls == "WIFI" and i["ipv4"]:
                return i["ipv4"][0], i["ifname"], "VERIFIED"
        return None, None, "UNVERIFIED"

    # AUTO / UNKNOWN
    # If a hotspot iface with IPv4 exists, assume host
    for i in ifaces:
        if classify_interface(i["ifname"], i["flags"]) == "HOTSPOT" and i["ipv4"]:
            return i["ipv4"][0], i["ifname"], "VERIFIED"
    # Else if wlan with IPv4, assume client
    for i in ifaces:
        if classify_interface(i["ifname"], i["flags"]) == "WIFI" and i["ipv4"]:
            return i["ipv4"][0], i["ifname"], "UNVERIFIED"
    return None, None, "UNVERIFIED"

# ============================================================
# SPINNER
# ============================================================
SPINNER_FRAMES = "◐◓◑◒"

def spinner(message, duration=2.0, interval=0.1, success=True):
    """Animate spinner for a fixed duration or with a callable."""
    if not _cfg.get("animation", True):
        print(f"{C.GREEN}»{C.RESET} {message}")
        return
    frames = SPINNER_FRAMES
    start = time.time()
    i = 0
    hide_cursor()
    try:
        while time.time() - start < duration:
            elapsed = time.time() - start
            frame = frames[i % len(frames)]
            sys.stdout.write(
                f"\r{C.LEMON}{frame}{C.RESET} {C.WHITE}{message}{C.RESET} "
                f"{C.DIM}[{elapsed:.1f}s]{C.RESET}   "
            )
            sys.stdout.flush()
            time.sleep(interval)
            i += 1
        sym = f"{C.GREEN}✔{C.RESET}" if success else f"{C.RED}✘{C.RESET}"
        sys.stdout.write(f"\r{sym} {C.WHITE}{message}{C.RESET}   \n")
        sys.stdout.flush()
    finally:
        show_cursor()

def spinner_steps(steps):
    """Run multiple spinner steps sequentially."""
    for msg in steps:
        spinner(msg, duration=0.7)

# ============================================================
# CLIPBOARD
# ============================================================
def copy_to_clipboard(text):
    """Copy text using termux-clipboard-set if available."""
    if not cmd_exists("termux-clipboard-set"):
        print(f"\n{C.RED}⚠ Termux:API not installed.{C.RESET}")
        print(f"{C.YELLOW}Copy manually:{C.RESET}")
        print(f"{C.BRIGHT_GREEN}{text}{C.RESET}")
        return False
    try:
        p = subprocess.run(
            ["termux-clipboard-set", text],
            capture_output=True, text=True, timeout=5
        )
        if p.returncode == 0:
            print(f"{C.GREEN}✔ Copied to clipboard: {C.BRIGHT_GREEN}{text}{C.RESET}")
            return True
        else:
            print(f"{C.RED}Clipboard failed: {p.stderr.strip()}{C.RESET}")
    except Exception as e:
        print(f"{C.RED}Clipboard error: {e}{C.RESET}")
    print(f"{C.YELLOW}Copy manually:{C.RESET} {C.BRIGHT_GREEN}{text}{C.RESET}")
    return False

# ============================================================
# SCAN ENGINE (repeated scanning)
# ============================================================
def scan_network(cfg, purpose="all"):
    """
    Repeatedly scan network until result is stable 3 consecutive times
    or max duration reached.
    Returns dict with results and stability info.
    """
    max_dur = cfg.get("scan_duration", 60)
    interval = cfg.get("scan_interval", 2)
    repeated = cfg.get("repeated_scanning", True)

    if not repeated:
        max_dur = 0

    start = time.time()
    last_sig = None
    stable_count = 0
    stable_result = None
    frames = SPINNER_FRAMES
    i = 0
    msg = "Detecting Network Interfaces..."

    hide_cursor()
    try:
        while True:
            ifaces = get_interfaces_with_ips()
            gw_ip, gw_dev = get_default_gateway()
            role = determine_network_role(cfg, ifaces, gw_dev)

            if purpose == "lan":
                ip, iface, status = get_lan_ip(cfg, ifaces, role)
                sig = f"{ip}|{iface}|{status}"
                result = {"ip": ip, "iface": iface, "status": status,
                          "role": role}
            else:
                pub4, _ = get_public_ip() if cfg.get("public_ip_lookup") else (None, None)
                ip, iface, status = get_lan_ip(cfg, ifaces, role)
                sig = f"{ip}|{iface}|{status}|{pub4}|{gw_ip}|{gw_dev}|{role}"
                result = {
                    "ifaces": ifaces,
                    "gateway": gw_ip,
                    "gateway_dev": gw_dev,
                    "role": role,
                    "lan_ip": ip,
                    "lan_iface": iface,
                    "lan_status": status,
                    "public_ipv4": pub4,
                }

            if sig == last_sig:
                stable_count += 1
            else:
                stable_count = 1
                last_sig = sig
                stable_result = result

            elapsed = time.time() - start
            frame = frames[i % len(frames)]
            i += 1
            sys.stdout.write(
                f"\r{C.LEMON}{frame}{C.RESET} {C.WHITE}{msg}{C.RESET} "
                f"{C.DIM}[{elapsed:.0f}s / {max_dur}s | stable {stable_count}/3]{C.RESET}   "
            )
            sys.stdout.flush()

            if stable_count >= 3:
                break
            if elapsed >= max_dur:
                break
            time.sleep(interval)

        sys.stdout.write(
            f"\r{C.GREEN}✔{C.RESET} {C.WHITE}Scan complete{C.RESET}   \n"
        )
        sys.stdout.flush()
    except KeyboardInterrupt:
        sys.stdout.write(f"\r{C.RED}✘ Scan cancelled{C.RESET}\n")
        sys.stdout.flush()
    finally:
        show_cursor()

    return stable_result or {}

# ============================================================
# MENU: MINECRAFT LAN IP
# ============================================================
def minecraft_menu(cfg):
    while True:
        clear()
        show_banner(compact=True)
        hr()
        print(f"{C.LEMON}{C.BOLD}  MINECRAFT LAN IP / DIRECT CONNECT{C.RESET}")
        hr()
        print()
        print(f"  {C.YELLOW}[1]{C.RESET} {C.WHITE}SHOW ALL IPs{C.RESET}")
        print(f"  {C.YELLOW}[2]{C.RESET} {C.WHITE}SHOW LAN IP ONLY{C.RESET}")
        print(f"  {C.YELLOW}[0]{C.RESET} {C.WHITE}BACK{C.RESET}")
        print()
        choice = input(f"{C.GREEN}  ➤ Select: {C.RESET}").strip()

        if choice == "1":
            minecraft_show_all(cfg)
        elif choice == "2":
            minecraft_show_lan(cfg)
        elif choice == "0":
            return
        else:
            print(f"{C.RED}Invalid option{C.RESET}")
            time.sleep(0.8)

def _render_full_ips(cfg, res, has_termux):
    """Print all-detected-IPs screen."""
    clear()
    show_banner(compact=True)
    hr()
    print(f"{C.LEMON}{C.BOLD}  NETWORK STATUS{C.RESET}")
    hr()
    print()

    ifaces = res.get("ifaces", [])
    role = res.get("role", "UNKNOWN")
    lan_ip = res.get("lan_ip")
    lan_iface = res.get("lan_iface")
    lan_status = res.get("lan_status", "UNVERIFIED")
    pub4 = res.get("public_ipv4")
    gw = res.get("gateway") or "—"
    gw_dev = res.get("gateway_dev") or "—"

    active_dev = gw_dev or lan_iface or "—"

    # Collect all local v4
    all_v4 = []
    all_v6 = []
    for i in ifaces:
        for ip in i["ipv4"]:
            all_v4.append((i["ifname"], classify_interface(i["ifname"], i["flags"]), ip))
        for ip in i["ipv6"]:
            all_v6.append((i["ifname"], classify_interface(i["ifname"], i["flags"]), ip))

    # Local IPv4
    print(f"  {C.YELLOW}Local IPv4:{C.RESET}")
    if all_v4:
        for ifn, cls, ip in all_v4:
            print(f"    {C.GREEN}●{C.RESET} {C.BRIGHT_GREEN}{ip:<40}{C.RESET} "
                  f"{C.DIM}[{ifn} / {cls}]{C.RESET}")
    else:
        print(f"    {C.RED}None detected{C.RESET}")
    print()

    # Local IPv6
    print(f"  {C.YELLOW}Local IPv6:{C.RESET}")
    if all_v6:
        for ifn, cls, ip in all_v6:
            print(f"    {C.GREEN}●{C.RESET} {C.BRIGHT_GREEN}{ip:<40}{C.RESET} "
                  f"{C.DIM}[{ifn} / {cls}]{C.RESET}")
    else:
        print(f"    {C.DIM}None detected{C.RESET}")
    print()

    # Public
    print(f"  {C.YELLOW}Public IPv4:{C.RESET} "
          f"{C.BRIGHT_GREEN}{pub4 or 'N/A'}{C.RESET}")
    print(f"  {C.YELLOW}Public IPv6:{C.RESET} "
          f"{C.DIM}Not queried{C.RESET}")
    print()

    # Hotspot
    print(f"  {C.YELLOW}Hotspot Host IP:{C.RESET}")
    hotspot_ip = None
    for ifn, cls, ip in all_v4:
        if cls == "HOTSPOT":
            hotspot_ip = (ifn, ip)
            print(f"    {C.GREEN}●{C.RESET} {C.BRIGHT_GREEN}{ip}{C.RESET} {C.DIM}[{ifn}]{C.RESET}")
    if not hotspot_ip:
        print(f"    {C.RED}UNVERIFIED{C.RESET} {C.DIM}(no hotspot interface detected){C.RESET}")
    print()

    # Gateway
    print(f"  {C.YELLOW}Gateway IP:{C.RESET} "
          f"{C.BRIGHT_GREEN}{gw}{C.RESET} {C.DIM}[{gw_dev}]{C.RESET}")
    print(f"  {C.YELLOW}Active Interface:{C.RESET} "
          f"{C.BRIGHT_GREEN}{active_dev}{C.RESET}")
    print(f"  {C.YELLOW}Network Role:{C.RESET} "
          f"{C.MAGENTA}{role}{C.RESET}")
    print()

    # Minecraft LAN
    print(f"  {C.LEMON}{C.BOLD}Minecraft LAN IP:{C.RESET} "
          f"{C.BRIGHT_GREEN}{C.BOLD}{lan_ip or 'UNVERIFIED'}{C.RESET} "
          f"{C.DIM}[{lan_status}]{C.RESET}")
    print()

    # Actions
    hr()
    print(f"  {C.YELLOW}[C]{C.RESET} COPY LAN IP  "
          f"{C.YELLOW}[R]{C.RESET} REFRESH  "
          f"{C.YELLOW}[B]{C.RESET} BACK")
    hr()

def minecraft_show_all(cfg):
    spinner_steps([
        "Initializing IP CHECKER...",
        "Detecting Network Interfaces...",
        "Checking Wi-Fi...",
        "Inspecting Hotspot...",
        "Verifying LAN Address...",
        "Checking Network Routes...",
        "Finalizing Results...",
    ])

    res = scan_network(cfg, purpose="all")

    while True:
        _render_full_ips(cfg, res, True)
        key = input(f"{C.GREEN}  ➤ Choice: {C.RESET}").strip().lower()
        if key == "c":
            ip = res.get("lan_ip")
            if ip:
                copy_to_clipboard(ip)
            else:
                print(f"{C.RED}No LAN IP to copy{C.RESET}")
            pause()
        elif key == "r":
            clear()
            res = scan_network(cfg, purpose="all")
            continue
        elif key in ("b", ""):
            return
        else:
            print(f"{C.RED}Invalid option{C.RESET}")
            time.sleep(0.5)

def _render_lan_only(res):
    clear()
    show_banner(compact=True)
    hr()
    print(f"{C.LEMON}{C.BOLD}")
    print(center("MINECRAFT LAN IP"))
    print(f"{C.RESET}")
    hr()
    print()

    ip = res.get("lan_ip")
    iface = res.get("lan_iface") or "—"
    status = res.get("lan_status", "UNVERIFIED")
    role = res.get("role", "UNKNOWN")

    if ip:
        print(f"{C.BRIGHT_GREEN}{C.BOLD}")
        print(center("╔══════════════════════════════════════╗"))
        print(center(f"║  {ip:<34}  ║"))
        print(center("╚══════════════════════════════════════╝"))
        print(f"{C.RESET}")
    else:
        print(f"{C.RED}{C.BOLD}")
        print(center("╔══════════════════════════════════════╗"))
        print(center("║       UNVERIFIED - No IP found       ║"))
        print(center("╚══════════════════════════════════════╝"))
        print(f"{C.RESET}")

    print()
    label("Interface:", iface)
    label("Network Role:", role)
    sc = C.GREEN if status == "VERIFIED" else C.RED
    print(f"  {C.CYAN}{'STATUS:':<22}{C.RESET} {sc}{C.BOLD}{status}{C.RESET}")
    print()

    hr()
    print(f"  {C.YELLOW}[C]{C.RESET} COPY IP  "
          f"{C.YELLOW}[R]{C.RESET} REFRESH  "
          f"{C.YELLOW}[B]{C.RESET} BACK")
    hr()

def minecraft_show_lan(cfg):
    spinner_steps([
        "Detecting LAN IP...",
        "Checking Network Role...",
        "Verifying Interface...",
        "Finalizing...",
    ])

    res = scan_network(cfg, purpose="lan")

    while True:
        _render_lan_only(res)
        key = input(f"{C.GREEN}  ➤ Choice: {C.RESET}").strip().lower()
        if key == "c":
            ip = res.get("ip")
            if ip:
                copy_to_clipboard(ip)
            else:
                print(f"{C.RED}No IP to copy{C.RESET}")
            pause()
        elif key == "r":
            res = scan_network(cfg, purpose="lan")
            continue
        elif key in ("b", ""):
            return
        else:
            print(f"{C.RED}Invalid option{C.RESET}")
            time.sleep(0.5)

# ============================================================
# IP DETAILS / INPUT
# ============================================================
def validate_ip_input(raw):
    """Return ipaddress object or None."""
    raw = raw.strip()
    if not raw:
        return None
    try:
        return ipaddress.ip_interface(raw) if "/" in raw else ipaddress.ip_address(raw)
    except ValueError:
        return None

def analyze_private(ip_obj, raw):
    """Local-only analysis of a private IP."""
    is_iface = isinstance(ip_obj, ipaddress.IPv4Interface) or \
               isinstance(ip_obj, ipaddress.IPv6Interface)
    ip = ip_obj.ip if is_iface else ip_obj
    prefix = ip_obj.network.prefixlen if is_iface else None
    net = ip_obj.network if is_iface else None

    info = {
        "ip": str(ip),
        "version": f"IPv{ip.version}",
        "private": ip.is_private,
        "loopback": ip.is_loopback,
        "link_local": ip.is_link_local,
        "multicast": ip.is_multicast,
        "reserved": ip.is_reserved,
        "cidr_prefix": prefix,
    }
    if net:
        info["network_address"] = str(net.network_address)
        if isinstance(net, ipaddress.IPv4Network) and net.num_addresses >= 4:
            hosts = list(net.hosts())
            info["host_range"] = f"{hosts[0]} – {hosts[-1]}"
            info["broadcast"] = str(net.broadcast_address)
        elif isinstance(net, ipaddress.IPv6Network) and net.num_addresses >= 4:
            hosts = list(net.hosts())
            if hosts:
                info["host_range"] = f"{hosts[0]} – {hosts[-1]}"

    # Interface match
    ifaces = get_interfaces_with_ips()
    for i in ifaces:
        if str(ip) in i["ipv4"] or str(ip) in i["ipv6"]:
            info["interface"] = i["ifname"]

    # Neighbor cache
    neigh = get_neigh(str(ip))
    if neigh:
        info["neighbor"] = neigh

    return info

def lookup_public_info(ip_str):
    """Fetch public IP info via HTTPS. Returns dict or (None, error)."""
    url = f"https://ipinfo.io/{ip_str}/json"
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "IPChecker/1.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
            return data, None
    except urllib.error.URLError as e:
        return None, f"Network error: {e.reason}"
    except Exception as e:
        return None, str(e)

def render_public_details(data, ip_obj):
    clear()
    show_banner(compact=True)
    hr()
    print(f"{C.LEMON}{C.BOLD}  PUBLIC IP DETAILS{C.RESET}")
    hr()

    def sec(t):
        print(f"\n  {C.YELLOW}{C.BOLD}{t}{C.RESET}")
        print(f"  {C.DIM}{'─' * (term_width() - 4)}{C.RESET}")

    sec("GENERAL")
    label("IP Address", data.get("ip", str(ip_obj)))
    label("IP Version", f"IPv{ip_obj.version}")
    label("IP Classification", "Public")
    label("Network Range", "N/A")

    sec("LOCATION (approximate)")
    label("Country", data.get("country", "N/A"))
    label("Country Code", "N/A")
    label("Region", data.get("region", "N/A"))
    label("City", data.get("city", "N/A"))
    label("Timezone", data.get("timezone", "N/A"))

    sec("NETWORK")
    label("ISP", data.get("org", "N/A"))
    label("Organization", data.get("org", "N/A"))
    label("ASN", data.get("org", "N/A").split()[0] if data.get("org") else "N/A")
    label("ASN Organization", data.get("org", "N/A"))
    label("Reverse DNS", data.get("hostname", "N/A"))

    sec("ADDITIONAL")
    label("Hosting Provider", "N/A")
    label("VPN / Proxy", "N/A")
    label("Datacenter", "N/A")

    print()
    print(f"  {C.DIM}Note: IP-based location is approximate and cannot{C.RESET}")
    print(f"  {C.DIM}identify an exact home address.{C.RESET}")
    print()
    hr()
    print(f"  {C.YELLOW}[C]{C.RESET} COPY IP  "
          f"{C.YELLOW}[A]{C.RESET} COPY ALL  "
          f"{C.YELLOW}[N]{C.RESET} NEW  "
          f"{C.YELLOW}[B]{C.RESET} BACK")
    hr()

    return data

def render_private_details(info):
    clear()
    show_banner(compact=True)
    hr()
    print(f"{C.LEMON}{C.BOLD}  PRIVATE / LOCAL IP DETAILS{C.RESET}")
    hr()

    def sec(t):
        print(f"\n  {C.YELLOW}{C.BOLD}{t}{C.RESET}")
        print(f"  {C.DIM}{'─' * (term_width() - 4)}{C.RESET}")

    sec("CLASSIFICATION")
    label("IP Address", info["ip"])
    label("IP Version", info["version"])
    label("Private", "Yes" if info["private"] else "No")
    label("Loopback", "Yes" if info["loopback"] else "No")
    label("Link-Local", "Yes" if info["link_local"] else "No")
    label("Multicast", "Yes" if info["multicast"] else "No")
    label("Reserved", "Yes" if info["reserved"] else "No")

    if info.get("cidr_prefix") is not None:
        sec("CIDR DETAILS")
        label("Prefix", f"/{info['cidr_prefix']}")
        label("Network Address", info.get("network_address", "N/A"))
        label("Broadcast Address", info.get("broadcast", "N/A"))
        label("Usable Hosts", info.get("host_range", "N/A"))

    if info.get("interface"):
        sec("LOCAL INTERFACE")
        label("Interface", info["interface"])

    if info.get("neighbor"):
        n = info["neighbor"]
        sec("NEIGHBOR CACHE")
        label("MAC Address", n.get("mac") or "N/A")
        label("State", n.get("state") or "N/A")
        label("Interface", n.get("dev") or "N/A")

    print()
    hr()
    print(f"  {C.YELLOW}[C]{C.RESET} COPY IP  "
          f"{C.YELLOW}[A]{C.RESET} COPY ALL  "
          f"{C.YELLOW}[N]{C.RESET} NEW  "
          f"{C.YELLOW}[B]{C.RESET} BACK")
    hr()

def ip_details_menu(cfg):
    last_input = ""
    while True:
        clear()
        show_banner(compact=True)
        hr()
        print(f"{C.LEMON}{C.BOLD}  IP DETAILS & INFORMATION{C.RESET}")
        hr()
        print()
        print(f"  {C.CYAN}Enter any IPv4, IPv6, Private, Public, or CIDR.{C.RESET}")
        print()
        if last_input:
            print(f"  {C.DIM}Last: {last_input}{C.RESET}")
        print()
        print(f"  {C.YELLOW}[1]{C.RESET} ENTER IP ADDRESS")
        print(f"  {C.YELLOW}[2]{C.RESET} LOOKUP IP")
        print(f"  {C.YELLOW}[3]{C.RESET} CLEAR")
        print(f"  {C.YELLOW}[0]{C.RESET} BACK")
        print()

        choice = input(f"{C.GREEN}  ➤ Select: {C.RESET}").strip()

        if choice == "0":
            return
        if choice == "3":
            last_input = ""
            continue
        if choice in ("1", "2"):
            raw = input(f"{C.CYAN}  IP Address: {C.RESET}").strip()
            last_input = raw
            obj = validate_ip_input(raw)
            if not obj is not None:
                print(f"{C.RED}✘ Invalid IP address format{C.RESET}")
                pause()
                continue

            ip = obj.ip if hasattr(obj, "ip") else obj

            if ip.is_private or ip.is_loopback or ip.is_link_local:
                info = analyze_private(obj, raw)
                render_private_details(info)
                key = input(f"{C.GREEN}  ➤ Choice: {C.RESET}").strip().lower()
                if key == "c":
                    copy_to_clipboard(info["ip"])
                    pause()
                elif key == "a":
                    txt = "\n".join(f"{k}: {v}" for k, v in info.items())
                    copy_to_clipboard(txt)
                    pause()
                elif key == "n":
                    continue
            else:
                # Public — confirm lookup
                if cfg.get("confirm_public_lookup", True):
                    print(f"{C.YELLOW}  This will send {ip} to a public IP-info service.{C.RESET}")
                    yn = input(f"  Continue? [Y/n]: ").strip().lower()
                    if yn not in ("", "y", "yes"):
                        continue
                data, err = lookup_public_info(str(ip))
                if err:
                    print(f"{C.RED}✘ Lookup failed: {err}{C.RESET}")
                    pause()
                    continue
                render_public_details(data, ip)
                key = input(f"{C.GREEN}  ➤ Choice: {C.RESET}").strip().lower()
                if key == "c":
                    copy_to_clipboard(str(ip))
                    pause()
                elif key == "a":
                    txt = "\n".join(f"{k}: {v}" for k, v in data.items())
                    copy_to_clipboard(txt)
                    pause()
                elif key == "n":
                    continue
        else:
            print(f"{C.RED}Invalid option{C.RESET}")
            time.sleep(0.6)

# ============================================================
# SETTINGS
# ============================================================
def settings_menu(cfg):
    while True:
        clear()
        show_banner(compact=True)
        hr()
        print(f"{C.LEMON}{C.BOLD}  SETTINGS{C.RESET}")
        hr()

        def sec(t):
            print(f"\n  {C.YELLOW}{C.BOLD}{t}{C.RESET}")
            print(f"  {C.DIM}{'─' * (term_width() - 4)}{C.RESET}")

        def opt(n, title, val):
            print(f"    {C.YELLOW}[{n}]{C.RESET} {title:<32} {C.BRIGHT_GREEN}{val}{C.RESET}")

        sec("SCANNING")
        opt(1, "Scan Duration", f"{cfg['scan_duration']}s")
        opt(2, "Scan Interval", f"{cfg['scan_interval']}s")
        opt(3, "Automatic Refresh", "ON" if cfg["auto_refresh"] else "OFF")
        opt(4, "Repeated Scanning", "ON" if cfg["repeated_scanning"] else "OFF")

        sec("NETWORK")
        opt(5, "Network Role", cfg["network_role"])
        opt(6, "Public IP Lookup", "ON" if cfg["public_ip_lookup"] else "OFF")
        opt(7, "Hotspot Detection", "ON" if cfg["hotspot_detection"] else "OFF")
        opt(8, "Local IP Detection", "ON" if cfg["local_ip_detection"] else "OFF")

        sec("APPEARANCE")
        opt(9, "Theme", cfg["theme"])
        opt(10, "Animation", "ON" if cfg["animation"] else "OFF")
        opt(11, "Layout", cfg["layout"])

        sec("PRIVACY")
        opt(12, "Lookup History", "ON" if cfg["lookup_history"] else "OFF")
        opt(13, "Clear Local History", "—")
        opt(14, "Public Lookup Confirmation", "ON" if cfg["confirm_public_lookup"] else "OFF")

        print(f"\n  {C.YELLOW}[0]{C.RESET} {C.WHITE}Back to Main Menu{C.RESET}")
        print()

        choice = input(f"{C.GREEN}  ➤ Select: {C.RESET}").strip()

        if choice == "0":
            save_config(cfg)
            return
        elif choice == "1":
            cycle = [10, 20, 30, 60]
            i = cycle.index(cfg["scan_duration"]) if cfg["scan_duration"] in cycle else 3
            cfg["scan_duration"] = cycle[(i + 1) % len(cycle)]
        elif choice == "2":
            cycle = [1, 2, 3]
            i = cycle.index(cfg["scan_interval"]) if cfg["scan_interval"] in cycle else 1
            cfg["scan_interval"] = cycle[(i + 1) % len(cycle)]
        elif choice == "3":
            cfg["auto_refresh"] = not cfg["auto_refresh"]
        elif choice == "4":
            cfg["repeated_scanning"] = not cfg["repeated_scanning"]
        elif choice == "5":
            cycle = ["AUTO", "HOTSPOT HOST", "CONNECTED CLIENT"]
            i = cycle.index(cfg["network_role"]) if cfg["network_role"] in cycle else 0
            cfg["network_role"] = cycle[(i + 1) % len(cycle)]
        elif choice == "6":
            cfg["public_ip_lookup"] = not cfg["public_ip_lookup"]
        elif choice == "7":
            cfg["hotspot_detection"] = not cfg["hotspot_detection"]
        elif choice == "8":
            cfg["local_ip_detection"] = not cfg["local_ip_detection"]
        elif choice == "9":
            cfg["theme"] = "GREEN" if cfg["theme"] == "LEMON_GREEN" else "LEMON_GREEN"
        elif choice == "10":
            cfg["animation"] = not cfg["animation"]
        elif choice == "11":
            cfg["layout"] = "COMPACT" if cfg["layout"] == "FULL" else "FULL"
        elif choice == "12":
            cfg["lookup_history"] = not cfg["lookup_history"]
        elif choice == "13":
            try:
                if HISTORY_FILE.exists():
                    HISTORY_FILE.unlink()
                print(f"{C.GREEN}✔ History cleared{C.RESET}")
            except Exception as e:
                print(f"{C.RED}Error: {e}{C.RESET}")
            time.sleep(0.7)
        elif choice == "14":
            cfg["confirm_public_lookup"] = not cfg["confirm_public_lookup"]
        else:
            print(f"{C.RED}Invalid option{C.RESET}")
            time.sleep(0.6)

        save_config(cfg)

# ============================================================
# ABOUT
# ============================================================
def about_screen():
    clear()
    show_banner(compact=False)
    hr()
    print(f"{C.LEMON}{C.BOLD}  ABOUT IP CHECKER{C.RESET}")
    hr()
    print()
    label("Application", "IP CHECKER", C.YELLOW, C.BRIGHT_GREEN)
    label("Version", VERSION, C.YELLOW, C.BRIGHT_GREEN)
    label("Developer", DEVELOPER, C.YELLOW, C.BRIGHT_GREEN)
    label("Platform", "Android Termux", C.YELLOW, C.BRIGHT_GREEN)
    label("Language", "Python 3", C.YELLOW, C.BRIGHT_GREEN)
    label("License", "Free for personal use", C.YELLOW, C.BRIGHT_GREEN)
    print()
    hr()
    print(f"{C.CYAN}  FEATURES{C.RESET}")
    print(f"  {C.GREEN}●{C.RESET} Detect LAN / Wi-Fi / Hotspot IPs")
    print(f"  {C.GREEN}●{C.RESET} Minecraft Direct-Connect helper")
    print(f"  {C.GREEN}●{C.RESET} Public & Private IP analysis")
    print(f"  {C.GREEN}●{C.RESET} Repeated scanning engine")
    print(f"  {C.GREEN}●{C.RESET} Clipboard integration (Termux:API)")
    print(f"  {C.GREEN}●{C.RESET} Lightweight, no root required")
    print()
    hr()
    pause()

# ============================================================
# MAIN MENU
# ============================================================
def main_menu(cfg):
    while True:
        clear()
        show_banner(compact=(cfg.get("layout") == "COMPACT"))
        hr()
        print(f"{C.LEMON}{C.BOLD}  MAIN MENU{C.RESET}")
        hr()
        print()
        print(f"  {C.YELLOW}[1]{C.RESET} {C.WHITE}MINECRAFT LAN IP / DIRECT CONNECT{C.RESET}")
        print(f"  {C.YELLOW}[2]{C.RESET} {C.WHITE}IP DETAILS / IP INPUT{C.RESET}")
        print(f"  {C.YELLOW}[3]{C.RESET} {C.WHITE}SETTINGS{C.RESET}")
        print(f"  {C.YELLOW}[4]{C.RESET} {C.WHITE}ABOUT IP CHECKER{C.RESET}")
        print(f"  {C.YELLOW}[0]{C.RESET} {C.WHITE}EXIT{C.RESET}")
        print()
        hr()

        # Quick status line
        try:
            ifaces = get_interfaces_with_ips()
            gw, gwdev = get_default_gateway()
            role = determine_network_role(cfg, ifaces, gwdev)
            ip, iface, status = get_lan_ip(cfg, ifaces, role)
            if ip:
                print(f"  {C.DIM}LAN IP:{C.RESET} {C.BRIGHT_GREEN}{ip}{C.RESET} "
                      f"{C.DIM}({iface})  Role: {role}{C.RESET}")
            else:
                print(f"  {C.DIM}LAN IP: {C.RED}UNVERIFIED{C.RESET}")
        except Exception:
            pass
        hr()

        choice = input(f"{C.GREEN}  ➤ Select: {C.RESET}").strip()

        if choice == "1":
            minecraft_menu(cfg)
        elif choice == "2":
            ip_details_menu(cfg)
        elif choice == "3":
            settings_menu(cfg)
        elif choice == "4":
            about_screen()
        elif choice == "0":
            return
        else:
            print(f"{C.RED}Invalid option{C.RESET}")
            time.sleep(0.6)

# ============================================================
# ENTRY POINT
# ============================================================
_cfg = {}

def main():
    global _cfg
    try:
        _cfg = load_config()

        # Startup animation
        clear()
        show_banner(compact=(_cfg.get("layout") == "COMPACT"))
        spinner_steps([
            "Initializing IP CHECKER...",
            "Loading Configuration...",
            "Detecting Termux Environment...",
            "Ready.",
        ])

        # Check environment
        if not cmd_exists("ip"):
            clear()
            print(f"{C.RED}⚠ 'ip' command not found.{C.RESET}")
            print(f"{C.YELLOW}Install with:{C.RESET} pkg install iproute2")
            pause()
            return

        main_menu(_cfg)

    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        clear()
        print(f"{C.LEMON}{C.BOLD}")
        print(center("Thank you for using IP CHECKER!"))
        print(f"{C.RESET}")
        print(f"{C.GREEN}{center(f'— {DEVELOPER}')}{C.RESET}")
        print()

if __name__ == "__main__":
    main()