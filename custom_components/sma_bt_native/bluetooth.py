from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass

_LOGGER = logging.getLogger(__name__)
MAC_RE = re.compile(r"([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})")

@dataclass(frozen=True)
class BluetoothDevice:
    address: str
    name: str | None = None
    rssi: int | None = None


def normalize_mac(address: str) -> str:
    return address.strip().upper()


def _run_bluetoothctl(*args: str, timeout: int = 12) -> str:
    try:
        completed = subprocess.run(
            ["bluetoothctl", *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        _LOGGER.debug("bluetoothctl not found")
        return ""
    except subprocess.TimeoutExpired:
        _LOGGER.debug("bluetoothctl %s timed out", args)
        return ""
    if completed.returncode != 0:
        _LOGGER.debug("bluetoothctl %s failed: %s", args, completed.stderr.strip())
    return completed.stdout or ""


def discover_sma_devices(timeout: int = 10) -> list[BluetoothDevice]:
    """Best-effort discovery for SMA Bluetooth devices.

    HAOS on Raspberry Pi normally exposes bluetoothctl. We first start a short scan,
    then read known devices. Manual entry is always available as fallback.
    """
    _run_bluetoothctl("--timeout", str(timeout), "scan", "on", timeout=timeout + 3)
    output = _run_bluetoothctl("devices", timeout=5)
    devices: list[BluetoothDevice] = []
    seen: set[str] = set()
    for line in output.splitlines():
        match = MAC_RE.search(line)
        if not match:
            continue
        address = normalize_mac(match.group(1))
        name = line[match.end():].strip() or None
        haystack = f"{address} {name or ''}".lower()
        # SMA devices often have generic names, so keep every discovered MAC but rank/name SMA ones in the UI.
        if address not in seen:
            devices.append(BluetoothDevice(address=address, name=name))
            seen.add(address)
    return devices


def read_rssi_dbm(address: str) -> int | None:
    """Read RSSI in dBm via bluetoothctl if BlueZ currently exposes it."""
    output = _run_bluetoothctl("info", normalize_mac(address), timeout=5)
    for line in output.splitlines():
        if "RSSI:" not in line:
            continue
        try:
            return int(line.split("RSSI:", 1)[1].strip().split()[0])
        except (ValueError, IndexError):
            return None
    return None


def rssi_to_percent(rssi: int | None) -> int | None:
    if rssi is None:
        return None
    # Conservative Bluetooth mapping: -100 dBm = 0 %, -40 dBm = 100 %.
    return max(0, min(100, round((rssi + 100) * 100 / 60)))


def read_device_name(address: str) -> str | None:
    """Read the current BlueZ name/alias for a Bluetooth address."""
    output = _run_bluetoothctl("info", normalize_mac(address), timeout=5)
    name = None
    alias = None
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("Name:"):
            name = line.split("Name:", 1)[1].strip() or None
        elif line.startswith("Alias:"):
            alias = line.split("Alias:", 1)[1].strip() or None
    return name or alias


def extract_serial_from_name(name: str | None) -> str | None:
    if not name:
        return None
    # Seen names: "SMA001d SN: 2100264508 SN2100264508"
    match = re.search(r"SN[:\s]+(\d{6,})", name, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"SN(\d{6,})", name, re.IGNORECASE)
    if match:
        return match.group(1)
    return None
