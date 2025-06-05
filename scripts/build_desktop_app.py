#!/usr/bin/env python3
"""
Cross-Platform Desktop App Builder for TauTranslator
===================================================

Builds native executables for Mac, Windows, and Linux.
Handles platform-specific requirements and packaging.

Author: DarkLightX/Dana Edwards
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
import argparse

class DesktopAppBuilder:
    """Cross-platform desktop app builder for TauTranslator."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.absolute()
        self.ui_dir = self.project_root / "ui"
        self.src_dir = self.project_root / "src"
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        
        # Platform detection
        self.system = platform.system()
        self.is_mac = self.system == "Darwin"
        self.is_windows = self.system == "Windows"
        self.is_linux = self.system == "Linux"
        
        # Application info
        self.app_name = "TauTranslator"
        self.app_version = "3.0.0"
        # Allow choosing between tkinter and PyQt6 versions
        use_qt = os.environ.get('USE_QT6', 'true').lower() == 'true'
        if use_qt and (self.ui_dir / "tau_translator_desktop_qt.py").exists():
            self.main_script = self.ui_dir / "tau_translator_desktop_qt.py"
            print("📱 Using PyQt6 interface")
        else:
            self.main_script = self.ui_dir / "tau_translator_desktop_tkinter.py"
            print("🖼️  Using tkinter interface")
        
        print(f"🖥️  Platform: {self.system}")
        print(f"📁 Project root: {self.project_root}")
        print(f"🎯 Main script: {self.main_script}")
    
    def check_dependencies(self):
        """Check and install required dependencies."""
        print("\n🔍 Checking dependencies...")
        
        # Check Python version
        python_version = sys.version_info
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        if python_version < (3, 8):
            print("❌ Python 3.8+ required")
            return False
        
        # Check PyInstaller
        try:
            import PyInstaller
            print(f"✅ PyInstaller {PyInstaller.__version__}")
        except ImportError:
            print("📦 Installing PyInstaller...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installed")
        
        # Platform-specific dependencies
        if self.is_mac:
            # Check for py2app (optional, for .app bundles)
            try:
                import py2app
                print(f"✅ py2app available")
            except ImportError:
                print("ℹ️  py2app not installed (optional for .app bundles)")
        
        return True
    
    def prepare_build(self):
        """Prepare build environment."""
        print("\n🧹 Preparing build environment...")
        
        # Clean previous builds
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        
        self.dist_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)
        
        print("✅ Build directories prepared")
    
    def get_hidden_imports(self):
        """Get list of hidden imports for PyInstaller."""
        hidden_imports = [
            # Core TauTranslator modules
            'tau_translator_omega',
            'tau_translator_omega.lmql_engine',
            'tau_translator_omega.lmql_engine.bidirectional_translator',
            'tau_translator_omega.lmql_engine.pattern_analyzers',
            'tau_translator_omega.lmql_engine.recognizers',
            'tau_translator_omega.core_engine',
            'tau_translator_omega.vocabulary',
            
            # GUI frameworks
            'tkinter',
            'tkinter.ttk',
            'tkinter.scrolledtext',
            'tkinter.filedialog',
            'tkinter.messagebox',
            
            # PyQt6 (if used)
            'PyQt6',
            'PyQt6.QtCore',
            'PyQt6.QtGui',
            'PyQt6.QtWidgets',
            
            # Standard library
            'json',
            'pathlib',
            'threading',
            'subprocess',
            'typing',
            're',
            'dataclasses',
            'enum',
            'abc',
            
            # Optional but useful
            'requests',
        ]
        
        # Platform-specific imports
        if self.is_mac:
            hidden_imports.extend([
                'platform',
                'os',
            ])
        elif self.is_windows:
            hidden_imports.extend([
                'win32api',
                'win32con',
            ])
        
        return hidden_imports
    
    def get_data_files(self):
        """Get list of data files to include."""
        data_files = []
        
        # Include src directory
        if self.src_dir.exists():
            data_files.append((str(self.src_dir), 'src'))
        
        # Include assets
        assets_dir = self.project_root / 'assets'
        if assets_dir.exists():
            data_files.append((str(assets_dir), 'assets'))
        
        # Include grammars
        grammars_dir = self.project_root / 'grammars'
        if grammars_dir.exists():
            data_files.append((str(grammars_dir), 'grammars'))
        
        # Include splash screen
        splash_screen = self.ui_dir / 'splash_screen.py'
        if splash_screen.exists():
            data_files.append((str(splash_screen), '.'))
        
        return data_files
    
    def build_mac_app(self):
        """Build macOS application."""
        print("\n🍎 Building macOS application...")
        
        app_name = f"{self.app_name}.app"
        
        # PyInstaller command
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--name', self.app_name,
            '--onedir',  # Use directory mode for better compatibility
            '--windowed',  # No console window
            '--osx-bundle-identifier', f'com.tautranslator.{self.app_name.lower()}',
        ]
        
        # Add icon if available
        icon_path = self.project_root / 'assets' / 'icon.icns'
        if not icon_path.exists():
            # Try to find or create icon
            icon_svg = self.project_root / 'assets' / 'icon.svg'
            if icon_svg.exists():
                print("📸 Converting SVG to ICNS...")
                self.create_mac_icon(icon_svg, icon_path)
        
        if icon_path.exists():
            cmd.extend(['--icon', str(icon_path)])
        
        # Add hidden imports
        for imp in self.get_hidden_imports():
            cmd.extend(['--hidden-import', imp])
        
        # Add data files
        for src, dst in self.get_data_files():
            cmd.extend(['--add-data', f'{src}:{dst}'])
        
        # Add paths
        cmd.extend([
            '--paths', str(self.src_dir),
            '--paths', str(self.ui_dir),
        ])
        
        # Exclude unnecessary modules
        cmd.extend([
            '--exclude-module', 'matplotlib',
            '--exclude-module', 'numpy',
            '--exclude-module', 'scipy',
            '--exclude-module', 'pandas',
        ])
        
        # Add main script
        cmd.append(str(self.main_script))
        
        # Run PyInstaller
        try:
            print("🔨 Running PyInstaller...")
            subprocess.check_call(cmd)
            
            # Move to dist directory
            app_bundle = self.dist_dir / app_name
            if (Path('dist') / self.app_name / self.app_name).exists():
                # Create proper app bundle structure
                self.create_mac_app_bundle(Path('dist') / self.app_name, app_bundle)
            
            print(f"✅ macOS app built: {app_bundle}")
            
            # Create DMG (optional)
            if shutil.which('hdiutil'):
                self.create_dmg(app_bundle)
            
            return app_bundle
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            return None
    
    def create_mac_icon(self, svg_path, icns_path):
        """Convert SVG to ICNS for macOS."""
        try:
            # Create temporary iconset
            iconset_path = icns_path.with_suffix('.iconset')
            iconset_path.mkdir(exist_ok=True)
            
            # Generate different sizes
            sizes = [16, 32, 64, 128, 256, 512]
            for size in sizes:
                for scale in [1, 2]:
                    actual_size = size * scale
                    suffix = f"_{size}x{size}" if scale == 1 else f"_{size}x{size}@2x"
                    png_path = iconset_path / f"icon{suffix}.png"
                    
                    # Convert SVG to PNG (requires rsvg-convert or similar)
                    if shutil.which('rsvg-convert'):
                        subprocess.run([
                            'rsvg-convert', '-w', str(actual_size), '-h', str(actual_size),
                            str(svg_path), '-o', str(png_path)
                        ])
            
            # Convert iconset to icns
            subprocess.run(['iconutil', '-c', 'icns', str(iconset_path)])
            
            # Clean up
            shutil.rmtree(iconset_path)
            
            print("✅ Icon created")
            
        except Exception as e:
            print(f"⚠️  Icon creation failed: {e}")
    
    def create_mac_app_bundle(self, src_dir, app_bundle):
        """Create proper macOS app bundle structure."""
        print("📦 Creating app bundle...")
        
        # Create bundle structure
        contents = app_bundle / "Contents"
        macos = contents / "MacOS"
        resources = contents / "Resources"
        
        contents.mkdir(parents=True, exist_ok=True)
        macos.mkdir(exist_ok=True)
        resources.mkdir(exist_ok=True)
        
        # Copy executable
        exe_src = src_dir / self.app_name
        if exe_src.exists():
            shutil.copy2(exe_src, macos / self.app_name)
            os.chmod(macos / self.app_name, 0o755)
        
        # Copy resources
        for item in src_dir.iterdir():
            if item.name != self.app_name:
                if item.is_dir():
                    shutil.copytree(item, resources / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, resources)
        
        # Create Info.plist
        info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>{self.app_name}</string>
    <key>CFBundleExecutable</key>
    <string>{self.app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.tautranslator.{self.app_name.lower()}</string>
    <key>CFBundleName</key>
    <string>{self.app_name}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>{self.app_version}</string>
    <key>CFBundleVersion</key>
    <string>{self.app_version}</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.12</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2024 TauTranslator Team</string>
</dict>
</plist>"""
        
        with open(contents / "Info.plist", "w") as f:
            f.write(info_plist)
        
        print("✅ App bundle created")
    
    def create_dmg(self, app_bundle):
        """Create DMG installer for macOS."""
        print("💿 Creating DMG installer...")
        
        dmg_name = f"{self.app_name}-{self.app_version}-mac.dmg"
        dmg_path = self.dist_dir / dmg_name
        
        try:
            # Create temporary directory for DMG contents
            dmg_temp = self.build_dir / "dmg_temp"
            dmg_temp.mkdir(exist_ok=True)
            
            # Copy app bundle
            shutil.copytree(app_bundle, dmg_temp / app_bundle.name)
            
            # Create Applications symlink
            os.symlink("/Applications", str(dmg_temp / "Applications"))
            
            # Create DMG
            subprocess.run([
                'hdiutil', 'create', '-volname', self.app_name,
                '-srcfolder', str(dmg_temp),
                '-ov', '-format', 'UDZO',
                str(dmg_path)
            ], check=True)
            
            print(f"✅ DMG created: {dmg_path}")
            
        except Exception as e:
            print(f"⚠️  DMG creation failed: {e}")
    
    def build_windows_exe(self):
        """Build Windows executable."""
        print("\n🪟 Building Windows executable...")
        
        # This method would be called when running on Windows
        # Similar structure to Mac build but with Windows-specific options
        pass
    
    def build_linux_app(self):
        """Build Linux application."""
        print("\n🐧 Building Linux application...")
        
        # This method would be called when running on Linux
        # Can create AppImage, deb, rpm, etc.
        pass
    
    def build(self):
        """Main build process."""
        print(f"\n🚀 Building {self.app_name} Desktop Application")
        print("=" * 50)
        
        if not self.check_dependencies():
            return False
        
        self.prepare_build()
        
        # Build for current platform
        if self.is_mac:
            result = self.build_mac_app()
        elif self.is_windows:
            result = self.build_windows_exe()
        elif self.is_linux:
            result = self.build_linux_app()
        else:
            print(f"❌ Unsupported platform: {self.system}")
            return False
        
        if result:
            print("\n✅ Build completed successfully!")
            print(f"📁 Output: {result}")
            return True
        else:
            print("\n❌ Build failed")
            return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build TauTranslator Desktop App")
    parser.add_argument('--platform', choices=['mac', 'windows', 'linux'],
                        help='Target platform (default: current platform)')
    
    args = parser.parse_args()
    
    builder = DesktopAppBuilder()
    
    # Override platform if specified
    if args.platform:
        builder.system = {'mac': 'Darwin', 'windows': 'Windows', 'linux': 'Linux'}[args.platform]
        builder.is_mac = args.platform == 'mac'
        builder.is_windows = args.platform == 'windows'
        builder.is_linux = args.platform == 'linux'
    
    success = builder.build()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()