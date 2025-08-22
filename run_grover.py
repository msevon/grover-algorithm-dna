#!/usr/bin/env python3
"""
Grover Algorithm - Main Entry Point
====================================

This is the main entry point for the Grover DNA search algorithm.
It provides easy access to all the main functionality.
"""

import sys
import os
import argparse

# Add src directory to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Add cpp directory to path for C++ module
cpp_path = os.path.join(os.path.dirname(__file__), 'cpp')
sys.path.insert(0, cpp_path)

from grover_accelerated import GroverDNASearchAccelerated

def read_dna_sequence(filepath):
    """Read DNA sequence from a text file."""
    try:
        with open(filepath, 'r') as f:
            sequence = f.read().strip()
        
        # Remove any whitespace, newlines, and make uppercase
        sequence = ''.join(sequence.split()).upper()
        
        # Validate DNA sequence (only A, T, G, C allowed)
        valid_bases = set('ATGC')
        if not all(base in valid_bases for base in sequence):
            invalid_bases = set(sequence) - valid_bases
            raise ValueError(f"Invalid DNA bases found: {invalid_bases}")
        
        return sequence
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def main():
    """Main entry point for Grover algorithm."""
    parser = argparse.ArgumentParser(
        description="Grover DNA Search Algorithm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Direct sequence input
  python run_grover.py ATCGATCGATCG AGCT
  
  # File input
  python run_grover.py --file dna_sequence.txt AGCT
  
  # Other options
  python src/grover_accelerated.py          # Full demo
  python examples/basic_usage.py            # Basic example
  python examples/performance_comparison.py # Performance test
        """
    )
    
    parser.add_argument('sequence_or_motif', nargs='?', 
                       help='DNA sequence (if no --file) or motif pattern')
    parser.add_argument('motif', nargs='?', 
                       help='Motif pattern to search for')
    parser.add_argument('--file', '-f', 
                       help='Read DNA sequence from file')
    
    args = parser.parse_args()
    
    print("Grover DNA Search Algorithm")
    print("=" * 40)
    print()
    
    # Determine sequence and motif based on arguments
    if args.file:
        if not args.sequence_or_motif:
            print("Error: Motif pattern required when using --file")
            print("Usage: python run_grover.py --file <filename> <motif>")
            return 1
        
        sequence = read_dna_sequence(args.file)
        if sequence is None:
            return 1
        motif = args.sequence_or_motif
        print(f"Reading DNA sequence from: {args.file}")
        
    else:
        if not args.sequence_or_motif or not args.motif:
            print("Usage:")
            print("  python run_grover.py <sequence> <motif>")
            print("  python run_grover.py --file <filename> <motif>")
            print()
            print("Examples:")
            print("  python run_grover.py 'ATCGATCGATCG' 'AGCT'")
            print("  python run_grover.py --file dna_sequence.txt 'AGCT'")
            return 1
        
        sequence = args.sequence_or_motif.upper()
        motif = args.motif.upper()
    
    # Validate motif
    valid_bases = set('ATGC')
    if not all(base in valid_bases for base in motif):
        invalid_bases = set(motif) - valid_bases
        print(f"Error: Invalid DNA bases in motif: {invalid_bases}")
        return 1
    
    print(f"DNA Sequence: {sequence[:50]}{'...' if len(sequence) > 50 else ''}")
    print(f"Searching for motif: {motif}")
    print(f"Sequence length: {len(sequence):,} bases")
    print()
    
    try:
        # Run Grover search
        grover = GroverDNASearchAccelerated(sequence, motif)
        counts = grover.run()
        grover.analyze(counts)
        
        print("\nGrover search completed successfully!")
        return 0
        
    except Exception as e:
        print(f"\nError during Grover search: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
