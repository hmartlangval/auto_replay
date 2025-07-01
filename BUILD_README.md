# Building Fiserv Automation Taskbar Distribution

This guide explains how to create a distributable `.exe` file from the Python source code.

## 🚀 Quick Build

### Option 1: Windows Batch File (Recommended)
1. Double-click `build_exe.bat`
2. Follow the prompts
3. Find your `.exe` in the `dist/` folder

### Option 2: Manual Python Build
```bash
python build_exe.py
```

## 📋 Prerequisites

- Python 3.8 or higher
- All dependencies installed (`pip install -r requirements.txt`)
- Windows OS (for Windows distribution)

## 📦 What Gets Built

The build process creates:

- **`FiservAutomationTaskbar.exe`** - Single executable file (~50-100MB)
- **`DISTRIBUTION_INFO.txt`** - Distribution information and instructions

## 🗂️ Runtime Directories

The following directories are treated as **runtime data** and will be created next to the `.exe` when first run:

- **`prompts/`** - AI prompts and templates (user-modifiable)
- **`sequences/`** - Recorded automation sequences (user-modifiable)  
- **`images/`** - Image templates for recognition (user-modifiable)

### Important Notes:
- These directories can be modified by end users
- If missing, they will be auto-created with default content
- Changes to these folders persist between application runs

## 🔧 Distribution

### What to Share:
- `FiservAutomationTaskbar.exe` (main executable)
- `DISTRIBUTION_INFO.txt` (optional documentation)

### What NOT to Share:
- Source code (`.py` files)
- Build artifacts (`build/`, `dist/` folders)
- Development dependencies

## ⚡ System Requirements

**Target Systems:**
- Windows 10/11 (64-bit)
- No Python installation required
- No additional dependencies required

**RAM:** ~200MB during runtime
**Disk:** ~100MB for executable + runtime data

## 🔍 Troubleshooting

### Build Fails
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (3.8+ required)
- Try updating PyInstaller: `pip install --upgrade pyinstaller`

### Runtime Issues on Target Machine
- Ensure Windows Defender isn't blocking the .exe
- Try running as Administrator if automation features fail
- Check that runtime directories are created in the same folder as the .exe

### Missing Dependencies
The build process automatically includes all required dependencies. If you see import errors:

1. Check that all imports work in development mode
2. Add missing modules to `hiddenimports` in `build_exe.spec`
3. Rebuild the executable

## 🎯 Build Process Details

The build process:

1. **Cleans** previous build artifacts
2. **Installs/Updates** PyInstaller
3. **Installs** all requirements from `requirements.txt`
4. **Bundles** the application using PyInstaller spec file
5. **Creates** single executable with all dependencies
6. **Generates** distribution documentation

## 📁 Project Structure

```
project/
├── build_exe.py          # Build script
├── build_exe.spec        # PyInstaller configuration
├── build_exe.bat         # Windows batch file
├── hello_world_gui.py    # Main application
├── requirements.txt      # Python dependencies
├── prompts/              # Runtime: AI prompts
├── sequences/            # Runtime: Recorded sequences
├── images/               # Runtime: Image templates
├── automation/           # Packaged: Automation modules
├── utils/                # Packaged: Utility modules
└── examples/             # Packaged: Example scripts
```

## 🔐 Security Notes

- The .exe is not digitally signed
- Windows Defender may flag it as "unknown publisher"
- Enterprise environments may require IT approval
- Consider code signing for production distribution

---

**Need Help?** Check the main project documentation or create an issue. 