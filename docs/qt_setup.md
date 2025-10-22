# Qt Setup Guide

This guide walks you through installing the Qt dependencies, running the new desktop application, and extending it with Qt Designer.

## 1. Prerequisites

- Python 3.9 or newer
- pip (ships with modern Python installers)
- (Optional) Qt Designer – included in the Qt Online Installer or Qt for Python tools

## 2. Create a Virtual Environment (recommended)

```powershell
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Project Dependencies

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This installs PySide6 (Qt for Python), NumPy, SciPy, pandas, OpenPyXL, and PyYAML.

## 4. Run the Qt Application

```powershell
python qt_app.py
```

### Using the App

1. **Config file** – choose the `config.yaml` that describes your test setup.  
2. **Experiment log** – select the `*log.xlsx` file exported from the lab notebook.  
3. **Data directory** – point to the folder containing the raw `.txt` load-cell files.  
4. **Output directory** – optional override for Excel exports (defaults to each data file’s folder).  
5. Press **Run Analysis**. Progress messages stream in the lower pane.  
6. Use the dataset selector to browse each processed case, review the computed forces, and open the generated Excel workbook.

## 5. Working with Qt Designer (optional)

Qt Designer provides a drag-and-drop way to prototype widgets:

1. Install Qt Designer via the [Qt Online Installer](https://www.qt.io/download) (Community Edition is fine).  
2. Launch Designer, create a **Main Window**, and arrange widgets.  
3. Save the layout as `*.ui`.  
4. Convert the `.ui` file into Python code if you prefer code generation:

   ```powershell
   pyside6-uic my_layout.ui -o ui_mainwindow.py
   ```

5. Import the generated class into `qt_app.py` and integrate it, or load the `.ui` dynamically with `QUiLoader`.

While the current application builds the interface programmatically (for easier customization in code), Designer can accelerate experimentation with new layouts.

## 6. Packaging the Application (advanced)

To create a standalone executable (optional):

```powershell
pip install pyinstaller
pyinstaller --noconfirm --windowed --name LoadCellAnalysisGUI qt_app.py
```

The packaged build appears in `dist/LoadCellAnalysisGUI`. Distribute the entire folder to end users.

## 7. Troubleshooting

- **Missing DLL errors** – ensure you ran the app from the activated virtual environment where PySide6 is installed.  
- **No log files found** – the GUI requires a single `*log.xlsx` file; double-check that transient files (prefixed `~$`) are deleted.  
- **Excel export already exists** – delete the previous `_output.xlsx` file or change the output directory before re-running.  
- **Slow UI / “Not Responding”** – the heavy analysis runs in a background thread; if you cancel, close the window and relaunch.
