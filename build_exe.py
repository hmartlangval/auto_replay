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
    
    # Build the main executable using the spec file
    if not run_command("pyinstaller build_exe.spec", "Building main executable with PyInstaller"):
        print("❌ Failed to build main executable")
        sys.exit(1)
    
    # Build the BTT executable using the spec file
    if not run_command("pyinstaller build_btt.spec", "Building BTT executable with PyInstaller"):
        print("❌ Failed to build BTT executable")
        sys.exit(1)
    
    # Organize the distribution structure
    print("\n🔧 Organizing distribution structure...")
    
    # BTT executable should remain as sibling to main executable
    btt_src = os.path.join('dist', 'btt.exe')
    
    if os.path.exists(btt_src):
        print(f"   📁 BTT executable ready: {btt_src}")
    else:
        print("   ⚠️ BTT executable not found, continuing anyway...")
    
    # Check if the main executable was created
    exe_path = os.path.join('dist', 'FiservAutomationTaskbar.exe')
    btt_exe_path = os.path.join('dist', 'btt.exe')
    
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path)
        file_size_mb = file_size / (1024 * 1024)
        
        btt_file_size = 0
        btt_file_size_mb = 0
        if os.path.exists(btt_exe_path):
            btt_file_size = os.path.getsize(btt_exe_path)
            btt_file_size_mb = btt_file_size / (1024 * 1024)
        
        total_size_mb = file_size_mb + btt_file_size_mb
        
        print(f"\n✅ BUILD SUCCESSFUL!")
        print(f"   📦 Main executable: {exe_path} ({file_size_mb:.1f} MB)")
        print(f"   🤖 BTT executable: {btt_exe_path} ({btt_file_size_mb:.1f} MB)")
        print(f"   📏 Total size: {total_size_mb:.1f} MB")
        print(f"\n🎯 DISTRIBUTION READY!")
        print(f"   The executables can be copied to any Windows machine")
        print(f"   Runtime folders (prompts, sequences, images) will be created automatically")
        print(f"   BTT can be run independently or via the main taskbar")
        
                 # Create distribution info
        dist_info = f"""
FISERV AUTOMATION TASKBAR - DISTRIBUTION INFO
============================================

📦 Main Executable: FiservAutomationTaskbar.exe ({file_size_mb:.1f} MB)
🤖 BTT Executable: btt.exe ({btt_file_size_mb:.1f} MB)
📏 Total Size: {total_size_mb:.1f} MB
🖥️  Platform: Windows (64-bit)

📁 DISTRIBUTION STRUCTURE:
FiservAutomationTaskbar.exe    (Main taskbar application)
btt.exe                        (BTT automation - can run independently)
prompts/                       (AI prompts and templates - user modifiable)
sequences/                     (Recorded automation sequences - user modifiable)
images/                        (Image templates for recognition - user modifiable)

🔧 USAGE:
1. Run FiservAutomationTaskbar.exe for the main taskbar interface
2. Use "Start BTT" button to launch BTT automation via the taskbar
3. Or run btt.exe directly for standalone BTT automation

📁 RUNTIME FOLDERS:
The prompts/, sequences/, and images/ folders will be created automatically
when first run. These folders can be modified by users as needed.

🔧 DEPLOYMENT:
1. Copy the entire folder structure to target machine
2. Run FiservAutomationTaskbar.exe or automation/btt.exe as needed
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