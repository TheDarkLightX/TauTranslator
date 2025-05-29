#!/usr/bin/env python3
"""
Ubuntu Desktop Launcher Creator for TauTranslatorOmega
=====================================================

Creates proper Ubuntu desktop integration with .desktop files,
application menu entries, and executable scripts.
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

class UbuntuLauncherCreator:
    """Creates Ubuntu desktop integration for TauTranslatorOmega."""
    
    def __init__(self):
        self.app_dir = Path(__file__).parent.absolute()
        self.home_dir = Path.home()
        self.desktop_dir = self.home_dir / "Desktop"
        self.applications_dir = self.home_dir / ".local/share/applications"
        self.bin_dir = self.home_dir / ".local/bin"
        
        # Ensure directories exist
        self.applications_dir.mkdir(parents=True, exist_ok=True)
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🏠 App Directory: {self.app_dir}")
        print(f"📁 Applications: {self.applications_dir}")
        print(f"🔧 Bin Directory: {self.bin_dir}")
    
    def create_executable_script(self):
        """Create executable script in ~/.local/bin."""
        script_content = f'''#!/bin/bash
# TauTranslatorOmega Launcher Script
# Auto-generated Ubuntu launcher

APP_DIR="{self.app_dir}"
cd "$APP_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    zenity --error --text="Python 3 is required but not installed.\\nPlease install Python 3 and try again."
    exit 1
fi

# Check if tkinter is available
if ! python3 -c "import tkinter" 2>/dev/null; then
    zenity --error --text="Python tkinter is required but not installed.\\nRun: sudo apt install python3-tk"
    exit 1
fi

# Launch the application
python3 tau_translator_app.py
'''
        
        script_path = self.bin_dir / "tau-translator-omega"
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_path, 0o755)
        
        print(f"✅ Executable script created: {script_path}")
        return script_path
    
    def create_desktop_file(self, script_path):
        """Create .desktop file for application menu."""
        desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name=TauTranslatorOmega
Comment=Professional AI-Enhanced Tau Language Translation
GenericName=Language Translator
Exec={script_path}
Icon={self.app_dir}/assets/icon.png
Terminal=false
StartupNotify=true
Categories=Development;Education;Science;
Keywords=tau;translation;formal;language;ai;
MimeType=text/plain;application/x-tau;
StartupWMClass=tau-translator-omega

# Additional metadata
X-GNOME-FullName=TauTranslatorOmega Professional
X-GNOME-SingleWindow=true
X-Ubuntu-Touch=true
'''
        
        desktop_path = self.applications_dir / "tau-translator-omega.desktop"
        
        with open(desktop_path, 'w') as f:
            f.write(desktop_content)
        
        # Make executable
        os.chmod(desktop_path, 0o755)
        
        print(f"✅ Desktop file created: {desktop_path}")
        return desktop_path
    
    def create_desktop_shortcut(self, desktop_file_path):
        """Create desktop shortcut."""
        if self.desktop_dir.exists():
            shortcut_path = self.desktop_dir / "TauTranslatorOmega.desktop"
            shutil.copy2(desktop_file_path, shortcut_path)
            os.chmod(shortcut_path, 0o755)
            print(f"✅ Desktop shortcut created: {shortcut_path}")
            return shortcut_path
        else:
            print("⚠️  Desktop directory not found, skipping desktop shortcut")
            return None
    
    def create_application_icon(self):
        """Create application icon."""
        # Create assets directory
        assets_dir = self.app_dir / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        # Create a simple SVG icon (since we can't use external images)
        icon_svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="128" height="128" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3498db;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#2c3e50;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background circle -->
  <circle cx="64" cy="64" r="60" fill="url(#grad1)" stroke="#2c3e50" stroke-width="4"/>
  
  <!-- Globe icon -->
  <circle cx="64" cy="64" r="35" fill="none" stroke="#ffffff" stroke-width="3"/>
  <path d="M 29 64 Q 64 40 99 64" fill="none" stroke="#ffffff" stroke-width="2"/>
  <path d="M 29 64 Q 64 88 99 64" fill="none" stroke="#ffffff" stroke-width="2"/>
  <line x1="64" y1="29" x2="64" y2="99" stroke="#ffffff" stroke-width="2"/>
  
  <!-- Translation arrows -->
  <path d="M 20 45 L 30 40 L 30 50 Z" fill="#f39c12"/>
  <path d="M 108 83 L 98 78 L 98 88 Z" fill="#f39c12"/>
  
  <!-- Text elements -->
  <text x="64" y="110" text-anchor="middle" font-family="Arial" font-size="12" font-weight="bold" fill="#2c3e50">Tau</text>
</svg>'''
        
        icon_path = assets_dir / "icon.svg"
        with open(icon_path, 'w') as f:
            f.write(icon_svg)
        
        # Try to convert to PNG using available tools
        png_path = assets_dir / "icon.png"
        
        try:
            # Try using rsvg-convert (usually available)
            subprocess.run(['rsvg-convert', '-w', '128', '-h', '128', str(icon_path), '-o', str(png_path)], 
                         check=True, capture_output=True)
            print(f"✅ PNG icon created: {png_path}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                # Try using ImageMagick convert
                subprocess.run(['convert', str(icon_path), str(png_path)], 
                             check=True, capture_output=True)
                print(f"✅ PNG icon created: {png_path}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  Could not convert SVG to PNG. Using SVG icon.")
                return icon_path
        
        return png_path
    
    def update_path(self):
        """Add ~/.local/bin to PATH if not already there."""
        bashrc_path = self.home_dir / ".bashrc"
        
        # Check if already in PATH
        try:
            result = subprocess.run(['bash', '-c', 'echo $PATH'], capture_output=True, text=True)
            if str(self.bin_dir) in result.stdout:
                print("✅ ~/.local/bin already in PATH")
                return
        except:
            pass
        
        # Add to .bashrc
        path_line = f'\n# Added by TauTranslatorOmega installer\nexport PATH="$HOME/.local/bin:$PATH"\n'
        
        try:
            with open(bashrc_path, 'a') as f:
                f.write(path_line)
            print("✅ Added ~/.local/bin to PATH in .bashrc")
            print("   Run 'source ~/.bashrc' or restart terminal to update PATH")
        except Exception as e:
            print(f"⚠️  Could not update .bashrc: {e}")
    
    def register_mime_type(self):
        """Register .tau file association."""
        mime_content = '''<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/x-tau">
    <comment>Tau Language File</comment>
    <comment xml:lang="en">Tau Language File</comment>
    <glob pattern="*.tau"/>
    <icon name="text-x-script"/>
  </mime-type>
</mime-info>'''
        
        mime_dir = self.home_dir / ".local/share/mime/packages"
        mime_dir.mkdir(parents=True, exist_ok=True)
        
        mime_path = mime_dir / "tau-language.xml"
        with open(mime_path, 'w') as f:
            f.write(mime_content)
        
        try:
            subprocess.run(['update-mime-database', str(self.home_dir / ".local/share/mime")], 
                         check=True, capture_output=True)
            print("✅ Registered .tau file type")
        except Exception as e:
            print(f"⚠️  Could not register MIME type: {e}")
    
    def create_uninstaller(self):
        """Create uninstaller script."""
        uninstall_content = f'''#!/bin/bash
# TauTranslatorOmega Uninstaller

echo "🗑️  Uninstalling TauTranslatorOmega..."

# Remove executable
rm -f "{self.bin_dir}/tau-translator-omega"

# Remove desktop files
rm -f "{self.applications_dir}/tau-translator-omega.desktop"
rm -f "{self.desktop_dir}/TauTranslatorOmega.desktop"

# Remove MIME type
rm -f "{self.home_dir}/.local/share/mime/packages/tau-language.xml"
update-mime-database "{self.home_dir}/.local/share/mime" 2>/dev/null

# Update desktop database
update-desktop-database "{self.applications_dir}" 2>/dev/null

echo "✅ TauTranslatorOmega uninstalled successfully"
echo "   Application files in {self.app_dir} were not removed"
'''
        
        uninstall_path = self.app_dir / "uninstall.sh"
        with open(uninstall_path, 'w') as f:
            f.write(uninstall_content)
        
        os.chmod(uninstall_path, 0o755)
        print(f"✅ Uninstaller created: {uninstall_path}")
    
    def update_desktop_database(self):
        """Update desktop database to refresh application menu."""
        try:
            subprocess.run(['update-desktop-database', str(self.applications_dir)], 
                         check=True, capture_output=True)
            print("✅ Desktop database updated")
        except Exception as e:
            print(f"⚠️  Could not update desktop database: {e}")
    
    def install(self):
        """Complete installation process."""
        print("🚀 Installing TauTranslatorOmega for Ubuntu...")
        print("=" * 50)
        
        # Create icon
        icon_path = self.create_application_icon()
        
        # Create executable script
        script_path = self.create_executable_script()
        
        # Create desktop file
        desktop_file = self.create_desktop_file(script_path)
        
        # Create desktop shortcut
        self.create_desktop_shortcut(desktop_file)
        
        # Update PATH
        self.update_path()
        
        # Register MIME type
        self.register_mime_type()
        
        # Create uninstaller
        self.create_uninstaller()
        
        # Update desktop database
        self.update_desktop_database()
        
        print("\n" + "=" * 50)
        print("🎉 INSTALLATION COMPLETE!")
        print("=" * 50)
        
        print("\n🚀 How to Launch:")
        print("   1. Applications Menu → Development → TauTranslatorOmega")
        print("   2. Desktop shortcut (if created)")
        print("   3. Terminal: tau-translator-omega")
        print("   4. Alt+F2 → tau-translator-omega")
        
        print("\n📁 Files Created:")
        print(f"   • Executable: {script_path}")
        print(f"   • Desktop file: {desktop_file}")
        print(f"   • Icon: {icon_path}")
        print(f"   • Uninstaller: {self.app_dir}/uninstall.sh")
        
        print("\n⚠️  Note:")
        print("   • Restart terminal or run 'source ~/.bashrc' for PATH update")
        print("   • Log out/in to refresh application menu")
        
        return True

def main():
    """Main installation function."""
    print("🐧 TauTranslatorOmega Ubuntu Launcher Creator")
    print("Creating desktop integration for Ubuntu...")
    
    try:
        installer = UbuntuLauncherCreator()
        success = installer.install()
        
        if success:
            print("\n✅ TauTranslatorOmega is now installed as a Ubuntu application!")
            print("🎯 You can now launch it from the Applications menu or desktop")
        else:
            print("\n❌ Installation failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Installation error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
