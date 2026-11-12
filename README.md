# IP CHECKER

**Advanced Network & Minecraft LAN IP Utility for Android Termux**

- **Developer:** KSURitam
- **Version:** 1.0.0
- **Platform:** Android Termux (ARM64)
- **Language:** Python 3
- **License:** Free for personal use

---

## 1. Introduction

IP CHECKER is a lightweight, full-featured terminal network utility
built specifically for **Android Termux**. It is designed for:

- Finding your **LAN IP** for Minecraft Direct Connect
- Distinguishing **Hotspot Host** vs **Connected Client** roles
- Analyzing **public and private IPs**
- Being **safe**, **offline-friendly**, and **root-free**

No root, Magisk, or Shizuku is required.                                              

---

## 2. Features

- 🎨 Colorful terminal UI (Lemon Yellow + Green theme)
- 🧱 Large startup ASCII banner
- 📡 Detect all local IPv4 / IPv6 interfaces
- 🎯 Minecraft LAN IP detection with role inference
- 🔁 Repeated scanning engine (stable-3 auto-finish)
- ⏱️ Live spinner with elapsed time
- 🌐 Public IP lookup via HTTPS
- 🔒 Local-only private IP analysis (never uploaded)
- ⚙️ JSON settings persistence
- 📋 Clipboard support via Termux:API (optional)
- 📦 Zero heavy dependencies, minimal RAM

---

3. #  Main Menu
```bash 
[1] MINECRAFT LAN IP / DIRECT CONNECT
[2] IP DETAILS / IP INPUT
[3] SETTINGS
[4] ABOUT IP CHECKER
[0] EXIT
```
4. # Show All IPs
```bash
Menu: [1] → [1]

Displays:

· Local IPv4 (per interface)
· Local IPv6 (per interface)
· Public IPv4
· Hotspot Host IP (if hosting)
· Gateway IP
· Active Interface
· Network Role (HOTSPOT HOST / CONNECTED CLIENT / UNKNOWN)

Actions: [C] Copy LAN IP · [R] Refresh · [B] Back
```

5. # Show LAN IP Only
```bash
Menu: [1] → [2]

Shows only the single LAN IP relevant for Minecraft hosting.

· VERIFIED — role clearly determined
· UNVERIFIED — role could not be determined (do not trust blindly)
```

6. # Minecraft Direct Connect
```bash
1. Open Minecraft → Play → Friends → Add Server
2. Server Address: <LAN_IP>
3. Port: enter manually (default 19132 for Bedrock, 25565 for Java)
4. Both devices must be on the same Wi-Fi or Hotspot network

⚠️ IP CHECKER never invents or appends ports. You must type the port
t yoursel
```

7. # IP Details / IP Input
```bash
Menu: [2]

· Accepts IPv4, IPv6, CIDR
· Private → local analysis only (never uploaded)
· Public → HTTPS lookup (user-confirmed)
```
```bash
Private IP shows

· Classification (private / loopback / link-local / reserved)
· CIDR prefix, network, broadcast, host range
· Matching local interface (if any)
· Neighbor cache (MAC / state) if present

Public IP shows

· Country, region, city, timezone
· ISP / Org / ASN
· Reverse DNS

ℹ️ Location is approximate. It cannot reveal an exact home address
```

8. # Settings

Menu: [3]
```bash
· Scan Duration: 10 / 20 / 30 / 60s
· Scan Interval: 1 / 2 / 3s
· Auto Refresh, Repeated Scanning
· Network Role: AUTO / HOTSPOT HOST / CONNECTED CLIENT
· Public IP Lookup ON/OFF
· Hotspot Detection ON/OFF
· Local IP Detection ON/OFF
· Theme: Lemon-Green
· Animation ON/OFF
· Layout: Full / Compact
· Lookup History ON/OFF
· Clear Local History
· Public Lookup Confirmation
```
```bash
Saved to: ~/.ip_checker/config.json
```
9. # Troubleshooting

Problem Fix
```bash
_______________________________________________________________________
ip: command not found| pkg install iproute2 -y                                              |
Clipboard not working  |Install termux-api + Termux:API app                    |
LAN IP shows                  |UNVERIFIED Toggle Network Role in Settings      |
Public IP lookup fails      |Check internet / try again later                               |
No IP detected                   |Connect to Wi-Fi or enable Hotspot                        |
______________________________________________________________________ ___|  
```              
10. # Android Permission Limitations

· ip addr / ip route may be restricted on some devices
· dumpsys wifi output is often restricted without root — IP CHECKER
  treats it as optional only
· Hotspot interfaces (ap0, swlan0, etc.) may not be exposed on
  all OEM ROMs → shows UNVERIFIED in that case

IP CHECKER never guesses an IP if the data is unavailable.


11. # Privacy & Security
```bash

· ❌ No telemetry
· ❌ No analytics
· ❌ No ads
· ❌ No private IP uploads
· ✅ HTTPS-only public lookups
· ✅ Local JSON storage only
· ❌ No port scanning / no network attacks
```

12. # Limitations
```bash
· Public IP location data comes from third-party services and is
  approximate
· VPN / proxy / datacenter classification may be N/A depending on
  the lookup service
· Hotspot interface naming varies by OEM; if not exposed, status is
  UNVERIFIED
· Clipboard requires Termux:API + companion app
```
```bash
Requirement Status
Android Termux only ✅
No root ✅
Large ASCII banner ✅
Lemon Yellow + Green ✅
Full-screen UI ✅
5-option main menu ✅
Minecraft LAN submenu ✅
Show All IPs (8 fields) ✅
Show LAN IP Only ✅
Role: Host / Client / Unknown ✅
Repeated scanning engine ✅
Spinner + elapsed time ✅
IP Details (IPv4/v6/CIDR) ✅
Public lookup (HTTPS) ✅
Private analysis (local-only) ✅
Settings (JSON) ✅
Clipboard (Termux:API) ✅
Lightweight / stdlib only ✅
README + install.sh + run.sh ✅
```

# Install 
```bash
git clone https://github.com/Anshaks/IP-CHECKER.git
```
```bash
cd IP-CHECKER
```
```bash
bash install.sh
```
