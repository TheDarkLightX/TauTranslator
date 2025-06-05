#!/usr/bin/env python3
"""
TauTranslatorOmega Executable Compiler
=====================================

Compiles TauTranslatorOmega into standalone executables for Ubuntu.
Creates both single-file and directory distributions.
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

class ExecutableCompiler:
    """Compiles TauTranslatorOmega into standalone executables."""
    
    def __init__(self):
        self.app_dir = Path(__file__).parent.absolute()
        self.dist_dir = self.app_dir / "dist"
        self.build_dir = self.app_dir / "build"
        
        print(f"📁 App Directory: {self.app_dir}")
        print(f"📦 Distribution: {self.dist_dir}")
    
    def check_dependencies(self):
        """Check if required tools are installed."""
        print("🔍 Checking dependencies...")
        
        # Check Python
        try:
            python_version = subprocess.run([sys.executable, '--version'], 
                                          capture_output=True, text=True)
            print(f"✅ Python: {python_version.stdout.strip()}")
        except Exception as e:
            print(f"❌ Python check failed: {e}")
            return False
        
        # Check PyInstaller
        try:
            result = subprocess.run([sys.executable, '-c', 'import PyInstaller'], 
                                  capture_output=True)
            if result.returncode == 0:
                print("✅ PyInstaller: Available")
            else:
                print("⚠️  PyInstaller not found, installing...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], 
                             check=True)
                print("✅ PyInstaller: Installed")
        except Exception as e:
            print(f"❌ PyInstaller installation failed: {e}")
            return False
        
        return True
    
    def create_spec_file(self):
        """Create PyInstaller spec file for advanced configuration."""
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Application info
app_name = 'TauTranslatorOmega'
app_dir = Path(r'{self.app_dir}')

# Analysis configuration
a = Analysis(
    [str(app_dir / 'tau_translator_app.py')],
    pathex=[str(app_dir), str(app_dir / 'src')],
    binaries=[],
    datas=[
        (str(app_dir / 'src'), 'src'),
        (str(app_dir / 'assets'), 'assets') if (app_dir / 'assets').exists() else None,
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tau_translator_omega.lmql_engine.bidirectional_translator',
        'tau_translator_omega.lmql_engine.pattern_analyzer',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PIL',
        'cv2',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove None entries from datas
a.datas = [item for item in a.datas if item is not None]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Single file executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(app_dir / 'assets' / 'icon.ico') if (app_dir / 'assets' / 'icon.ico').exists() else None,
)

# Directory distribution (faster startup)
exe_dir = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name + '_dir',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe_dir,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name + '_dir',
)
'''
        
        spec_path = self.app_dir / "tau_translator_omega.spec"
        with open(spec_path, 'w') as f:
            f.write(spec_content)
        
        print(f"✅ Spec file created: {spec_path}")
        return spec_path
    
    def compile_single_file(self):
        """Compile to single executable file."""
        print("\n📦 Compiling single-file executable...")
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onefile',
            '--windowed',
            '--name', 'TauTranslatorOmega',
            '--distpath', str(self.dist_dir),
            '--workpath', str(self.build_dir),
            '--add-data', f'{self.app_dir}/src:src',
            '--hidden-import', 'tkinter',
            '--hidden-import', 'tkinter.ttk',
            '--exclude-module', 'matplotlib',
            '--exclude-module', 'numpy',
            '--exclude-module', 'scipy',
            str(self.app_dir / 'tau_translator_app.py')
        ]
        
        # Add icon if available
        icon_path = self.app_dir / 'assets' / 'icon.ico'
        if icon_path.exists():
            cmd.extend(['--icon', str(icon_path)])
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Single-file executable compiled successfully")
            
            executable_path = self.dist_dir / 'TauTranslatorOmega'
            if executable_path.exists():
                size_mb = executable_path.stat().st_size / (1024 * 1024)
                print(f"   📁 Location: {executable_path}")
                print(f"   📏 Size: {size_mb:.1f} MB")
                return executable_path
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Single-file compilation failed: {e}")
            print(f"   Error output: {e.stderr}")
            return None
    
    def compile_directory(self):
        """Compile to directory distribution."""
        print("\n📁 Compiling directory distribution...")
        
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--onedir',
            '--windowed',
            '--name', 'TauTranslatorOmega_dir',
            '--distpath', str(self.dist_dir),
            '--workpath', str(self.build_dir),
            '--add-data', f'{self.app_dir}/src:src',
            '--hidden-import', 'tkinter',
            '--hidden-import', 'tkinter.ttk',
            '--exclude-module', 'matplotlib',
            '--exclude-module', 'numpy',
            str(self.app_dir / 'tau_translator_app.py')
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Directory distribution compiled successfully")
            
            dist_path = self.dist_dir / 'TauTranslatorOmega_dir'
            if dist_path.exists():
                # Calculate total size
                total_size = sum(f.stat().st_size for f in dist_path.rglob('*') if f.is_file())
                size_mb = total_size / (1024 * 1024)
                print(f"   📁 Location: {dist_path}")
                print(f"   📏 Size: {size_mb:.1f} MB")
                return dist_path
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Directory compilation failed: {e}")
            return None
    
    def create_appimage(self):
        """Create AppImage for portable Linux distribution."""
        print("\n📱 Creating AppImage...")
        
        try:
            # Check if appimagetool is available
            subprocess.run(['appimagetool', '--version'], 
                         check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  appimagetool not found, skipping AppImage creation")
            print("   Install with: wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage")
            return None
        
        # Create AppDir structure
        appdir = self.dist_dir / 'TauTranslatorOmega.AppDir'
        appdir.mkdir(exist_ok=True)
        
        # Copy executable
        exe_path = self.dist_dir / 'TauTranslatorOmega'
        if exe_path.exists():
            shutil.copy2(exe_path, appdir / 'AppRun')
            os.chmod(appdir / 'AppRun', 0o755)
        
        # Create desktop file
        desktop_content = '''[Desktop Entry]
Type=Application
Name=TauTranslatorOmega
Exec=AppRun
Icon=tau-translator-omega
Categories=Development;Education;
'''
        
        with open(appdir / 'tau-translator-omega.desktop', 'w') as f:
            f.write(desktop_content)
        
        # Copy icon
        icon_path = self.app_dir / 'assets' / 'icon.png'
        if icon_path.exists():
            shutil.copy2(icon_path, appdir / 'tau-translator-omega.png')
        
        # Create AppImage
        try:
            subprocess.run(['appimagetool', str(appdir)], 
                         check=True, cwd=str(self.dist_dir))
            
            appimage_path = self.dist_dir / 'TauTranslatorOmega-x86_64.AppImage'
            if appimage_path.exists():
                print(f"✅ AppImage created: {appimage_path}")
                return appimage_path
        except subprocess.CalledProcessError as e:
            print(f"❌ AppImage creation failed: {e}")
        
        return None
    
    def create_deb_package(self):
        """Create .deb package for Ubuntu."""
        print("\n📦 Creating .deb package...")
        
        # Create package structure
        pkg_dir = self.dist_dir / 'tau-translator-omega_3.0-1_amd64'
        pkg_dir.mkdir(exist_ok=True)
        
        # DEBIAN control directory
        debian_dir = pkg_dir / 'DEBIAN'
        debian_dir.mkdir(exist_ok=True)
        
        # Control file
        control_content = '''Package: tau-translator-omega
Version: 3.0-1
Section: devel
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.8), python3-tk
Maintainer: TauTranslatorOmega Team <info@tautranslator.com>
Description: Professional AI-Enhanced Tau Language Translation
 TauTranslatorOmega is a professional desktop application for translating
 between Tau Language and natural language. Features AI-enhanced translation
 with Google's Gemma 3 model and reliable pattern-based fallback.
 .
 Key features:
  * Bidirectional Tau ↔ Natural Language translation
  * AI-enhanced translation with Gemma 3
  * Professional desktop interface
  * Pattern-based fallback system
  * Real-time translation statistics
Homepage: https://github.com/tautranslator/omega
'''
        
        with open(debian_dir / 'control', 'w') as f:
            f.write(control_content)
        
        # Application directory
        app_install_dir = pkg_dir / 'opt' / 'tau-translator-omega'
        app_install_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy application files
        for file in ['tau_translator_app.py', 'splash_screen.py']:
            if (self.app_dir / file).exists():
                shutil.copy2(self.app_dir / file, app_install_dir)
        
        # Copy src directory
        if (self.app_dir / 'src').exists():
            shutil.copytree(self.app_dir / 'src', app_install_dir / 'src', 
                          dirs_exist_ok=True)
        
        # Desktop file
        desktop_dir = pkg_dir / 'usr' / 'share' / 'applications'
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_content = '''[Desktop Entry]
Version=1.0
Type=Application
Name=TauTranslatorOmega
Comment=Professional AI-Enhanced Tau Language Translation
Exec=/opt/tau-translator-omega/tau_translator_app.py
Icon=tau-translator-omega
Terminal=false
Categories=Development;Education;Science;
'''
        
        with open(desktop_dir / 'tau-translator-omega.desktop', 'w') as f:
            f.write(desktop_content)
        
        # Build package
        try:
            subprocess.run(['dpkg-deb', '--build', str(pkg_dir)], 
                         check=True, cwd=str(self.dist_dir))
            
            deb_path = self.dist_dir / 'tau-translator-omega_3.0-1_amd64.deb'
            if deb_path.exists():
                print(f"✅ .deb package created: {deb_path}")
                return deb_path
        except subprocess.CalledProcessError as e:
            print(f"❌ .deb package creation failed: {e}")
        
        return None
    
    def cleanup(self):
        """Clean up build artifacts."""
        print("\n🧹 Cleaning up...")
        
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            print("✅ Build directory cleaned")
        
        # Remove spec file
        spec_file = self.app_dir / "tau_translator_omega.spec"
        if spec_file.exists():
            spec_file.unlink()
            print("✅ Spec file removed")
    
    def compile_all(self):
        """Compile all distribution formats."""
        print("🔨 TauTranslatorOmega Executable Compiler")
        print("=" * 50)
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Clean previous builds
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        self.dist_dir.mkdir()
        
        # Create spec file
        spec_path = self.create_spec_file()
        
        # Compile different formats
        single_exe = self.compile_single_file()
        dir_dist = self.compile_directory()
        appimage = self.create_appimage()
        deb_package = self.create_deb_package()
        
        # Cleanup
        self.cleanup()
        
        # Summary
        print("\n" + "=" * 50)
        print("🎉 COMPILATION COMPLETE!")
        print("=" * 50)
        
        print("\n📦 Created Distributions:")
        if single_exe:
            print(f"   ✅ Single Executable: {single_exe}")
        if dir_dist:
            print(f"   ✅ Directory Distribution: {dir_dist}")
        if appimage:
            print(f"   ✅ AppImage: {appimage}")
        if deb_package:
            print(f"   ✅ .deb Package: {deb_package}")
        
        print("\n🚀 Usage:")
        if single_exe:
            print(f"   • Run directly: {single_exe}")
        if deb_package:
            print(f"   • Install .deb: sudo dpkg -i {deb_package}")
        if appimage:
            print(f"   • Run AppImage: {appimage}")
        
        return True

def main():
    """Main compilation function."""
    try:
        compiler = ExecutableCompiler()
        success = compiler.compile_all()
        
        if success:
            print("\n✅ TauTranslatorOmega compiled successfully!")
        else:
            print("\n❌ Compilation failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Compilation error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
