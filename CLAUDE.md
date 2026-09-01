# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python Tkinter GUI application for the USF WEPS (Wearable Electronic Patch Sensors) research project. It controls electrochemical sensor experiments via an ESP32-S3 microcontroller and logs/visualizes sensor readings in real-time.

All application logic lives in [main.py](main.py) — a single script, no package structure, no entry-point guard (the GUI is built at module level and `window.mainloop()` runs at the end).

## Running the Application

```
python main.py
```

The GUI must be run interactively (not headless), on Windows, on the lab machine attached to the ESP32-S3. It cannot be meaningfully run or tested in this environment — do not claim a change is verified by running the app; syntax-check it and say what was not exercised.

### Typical lab run

1. **Open the Windows Camera app and switch it to video mode** before anything else. `start_camera_recording()` looks for a window titled "Camera" and aborts the recording with an error dialog if it is not already open — it does not launch the app.
2. Select the COM port (**Refresh COM Ports** if it is not listed), then **Connect**.
3. Leave the connection dropdown on **UART** (the default).
4. Fill in Voltage (V), Syringe Size (ml), Speed (ml/hr), Current limit (mA), then **Send to Device**.
5. **Fetch Current** — this starts one run: it mints a new `run_id` folder, saves the input values, starts the camera recording, and begins polling.
6. **Stop Fetch** — ends the run and stops the camera recording.

Repeat 4–6 for each recording; each one gets its own folder. **Stop Process** is separate — it sends a `STOP` command to the device and does not end the logging run.

## The notebooks are frozen history

[GUI_main_page_wStop-2026.ipynb](GUI_main_page_wStop-2026.ipynb) and [GUI_main_page_wStop_2026_Modified.ipynb](GUI_main_page_wStop_2026_Modified.ipynb) are the earlier notebook versions of this application, kept only for reference.

**They are not the application and must never be edited.** `main.py` is the single source of truth. When changing behavior, change `main.py` only — do not mirror changes into the notebooks, and do not treat their contents as current.

## Dependencies

No requirements file exists. Key packages needed:

```
pip install pyserial requests matplotlib pyautogui pygetwindow
```

`tkinter` and standard library modules (`threading`, `time`, `os`, `subprocess`) are included with Python.

## Architecture

Structure within [main.py](main.py), in file order:

- **Imports and globals** — `DATA_DIR` (fixed output path), `run_id`, `start_time`, `running`, the serial handle, and `ESP32_IP`
- **LaserGRBL integration** — `open_lasergrbl_with_file()` / `upload_file()`; a file dialog takes G-code or image files and `subprocess.Popen` hands them to LaserGRBL at a hardcoded path
- **Serial setup** — `get_com_ports()` / `refresh_ports()` / `connect_to_com_port()` open the port at 115200 baud
- **Sending config to the device** — `send_data_to_device()` dispatches on the connection dropdown to `send_data_via_uart()` or `send_data_via_wifi()` (voltage, syringe size, speed)
- **Fetching readings** — `fetch_current()` dispatches the same way to `fetch_current_via_uart()` / `fetch_current_via_wifi()`. `fetch_loop()` calls it every 0.1 s on a daemon thread while `running` is true
- **Run lifecycle** — `start_fetch()` begins a run: `new_run_id()` for a fresh folder, `start_time = None` to restart elapsed time at 0, clears the plot lists, writes the inputs, starts the camera. `stop_fetch()` clears `running` and stops the camera
- **Data logging** — `enter_data()` writes the input parameters, `save_readings()` appends one line per reading. Both open in append mode and target the current run's folder (see below)
- **Camera control** — `start_camera_recording()` / `stop_camera_recording()` focus the existing Windows Camera window via `pygetwindow` and send a spacebar keystroke via `pyautogui`
- **Real-time plot** — matplotlib figure embedded in the Tkinter window; scrolls a 100-point window of Time vs. Current (UART path only)
- **GUI layer** — Tkinter `LabelFrame` with the input fields, the UART/Wi-Fi dropdown, and the action buttons; `window.mainloop()` on the last line

### Data output

Each click of **Fetch Current** creates a new timestamped folder:

```
C:\WEPS(final files)\Input-Output Data\<run_id>\
    input_data.txt     one line per run: voltage, syringe size, speed, current limit
    output_data.txt    one line per reading: Time, <s>, Current, <mA>, Voltage, <V>
```

- `DATA_DIR` is a fixed absolute path, deliberately **not** relative to the launch directory — the code runs on a lab machine where the working directory is not predictable. Do not change it back to `os.getcwd()`.
- `run_id` comes from `new_run_id()`, minted fresh in `start_fetch()` so runs never share a file. It appends `_2`, `_3` etc. if two runs start in the same second.
- Despite the commas, `output_data.txt` is **not** CSV — labels are interleaved with values.

## Hardware Context

- **ESP32-S3** communicates over UART at 115200 baud, or over Wi-Fi via HTTP (`/set_inputs`, `/get_readings`). UART is the dropdown default; using Wi-Fi requires filling in the `ESP32_IP` placeholder at the top of the file
- The GUI sends experiment parameters and receives current (mA) and voltage (V) readings
- LaserGRBL is an external engraving application invoked via `subprocess` from `C:\Program Files (x86)\LaserGRBL\LaserGRBL.exe`
- Camera recordings are saved wherever the Windows Camera app is configured to save them — they are **not** moved into the run folder
- Firmware/Arduino code for the ESP32-S3 is **not** in this repository
