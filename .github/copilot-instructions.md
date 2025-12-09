**Quick Repo Summary**

- Project: Raspberry-Pi / laptop Python utilities for an automated loan locker (GUI + camera scanning).
- Languages: Python 3.x (several scripts and one Jupyter notebook `PDF417.ipynb`).
- Main concerns: camera capture + barcode decoding (PDF417/QR), Tkinter GUI, Raspberry Pi GPIO and Picamera2.

**Key files and places to look**

- `PDF417.ipynb` — primary scanner logic using OpenCV (`cv2`) + `zxingcpp`. See camera config (CAP_PROP_FRAME_WIDTH/HEIGHT) and the scan flow: press `s` to scan, `ESC` to exit.
- `Integracinfinal1.py`, `Inicial Menu.py` — Tkinter GUI examples. Pattern: `sidebar` frame (width=200) + `content` frame; `menu_items` list defines buttons that call view functions.
- `leds.py` — Raspberry Pi specific: `RPi.GPIO`, `picamera2`. Run on Pi OS; controls GPIO and optional camera recording.
- `nuevo registro.py`, `lista de usuarios.py` — simple CLI utilities that update in-memory structures; useful for examples of data handling.
- `prestamos_db.json` — project data file (use when persisting loan records).
- `mcp2/` — a virtualenv-like tree containing site-packages (Adafruit libraries present). Use it as a reference for required hardware libs.

**Project-specific patterns & conventions (do not invent)**

- Camera scanners: all scanner scripts call `cap = cv2.VideoCapture(0)` and set resolution with `cap.set(...)`. They crop to a fixed rectangle (`x1,y1,x2,y2 = 500,150,1700,800`) and convert BGR→RGB before calling `zxingcpp.read_barcodes(...)`.
- Interaction: `cv2.imshow()` shows live feed; `cv2.waitKey(1)` reads keys. The convention in these scripts: `if key == ord('s'):` → scan, `if key == 27:` → exit.
- GUI: simple Tkinter layout using `.pack()` only; sidebar buttons call functions that clear `content` and populate widgets. Expect text labels in Spanish.
- File names contain spaces and non-ASCII characters (e.g. `Inicial Menu.py`, `Código de prueba cam.py`, `integración...`). When referencing modules or running scripts, use quoted paths.

**Dependencies & environment hints**

- Runtime: Scripts target Python 3 (venv found under `mcp2/` with Python 3.12). Use a matching Python 3.x runtime.
- Probable pip packages: `opencv-python` (cv2), `zxingcpp` (or equivalent ZXing binding), `picamera2` (on Raspberry Pi), `RPi.GPIO`, and Adafruit Blinka/MCP libraries (present under `mcp2/lib/...`).
- Virtualenv: a `mcp2/` environment is present; to reuse on Linux/macOS: `source mcp2/bin/activate`. On Windows PowerShell use `mcp2\bin\Activate.ps1`.

**Run / debug examples**

- Run a scanner quickly (notebook or script):
  - On Linux/WSL/PI (bash):
    - `source mcp2/bin/activate` (if using included env)
    - `python "PDF417.ipynb"` (open in Jupyter) or run an equivalent .py cell script
  - On PowerShell (Windows):
    - `mcp2\bin\Activate.ps1` then `python "PDF417.ipynb"` or open the notebook in VS Code.
- For camera scripts: attach a webcam / Pi camera. Use `s` to trigger a scan and `ESC` to exit. Check the crop coordinates if the barcode is off-center.
- For GPIO scripts (`leds.py`): run on Raspberry Pi OS, with appropriate privileges (GPIO often requires root). Stop safely — all scripts call `GPIO.cleanup()` on exit.

**Editing & contribution notes for AI agents**

- Prefer minimal, local changes: most scripts are standalone examples rather than a single packaged app. When adding features, update the specific script and keep other example scripts untouched.
- When changing camera code, update the cropping constants at the top of the file (e.g. `x1,y1,x2,y2`) and keep the `cap.release(); cv2.destroyAllWindows()` pattern.
- Maintain Spanish UI text and labels where present; these scripts mix Spanish and English — follow the existing language per-file.
- Avoid renaming files with spaces/accents unless you also update any scripts that reference them; run commands should use quoted paths.

**Where to look next / recommended starting tasks**

- Open `PDF417.ipynb` to validate barcode parsing and to see the `parse_pdf417()` helpers.
- Inspect `Integracinfinal1.py` for the main UI flow — useful if integrating scanner output into the GUI.
- Check `mcp2/lib/python3.12/site-packages/` to enumerate exact dependency versions available in the local environment.

If anything here is unclear or you want the file to include additional examples (e.g. exact `pip install` list or a short `requirements.txt`), tell me what to extract and I'll update the file.
