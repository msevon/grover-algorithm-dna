"""
Grover's Algorithm for DNA Motif Search
======================================

This script uses Grover's algorithm to find occurrences of a DNA motif
(e.g., "AGCT") within a longer DNA sequence. It builds a multi-solution
oracle that marks all positions where the motif appears and amplifies
those positions using Grover iterations.
"""

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
from qiskit_aer import AerSimulator
from qiskit.circuit.library import DiagonalGate

class GroverDNASearch:
    """Grover search specialized for DNA motif finding."""
    
    def __init__(self, sequence: str, motif: str):
        self.data = sequence
        self.pattern = motif
        
        self.data_length = len(sequence)
        self.pattern_length = len(motif)
        self.num_candidates = self.data_length - self.pattern_length + 1
        
        self.n_qubits = self._calculate_qubits_needed()
        self.position_to_state, self.state_to_position = self._create_encoding_mappings()
        
        print("DNA Motif Search Setup:")
        print(f"  Sequence: '{sequence}' (length: {self.data_length})")
        print(f"  Motif:    '{motif}' (length: {self.pattern_length})")
        print(f"  Candidates: {self.num_candidates}")
        print(f"  Qubits:    {self.n_qubits} (database size {2**self.n_qubits})")
    
    def _calculate_qubits_needed(self) -> int:
        if self.num_candidates <= 1:
            return 1
        return int(np.ceil(np.log2(self.num_candidates)))
    
    def _create_encoding_mappings(self) -> Tuple[Dict[int, str], Dict[str, int]]:
        position_to_state, state_to_position = {}, {}
        for pos in range(self.num_candidates):
            binary_state = bin(pos)[2:].zfill(self.n_qubits)
            position_to_state[pos] = binary_state
            state_to_position[binary_state] = pos
        return position_to_state, state_to_position
    
    def _check_pattern_match(self, position: int) -> bool:
        if position + self.pattern_length > self.data_length:
            return False
        return self.data[position:position + self.pattern_length] == self.pattern
    
    def _find_matching_positions(self) -> List[int]:
        matches = [pos for pos in range(self.num_candidates) if self._check_pattern_match(pos)]
        print(f"Motif '{self.pattern}' matches at positions: {matches}")
        return matches
    
    def create_oracle(self) -> QuantumCircuit:
        """
        Multi-solution oracle via DiagonalGate: -1 on matching positions, +1 elsewhere.
        """
        matches = self._find_matching_positions()
        oracle = QuantumCircuit(self.n_qubits)
        if not matches:
            return oracle
        size = 2 ** self.n_qubits
        diag = [1.0] * size
        for pos in matches:
            if pos < size:
                diag[pos] = -1.0
        oracle.append(DiagonalGate(diag), list(range(self.n_qubits)))
        return oracle
    
    def create_diffusion_operator(self) -> QuantumCircuit:
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
        """Normalize and aggregate raw simulator counts to first n_qubits bits (MSB-first in printed keys)."""
        aggregated: Dict[str, int] = {}
        for key, value in counts.items():
            clean = key.replace(" ", "")
            if len(clean) <= self.n_qubits:
                trimmed = clean.zfill(self.n_qubits)
            else:
                trimmed = clean[:self.n_qubits]
            aggregated[trimmed] = aggregated.get(trimmed, 0) + value
        return aggregated
    
    def run(self, num_iterations: int = None) -> Dict[str, int]:
        matches = self._find_matching_positions()
        M = max(1, len(matches))
        N = self.num_candidates if self.num_candidates > 0 else 1
        if num_iterations is None:
            num_iterations = max(1, int(np.floor((np.pi/4) * np.sqrt(N / M))))
        
        print("\nExecuting Grover's DNA Search:")
        print(f"  Candidates (N): {self.num_candidates}")
        print(f"  Matches (M):    {len(matches)}")
        print(f"  Iterations:     {num_iterations}")
        
        qc = QuantumCircuit(self.n_qubits, self.n_qubits)
        qc.h(range(self.n_qubits))
        
        oracle = self.create_oracle()
        diffusion = self.create_diffusion_operator()
        for _ in range(num_iterations):
            qc.append(oracle, range(self.n_qubits))
            qc.append(diffusion, range(self.n_qubits))
        
        qc.measure_all()
        
        backend = AerSimulator()
        tqc = transpile(qc, backend)
        result = backend.run(tqc, shots=1000).result()
        raw_counts = result.get_counts()
        return self._trim_counts(raw_counts)
    
    def analyze(self, counts: Dict[str, int]) -> None:
        print("\n" + "=" * 60)
        print("DNA MOTIF SEARCH RESULTS")
        print("=" * 60)
        
        sorted_results = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        matches = self._find_matching_positions()
        
        # Show top 50 results to avoid overwhelming output
        top_results = sorted_results[:50]
        print("State (pos): count [%]  [match]")
        for state, c in top_results:
            pct = 100 * c / 1000
            if state in self.state_to_position:
                pos = self.state_to_position[state]
                mark = "✓" if pos in matches else ""
                print(f"  {state} ({pos}): {c} [{pct:.1f}%] {mark}")
            else:
                print(f"  {state} (invalid): {c} [{pct:.1f}%]")
        
        if len(sorted_results) > 50:
            print(f"  ... and {len(sorted_results) - 50} more results")
        
        total_match = sum(c for s, c in counts.items()
                          if s in self.state_to_position and self.state_to_position[s] in matches)
        print(f"\nTotal match shots: {total_match}/1000 ({100*total_match/1000:.1f}%)")
        
        # Create a compact visualization for large datasets
        if len(counts) > 100:
            print("\n" + "=" * 60)
            print("COMPACT VISUALIZATION (Large Dataset)")
            print("=" * 60)
            
            # Aggregate results into position ranges for visualization
            position_counts = {}
            for state, count in counts.items():
                if state in self.state_to_position:
                    pos = self.state_to_position[state]
                    # Group positions into ranges of 1000 bases
                    range_start = (pos // 1000) * 1000
                    range_end = range_start + 999
                    range_key = f"{range_start:,}-{range_end:,}"
                    position_counts[range_key] = position_counts.get(range_key, 0) + count
            
            if position_counts:
                # Create compact bar chart
                plt.figure(figsize=(12, 6))
                ranges = list(position_counts.keys())
                counts_list = list(position_counts.values())
                
                # Sort by range start position
                ranges.sort(key=lambda x: int(x.split('-')[0].replace(',', '')))
                counts_list = [position_counts[r] for r in ranges]
                
                bars = plt.bar(range(len(ranges)), counts_list, alpha=0.7, color='skyblue')
                plt.xlabel('Position Range (bases)')
                plt.ylabel('Total Count')
                plt.title(f'AGCT Motif Distribution in {len(self.data):,}-base DNA Sequence')
                plt.xticks(range(len(ranges)), ranges, rotation=45, ha='right')
                
                # Add value labels on bars
                for i, (bar, count) in enumerate(zip(bars, counts_list)):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                            str(count), ha='center', va='bottom', fontsize=8)
                
                plt.tight_layout()
                plt.savefig("grover_dna_results.png", dpi=300, bbox_inches='tight')
                print("✓ Saved compact visualization to 'grover_dna_results.png'")
                plt.show()
                
                # Print summary statistics
                print(f"\nPosition Range Summary:")
                print(f"  Total ranges: {len(ranges)}")
                print(f"  Highest count: {max(counts_list)} in range {ranges[counts_list.index(max(counts_list))]}")
                print(f"  Average count per range: {sum(counts_list)/len(counts_list):.1f}")
            else:
                print("  No valid positions found for visualization")
        else:
            # Original histogram for small datasets
            plt.figure(figsize=(8, 5))
            plot_histogram(counts)
            plt.title(f"DNA Search: '{self.pattern}' in '{self.data[:50]}...'")
            plt.xlabel("Position (Binary)")
            plt.ylabel("Count")
            plt.tight_layout()
            plt.savefig("grover_dna_results.png", dpi=300, bbox_inches='tight')
            print("✓ Saved plot to 'grover_dna_results.png'")
            plt.show()


def main():
    # Realistic gene-sized DNA sequence - ~50,000 bases
    # Simulating a typical human gene with exons, introns, and regulatory regions
    
    # Build a large, varied sequence with realistic patterns
    sequence = ""
    
    # Regulatory region (promoter/enhancer) - 2000 bases
    sequence += "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG" * 20
    
    # Intron 1 - 8000 bases with some AGCT patterns
    sequence += "TAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT" * 40
    sequence += "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG" * 40
    
    # Exon 1 - 1500 bases (coding region)
    sequence += "AGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT" * 15
    sequence += "TAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT" * 15
    sequence += "GCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAG" * 15
    
    # Intron 2 - 12000 bases
    sequence += "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG" * 60
    
    # Exon 2 - 2000 bases
    sequence += "AGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT" * 20
    
    # Intron 3 - 15000 bases with scattered AGCT patterns
    sequence += "TAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCT" * 75
    
    # Exon 3 - 1800 bases
    sequence += "GCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAG" * 18
    
    # 3' UTR and regulatory region - 3000 bases
    sequence += "ATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG" * 30
    
    motif = "AGCT"
    
    print("=" * 70)
    print("GROVER'S ALGORITHM – DNA MOTIF SEARCH (GENE-SIZED DATASET)")
    print("=" * 70)
    print(f"Sequence length: {len(sequence):,} bases")
    print(f"Motif: '{motif}'")
    print(f"Classical search: O({len(sequence):,}) = {len(sequence):,} operations")
    print(f"Expected matches: ~{len(sequence)//100} (rough estimate)")
    
    grover = GroverDNASearch(sequence, motif)
    counts = grover.run()
    grover.analyze(counts)

if __name__ == "__main__":
    main()
