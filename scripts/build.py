#!/usr/bin/env python3
"""
Simple build script for the Grover C++ accelerator
"""

import os
import sys
import subprocess
import platform

def main():
    print("Building Grover C++ Accelerator...")
    
    # Check if we're on Windows
    if platform.system() == "Windows":
        print("Windows detected - using Visual Studio build tools")
        
        # Try to set up Visual Studio environment
        vs_path = r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvarsall.bat"
        
        if os.path.exists(vs_path):
            print("Visual Studio Build Tools found")
            
            # Build using the main build script
            try:
                result = subprocess.run([
                    sys.executable, "scripts/build_accelerator.py", "--install"
                ], check=True)
                print("Build completed successfully!")
                return 0
            except subprocess.CalledProcessError as e:
                print(f"Build failed: {e}")
                return 1
        else:
            print("Visual Studio Build Tools not found")
            print("Please install Visual Studio 2022 Build Tools")
            return 1
    else:
        print("Non-Windows platform - using standard build")
        try:
            result = subprocess.run([
                sys.executable, "scripts/build_accelerator.py", "--install"
            ], check=True)
            print("Build completed successfully!")
            return 0
        except subprocess.CalledProcessError as e:
            print(f"Build failed: {e}")
            return 1

if __name__ == "__main__":
    sys.exit(main())
