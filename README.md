# WEPS Sensor GUI — Summer 2026

This application provides a graphical interface for running electrochemical sensor experiments as part of the USF Wearable Electronic Patch Sensors (WEPS) research project. It communicates with an ESP32-S3 microcontroller, logs sensor readings in real time, and (in the Modified version) automatically starts and stops Windows Camera recording in sync with data collection.

---

## Files

| File | Description |
|---|---|
| `GUI_main_page_wStop-2026.ipynb` | Original version — data collection and logging only |
| `GUI_main_page_wStop_2026_Modified.ipynb` | **Use this one** — same as original plus synchronized camera recording |

---

## Setup

### 1. Run the notebook

Open Jupyter and run all cells:

```
jupyter notebook
```

Select `GUI_main_page_wStop_2026_Modified.ipynb`, then use **Run → Run All Cells**. A Tkinter window will open — this is the experiment GUI.

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

Use the **Refresh COM Ports** dropdown to detect available ports.

### Buttons

| Button | What it does |
|---|---|
| **Enter Data** | Saves the current input field values to `input_data.txt` in the run folder |
| **Send to Device** | Transmits voltage, syringe size, and flow rate to the ESP32-S3 |
| **Connect** | Opens the selected COM port at 115200 baud (UART mode only) |
| **Fetch Current** | Starts continuous data collection, camera recording, and the real-time plot |
| **Stop Fetch** | Stops data collection and stops camera recording |
| **Stop Process** | Sends a `STOP` command directly to the microcontroller over UART |
| **Upload File** | Opens a file picker for G-code (`.gcode`) or image files |
| **Open Software** | Launches LaserGRBL with the uploaded file |

### Real-time plot

While fetching, a live **Time vs. Current** graph updates inside the GUI window. It displays a rolling window of the 100 most recent readings. Elapsed time is measured from the moment the first reading is received.

---

## Data Logging — What's New

Previously, all output files were written to a hardcoded Windows path (`C:\WEPS(final files)\`). This caused problems if that folder didn't exist and made it impossible to keep data from separate runs separate.

**The Modified notebook now saves data into a timestamped subfolder inside a `samples/` directory located in the same folder as the notebook.**

### Folder structure

Every time you launch the notebook and run the cells, a unique `run_id` is generated from the current date and time:

```
samples/
└── 2026-06-10_14-32-07/
    ├── input_data.txt
    └── output_data.txt
```

The subfolder is created automatically the first time data is written — you do not need to create it manually.

### File contents

**`input_data.txt`** — written when you click **Enter Data**:
```
Voltage: 1.5, Syringe Size: 10, Speed: 5, Current limit: 2.5
```

**`output_data.txt`** — written on every reading while **Fetch Current** is active:
```
Time, 0.0, Current, 2.34, Voltage, 1.50
Time, 1.02, Current, 2.37, Voltage, 1.50
...
```

Because each run gets its own folder named by timestamp, you can run multiple experiments back-to-back without overwriting previous data.

---

## Camera Recording (Modified Version Only)

### Prerequisite — do this before each session _(updated June 17, 2026)_

Before clicking **Fetch Current**:
1. Open the **Windows Camera** app manually
2. Click the **video icon** on the right side of the screen to switch from photo to video mode
3. Leave the Camera app open in the background — do not close or minimize it to the taskbar

The program does not open the Camera app for you. If it is not already open and in video mode when you click **Fetch Current**, an error dialog will appear and data collection will start without a recording.

### How it works

When you click **Fetch Current**, the app:
1. Finds the open Camera window by title and brings it into focus
2. Sends a **spacebar keystroke** to start recording
3. Returns focus to the GUI so you can continue using it normally

When you click **Stop Fetch**, the same steps repeat to stop recording.

### Where recordings are saved

Camera recordings are saved to the default Windows Camera save location (typically `C:\Users\<you>\Videos\`) and are not moved into the `samples/` folder automatically.
