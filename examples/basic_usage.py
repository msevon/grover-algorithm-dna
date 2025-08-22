#!/usr/bin/env python3
"""
Basic Usage Example for Grover DNA Search Algorithm
==================================================

This example demonstrates the basic usage of the Grover algorithm
for DNA motif searching with C++ acceleration.
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from grover_accelerated import GroverDNASearchAccelerated

def main():
    """Demonstrate basic Grover algorithm usage."""
    print("Basic Grover DNA Search Example")
    print("=" * 50)
    
    # Example 1: Direct sequence input
    print("Example 1: Direct sequence input")
    sequence = "ATCGATCGATCGAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT"
    motif = "AGCT"
    
    print(f"DNA Sequence: {sequence}")
    print(f"Searching for motif: {motif}")
    print(f"Sequence length: {len(sequence)} bases")
    print()
    
    # Create and run the Grover search
    grover = GroverDNASearchAccelerated(sequence, motif)
    counts = grover.run()
    
    # Analyze results
    grover.analyze(counts)
    
    # Example 2: File input (if file exists)
    print("\n" + "=" * 50)
    print("Example 2: File input")
    
    import os
    dna_file = os.path.join(os.path.dirname(__file__), '..', 'dna_sequence.txt')
    
    if os.path.exists(dna_file):
        print(f"Reading DNA sequence from: {os.path.basename(dna_file)}")
        
        try:
            with open(dna_file, 'r') as f:
                file_sequence = f.read().strip()
            
            # Clean and validate the sequence
            file_sequence = ''.join(file_sequence.split()).upper()
            
            print(f"File sequence length: {len(file_sequence):,} bases")
            print(f"First 50 bases: {file_sequence[:50]}...")
            print(f"Searching for motif: {motif}")
            print()
            
            # Run Grover search on file data
            file_grover = GroverDNASearchAccelerated(file_sequence, motif)
            file_counts = file_grover.run()
            file_grover.analyze(file_counts)
            
        except Exception as e:
            print(f"Error reading file: {e}")
    else:
        print("DNA sequence file not found - skipping file example")
        print("To test file input, create a 'dna_sequence.txt' file in the project root")
    
    print("\nBasic example completed successfully!")

if __name__ == "__main__":
    main()
