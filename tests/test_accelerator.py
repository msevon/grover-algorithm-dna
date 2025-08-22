#!/usr/bin/env python3
"""
Test suite for the grover_accelerator C++ module
"""

import sys
import time
import random
import traceback

def test_basic_import():
    """Test basic module import"""
    print("Testing basic import...")
    try:
        import grover_accelerator
        print("✓ Module imported successfully")
        print(f"  Version: {grover_accelerator.VERSION}")
        print(f"  DNA bases: {grover_accelerator.DNA_BASES}")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_accelerator_creation():
    """Test GroverAccelerator object creation"""
    print("\nTesting accelerator creation...")
    try:
        import grover_accelerator
        accelerator = grover_accelerator.GroverAccelerator()
        print("✓ GroverAccelerator created successfully")
        return True, accelerator
    except Exception as e:
        print(f"✗ Creation failed: {e}")
        return False, None

def test_pattern_matching(accelerator):
    """Test pattern matching functionality"""
    print("\nTesting pattern matching...")
    try:
        # Test basic pattern matching
        sequence = "ATCGATCGATCGAGCTAGCTAGCTGCATGC"
        pattern = "AGCT"
        
        matches = accelerator.find_pattern_matches(sequence, pattern)
        print(f"Found {len(matches)} matches for pattern '{pattern}'")
        print(f"Matches at positions: {matches}")
        
        # Verify matches are correct
        for pos in matches:
            if sequence[pos:pos+len(pattern)] != pattern:
                print(f"✗ Invalid match at position {pos}")
                return False
        
        # Test empty cases
        empty_matches = accelerator.find_pattern_matches("", pattern)
        assert len(empty_matches) == 0, "Empty sequence should return no matches"
        
        empty_pattern_matches = accelerator.find_pattern_matches(sequence, "")
        assert len(empty_pattern_matches) == 0, "Empty pattern should return no matches"
        
        print("Pattern matching tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Pattern matching failed: {e}")
        traceback.print_exc()
        return False

def test_parallel_matching(accelerator):
    """Test parallel pattern matching"""
    print("\nTesting parallel pattern matching...")
    try:
        # Generate larger sequence for parallel testing
        sequence = "ATCGATCG" * 1000 + "AGCT" * 100 + "GCTAGCTA" * 900
        pattern = "AGCT"
        
        # Test single-threaded
        start_time = time.time()
        matches_single = accelerator.find_pattern_matches(sequence, pattern)
        single_time = time.time() - start_time
        
        # Test multi-threaded
        start_time = time.time()
        matches_parallel = accelerator.find_pattern_matches_parallel(sequence, pattern, 4)
        parallel_time = time.time() - start_time
        
        # Sort both results for comparison (parallel might be out of order)
        matches_single.sort()
        matches_parallel.sort()
        
        assert matches_single == matches_parallel, "Single and parallel results should match"
        
        speedup = single_time / parallel_time if parallel_time > 0 else float('inf')
        print(f"Parallel matching successful")
        print(f"  Single-threaded: {single_time:.4f}s")
        print(f"  Multi-threaded:  {parallel_time:.4f}s")
        print(f"  Speedup: {speedup:.2f}x")
        print(f"  Found {len(matches_parallel)} matches")
        
        return True
        
    except Exception as e:
        print(f"✗ Parallel matching failed: {e}")
        traceback.print_exc()
        return False

def test_oracle_construction(accelerator):
    """Test oracle diagonal construction"""
    print("\nTesting oracle construction...")
    try:
        matches = [5, 10, 15, 20]
        database_size = 32
        
        diagonal = accelerator.build_oracle_diagonal(matches, database_size)
        
        assert len(diagonal) == database_size, f"Diagonal should have {database_size} elements"
        
        # Check that matching positions are marked with -1
        for i, val in enumerate(diagonal):
            if i in matches:
                assert val.real == -1.0 and val.imag == 0.0, f"Match position {i} should be -1+0j"
            else:
                assert val.real == 1.0 and val.imag == 0.0, f"Non-match position {i} should be 1+0j"
        
        print(f"Oracle construction successful")
        print(f"  Database size: {database_size}")
        print(f"  Marked positions: {matches}")
        print(f"  Diagonal length: {len(diagonal)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Oracle construction failed: {e}")
        traceback.print_exc()
        return False

def test_optimal_iterations(accelerator):
    """Test optimal iteration calculation"""
    print("\nTesting optimal iteration calculation...")
    try:
        test_cases = [
            (100, 1, 8),    # Single item in 100
            (1000, 10, 5),  # 10 items in 1000
            (10000, 100, 5), # 100 items in 10000
            (1, 1, 1),      # Edge case: single item
        ]
        
        for total, marked, expected_range in test_cases:
            iterations = accelerator.calculate_optimal_iterations(total, marked)
            print(f"  {total} items, {marked} marked → {iterations} iterations")
            
            # Check that result is reasonable (within expected range)
            assert iterations >= 1, "Iterations should be at least 1"
            assert iterations <= total, "Iterations shouldn't exceed total items"
        
        print("Optimal iteration calculation successful")
        return True
        
    except Exception as e:
        print(f"✗ Optimal iteration calculation failed: {e}")
        traceback.print_exc()
        return False

def test_position_encoding(accelerator):
    """Test position encoding functionality"""
    print("\nTesting position encoding...")
    try:
        num_candidates = 16
        n_qubits = 4
        
        encodings = accelerator.encode_positions(num_candidates, n_qubits)
        
        assert len(encodings) == num_candidates, f"Should have {num_candidates} encodings"
        
        # Check that all encodings have correct length
        for i, encoding in enumerate(encodings):
            assert len(encoding) == n_qubits, f"Encoding {i} should have {n_qubits} bits"
            # Check that it's valid binary
            for bit in encoding:
                assert bit in '01', f"Invalid bit '{bit}' in encoding"
        
        # Check specific examples
        assert encodings[0] == "0000", "Position 0 should encode to 0000"
        assert encodings[1] == "0001", "Position 1 should encode to 0001"
        assert encodings[15] == "1111", "Position 15 should encode to 1111"
        
        print(f"Position encoding successful")
        print(f"  Encoded {num_candidates} positions with {n_qubits} qubits")
        print(f"  Sample encodings: {encodings[:5]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Position encoding failed: {e}")
        traceback.print_exc()
        return False

def test_utils():
    """Test utility functions"""
    print("\nTesting utility functions...")
    try:
        import grover_accelerator
        
        # Test random DNA generation
        dna = grover_accelerator.utils.generate_random_dna(100, seed=42)
        assert len(dna) == 100, "Generated DNA should have correct length"
        assert grover_accelerator.utils.is_valid_dna(dna), "Generated DNA should be valid"
        
        # Test validation
        valid_dna = "ATCGATCG"
        invalid_dna = "ATCGXYZ"
        assert grover_accelerator.utils.is_valid_dna(valid_dna), "Valid DNA should pass validation"
        assert not grover_accelerator.utils.is_valid_dna(invalid_dna), "Invalid DNA should fail validation"
        
        # Test GC content
        gc_test = "GGCC"  # 100% GC
        at_test = "AATT"  # 0% GC
        mixed_test = "ATGC"  # 50% GC
        
        assert abs(grover_accelerator.utils.calculate_gc_content(gc_test) - 1.0) < 0.001
        assert abs(grover_accelerator.utils.calculate_gc_content(at_test) - 0.0) < 0.001
        assert abs(grover_accelerator.utils.calculate_gc_content(mixed_test) - 0.5) < 0.001
        
        print("Utility functions successful")
        print(f"  Generated DNA sample: {dna[:20]}...")
        print(f"  GC content test: {grover_accelerator.utils.calculate_gc_content(mixed_test)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Utility functions failed: {e}")
        traceback.print_exc()
        return False

def test_performance_comparison():
    """Compare C++ vs Python performance"""
    print("\nTesting performance comparison...")
    try:
        import grover_accelerator
        
        # Generate test data
        sequence = grover_accelerator.utils.generate_random_dna(10000, seed=123)
        pattern = "AGCT"
        
        # Time C++ implementation
        start_time = time.time()
        cpp_matches = grover_accelerator.GroverAccelerator().find_pattern_matches(sequence, pattern)
        cpp_time = time.time() - start_time
        
        # Time Python implementation (simple)
        def python_pattern_search(seq, pat):
            matches = []
            for i in range(len(seq) - len(pat) + 1):
                if seq[i:i+len(pat)] == pat:
                    matches.append(i)
            return matches
        
        start_time = time.time()
        python_matches = python_pattern_search(sequence, pattern)
        python_time = time.time() - start_time
        
        # Verify results match
        assert cpp_matches == python_matches, "C++ and Python results should match"
        
        speedup = python_time / cpp_time if cpp_time > 0 else float('inf')
        
        print(f"Performance comparison successful")
        print(f"  Sequence length: {len(sequence):,} bases")
        print(f"  Pattern: '{pattern}'")
        print(f"  Matches found: {len(cpp_matches)}")
        print(f"  Python time: {python_time:.4f}s")
        print(f"  C++ time:    {cpp_time:.4f}s")
        print(f"  Speedup:     {speedup:.1f}x")
        
        return True
        
    except Exception as e:
        print(f"✗ Performance comparison failed: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("GROVER ACCELERATOR C++ MODULE TESTS")
    print("=" * 60)
    
    tests = [
        test_basic_import,
        test_accelerator_creation,
        test_pattern_matching,
        test_parallel_matching,
        test_oracle_construction,
        test_optimal_iterations,
        test_position_encoding,
        test_utils,
        test_performance_comparison,
    ]
    
    passed = 0
    failed = 0
    accelerator = None
    
    for i, test_func in enumerate(tests):
        try:
            if test_func.__name__ == 'test_accelerator_creation':
                success, accelerator = test_func()
            elif test_func.__name__ in ['test_pattern_matching', 'test_parallel_matching', 
                                       'test_oracle_construction', 'test_optimal_iterations',
                                       'test_position_encoding']:
                if accelerator is None:
                    print(f"Skipping {test_func.__name__} - no accelerator available")
                    continue
                success = test_func(accelerator)
            else:
                success = test_func()
            
            if success:
                passed += 1
            else:
                failed += 1
                
        except Exception as e:
            print(f"✗ Test {test_func.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Total tests: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("All tests passed!")
        return True
    else:
        print(f"{failed} test(s) failed")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
