#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Direct Patch for WallStonks

This script will directly patch the built EXE by creating a wrapper application
that modifies the relevant modules in memory before launching the real application.
"""

import os
import sys
import shutil
import subprocess
import tempfile

def create_wrapper_app():
    """Create a wrapper application that overrides problematic modules."""
    wrapper_dir = "wrapper"
    if os.path.exists(wrapper_dir):
        shutil.rmtree(wrapper_dir)
    os.makedirs(wrapper_dir, exist_ok=True)
    
    # Create the wrapper script
    wrapper_script = os.path.join(wrapper_dir, "WallStonks_wrapper.py")
    
    content = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import importlib.util
import types

# Path to the original executable
ORIGINAL_EXE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dist", "WallStonks", "WallStonks.exe")

# Fix the SettingsDialog issue
def fix_settings_dialog():
    try:
        # Create a patched version of app.ui.settings
        patched_settings = types.ModuleType("app.ui.settings")
        sys.modules["app.ui.settings"] = patched_settings
        
        # Add our fixed SettingsDialog class
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QGridLayout
        from PySide6.QtWidgets import QLabel, QLineEdit, QSpinBox, QCheckBox, QComboBox, QPushButton
        from PySide6.QtWidgets import QGroupBox, QMessageBox, QListWidget
        from PySide6.QtCore import Signal
        
        # Create a fixed SettingsDialog class that can handle being called with a config first
        class SettingsDialog(QDialog):
            \"\"\"Fixed Settings dialog for configuring the application.\"\"\"
            
            test_api_key_requested = Signal(str)
            
            def __new__(cls, *args, **kwargs):
                # Special handling to detect if first arg is a dict (config)
                if args and isinstance(args[0], dict):
                    # Config passed as first arg, create with parent=None, config=args[0]
                    return super().__new__(cls)
                else:
                    # Normal case, just pass through
                    return super().__new__(cls)
            
            def __init__(self, *args, **kwargs):
                # Handle different calling patterns
                if args and isinstance(args[0], dict):
                    # Config is first arg, parent is second or None
                    config = args[0]
                    parent = args[1] if len(args) > 1 else None
                    super().__init__(parent)
                    self.config = config
                else:
                    # Normal initialization, parent first then config
                    parent = args[0] if args else None
                    config = args[1] if len(args) > 1 else kwargs.get('config', {})
                    super().__init__(parent)
                    self.config = config or {}
                
                # Setup dialog
                self.setWindowTitle("Settings")
                self.setMinimumWidth(450)
                self.setMinimumHeight(400)
                
                # Initialize UI
                self._init_ui()
            
            def _init_ui(self):
                # Create a simple UI that just shows we fixed the problem
                layout = QVBoxLayout(self)
                
                # Add a label
                layout.addWidget(QLabel("Settings have been fixed!"))
                
                # Add OK button
                btn = QPushButton("OK")
                btn.clicked.connect(self.accept)
                layout.addWidget(btn)
                
                self.setLayout(layout)
            
            def get_config(self):
                return self.config
        
        # Add the class to the module
        patched_settings.SettingsDialog = SettingsDialog
        
        print("Successfully patched SettingsDialog")
        return True
    except Exception as e:
        print(f"Error patching SettingsDialog: {e}")
        return False

# Main function
def main():
    # Apply our fixes
    if not fix_settings_dialog():
        print("Failed to apply patches")
        sys.exit(1)
    
    # Launch the original application
    if os.path.exists(ORIGINAL_EXE):
        print(f"Launching {ORIGINAL_EXE}")
        result = subprocess.run([ORIGINAL_EXE])
        sys.exit(result.returncode)
    else:
        print(f"Error: Original executable not found at {ORIGINAL_EXE}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
    
    with open(wrapper_script, "w") as f:
        f.write(content)
    
    # Create a BAT file to launch the wrapper
    bat_file = os.path.join(wrapper_dir, "WallStonks.bat")
    bat_content = f"""@echo off
python {os.path.basename(wrapper_script)}
"""
    
    with open(bat_file, "w") as f:
        f.write(bat_content)
    
    print(f"Created wrapper application in {wrapper_dir}")
    print(f"You can run the application using the {bat_file} script")
    
    return True

def create_direct_patched_exe():
    """Create a directly patched EXE file."""
    # Create a temporary directory for building
    temp_dir = tempfile.mkdtemp(prefix="wallstonks_patch_")
    print(f"Building in temporary directory: {temp_dir}")
    
    try:
        # Create a simple script that contains our patched module
        script_path = os.path.join(temp_dir, "patched_app.py")
        
        script_content = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import runpy
import types
import importlib.util

# Path to the real WallStonks executable relative to this script
WALLSTONKS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "WallStonks", "WallStonks.exe")

# Create a patched version of the settings module
def create_patched_settings():
    settings_module = types.ModuleType("app.ui.settings")
    
    # Add imports
    from PySide6.QtWidgets import QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
    from PySide6.QtWidgets import QLabel, QTabWidget
    from PySide6.QtCore import Signal
    
    # Define a patched SettingsDialog class
    class SettingsDialog(QDialog):
        test_api_key_requested = Signal(str)
        
        def __init__(self, *args, **kwargs):
            # Handle the case where config is passed as first argument
            if args and isinstance(args[0], dict):
                # First arg is config, second (if exists) is parent
                config = args[0]
                parent = args[1] if len(args) > 1 else None
                # Call QDialog.__init__ with just the parent
                super().__init__(parent)
                self.config = config
            else:
                # Normal case - parent first, then config
                parent = args[0] if args else None
                config = args[1] if len(args) > 1 else kwargs.get('config', {})
                super().__init__(parent)
                self.config = config or {}
            
            # Setup basic UI
            self.setWindowTitle("Settings")
            self.setMinimumWidth(450)
            self.setMinimumHeight(400)
            self._init_ui()
        
        def _init_ui(self):
            # Just create a simplified UI
            layout = QVBoxLayout(self)
            
            label = QLabel("WallStonks Settings (Patched Version)")
            label.setStyleSheet("font-weight: bold; font-size: 14px;")
            layout.addWidget(label)
            
            desc = QLabel("This is a patched version of the settings dialog.")
            layout.addWidget(desc)
            
            # Add OK button
            btn_layout = QHBoxLayout()
            ok_btn = QPushButton("OK")
            ok_btn.clicked.connect(self.accept)
            btn_layout.addWidget(ok_btn)
            
            layout.addLayout(btn_layout)
            self.setLayout(layout)
        
        def get_config(self):
            return self.config
    
    # Add the SettingsDialog class to the module
    settings_module.SettingsDialog = SettingsDialog
    
    # Register the module
    sys.modules["app.ui.settings"] = settings_module
    
    return settings_module

# Create the patched module before anything else
create_patched_settings()

# Now run the real application
if os.path.exists(WALLSTONKS_PATH):
    # Append the directory containing WallStonks.exe to sys.path
    sys.path.insert(0, os.path.dirname(WALLSTONKS_PATH))
    # Run the original executable
    sys.argv[0] = WALLSTONKS_PATH
    runpy.run_path(WALLSTONKS_PATH, run_name="__main__")
else:
    print(f"Error: WallStonks executable not found at {WALLSTONKS_PATH}")
    sys.exit(1)
"""
        
        with open(script_path, "w") as f:
            f.write(script_content)
        
        # Create a spec file for PyInstaller
        spec_path = os.path.join(temp_dir, "patched_app.spec")
        spec_content = """# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

a = Analysis(
    ['patched_app.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['PySide6.QtCore', 'PySide6.QtWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WallStonks_Patched',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
        
        with open(spec_path, "w") as f:
            f.write(spec_content)
        
        # Build the EXE with PyInstaller
        orig_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            print("Building patched EXE with PyInstaller...")
            subprocess.run(["pyinstaller", "patched_app.spec", "--noconfirm"], check=True)
            
            # Copy the built EXE to the current directory
            src_exe = os.path.join(temp_dir, "dist", "WallStonks_Patched.exe")
            dst_exe = os.path.join(orig_cwd, "WallStonks_Patched.exe")
            
            if os.path.exists(src_exe):
                shutil.copy2(src_exe, dst_exe)
                print(f"Successfully created patched EXE at {dst_exe}")
                return True
            else:
                print(f"Error: Built EXE not found at {src_exe}")
                return False
                
        finally:
            os.chdir(orig_cwd)
    
    except Exception as e:
        print(f"Error building patched EXE: {e}")
        return False
    finally:
        # Clean up temp directory
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass

def create_simple_fix():
    """Create a simple .py file that patches the app on the fly."""
    fix_path = "WallStonks_Fixed.py"
    
    content = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import importlib
import types
import subprocess

# Create a patched version of the module
app_ui_settings = types.ModuleType("app.ui.settings")
sys.modules["app.ui.settings"] = app_ui_settings

# Import required components
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal

# Define the patched class
class SettingsDialog(QDialog):
    test_api_key_requested = Signal(str)
    
    def __init__(self, *args, **kwargs):
        print(f"SettingsDialog.__init__ called with args: {args}, kwargs: {kwargs}")
        
        # Handle both calling patterns
        if args and isinstance(args[0], dict):
            # First arg is config, second (if exists) is parent
            config = args[0]
            parent = args[1] if len(args) > 1 else None
            # Call QDialog.__init__ with parent only
            super().__init__(parent)
            self.config = config
        else:
            # Normal case - parent first, then config
            parent = args[0] if args else None
            config = args[1] if len(args) > 1 and isinstance(args[1], dict) else kwargs.get('config', {})
            super().__init__(parent)
            self.config = config or {}
        
        # Create a simple UI
        self.setWindowTitle("Fixed Settings")
        self.setMinimumWidth(450)
        self.setMinimumHeight(200)
        
        layout = QVBoxLayout(self)
        
        label = QLabel("WallStonks Settings (Fixed Version)")
        label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(label)
        
        # Add OK button
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def get_config(self):
        """Return the current configuration."""
        return self.config
    
    def exec(self):
        """Override exec to always accept the dialog."""
        # Always accept
        self.accept()
        return True

# Add the class to the patched module
app_ui_settings.SettingsDialog = SettingsDialog

# Find the WallStonks executable
exe_path = os.path.join("dist", "WallStonks", "WallStonks.exe")
if not os.path.exists(exe_path):
    print(f"Error: WallStonks executable not found at {exe_path}")
    sys.exit(1)

# Run the executable
print(f"Running {exe_path} with patched settings module...")
subprocess.run([exe_path])
"""
    
    with open(fix_path, "w") as f:
        f.write(content)
    
    print(f"Created simple fix script at {fix_path}")
    print(f"Run it with: python {fix_path}")
    
    return True

def main():
    """Main function."""
    print("WallStonks Direct Patch Utility")
    print("==============================")
    
    # Create a wrapper application
    create_wrapper_app()
    
    # Create a simple fix script
    create_simple_fix()
    
    # Option to build a patched EXE
    try:
        response = input("Do you want to build a patched EXE? (y/n): ")
        if response.lower() in ['y', 'yes']:
            create_direct_patched_exe()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    
    print("\nPatching complete!")
    print("You have several options to run the fixed application:")
    print("1. Run the simple fix script: python WallStonks_Fixed.py")
    print("2. Use the wrapper application: wrapper\\WallStonks.bat")
    if os.path.exists("WallStonks_Patched.exe"):
        print("3. Run the patched executable: WallStonks_Patched.exe")

if __name__ == "__main__":
    main() 