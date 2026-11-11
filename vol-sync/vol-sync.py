#!/usr/bin/env python3
"""bobot volume sync.

Mirrors AVRCP absolute volume between the Mac (A2DP source -> Pi) and the
Acton (Pi -> A2DP sink) by reading/writing MediaTransport1.Volume over D-Bus,
and undoes PipeWire's software gain on the Mac's stream node, so that the
Mac slider behaves like it did when connected directly to the Acton.

Needs: sudo apt install python3-dbus python3-gi
Run:   python3 volsync.py
"""
import json
import subprocess
import time

import dbus
import dbus.mainloop.glib
from gi.repository import GLib

BLUEZ = "org.bluez"
TRANSPORT = "org.bluez.MediaTransport1"
DEVICE = "org.bluez.Device1"
ACTON_HINT = "acton"                # substring of the Acton's Bluetooth alias (case-insensitive)
SUPPRESS_S = 0.4                    # ignore echoes of our own writes for this long
NEUTRALIZE_DELAYS_MS = (50, 250, 1000)

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()

roles = {}      # transport path -> "mac" | "acton"
suppress = {}   # transport path -> monotonic time until which events are ignored


def log(*args):
    print(time.strftime("%H:%M:%S"), *args, flush=True)


def props(path):
    return dbus.Interface(bus.get_object(BLUEZ, path), "org.freedesktop.DBus.Properties")


def path_of(role):
    return next((p for p, r in roles.items() if r == role), None)


def scan():
    om = dbus.Interface(bus.get_object(BLUEZ, "/"), "org.freedesktop.DBus.ObjectManager")
    found = {}
    for path, ifaces in om.GetManagedObjects().items():
        t = ifaces.get(TRANSPORT)
        if t is None:
            continue
        alias = str(props(t["Device"]).Get(DEVICE, "Alias"))
        found[str(path)] = "acton" if ACTON_HINT in alias.lower() else "mac"
    roles.clear()
    roles.update(found)
    log("transports:", roles)


def neutralize():
    """Reset the software gain PipeWire applies to the Mac stream node to 1.0."""
    try:
        out = subprocess.run(["pw-dump"], capture_output=True, text=True, timeout=5).stdout
        for obj in json.loads(out):
            p = obj.get("info", {}).get("props", {})
            if obj.get("type") == "PipeWire:Interface:Node" and p.get("node.name", "").startswith("bluez_input"):
                subprocess.run(["pw-cli", "s", str(obj["id"]), "Props", "{ volume: 1.0 }"],
                               capture_output=True, timeout=5)
    except Exception as e:  # never let a PipeWire hiccup kill the loop
        log("neutralize failed:", e)
    return False  # one-shot GLib timeout


def schedule_neutralize():
    # BlueZ and PipeWire both react to the same property change; re-assert after they have.
    for ms in NEUTRALIZE_DELAYS_MS:
        GLib.timeout_add(ms, neutralize)


def set_volume(path, v):
    try:
        suppress[path] = time.monotonic() + SUPPRESS_S
        props(path).Set(TRANSPORT, "Volume", dbus.UInt16(v))
        if roles.get(path) == "mac":
            schedule_neutralize()
    except dbus.DBusException as e:
        log("set failed:", roles.get(path), e.get_dbus_message())


def reconcile():
    """Mac wins: push the Mac's volume to the Acton (stream start / reconnect)."""
    mac, acton = path_of("mac"), path_of("acton")
    if not (mac and acton):
        return
    try:
        v = int(props(mac).Get(TRANSPORT, "Volume"))
    except dbus.DBusException as e:
        log("reconcile failed:", e.get_dbus_message())
        return
    log("reconcile: acton <-", v)
    set_volume(acton, v)


def on_props(iface, changed, invalidated, path=None):
    if iface != TRANSPORT:
        return
    path = str(path)
    if path not in roles:
        scan()
        if path not in roles:
            return
    role = roles[path]

    if "State" in changed:
        state = str(changed["State"])
        log(role, "state ->", state)
        if state == "active":
            if role == "mac":
                schedule_neutralize()
            reconcile()

    if "Volume" in changed:
        v = int(changed["Volume"])
        if role == "mac":
            schedule_neutralize()
        if time.monotonic() < suppress.get(path, 0):
            return  # echo of our own write
        log(role, "volume ->", v)
        other = path_of("acton" if role == "mac" else "mac")
        if other:
            set_volume(other, v)


def on_topology(*_args):
    scan()
    GLib.timeout_add(300, lambda: reconcile() or False)


def main():
    scan()
    reconcile()
    bus.add_signal_receiver(on_props, "PropertiesChanged", "org.freedesktop.DBus.Properties",
                            BLUEZ, path_keyword="path")
    for sig in ("InterfacesAdded", "InterfacesRemoved"):
        bus.add_signal_receiver(on_topology, sig, "org.freedesktop.DBus.ObjectManager", BLUEZ)
    log("volsync running")
    try:
        GLib.MainLoop().run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
