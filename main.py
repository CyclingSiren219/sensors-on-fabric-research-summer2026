import tkinter                              # Importing the Tkinter module for GUI
from tkinter import ttk                     # Importing themed widgets from Tkinter
from tkinter import filedialog, messagebox  # Importing file dialog and message box modules

import subprocess                           # Importing subprocess for opening external applications
import serial                               # Importing serial module for communication
import serial.tools.list_ports              # Importing serial tools to list available COM ports
import os                                   # Importing os module for system operations
import requests                             # Importing requests module for HTTP requests
import time  # Import time module
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pyautogui
import pygetwindow as gw
from datetime import datetime

start_time = None  # Global variable to track start time
running = False

# Fixed location for saved data, independent of where this script is launched from
DATA_DIR = r'C:\WEPS(final files)\Input-Output Data'


def new_run_id():
    """Returns a timestamped folder name for one run, kept unique if two runs start in the same second."""
    stamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    candidate = stamp
    suffix = 2
    while os.path.exists(os.path.join(DATA_DIR, candidate)):
        candidate = f"{stamp}_{suffix}"
        suffix += 1
    return candidate


run_id = new_run_id()   # Folder for the current run; a fresh one is created each time Fetch Current is clicked

serial_connection = None                    # Global serial connection variable

ESP32_IP = "http://<ESP32_IP>"              # ESP32-S3 IP Address placeholder (Replace with actual IP)

def open_lasergrbl_with_file():                                                # Function to open LaserGRBL with a selected file
    lasergrbl_path = "C:\\Program Files (x86)\\LaserGRBL\\LaserGRBL.exe"      # Path to LaserGRBL executable
    if "selected_file" not in globals():                                       # Check if a file is selected
        messagebox.showwarning("Warning", "No file selected!")                 # Show warning if no file is selected
        return
    try:
        subprocess.Popen([lasergrbl_path, selected_file])                      # Open LaserGRBL with the selected file
    except FileNotFoundError:
        messagebox.showerror("Error", "LaserGRBL not found. Check the path.")  # Show error if the application is not found

def upload_file():                                        # Function to upload a file
    file_path = filedialog.askopenfilename(
        title="Select a File",
        filetypes=(
            ("G-code Files", "*.gcode"),                  # Filter for G-code files
            ("Image Files", "*.png *.jpg *.jpeg *.bmp"),  # Filter for image files
            ("All Files", "."),                         # Allow all file types
        )
    )
    if file_path:                                                            # If a file is selected
        uploaded_label.config(text=f"Uploaded: {file_path.split('/')[-1]}")  # Display file name
        global selected_file                                                 # Define selected_file globally
        selected_file = file_path                                            # Store selected file path
    else:
        uploaded_label.config(text="No file selected")                       # Display message if no file is selected

def validate_entry(num):          # Function to validate numeric entries
    if num.isdigit():             # Check if input is a digit
        return True
    elif '.' in num:              # Allow decimal numbers
        return True
    else:
        return False              # Reject non-numeric input

def get_com_ports():                            # Function to retrieve available COM ports
    ports = serial.tools.list_ports.comports()  # List available COM ports
    return [port.device for port in ports]      # Return list of COM port names

def refresh_ports():                            # Function to refresh the available COM ports
    ports = get_com_ports()                     # Get available COM ports
    select_combobox['values'] = ports           # Update combobox with new port list
    if ports:
        select_combobox.set(ports[0])           # Set to the first available port
    else:
        select_combobox.set('')                 # Clear selection if no ports are available

def on_select(event=None):                              # Function triggered when a COM port is selected
    print("Selected COM Port:", select_combobox.get())  # Print selected port

def connect_to_com_port():                                          # Function to connect to the selected COM port
    global serial_connection                                        # Use global serial connection variable
    selected_port = select_combobox.get()                           # Get selected COM port
    if not selected_port:
        messagebox.showerror("Error", "Please select a COM port!")  # Show error if no port is selected
        return

    try:
        serial_connection = serial.Serial(selected_port, baudrate=115200, timeout=1)  # Open serial connection
        messagebox.showinfo("Success", f"Connected to {selected_port}")             # Show success message
        connect_button.config(state="disabled")                                     # Disable connect button after successful connection
    except Exception as e:
        messagebox.showerror("Error", f"Failed to connect to {selected_port}:\n{e}") # Show error message

def send_data_via_uart():                                                    # Function to send data to the connected device
    global serial_connection                                                  # Use global serial connection variable
    if not serial_connection or not serial_connection.is_open:
        messagebox.showerror("Error", "Please connect to a COM port first!")  # Show error if no connection
        return

    try:
        voltage = voltage_entry.get()                                           # Get voltage input
        syringe_size = syringe_size_entry.get()                                 # Get syringe size input
        speed = speed_entry.get()                                               # Get speed input
        current_limit=current_limit_entry.get()
        data = f"{syringe_size},{speed},{voltage},(current_limit)\n"  # Format data string
        serial_connection.write(data.encode())                                  # Send encoded data to device
        messagebox.showinfo("Success", "Data sent to device!")                  # Show success message
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send data:\n{e}")             # Show error message

def enter_data(show_message=True):               # Function to enter data into the Excel file
    voltage = voltage_entry.get()                # Get voltage input
    syringe_size = syringe_size_entry.get()      # Get syringe size input
    speed = speed_entry.get()                    # Get speed input
    current_limit=current_limit_entry.get()

    folder = os.path.join(DATA_DIR, run_id)
    file_name = "input_data.txt"
    file_path = os.path.join(folder, file_name)

    try:
        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(file_path, "a") as file:
            file.write(f"Voltage: {voltage}, Syringe Size: {syringe_size}, Speed: {speed}, Current limit: {current_limit}\n")
        if show_message:
            messagebox.showinfo("Success", f"Data saved successfully to:\n{file_path}")  # Show success message


    except Exception as e:
        messagebox.showerror("Error", f"Failed to save data:\n{e}") # Show error message

def send_data_via_wifi():
    """Sends user input data (voltage, syringe size, speed) to the ESP32-S3 via an HTTP POST request."""
    syringe_size = syringe_size_entry.get()  # Get syringe size value from the entry field
    speed = speed_entry.get()                # Get speed value from the entry field

    if not voltage or not syringe_size or not speed:                       # Check if any field is empty
        messagebox.showerror("Error", "Please fill in all input fields!")  # Show error message if fields are empty
        return                                                             # Exit function

    try:
        # Prepare the data dictionary to be sent in the POST request
        data = {
            "syringeVolume": syringe_size,
            "flowRate": speed,
            "vset": voltage
        }
        response = requests.post(f"{ESP32_IP}/set_inputs", data=data)               # Send data to ESP32-S3

        if response.status_code == 200:                                             # Check if request was successful
            messagebox.showinfo("Success", "Data sent to ESP32-S3 successfully!")   # Show success message
        else:
            messagebox.showerror("Error", f"Failed to send data: {response.text}")  # Show error message if request fails
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Connection error:\n{e}")                    # Handle connection errors

def send_data_to_device():
    if connection_mode.get() == "UART":
        send_data_via_uart()
    elif connection_mode.get() == "Wi-Fi":
        send_data_via_wifi()
    else:
        messagebox.showerror("Error", "Please select a connection mode.")


def fetch_current_via_wifi():
    """Fetches current and voltage readings from ESP32 and saves to an Excel file with elapsed time."""

    try:
        response = requests.get(f"{ESP32_IP}/get_readings")  # Request data from ESP32
        if response.status_code == 200:
            data = response.json()  # Parse JSON response

            # Extract current and voltage values from JSON
            current_value = data.get("current", "N/A")
            bus_voltage = data.get("busVoltage", "N/A")

            # Start timer on first data fetch
            if start_time is None:
                start_time = time.time()  # Capture start time

            # Calculate elapsed time in seconds
            elapsed_time = round(time.time() - start_time, 2)

            # Update GUI label with fetched values
            current_label.config(text=f"Time: {elapsed_time} s, Current: {current_value} mA, Voltage: {bus_voltage} V")

            # Save this reading to output_data.txt
            save_readings(elapsed_time, current_value, bus_voltage)

        else:
            messagebox.showerror("Error", f"Failed to fetch data: {response.text}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Connection error:\n{e}")

def fetch_current_via_uart():
    global start_time

    if not serial_connection or not serial_connection.is_open:
        messagebox.showerror("Error", "Please connect to a COM port first!")
        return

    try:
        # Clear previous data
        serial_connection.reset_input_buffer()

        # Send the command to Arduino
        print(">> Sending: GET_DATA")
        serial_connection.write(b"GET_DATA\n")
        time.sleep(0.3)  # wait for Arduino to respond

        line = ""
        for _ in range(5):  # Try reading 5 lines to catch the correct one
            raw_line = serial_connection.readline()
            line = raw_line.decode("utf-8", errors="ignore").strip()
            print(f"Arduino replied: {line!r}")  # Terminal log for debugging

            if "Voltage" in line and "Current" in line:
                break  # Found the valid data line

        # If no valid line found
        if "Voltage" not in line or "Current" not in line:
            messagebox.showerror("Error", f"Invalid data format received: {line}")
            return

        # Extract voltage and current values
        parts = line.replace(" ", "").split(",")
        voltage = current = None

        for part in parts:
            if "Voltage:" in part:
                voltage = part.replace("Voltage:", "").replace("V", "")
            elif "Current:" in part:
                current = part.replace("Current:", "").replace("mA", "")

        if voltage is None or current is None:
            messagebox.showerror("Error", f"Could not extract values from: {line}")
            return

        # Calculate time and update GUI
        if start_time is None:
            start_time = time.time()

        elapsed_time = round(time.time() - start_time, 2)
        current_label.config(text=f"Time: {elapsed_time} s, Current: {current} mA, Voltage: {voltage} V")

        # Save this reading to output_data.txt
        save_readings(elapsed_time, current, voltage)

        try:
            time_list.append(float(elapsed_time))
            current_list.append(float(current))
        except ValueError:
            return  # Skip bad data


        if len(time_list) > 100:
            time_list.pop(0)
            current_list.pop(0)

        plot.clear()
        plot.set_xlabel("Time (s)")
        plot.set_ylabel("Current (mA)")
        plot.set_title("Time vs Current")
        plot.plot(time_list, current_list, marker='o', linestyle='-')
        canvas.draw()


    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch via UART:\n{e}")

        if running:
            current_label.after(1000, fetch_current_via_uart)


def fetch_loop():
    global running
    while running:
        fetch_current()
        time.sleep(0.1)



def fetch_current():
    if connection_mode.get() == "UART":
        fetch_current_via_uart()
    elif connection_mode.get() == "Wi-Fi":
        fetch_current_via_wifi()
    else:
        messagebox.showerror("Error", "Please select a connection mode.")

def start_camera_recording():
    camera_windows = gw.getWindowsWithTitle("Camera")
    if not camera_windows:
        messagebox.showerror("Error", "Camera app is not open.\nPlease open the Windows Camera app and switch to video mode before starting.")
        return
    camera_windows[0].activate()
    time.sleep(0.3)
    pyautogui.press("space")
    window.focus_force()
    print("Camera recording started.")

def stop_camera_recording():
    camera_windows = gw.getWindowsWithTitle("Camera")
    if not camera_windows:
        return
    camera_windows[0].activate()
    time.sleep(0.3)
    pyautogui.press("space")
    window.focus_force()
    print("Camera recording stopped.")

def start_fetch():
    global running, run_id, start_time
    if not running:
        run_id = new_run_id()      # Start a new run folder so this recording is kept on its own
        start_time = None          # Restart the elapsed-time clock at 0 for this run
        time_list.clear()          # Clear the plot so it shows only this run
        current_list.clear()
        enter_data(show_message=False)
        start_camera_recording()
        running = True
        threading.Thread(target=fetch_loop, daemon=True).start()

def stop_fetch():
    global running
    running = False
    stop_camera_recording()

def stop_process():                # Send STOP to stop the process. Arduino code should be updated
        print(">> Sending: STOP")
        serial_connection.write(b"STOP\n")


def save_readings(elapsed_time, current, voltage):
    folder = os.path.join(DATA_DIR, run_id)
    file_name = "output_data.txt"
    file_path = os.path.join(folder, file_name)

    try:
        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(file_path, "a") as file:
            file.write(f"Time, {elapsed_time}, Current, {current}, Voltage, {voltage}\n")



    except Exception as e:
        messagebox.showerror("Error", f"Failed to save data:\n{e}") # Show error message



time_list = []
current_list = []

# Create Matplotlib figure
fig = Figure(figsize=(5, 4), dpi=100)
plot = fig.add_subplot(1, 1, 1)


# Initialise GUI window
window = tkinter.Tk()
window.title("Data Entry Form")  # Set window title

frame = tkinter.Frame(window)  # Create main frame for widgets
frame.pack()  # Pack frame into the window

# Create a labeled frame for user inputs
user_info_frame = tkinter.LabelFrame(frame, text="Inputs")
user_info_frame.grid(row=0, column=0, padx=20, pady=20)  # Place input frame in grid

# Create and place labels for input fields
voltage_label = tkinter.Label(user_info_frame, text="Voltage(V)")
voltage_label.grid(row=0, column=0)

syringe_size_label = tkinter.Label(user_info_frame, text="Syringe Size(ml)")
syringe_size_label.grid(row=0, column=1)

speed_label = tkinter.Label(user_info_frame, text="Speed(ml/hr)")
speed_label.grid(row=0, column=2)


current_limit_label = tkinter.Label(user_info_frame, text="Current limit (mA)")
current_limit_label.grid(row=0, column=3)

select_label = tkinter.Label(user_info_frame, text="Select Serial Port")
select_label.grid(row=2, column=0)

uploaded_label = tkinter.Label(user_info_frame, text="No file Selected")
uploaded_label.grid(row=3, column=0)

# Create entry fields for user inputs with validation
voltage_entry = tkinter.Entry(
    user_info_frame,
    validate="key",
    validatecommand=(user_info_frame.register(validate_entry), "%S")
)
voltage_entry.grid(row=1, column=0)

syringe_size_entry = tkinter.Entry(
    user_info_frame,
    validate="key",
    validatecommand=(user_info_frame.register(validate_entry), "%S")
)
syringe_size_entry.grid(row=1, column=1)

speed_entry = tkinter.Entry(
    user_info_frame,
    validate="key",
    validatecommand=(user_info_frame.register(validate_entry), "%S")
)
speed_entry.grid(row=1, column=2)

current_limit_entry = tkinter.Entry(
    user_info_frame,
    validate="key",
    validatecommand=(user_info_frame.register(validate_entry), "%S")
)
current_limit_entry.grid(row=1, column=3)


# Create dropdown menu for selecting COM port
select_combobox = ttk.Combobox(user_info_frame, state="readonly")
select_combobox.grid(row=2, column=1)
select_combobox.bind("<<ComboboxSelected>>", on_select)  # Bind event to selection

connection_mode = ttk.Combobox(user_info_frame, state="readonly", values=["UART", "Wi-Fi"])
connection_mode.set("UART")  # Default selection
connection_mode.grid(row=2, column=2)


# Create buttons for various functionalities
connect_button = tkinter.Button(user_info_frame, text="Connect", command=connect_to_com_port)
connect_button.grid(row=2, column=4, padx=10, pady=10)

stop_process_button = tkinter.Button(user_info_frame, text="Stop Process", command=stop_process)
stop_process_button.grid(row=2, column=5, padx=20, pady=40)


enter_data_button = tkinter.Button(user_info_frame, text="Enter data", command=enter_data)
enter_data_button.grid(row=1, column=5, sticky="news", padx=20, pady=20)

send_data_button = tkinter.Button(user_info_frame, text="Send to Device", command=send_data_to_device)
send_data_button.grid(row=1, column=4, sticky="news", padx=20, pady=20)

fetch_current_button = ttk.Button(user_info_frame, text="Fetch Current", command=start_fetch)
fetch_current_button.grid(row=4, column=0, columnspan=2, pady=10)

stop_fetch_button = ttk.Button(user_info_frame, text="Stop Fetch", command=stop_fetch)
stop_fetch_button.grid(row=4, column=4, columnspan=2, pady=10)

# Label to display fetched current value
current_label = ttk.Label(user_info_frame, text="Current: N/A")
current_label.grid(row=4, column=2, columnspan=3, pady=10)

canvas = FigureCanvasTkAgg(fig, master=user_info_frame)
canvas.draw()
canvas.get_tk_widget().grid(row=5, column=0, columnspan=6, pady=10)

# Button to open external software (LaserGRBL)
open_software_button = tkinter.Button(user_info_frame, text="Open Software", command=open_lasergrbl_with_file)
open_software_button.grid(row=3, column=2, sticky="news", padx=10, pady=10)

# Button to refresh COM ports
refresh_button = tkinter.Button(user_info_frame, text="Refresh COM Ports", command=refresh_ports)
refresh_button.grid(row=2, column=3, pady=7)

# Button to upload a file
upload_button = tkinter.Button(user_info_frame, text="Upload File", command=upload_file)
upload_button.grid(row=3, column=1, pady=7)

# Initial loading of COM ports
refresh_ports()

# Run the GUI event loop
window.mainloop()
