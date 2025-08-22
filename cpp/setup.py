"""
Setup script for building the grover_accelerator C++ extension module
"""

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, Extension
import pybind11
import platform
import multiprocessing

# Determine the number of parallel jobs for compilation
def get_parallel_jobs():
    try:
        return multiprocessing.cpu_count()
    except:
        return 1

# Compiler and linker flags based on platform
def get_compile_args():
    if platform.system() == "Windows":
        return ["/O2", "/W4", "/std:c++17"]
    else:
        return ["-O3", "-Wall", "-Wextra", "-std=c++17", "-march=native"]

def get_link_args():
    if platform.system() == "Windows":
        return []
    else:
        return ["-pthread"]

# Define the extension module
ext_modules = [
    Pybind11Extension(
        "grover_accelerator",
        [
            "grover_accelerator.cpp",
        ],
        include_dirs=[
            pybind11.get_cmake_dir() + "/../../../include",
        ],
        cxx_std=17,
        extra_compile_args=get_compile_args(),
        extra_link_args=get_link_args(),
    ),
]

# Custom build class to handle parallel compilation
class ParallelBuildExt(build_ext):
    def build_extensions(self):
        # Set parallel jobs for compilation
        self.parallel = get_parallel_jobs()
        super().build_extensions()

setup(
    name="grover_accelerator",
    version="1.0.0",
    author="Grover DNA Search Team",
    author_email="contact@grover-dna.com",
    description="High-performance C++ accelerator for Grover DNA search algorithm",
    long_description="""
    This module provides C++ acceleration for computationally intensive operations
    in the Grover quantum search algorithm applied to DNA sequence analysis.
    
    Features:
    - Fast pattern matching with parallel processing
    - Optimized oracle construction
    - Statistical analysis of quantum measurements
    - DNA sequence utilities and validation
    """,
    ext_modules=ext_modules,
    cmdclass={"build_ext": ParallelBuildExt},
    python_requires=">=3.7",
    install_requires=[
        "pybind11>=2.6.0",
        "numpy>=1.18.0",
    ],
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: C++",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
