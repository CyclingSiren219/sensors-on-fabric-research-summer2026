# WEPS Sensor GUI — Summer 2026

This application provides a graphical interface for running electrochemical sensor experiments as part of the USF Wearable Electronic Patch Sensors (WEPS) research project. It communicates with an ESP32-S3 microcontroller, logs sensor readings in real time, automatically starts and stops Windows Camera recording in sync with data collection, and files the resulting video into the same folder as that run's data.

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
5. Click **Fetch Current** to start the run. This does four things at once: creates a new timestamped run folder, saves the input values into it, starts the camera recording, and begins logging and plotting readings. If the previous run's video is still being saved, the app asks you to wait (up to 30 seconds) instead of starting.
6. Click **Stop Fetch** to end the run. This stops both the logging and the camera recording, then moves the video into the run folder as `video.mp4`. A **Video saved** dialog confirms it; if you see **Video not saved** instead, see [Camera Recording](#camera-recording).

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
| **Fetch Current** | Saves the current input field values to `input_data.txt`, then starts continuous data collection, camera recording, and the real-time plot. Refuses to start while the previous recording is still running or its video is still being saved |
| **Stop Fetch** | Stops data collection and camera recording, then moves the recording into the run folder as `video.mp4` |
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
│   ├── output_data.txt
│   └── video.mp4
└── 2026-06-10_15-04-51/     <- second Fetch
    ├── input_data.txt
    ├── output_data.txt
    └── video.mp4
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

**`video.mp4`** — the Camera recording, moved in from the Camera Roll after **Stop Fetch**. It appears a few seconds after you stop, not instantly. If it could not be moved, it is missing from the run folder and stays in the Camera Roll instead — see [Slow release](#slow-release-the-video-is-left-in-the-camera-roll).

Because each run gets its own folder named by timestamp, you can run multiple experiments back-to-back without overwriting previous data.

---

## Camera Recording

### Prerequisite — do this before each session _(updated June 17, 2026)_

Before clicking **Fetch Current**:
1. Open the **Windows Camera** app manually
2. Click the **video icon** on the right side of the screen to switch from photo to video mode
3. Leave the Camera app open in the background — do not close or minimize it to the taskbar
4. Leave the Camera app's save location at its default (the **Camera Roll**) — that is the folder the app watches for the new video

The first time Camera runs on a machine it may ask for permissions (camera, microphone, location). Accept them with a manual test recording first, or the prompt can swallow the spacebar the app sends.

`main.py` does not open the Camera app for you. If it is not open when you click **Fetch Current**, an error dialog appears and the run starts without a recording.

### How it works

**Fetch Current** notes which `WIN_*.mp4` files are already in the Camera Roll, then brings the Camera window into focus, sends a **spacebar keystroke** to start recording, and returns focus to the GUI.

**Stop Fetch** sends the spacebar again, but only if **Fetch Current** actually started a recording, so clicking it twice is harmless. A background thread then checks the Camera Roll once a second until the new `WIN_*.mp4` is non-empty, has stopped growing, and can be opened for writing. It **moves** (not copies) that file to `<run_id>\video.mp4` and shows a **Video saved** dialog. Older recordings and non-`WIN_` files, such as phone uploads synced by OneDrive, are ignored.

Keep your hands off the keyboard and mouse for about a second after clicking either button, and keep the mouse out of the top-left corner of the screen (`pyautogui` aborts there). The app finds Camera by the exact window title "Camera" and falls back to any title containing it, so avoid keeping Explorer open on the Camera Roll folder during a run.

### If the video isn't saved

| Dialog | What to do |
|---|---|
| **Previous recording still running** | The last **Stop Fetch** failed. Click **Stop Fetch** again before starting a new run |
| **Please wait** | The previous video is still being saved (up to 30 seconds). Try again shortly |
| **Video not moved** | The app could not find or read the Camera Roll, so it cannot track the file. The video is wherever Camera saves recordings |
| **Video not saved** | The video is not in the run folder. The message names the file or folder involved and nothing is deleted. If it says *no new video appeared*, check that Camera was in video mode; otherwise move the file by hand from the path shown |

### Slow release: the video is left in the Camera Roll

Sometimes the file is not released quickly after recording stops: Camera is still finalizing it, or OneDrive, antivirus or the search indexer is holding it. The app waits up to **30 seconds** after **Stop Fetch**. If the file is still changing or locked when that runs out:

- The video is **not moved**. It stays in the Camera Roll under its original `WIN_..._Pro.mp4` name, and nothing is deleted.
- A **Video not saved** dialog says it *"was still being written or locked after 30 seconds, so it was left there"* and gives the full path.
- The run folder has `input_data.txt` and `output_data.txt` as usual, but no `video.mp4`. The data files are not affected.
- **Fetch Current** is blocked during the wait (a **Please wait** dialog) and works again once the **Video not saved** dialog appears.

To recover, wait a little (or close the Camera app) until the file is released, then move it by hand from the path in the dialog into that run's folder, the newest timestamped folder under `C:\WEPS(final files)\Input-Output Data`, and rename it `video.mp4`. The leftover file will not be mistaken for the next run's video.

The readiness check opens the file for writing, so a program holding a *finished* file without allowing writes can also trigger this. The video is then fine: check that it plays, then move it by hand.

If you close the GUI within 30 seconds of **Stop Fetch**, the process stays alive until the video has been dealt with, and the result is printed to the terminal instead of shown in a dialog.
