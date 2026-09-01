# WEPS Sensor GUI — Summer 2026

This application provides a graphical interface for running electrochemical sensor experiments as part of the USF Wearable Electronic Patch Sensors (WEPS) research project. It communicates with an ESP32-S3 microcontroller, logs sensor readings in real time, and automatically starts and stops Windows Camera recording in sync with data collection.

---

## Files

| File | Description |
|---|---|
| `main.py` | **Use this one** — run directly with Python, includes all features |
| `GUI_main_page_wStop_2026_Modified.ipynb` | Backup — unfixed source the `main.py` was converted from |
| `GUI_main_page_wStop-2026.ipynb` | Original notebook — data collection and logging only, no camera recording |

---

## Setup

### Run the app

```
python main.py
```

A Tkinter window will open — this is the experiment GUI.

---

## Running an Experiment — Step by Step

Do these in order. Steps 1–3 are once per session; steps 4–6 repeat for each recording.

1. **Open the Windows Camera app and switch it to video mode**, and leave it open in the background. Do this *before* launching the GUI — the app will not open Camera for you. (Details under [Camera Recording](#camera-recording).)
2. **Select the Serial Port** for the ESP32-S3 — click **Refresh COM Ports** if it isn't listed — then click **Connect**.
3. Leave the connection dropdown on **UART** (the default).
4. Fill in **Voltage**, **Syringe Size**, **Speed**, and **Current Limit**, then click **Send to Device** to push them to the ESP32-S3.
5. Click **Fetch Current** to start the run. This does four things at once: creates a new timestamped run folder, saves the input values into it, starts the camera recording, and begins logging and plotting readings.
6. Click **Stop Fetch** to end the run. This stops both the logging and the camera recording.

To do another recording, repeat steps 4–6 — each **Fetch Current** starts a fresh run in its own folder. You do not need to restart the program between runs.

> **Fetch Current / Stop Fetch** start and stop a *run*. **Stop Process** is unrelated — it sends a `STOP` command to the microcontroller and does not end the run or the recording.

---

## Legacy / Backup notebooks

The `.ipynb` files are kept as backups only. To open them:

```
jupyter notebook
```

Select the file, then use **Run → Run All Cells**.

---

## How the GUI Works

### Input fields

| Field | What to enter |
|---|---|
| Voltage (V) | Target voltage to apply during the experiment |
| Syringe Size (ml) | Volume of the syringe being used |
| Speed (ml/hr) | Flow rate of the syringe pump |
| Current Limit (mA) | Maximum allowable current |
| Serial Port | COM port for UART connection (e.g. `COM3`) |
| Connection mode | Dropdown: **UART** (default) or **Wi-Fi** |

Click **Refresh COM Ports** to re-scan for available ports if yours isn't in the list.

### Buttons

| Button | What it does |
|---|---|
| **Enter Data** | Saves the current input field values to `input_data.txt` in the run folder |
| **Send to Device** | Transmits voltage, syringe size, and flow rate to the ESP32-S3 |
| **Connect** | Opens the selected COM port at 115200 baud (UART mode only) |
| **Fetch Current** | Saves the current input field values to `input_data.txt`, then starts continuous data collection, camera recording, and the real-time plot |
| **Stop Fetch** | Stops data collection and stops camera recording |
| **Stop Process** | Sends a `STOP` command directly to the microcontroller over UART |
| **Upload File** | Opens a file picker for G-code (`.gcode`) or image files |
| **Open Software** | Launches LaserGRBL with the uploaded file |

### Real-time plot

While fetching, a live **Time vs. Current** graph updates inside the GUI window. It displays a rolling window of the 100 most recent readings. Elapsed time restarts at 0 at the start of each run, and the graph is cleared so it shows only the current run.

Note: the plot is only drawn in **UART** mode. In Wi-Fi mode readings are still logged to file, but the graph does not update.

---

## Data Logging

Earlier versions wrote all output straight into a hardcoded Windows path (`C:\WEPS(final files)\`), so data from separate runs was impossible to keep apart.

**Data is now saved into a timestamped subfolder inside a fixed folder: `C:\WEPS(final files)\Input-Output Data`.** The path is set once at the top of [main.py](main.py) as `DATA_DIR`, so it does not depend on the directory the script is launched from.

### Folder structure

Every time you click **Fetch Current**, a new `run_id` is generated from the current date and time, and that recording gets its own folder:

```
C:\WEPS(final files)\Input-Output Data\
├── 2026-06-10_14-32-07/     <- first Fetch
│   ├── input_data.txt
│   └── output_data.txt
└── 2026-06-10_15-04-51/     <- second Fetch
    ├── input_data.txt
    └── output_data.txt
```

The subfolder is created automatically the first time data is written — you do not need to create it manually. Elapsed time restarts at 0 for each run, so each `output_data.txt` holds exactly one recording and nothing has to be split apart afterwards.

### File contents

**`input_data.txt`** — written automatically the moment you click **Fetch Current**, capturing whatever values are in effect at the start of the run. You can also click **Enter Data** yourself at any point as a manual backup (e.g. to log a mid-run change):
```
Voltage: 1.5, Syringe Size: 10, Speed: 5, Current limit: 2.5
```

Note: if you change an input field mid-recording, it is only logged if you click **Enter Data** again — the auto-capture on **Fetch Current** only happens once, at the start of the run. Clicking **Enter Data** *before* your first **Fetch Current** of the session writes into a run folder of its own, which will then contain an `input_data.txt` with no matching `output_data.txt`. Each line is appended, not overwritten, and is not timestamped, so multiple lines in the file aren't tied to a specific point in the run.

**`output_data.txt`** — written on every reading while **Fetch Current** is active:
```
Time, 0.0, Current, 2.34, Voltage, 1.50
Time, 1.02, Current, 2.37, Voltage, 1.50
...
```

Because each run gets its own folder named by timestamp, you can run multiple experiments back-to-back without overwriting previous data.

---

## Camera Recording

### Prerequisite — do this before each session _(updated June 17, 2026)_

Before clicking **Fetch Current**:
1. Open the **Windows Camera** app manually
2. Click the **video icon** on the right side of the screen to switch from photo to video mode
3. Leave the Camera app open in the background — do not close or minimize it to the taskbar

`main.py` does not open the Camera app for you. If it is not already open and in video mode when you click **Fetch Current**, an error dialog will appear and data collection will start without a recording.

### How it works

When you click **Fetch Current**, the app:
1. Finds the open Camera window by title and brings it into focus
2. Sends a **spacebar keystroke** to start recording
3. Returns focus to the GUI so you can continue using it normally

When you click **Stop Fetch**, the same steps repeat to stop recording.

### Where recordings are saved

Camera recordings are saved to the default Windows Camera save location (typically `C:\Users\<you>\Videos\`) and are not moved into the run folder automatically.
