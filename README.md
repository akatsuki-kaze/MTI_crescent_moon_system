# MTI_crescent_moon_system——MCMS
# MTI Crescent Moon System (MCMS)

Overview
---
MCMS is a small Python robot control framework derived from MTI_volleyball_opensource. It is organized into three main parts: algorithms, hardware abstraction, and image detection. The project focuses on simple serial-controlled robot workflows but is written so other transports (e.g., CAN) can be added.

Architecture
---
- `basic_functional` — control algorithms (e.g., PID). Outputs are mapped to remote control ranges (0–255, neutral=127). See `basic_functional/pid.py`.
- `HAL` — hardware abstraction: serial I/O, gamepad/keyboard/mouse mapping, simple camera adapter. Key files: `HAL/message_process.py` and `HAL/pc_remote.py`.
- `image_detection` — OpenCV helpers that produce masks or coordinates for control logic. Example: `image_detection/color_detect.py`.

Key conventions
---
- Serial frame: fixed 20 bytes. `HAL/message_process.py` treats bytes at indices {0, 5, 13, 19} as check positions — do not change without coordinating all users.
- Control values: use integer range 0–255, with 127 representing neutral/center.
- Image helpers often call `cv2.imshow()` for debugging; for headless usage remove or wrap these calls and return arrays instead.

Important files & functions
---
- `HAL/message_process.py`
	- `msg` / `msg_get`: 20-element lists used for send/receive frames.
	- `SerialCommunicator.open(port, baudrate, ...)` — open serial port.
	- `SerialCommunicator.send()` — writes `msg` to serial per-byte.
	- `SerialCommunicator.read(size=20, check_values)` — reads 20 bytes and validates the check indices; `check_values` must be a dict containing keys {0,5,13,19} with integer values 0–255.
	- `xy_collect(...)` and `mapping(...)` — map stick inputs to control ranges and apply deadzones.

- `HAL/pc_remote.py`
	- `key_array` (4 values) maps WSAD → `[up/down, left/right, reserved, reserved]` with neutral=127.
	- `update_key_array()` maintains WS/AD mutual exclusion and sets values to 0/127/255.
	- `get_mouse_center_offset()` returns (dx, dy) from screen center; `move_mouse_relative(dx, dy)` moves the pointer with bounds checks.

- `basic_functional/pid.py`
	- `ProportionalPID.update(current: float, target=0.0)` — compute PID and return a control value in 0–255 (note: implementation negates `current` and uses `127 - pid_output` mapping).

- `image_detection/color_detect.py`
	- `extract_red_regions(image_path=None, image=None)` and `extract_blue_regions(...)` — return binary masks (ndarray) after HSV thresholding and morphology.

Quick start (Windows)
---
Create a virtual env and install dependencies (example):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install numpy opencv-python pygame pyserial pynput pyautogui
```

There is no single entrypoint in the repo — create a small `main.py` that imports HAL and algorithms, for example:

```python
from HAL import message_process as mp
from basic_functional.pid import ProportionalPID

sc = mp.SerialCommunicator()
sc.open('COM3', 115200)
# use sc.send(), sc.read(...) and PID to control
```

Testing tips
---
- Serial: test `SerialCommunicator.read()` with a known 20-byte frame and the expected `check_values` dict.
- Gamepad: `pygame` axis/button indices vary by OS; validate axis mapping on target machine.
- Image code: run image functions locally and avoid `cv2.imshow()` in CI/headless runs.