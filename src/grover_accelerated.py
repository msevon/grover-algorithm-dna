"""
Enhanced Grover's Algorithm for DNA Motif Search with C++ Acceleration
======================================================================

This version uses the C++ accelerator module for high-performance operations
while maintaining the same interface as the pure Python version.
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to prevent display windows
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Optional
from qiskit_aer import AerSimulator
from qiskit.circuit.library import DiagonalGate
import time
import warnings

# Try to import the C++ accelerator, fall back to pure Python if not available
try:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'cpp'))
    import grover_accelerator
    ACCELERATOR_AVAILABLE = True
    print("C++ accelerator loaded successfully!")
except ImportError:
    ACCELERATOR_AVAILABLE = False
    print("⚠️  C++ accelerator not available, using pure Python implementation")
    print("   To build the accelerator: python scripts/build.py")

class GroverDNASearchAccelerated:
    """Enhanced Grover search with optional C++ acceleration for DNA motif finding."""
    
    def __init__(self, sequence: str, motif: str, use_accelerator: bool = True):
        self.data = sequence
        self.pattern = motif
        
        # Initialize accelerator if available and requested
        self.use_accelerator = use_accelerator and ACCELERATOR_AVAILABLE
        if self.use_accelerator:
            self.accelerator = grover_accelerator.GroverAccelerator()
            print(f"🔧 Using C++ accelerator (version {grover_accelerator.VERSION})")
        else:
            self.accelerator = None
            if use_accelerator and not ACCELERATOR_AVAILABLE:
                print("⚠️  C++ accelerator requested but not available, falling back to Python")
        
        self.data_length = len(sequence)
        self.pattern_length = len(motif)
        self.num_candidates = self.data_length - self.pattern_length + 1
        
        self.n_qubits = self._calculate_qubits_needed()
        self.position_to_state, self.state_to_position = self._create_encoding_mappings()
        
        # Validate DNA sequence if accelerator is available
        if self.use_accelerator:
            if not grover_accelerator.utils.is_valid_dna(sequence):
                warnings.warn("Input sequence contains invalid DNA bases (not A, T, G, C)")
            if not grover_accelerator.utils.is_valid_dna(motif):
                warnings.warn("Motif contains invalid DNA bases (not A, T, G, C)")
        
        print("Enhanced DNA Motif Search Setup:")
        print(f"  Sequence: '{sequence[:50]}{'...' if len(sequence) > 50 else ''}' (length: {self.data_length:,})")
        print(f"  Motif:    '{motif}' (length: {self.pattern_length})")
        print(f"  Candidates: {self.num_candidates:,}")
        print(f"  Qubits:    {self.n_qubits} (database size {2**self.n_qubits:,})")
        
        if self.use_accelerator:
            gc_content = grover_accelerator.utils.calculate_gc_content(sequence)
            print(f"  GC Content: {gc_content:.1%}")
    
    def _calculate_qubits_needed(self) -> int:
        if self.num_candidates <= 1:
            return 1
        return int(np.ceil(np.log2(self.num_candidates)))
    
    def _create_encoding_mappings(self) -> Tuple[Dict[int, str], Dict[str, int]]:
        if self.use_accelerator:
            # Use C++ accelerated encoding
            encodings = self.accelerator.encode_positions(self.num_candidates, self.n_qubits)
            position_to_state = {i: encodings[i] for i in range(self.num_candidates)}
            state_to_position = {encodings[i]: i for i in range(self.num_candidates)}
        else:
            # Pure Python encoding
            position_to_state, state_to_position = {}, {}
            for pos in range(self.num_candidates):
                binary_state = bin(pos)[2:].zfill(self.n_qubits)
                position_to_state[pos] = binary_state
                state_to_position[binary_state] = pos
        
        return position_to_state, state_to_position
    
    def _find_matching_positions(self) -> List[int]:
        """Find all positions where the pattern matches using accelerated search if available."""
        if self.use_accelerator:
            # Use C++ accelerated pattern matching
            start_time = time.time()
            if self.data_length > 100000:  # Use parallel for large sequences
                matches = self.accelerator.find_pattern_matches_parallel(
                    self.data, self.pattern, num_threads=4
                )
                search_method = "C++ (parallel)"
            else:
                matches = self.accelerator.find_pattern_matches(self.data, self.pattern)
                search_method = "C++ (single-threaded)"
            search_time = time.time() - start_time
            
            print(f"Pattern search completed using {search_method} in {search_time:.4f}s")
            print(f"Motif '{self.pattern}' matches at {len(matches)} positions")
            
            if len(matches) <= 20:  # Show positions for small result sets
                print(f"Match positions: {matches}")
            else:
                print(f"Match positions: {matches[:10]}...{matches[-10:]} (showing first/last 10)")
            
            return matches
        else:
            # Pure Python pattern matching
            start_time = time.time()
            matches = [pos for pos in range(self.num_candidates) 
                      if self._check_pattern_match(pos)]
            search_time = time.time() - start_time
            
            print(f"Pattern search completed using Python in {search_time:.4f}s")
            print(f"Motif '{self.pattern}' matches at {len(matches)} positions")
            return matches
    
    def _check_pattern_match(self, position: int) -> bool:
        """Pure Python pattern matching for fallback."""
        if position + self.pattern_length > self.data_length:
            return False
        return self.data[position:position + self.pattern_length] == self.pattern
    
    def create_oracle(self) -> QuantumCircuit:
        """
        Multi-solution oracle using accelerated diagonal construction if available.
        """
        matches = self._find_matching_positions()
        oracle = QuantumCircuit(self.n_qubits)
        
        if not matches:
            return oracle
        
        if self.use_accelerator:
            # Use C++ accelerated oracle construction
            start_time = time.time()
            size = 2 ** self.n_qubits
            diag = self.accelerator.build_oracle_diagonal(matches, size)
            construction_time = time.time() - start_time
            print(f"Oracle construction completed using C++ in {construction_time:.4f}s")
        else:
            # Pure Python oracle construction
            start_time = time.time()
            size = 2 ** self.n_qubits
            diag = [1.0] * size
            for pos in matches:
                if pos < size:
                    diag[pos] = -1.0
            construction_time = time.time() - start_time
            print(f"Oracle construction completed using Python in {construction_time:.4f}s")
        
        oracle.append(DiagonalGate(diag), list(range(self.n_qubits)))
        return oracle
    
    def create_diffusion_operator(self) -> QuantumCircuit:
        """Standard Grover diffusion operator."""
        diffusion = QuantumCircuit(self.n_qubits)
        diffusion.h(range(self.n_qubits))
        diffusion.x(range(self.n_qubits))
        diffusion.h(self.n_qubits - 1)
        if self.n_qubits > 1:
            diffusion.mcx(list(range(self.n_qubits - 1)), self.n_qubits - 1)
        diffusion.h(self.n_qubits - 1)
        diffusion.x(range(self.n_qubits))
        diffusion.h(range(self.n_qubits))
        return diffusion
    
    def _trim_counts(self, counts: Dict[str, int]) -> Dict[str, int]:
        """Normalize and aggregate raw simulator counts."""
        aggregated: Dict[str, int] = {}
        for key, value in counts.items():
            clean = key.replace(" ", "")
            if len(clean) <= self.n_qubits:
                trimmed = clean.zfill(self.n_qubits)
            else:
                trimmed = clean[:self.n_qubits]
            aggregated[trimmed] = aggregated.get(trimmed, 0) + value
        return aggregated
    
    def run(self, num_iterations: Optional[int] = None) -> Dict[str, int]:
        """Run the enhanced Grover search algorithm."""
        matches = self._find_matching_positions()
        M = max(1, len(matches))
        N = self.num_candidates if self.num_candidates > 0 else 1
        
        if num_iterations is None:
            if self.use_accelerator:
                # Use C++ accelerated calculation
                num_iterations = self.accelerator.calculate_optimal_iterations(N, M)
            else:
                # Pure Python calculation
                num_iterations = max(1, int(np.floor((np.pi/4) * np.sqrt(N / M))))
        
        print("\nExecuting Enhanced Grover's DNA Search:")
        print(f"  Candidates (N): {self.num_candidates:,}")
        print(f"  Matches (M):    {len(matches):,}")
        print(f"  Iterations:     {num_iterations}")
        print(f"  Expected success probability: ~{100 * M / N:.1f}%")
        
        # Build and execute quantum circuit
        circuit_start = time.time()
        qc = QuantumCircuit(self.n_qubits, self.n_qubits)
        qc.h(range(self.n_qubits))
        
        oracle = self.create_oracle()
        diffusion = self.create_diffusion_operator()
        
        for i in range(num_iterations):
            qc.append(oracle, range(self.n_qubits))
            qc.append(diffusion, range(self.n_qubits))
        
        qc.measure_all()
        circuit_time = time.time() - circuit_start
        print(f"  Circuit construction: {circuit_time:.4f}s")
        
        # Execute on quantum simulator
        execution_start = time.time()
        backend = AerSimulator()
        tqc = transpile(qc, backend)
        result = backend.run(tqc, shots=1000).result()
        raw_counts = result.get_counts()
        execution_time = time.time() - execution_start
        print(f"  Quantum simulation: {execution_time:.4f}s")
        
        return self._trim_counts(raw_counts)
    
    def analyze(self, counts: Dict[str, int]) -> None:
        """Enhanced analysis with C++ acceleration if available."""
        print("\n" + "=" * 70)
        print("ENHANCED DNA MOTIF SEARCH RESULTS")
        print("=" * 70)
        
        sorted_results = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        matches = self._find_matching_positions()
        
        # Show top results
        top_results = sorted_results[:50]
        print("State (pos): count [%]  [match]")
        for state, c in top_results:
            pct = 100 * c / 1000
            if state in self.state_to_position:
                pos = self.state_to_position[state]
                mark = "✓" if pos in matches else ""
                print(f"  {state} ({pos:,}): {c} [{pct:.1f}%] {mark}")
            else:
                print(f"  {state} (invalid): {c} [{pct:.1f}%]")
        
        if len(sorted_results) > 50:
            print(f"  ... and {len(sorted_results) - 50:,} more results")
        
        # Calculate statistics with better debugging
        total_match = 0
        valid_states = 0
        
        for state, count in counts.items():
            if state in self.state_to_position:
                pos = self.state_to_position[state]
                if pos in matches:
                    total_match += count
                valid_states += count
        
        success_rate = 100 * total_match / 1000 if total_match > 0 else 0
        
        print(f"\nSTATISTICS:")
        print(f"  Total match shots: {total_match:,}/1000 ({success_rate:.1f}%)")
        print(f"  Valid states measured: {valid_states:,}/1000")
        print(f"  Unique states measured: {len(counts):,}")
        print(f"  Most frequent state: {sorted_results[0][0]} ({sorted_results[0][1]} shots)")
        
        # Debug information
        print(f"  Expected matches: {len(matches)} positions")
        print(f"  Valid state mappings: {len([s for s in counts.keys() if s in self.state_to_position])}")
        if matches:
            print(f"  Match positions: {matches[:10]}{'...' if len(matches) > 10 else ''}")
        
        # Show first few state mappings for debugging
        print(f"  Sample state mappings:")
        sample_states = list(counts.keys())[:5]
        for state in sample_states:
            if state in self.state_to_position:
                pos = self.state_to_position[state]
                is_match = pos in matches
                print(f"    {state} -> position {pos} {'✓' if is_match else ''}")
            else:
                print(f"    {state} -> invalid position")
        
        # Enhanced statistics with C++ if available
        if self.use_accelerator and len(counts) <= 10000:  # Avoid memory issues
            try:
                stats = self.accelerator.analyze_measurement_statistics(
                    counts, matches, 1000
                )
                print(f"  Success probability: {stats['success_probability']:.3f}")
                print(f"  Max amplitude: {stats['max_amplitude']:.3f}")
                print(f"  Shannon entropy: {stats['entropy']:.3f}")
            except Exception as e:
                print(f"  Enhanced statistics unavailable: {e}")
        
        # Create visualization
        self._create_visualization(counts, matches)
    
    def _create_visualization(self, counts: Dict[str, int], matches: List[int]) -> None:
        """Create appropriate visualization based on result size."""
        if len(counts) > 100:
            print(f"\n{'='*70}")
            print("COMPACT VISUALIZATION (Large Dataset)")
            print("="*70)
            
            # Aggregate results into position ranges
            position_counts = {}
            for state, count in counts.items():
                if state in self.state_to_position:
                    pos = self.state_to_position[state]
                    range_start = (pos // 1000) * 1000
                    range_end = min(range_start + 999, self.data_length - 1)
                    range_key = f"{range_start:,}-{range_end:,}"
                    position_counts[range_key] = position_counts.get(range_key, 0) + count
            
            if position_counts:
                plt.figure(figsize=(14, 7))
                ranges = list(position_counts.keys())
                counts_list = list(position_counts.values())
                
                # Sort by range start position
                ranges.sort(key=lambda x: int(x.split('-')[0].replace(',', '')))
                counts_list = [position_counts[r] for r in ranges]
                
                bars = plt.bar(range(len(ranges)), counts_list, alpha=0.8, 
                              color='skyblue', edgecolor='navy', linewidth=0.5)
                plt.xlabel('Position Range (bases)', fontsize=12)
                plt.ylabel('Total Count', fontsize=12)
                plt.title(f'Enhanced Grover Search: {self.pattern} in {len(self.data):,}-base DNA Sequence\n'
                         f'Success Rate: {100*sum(counts_list)/1000:.1f}%, '
                         f'Accelerator: {"C++" if self.use_accelerator else "Python"}', 
                         fontsize=14)
                plt.xticks(range(len(ranges)), ranges, rotation=45, ha='right')
                plt.grid(axis='y', alpha=0.3)
                
                # Add value labels on bars
                for i, (bar, count) in enumerate(zip(bars, counts_list)):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                            str(count), ha='center', va='bottom', fontsize=9, fontweight='bold')
                
                plt.tight_layout()
                plt.savefig("grover_enhanced_results.png", dpi=300, bbox_inches='tight')
                print("✓ Saved enhanced visualization to 'grover_enhanced_results.png'")
                plt.close()  # Close the figure to prevent display
                
                # Summary statistics
                print(f"\nPosition Range Summary:")
                print(f"  Total ranges: {len(ranges)}")
                print(f"  Highest count: {max(counts_list)} in range {ranges[counts_list.index(max(counts_list))]}")
                print(f"  Average count per range: {sum(counts_list)/len(counts_list):.1f}")
        else:
            # Standard histogram for smaller datasets
            plt.figure(figsize=(10, 6))
            plot_histogram(counts)
            plt.title(f'Enhanced Grover Search: {self.pattern} in {self.data[:30]}...\n'
                     f'Accelerator: {"C++" if self.use_accelerator else "Python"}')
            plt.xlabel("Position (Binary)")
            plt.ylabel("Count")
            plt.tight_layout()
            plt.savefig("grover_enhanced_results.png", dpi=300, bbox_inches='tight')
            print("✓ Saved visualization to 'grover_enhanced_results.png'")
            plt.close()  # Close the figure to prevent display


def performance_comparison_demo():
    """Demonstrate performance difference between Python and C++ implementations."""
    print("\n" + "=" * 70)
    print("PERFORMANCE COMPARISON DEMO")
    print("=" * 70)
    
    if not ACCELERATOR_AVAILABLE:
        print("C++ accelerator not available - skipping performance comparison")
        return
    
    # Generate test data
    test_sequence = grover_accelerator.utils.generate_random_dna(50000, seed=42)
    test_motif = "AGCT"
    
    print(f"Test data: {len(test_sequence):,} base sequence, motif '{test_motif}'")
    
    # Python implementation
    print("\nRunning Python implementation...")
    start_time = time.time()
    python_grover = GroverDNASearchAccelerated(test_sequence, test_motif, use_accelerator=False)
    python_counts = python_grover.run()
    python_time = time.time() - start_time
    
    # C++ implementation
    print("\nRunning C++ accelerated implementation...")
    start_time = time.time()
    cpp_grover = GroverDNASearchAccelerated(test_sequence, test_motif, use_accelerator=True)
    cpp_counts = cpp_grover.run()
    cpp_time = time.time() - start_time
    
    # Compare results
    speedup = python_time / cpp_time if cpp_time > 0 else float('inf')
    
    print(f"\n{'='*70}")
    print("PERFORMANCE RESULTS")
    print("="*70)
    print(f"Python implementation:    {python_time:.3f}s")
    print(f"C++ accelerated:          {cpp_time:.3f}s")
    print(f"Speedup:                  {speedup:.1f}x")
    print(f"Results match:            {set(python_counts.keys()) == set(cpp_counts.keys())}")


def main():
    """Main demonstration of enhanced Grover DNA search."""
    # Large gene-sized DNA sequence with C++ acceleration
    sequence = ""
    
    # Build realistic gene structure
    sequence += "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG" * 50  # Promoter
    sequence += "TAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT" * 100  # Intron with AGCT
    sequence += "AGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT" * 30   # Exon
    sequence += "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG" * 150  # Large intron
    sequence += "AGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT" * 40   # Exon
    sequence += "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG" * 100  # UTR
    
    motif = "AGCT"
    
    print("=" * 70)
    print("ENHANCED GROVER'S ALGORITHM – DNA MOTIF SEARCH")
    print("=" * 70)
    print(f"Sequence length: {len(sequence):,} bases")
    print(f"Motif: '{motif}'")
    print(f"Classical search complexity: O({len(sequence):,})")
    
    # Run enhanced search
    grover = GroverDNASearchAccelerated(sequence, motif)
    counts = grover.run()
    grover.analyze(counts)
    
    # Optional performance comparison
    response = input("\nRun performance comparison demo? (y/n): ").lower().strip()
    if response == 'y':
        performance_comparison_demo()


if __name__ == "__main__":
    main()
