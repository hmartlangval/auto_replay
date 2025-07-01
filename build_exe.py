#!/usr/bin/env python3
"""
Build script for Fiserv Automation Taskbar
Creates a distributable .exe file for Windows
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}...")
    print(f"   Command: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ Success")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed: {e}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False

def ensure_directories():
    """Ensure required directories exist"""
    directories = ['prompts', 'sequences', 'images', 'automation', 'utils']
    
    for directory in directories:
        if not os.path.exists(directory):
            print(f"⚠️  Warning: Directory '{directory}' not found")
            os.makedirs(directory, exist_ok=True)
            print(f"   Created empty directory: {directory}")
        else:
            print(f"✅ Found directory: {directory}")

def clean_build():
    """Clean previous build artifacts"""
    print("\n🧹 Cleaning previous build artifacts...")
    
    directories_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.pyc', '*.pyo']
    
    for directory in directories_to_clean:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"   Removed: {directory}")
    
    # Clean .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc') or file.endswith('.pyo'):
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"   Removed: {file_path}")

def main():
    """Main build process"""
    print("🚀 Building Fiserv Automation Taskbar .exe")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('hello_world_gui.py'):
        print("❌ Error: hello_world_gui.py not found!")
        print("   Please run this script from the project root directory")
        sys.exit(1)
    
    # Ensure required directories exist
    ensure_directories()
    
    # Clean previous builds
    clean_build()
    
    # Install/upgrade PyInstaller
    if not run_command("pip install --upgrade pyinstaller", "Installing/upgrading PyInstaller"):
        print("❌ Failed to install PyInstaller")
        sys.exit(1)
    
    # Install all requirements
    if not run_command("pip install -r requirements.txt", "Installing requirements"):
        print("❌ Failed to install requirements")
        sys.exit(1)
    
    # Build the executable using the spec file
    if not run_command("pyinstaller build_exe.spec", "Building executable with PyInstaller"):
        print("❌ Failed to build executable")
        sys.exit(1)
    
    # Check if the executable was created
    exe_path = os.path.join('dist', 'FiservAutomationTaskbar.exe')
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"\n✅ BUILD SUCCESSFUL!")
        print(f"   📦 Executable created: {exe_path}")
        print(f"   📏 File size: {file_size_mb:.1f} MB")
        print(f"\n🎯 DISTRIBUTION READY!")
        print(f"   The executable can be copied to any Windows machine")
        print(f"   Runtime folders (prompts, sequences, images) will be created automatically")
        
        # Create distribution info
        dist_info = f"""
FISERV AUTOMATION TASKBAR - DISTRIBUTION INFO
============================================

📦 Executable: FiservAutomationTaskbar.exe
📏 Size: {file_size_mb:.1f} MB
🖥️  Platform: Windows (64-bit)

📁 RUNTIME FOLDERS:
The following folders will be created next to the .exe when first run:
- prompts/     (AI prompts and templates)
- sequences/   (Recorded automation sequences) 
- images/      (Image templates for recognition)

These folders can be modified by users as needed.

🔧 DEPLOYMENT:
1. Copy FiservAutomationTaskbar.exe to target machine
2. Run the executable
3. Runtime folders will be created automatically
4. No additional installation required

⚡ REQUIREMENTS:
- Windows 10/11 (64-bit)
- No Python installation required
- No additional dependencies required
"""
        
        with open('dist/DISTRIBUTION_INFO.txt', 'w', encoding='utf-8') as f:
            f.write(dist_info)
        
        print(f"   📄 Distribution info saved: dist/DISTRIBUTION_INFO.txt")
        
    else:
        print(f"❌ BUILD FAILED!")
        print(f"   Executable not found at: {exe_path}")
        sys.exit(1)

if __name__ == "__main__":
    main() 