# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python Jupyter notebook–based GUI application for the USF WEPS (Wearable Electronic Patch Sensors) research project. It controls electrochemical sensor experiments via an ESP32-S3 microcontroller and logs/visualizes sensor readings in real-time.

## Running the Application

Open and run either notebook in Jupyter:

```
jupyter notebook
```

- [GUI_main_page_wStop-2026.ipynb](GUI_main_page_wStop-2026.ipynb) — original version
- [GUI_main_page_wStop_2026_Modified.ipynb](GUI_main_page_wStop_2026_Modified.ipynb) — adds automated Windows Camera recording synchronized with data collection

Run all cells to launch the Tkinter GUI window. The GUI must be run interactively (not headless).

## Dependencies

No requirements file exists. Key packages needed:

```
pip install pyserial requests openpyxl matplotlib pyautogui
```

`tkinter` and standard library modules (`threading`, `time`, `os`, `subprocess`, `shutil`) are included with Python.

## Architecture

Both notebooks contain all application logic in a single notebook. The structure within each notebook:

- **Imports and globals** — serial port handle, WiFi base URL (`http://192.168.4.1`), shared state for current/voltage readings
- **Hardware communication layer** — `fetch_current_wifi()` / `fetch_current_uart()` make HTTP GET or serial reads; `send_data_wifi()` / `send_data_uart()` push config (voltage, flow rate, syringe size) to the device
- **Data logging** — writes input parameters to `C:\WEPS(final files)\input_data.txt` and timestamped readings to `C:\WEPS(final files)\output_data.txt`; these paths are hardcoded
- **Real-time plot** — matplotlib figure embedded in the Tkinter window; scrolls a 100-point window of Time vs. Current
- **GUI layer** — Tkinter `LabelFrame` widgets for inputs (voltage, syringe size, flow rate, current limit, COM port), connection mode toggle (UART/WiFi), and action buttons (Fetch, Stop, LaserGRBL integration)
- **Modified version extras** — `start_camera_recording()` and `stop_camera_recording()` launch the Windows Camera app via `subprocess` and send spacebar keystrokes via `pyautogui`

## Hardware Context

- **ESP32-S3** communicates over WiFi (access point mode at `192.168.4.1`) or UART at 115200 baud
- The GUI sends experiment parameters and receives current (mA) and voltage (V) readings
- LaserGRBL is an external engraving application invoked via `subprocess`; G-code and image file uploads are supported through a file dialog
- Firmware/Arduino code for the ESP32-S3 is **not** in this repository
