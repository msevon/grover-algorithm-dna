#!/usr/bin/env python3
"""
Build script for the Grover DNA Search C++ accelerator module
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def check_requirements():
    """Check if all build requirements are available."""
    print("Checking build requirements...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or later required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check for C++ compiler
    compilers = []
    if platform.system() == "Windows":
        compilers = ["cl", "g++", "clang++"]
    else:
        compilers = ["g++", "clang++", "c++"]
    
    compiler_found = False
    for compiler in compilers:
        if shutil.which(compiler):
            print(f"✓ C++ compiler found: {compiler}")
            compiler_found = True
            break
    
    if not compiler_found:
        print("❌ No C++ compiler found")
        print("  Install build tools for your platform:")
        if platform.system() == "Windows":
            print("  - Visual Studio 2019+ with C++ tools")
            print("  - Or MinGW-w64")
        elif platform.system() == "Darwin":
            print("  - Xcode Command Line Tools: xcode-select --install")
        else:
            print("  - GCC: sudo apt-get install build-essential")
            print("  - Or Clang: sudo apt-get install clang")
        return False
    
    # Check for required Python packages
    required_packages = ["pybind11", "numpy"]
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"❌ {package} not installed")
            print(f"  Install with: pip install {package}")
            return False
    
    return True

def install_requirements():
    """Install Python requirements."""
    print("Installing Python requirements...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True, text=True)
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def build_with_setuptools():
    """Build using setuptools (recommended method)."""
    print("Building with setuptools...")
    
    cpp_dir = Path("cpp")
    if not cpp_dir.exists():
        print("❌ cpp directory not found")
        return False
    
    original_dir = os.getcwd()
    try:
        os.chdir(cpp_dir)
        
        # Build the extension
        cmd = [sys.executable, "setup.py", "build_ext", "--inplace"]
        
        # Add verbose flag for debugging
        if "--verbose" in sys.argv:
            cmd.append("--verbose")
        
        # Add debug flag if requested
        if "--debug" in sys.argv:
            cmd.append("--debug")
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Build successful")
            print("✓ Module built in cpp/")
            return True
        else:
            print("❌ Build failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    finally:
        os.chdir(original_dir)

def build_with_cmake():
    """Build using CMake (alternative method)."""
    print("Building with CMake...")
    
    cpp_dir = Path("cpp")
    build_dir = cpp_dir / "build"
    
    if not cpp_dir.exists():
        print("❌ cpp directory not found")
        return False
    
    # Check if CMake is available
    if not shutil.which("cmake"):
        print("❌ CMake not found")
        print("  Install CMake from https://cmake.org/")
        return False
    
    try:
        # Create build directory
        build_dir.mkdir(exist_ok=True)
        
        original_dir = os.getcwd()
        os.chdir(build_dir)
        
        # Configure
        cmd = ["cmake", "..", "-DCMAKE_BUILD_TYPE=Release"]
        print(f"Configuring: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ CMake configuration failed")
            print("STDERR:", result.stderr)
            return False
        
        # Build
        cmd = ["cmake", "--build", ".", "--config", "Release"]
        if platform.system() != "Windows":
            cmd.extend(["-j", str(os.cpu_count() or 1)])
        
        print(f"Building: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ CMake build successful")
            return True
        else:
            print("❌ CMake build failed")
            print("STDERR:", result.stderr)
            return False
            
    finally:
        os.chdir(original_dir)

def test_module():
    """Test the built module."""
    print("Testing built module...")
    
    # Add cpp to Python path
    cpp_dir = Path("cpp").resolve()
    if str(cpp_dir) not in sys.path:
        sys.path.insert(0, str(cpp_dir))
    
    try:
        import grover_accelerator
        print(f"✓ Module imported successfully (version {grover_accelerator.VERSION})")
        
        # Run basic test
        accelerator = grover_accelerator.GroverAccelerator()
        test_sequence = "ATCGATCGAGCTAGCT"
        test_pattern = "AGCT"
        matches = accelerator.find_pattern_matches(test_sequence, test_pattern)
        print(f"✓ Basic functionality test passed (found {len(matches)} matches)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Module import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Module test failed: {e}")
        return False

def run_full_tests():
    """Run the comprehensive test suite."""
    print("Running comprehensive tests...")
    
    cpp_dir = Path("cpp")
    test_script = cpp_dir / "test_accelerator.py"
    
    if not test_script.exists():
        print("❌ Test script not found")
        return False
    
    try:
        # Add cpp to Python path for the test
        env = os.environ.copy()
        cpp_dir_str = str(cpp_dir.resolve())
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{cpp_dir_str}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = cpp_dir_str
        
        result = subprocess.run([sys.executable, str(test_script)], 
                              capture_output=True, text=True, env=env)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✓ All tests passed")
            return True
        else:
            print("❌ Some tests failed")
            return False
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return False

def clean_build():
    """Clean build artifacts."""
    print("Cleaning build artifacts...")
    
    patterns_to_remove = [
        "cpp/build/",
        "cpp/*.so",
        "cpp/*.pyd",
        "cpp/*.dll",
        "cpp/grover_accelerator.*.so",
        "cpp/__pycache__/",
        "build/",
        "dist/",
        "*.egg-info/",
    ]
    
    for pattern in patterns_to_remove:
        for path in Path(".").glob(pattern):
            if path.is_file():
                path.unlink()
                print(f"  Removed file: {path}")
            elif path.is_dir():
                shutil.rmtree(path)
                print(f"  Removed directory: {path}")

def main():
    """Main build script."""
    print("=" * 60)
    print("GROVER DNA SEARCH C++ ACCELERATOR BUILD SCRIPT")
    print("=" * 60)
    
    # Parse command line arguments
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python build_accelerator.py [options]")
        print("Options:")
        print("  --clean       Clean build artifacts")
        print("  --cmake       Use CMake instead of setuptools")
        print("  --install     Install requirements first")
        print("  --test        Run tests after building")
        print("  --full-test   Run comprehensive test suite")
        print("  --verbose     Verbose build output")
        print("  --debug       Debug build")
        print("  --help        Show this help")
        return
    
    if "--clean" in sys.argv:
        clean_build()
        return
    
    # Check requirements
    if not check_requirements():
        if "--install" in sys.argv:
            if not install_requirements():
                print("❌ Failed to install requirements")
                sys.exit(1)
            if not check_requirements():
                print("❌ Requirements still not satisfied")
                sys.exit(1)
        else:
            print("❌ Requirements not satisfied")
            print("   Use --install to automatically install requirements")
            sys.exit(1)
    
    # Choose build method
    if "--cmake" in sys.argv:
        success = build_with_cmake()
    else:
        success = build_with_setuptools()
    
    if not success:
        print("❌ Build failed")
        sys.exit(1)
    
    # Test the module
    if not test_module():
        print("❌ Module test failed")
        sys.exit(1)
    
    # Run comprehensive tests if requested
    if "--test" in sys.argv or "--full-test" in sys.argv:
        if not run_full_tests():
            print("❌ Comprehensive tests failed")
            sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 BUILD SUCCESSFUL!")
    print("=" * 60)
    print("The C++ accelerator module is ready to use.")
    print("Try running: python grover_accelerated.py")

if __name__ == "__main__":
    main()
