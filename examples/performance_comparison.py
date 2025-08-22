#!/usr/bin/env python3
"""
Performance Comparison Example
==============================

This example demonstrates the performance difference between
Python and C++ implementations of the Grover algorithm.
"""

import sys
import os
import time

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from grover_accelerated import GroverDNASearchAccelerated

def performance_test():
    """Run performance comparison between Python and C++ implementations."""
    print("⚡ Performance Comparison: Python vs C++")
    print("=" * 50)
    
    # Generate a larger test sequence
    sequence = "ATCGATCGATCGAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT" * 1000
    motif = "AGCT"
    
    print(f"Test sequence length: {len(sequence):,} bases")
    print(f"Searching for motif: {motif}")
    print()
    
    # Test Python implementation
    print("🐍 Testing Python implementation...")
    start_time = time.time()
    python_grover = GroverDNASearchAccelerated(sequence, motif, use_accelerator=False)
    python_counts = python_grover.run()
    python_time = time.time() - start_time
    
    print(f"Python execution time: {python_time:.4f}s")
    print()
    
    # Test C++ implementation
    print("🚀 Testing C++ accelerated implementation...")
    start_time = time.time()
    cpp_grover = GroverDNASearchAccelerated(sequence, motif, use_accelerator=True)
    cpp_counts = cpp_grover.run()
    cpp_time = time.time() - start_time
    
    print(f"C++ execution time: {cpp_time:.4f}s")
    print()
    
    # Calculate speedup
    if cpp_time > 0:
        speedup = python_time / cpp_time
        print(f"🎯 Performance Results:")
        print(f"  Python: {python_time:.4f}s")
        print(f"  C++:    {cpp_time:.4f}s")
        print(f"  Speedup: {speedup:.1f}x")
    else:
        print("⚠️  Could not calculate speedup (C++ time was 0)")
    
    # Verify results match
    python_keys = set(python_counts.keys())
    cpp_keys = set(cpp_counts.keys())
    results_match = python_keys == cpp_keys
    
    print(f"  Results match: {results_match}")

def main():
    """Main performance comparison demo."""
    try:
        performance_test()
        print("\n✅ Performance comparison completed!")
    except Exception as e:
        print(f"\n❌ Error during performance test: {e}")
        print("This might happen if the C++ accelerator is not available.")

if __name__ == "__main__":
    main()
