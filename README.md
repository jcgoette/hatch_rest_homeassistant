# Hatch Rest – Home Assistant Integration

This is a custom Home Assistant integration for controlling the **Hatch Rest** (1st-generation) nightlight and sound machine over Bluetooth Low Energy (BLE).

It provides a fully asynchronous, locally-controlled interface using a rewritten BLE API based on — and with gratitude to — the original work by **kjoconnor** in the `pyhatchbabyrest` project.

## ✨ Features

* **Local BLE control** — no cloud required
* **Three (3) entities exposed:**
  * Light (RGB + brightness)
  * Switch (main power)
  * Media Player (sounds + volume)

## 📦 Installation

### HACS

1. Add this repository as a **Custom Repository**
   *(HACS → Integrations → Custom Repositories)*
2. Search for **Hatch Rest**
3. Install → Restart Home Assistant

## 🔍 Adding the Device

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **Hatch Rest**
3. Choose your discovered device from the list
4. Confirm the Bluetooth address
5. Done!

## 🧩 Supported Entities

### 🔌 Switch
* Master on/off power state of the device

### 🟡 Light

### 🔊 Media Player

## 📡 Bluetooth Requirements

Because the Hatch Rest is a BLE device:

* A compatible Home Assistant Bluetooth controller is required


This integration uses BLE connections aggressively but cleanly:

* Queues operations
* Avoids simultaneous connects
* Disconnects when idle
* Automatically retries on common BLE failures

## 🧪 Contributing

Issues and PRs are welcome!

If you improve the async BLE API or add new services (timers, programs, gradients), feel free to submit a pull request.
