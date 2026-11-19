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

## 📶 Extending Bluetooth Range (ESPHome Bluetooth Proxy)

If your Home Assistant server is located in a basement, server closet, or another floor far from the bedroom—or if you get `no_devices_found` during setup due to weak BLE signal—you can extend your Bluetooth range over Wi-Fi using an inexpensive **ESP32** running an **ESPHome Bluetooth Proxy**:

* **Why it works:** Home Assistant's Bluetooth integration natively supports ESPHome Bluetooth Proxies with active connections (`active: true`). Once adopted, Home Assistant automatically routes commands to your Hatch Rest through the proxy with zero extra configuration in this integration.
* **Hardware needed:** Any standard **ESP32** development board (e.g., ESP32-WROOM-32 or M5Stack Atom Lite) and a 5V/500mA+ USB power adapter. *(Note: Avoid ESP32-S2 boards, which lack Bluetooth.)*
* **Quick setup:**
  1. Plug the ESP32 into your computer via USB and open the [ESPHome Bluetooth Proxy web installer](https://esphome.io/projects/?type=bluetooth) in Chrome or Edge.
  2. Click **Install Bluetooth Proxy**, connect your Wi-Fi credentials, and adopt the discovered ESPHome device in Home Assistant (**Settings → Devices & Services**).
  3. Place the ESP32 in a hallway or outlet near the bedroom(s), wait ~30 seconds for advertisements to populate, and add the Hatch Rest integration.
* **Multi-unit support:** A single ESP32 Bluetooth Proxy supports up to **3 simultaneous active BLE connections**, making one proxy plenty to control multiple 1st-gen Hatch Rest units in adjacent bedrooms.

## 🧪 Contributing

Issues and PRs are welcome!

If you improve the async BLE API or add new services (timers, programs, gradients), feel free to submit a pull request.
