# Grover algorithm for DNA motif search

A high-performance implementation of Grover's quantum search algorithm for DNA sequence analysis, featuring C++ acceleration for computational speedup.

## Features

- **Quantum-inspired algorithm** for DNA motif searching
- **C++ acceleration** providing 10-50x performance improvements
- **Multi-threading support** for large sequence analysis
- **Real-time DNA validation** and GC content calculation
- **Comprehensive testing** framework

## Project structure

```
grover-algorithm/
├── src/                            # Source code
│   ├── grover_accelerated.py       # Enhanced Grover algorithm
│   └── grover_pattern_search.py    # Basic pattern search
├── cpp/                            # C++ accelerator code
├── scripts/                        # Build automation
├── tests/                          # Test suites
├── examples/                       # Usage examples
├── docs/                           # Documentation
└── run_grover.py                   # Main entry point
```

## Quick start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Build C++ accelerator
```bash
python scripts/build.py
```

### 3. Run the algorithm
```bash
# Direct sequence input
python run_grover.py "ATCGATCGATCG" "AGCT"

# File input (recommended for large sequences)
python run_grover.py --file dna_sequence.txt "AGCT"

# Full demo
python src/grover_accelerated.py

# Examples
python examples/basic_usage.py
python examples/performance_comparison.py
```

## Usage examples

### Command line interface
```bash
# Search for motif in DNA sequence (direct input)
python run_grover.py "ATCGATCGATCGAGCTAGCTAGCT" "AGCT"

# Search using file input (recommended for large sequences)
python run_grover.py --file my_dna_sequence.txt "AGCT"

# Get help and see all options
python run_grover.py --help

# Run performance comparison
python examples/performance_comparison.py

# Run comprehensive tests
python tests/run_all_tests.py
```

### File input format
For large DNA sequences, create a text file with your sequence:

```
# dna_sequence.txt
AACTTTAAGAAATTATGTGCATGCCTTCAAGACCCAGAGACCTAATCATA
GCGCTCCTCATTTGGCTCATACGCATCTGGGTCTTCGGCTTGAAATTGAG
GGCAACCACGTGACTACTTCTACGAACCTATAAGATTGTCGTTCGCGGAT
...
```

**Requirements:**
- Only DNA bases (A, T, G, C) are allowed
- Whitespace and newlines are automatically removed
- Case insensitive (converted to uppercase)
- Maximum sequence length depends on available memory

### Python API
```python
from src.grover_accelerated import GroverDNASearchAccelerated

# Create Grover search instance
grover = GroverDNASearchAccelerated(sequence, motif)

# Run the search
counts = grover.run()

# Analyze results
grover.analyze(counts)
```

## Building from Source

### Prerequisites
- **Python 3.7+**
- **C++ Compiler**: Visual Studio 2019+ (Windows), GCC 7+ (Linux), Clang 6+ (macOS)
- **pybind11**: `pip install pybind11`

### Build Commands
```bash
# Simple build
python scripts/build.py

# Comprehensive build with testing
python scripts/build_accelerator.py --install --test

# Clean build artifacts
python scripts/build_accelerator.py --clean
```

## Testing

```bash
# Run all tests
python tests/run_all_tests.py

# Run specific test suite
python tests/test_accelerator.py

# Run examples
python examples/basic_usage.py
```

## Development

### Adding New Features
1. **Algorithms**: Add to `src/` directory
2. **C++ acceleration**: Modify `cpp/grover_accelerator.cpp`
3. **Tests**: Add to `tests/` directory
4. **Examples**: Create in `examples/` directory
5. **Documentation**: Update `docs/` directory

### Code Organization
- **`src/`**: Core algorithm implementations
- **`cpp/`**: High-performance C++ extensions
- **`scripts/`**: Build automation and utilities
- **`tests/`**: Test suites and validation
- **`examples/`**: Usage demonstrations
- **`docs/`**: Project documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.