#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include <vector>
#include <string>
#include <complex>
#include <unordered_map>
#include <algorithm>
#include <cmath>
#include <thread>
#include <future>

// Define M_PI for Windows if not available
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace py = pybind11;

class GroverAccelerator {
public:
    /**
     * Fast DNA sequence encoding - converts positions to binary representations
     */
    std::vector<std::string> encode_positions(int num_candidates, int n_qubits) {
        std::vector<std::string> encodings;
        encodings.reserve(num_candidates);
        
        for (int pos = 0; pos < num_candidates; ++pos) {
            std::string binary;
            binary.reserve(n_qubits);
            
            // Convert to binary with zero padding
            for (int bit = n_qubits - 1; bit >= 0; --bit) {
                binary += ((pos >> bit) & 1) ? '1' : '0';
            }
            encodings.push_back(binary);
        }
        
        return encodings;
    }
    
    /**
     * High-performance pattern matching using optimized string search
     */
    std::vector<int> find_pattern_matches(const std::string& sequence, const std::string& pattern) {
        std::vector<int> matches;
        
        if (pattern.empty() || sequence.empty() || pattern.length() > sequence.length()) {
            return matches;
        }
        
        // Reserve space to avoid reallocations
        matches.reserve(sequence.length() / 10); // Rough estimate
        
        // Boyer-Moore-inspired optimization for DNA sequences
        const size_t pattern_len = pattern.length();
        const size_t sequence_len = sequence.length();
        
        for (size_t i = 0; i <= sequence_len - pattern_len; ++i) {
            bool match = true;
            for (size_t j = 0; j < pattern_len; ++j) {
                if (sequence[i + j] != pattern[j]) {
                    match = false;
                    break;
                }
            }
            if (match) {
                matches.push_back(static_cast<int>(i));
            }
        }
        
        return matches;
    }
    
    /**
     * Parallel pattern matching for large sequences
     */
    std::vector<int> find_pattern_matches_parallel(const std::string& sequence, const std::string& pattern, int num_threads = 4) {
        if (pattern.empty() || sequence.empty() || pattern.length() > sequence.length()) {
            return std::vector<int>();
        }
        
        const size_t sequence_len = sequence.length();
        const size_t pattern_len = pattern.length();
        const size_t search_len = sequence_len - pattern_len + 1;
        const size_t chunk_size = search_len / num_threads;
        
        std::vector<std::future<std::vector<int>>> futures;
        
        for (int t = 0; t < num_threads; ++t) {
            size_t start = t * chunk_size;
            size_t end = (t == num_threads - 1) ? search_len : (t + 1) * chunk_size;
            
            futures.push_back(std::async(std::launch::async, [&, start, end]() {
                std::vector<int> local_matches;
                for (size_t i = start; i < end; ++i) {
                    bool match = true;
                    for (size_t j = 0; j < pattern_len; ++j) {
                        if (sequence[i + j] != pattern[j]) {
                            match = false;
                            break;
                        }
                    }
                    if (match) {
                        local_matches.push_back(static_cast<int>(i));
                    }
                }
                return local_matches;
            }));
        }
        
        // Collect results from all threads
        std::vector<int> all_matches;
        for (auto& future : futures) {
            auto local_matches = future.get();
            all_matches.insert(all_matches.end(), local_matches.begin(), local_matches.end());
        }
        
        // Sort since parallel execution might return out-of-order results
        std::sort(all_matches.begin(), all_matches.end());
        
        return all_matches;
    }
    
    /**
     * Fast diagonal matrix construction for oracle
     */
    std::vector<std::complex<double>> build_oracle_diagonal(const std::vector<int>& matches, int database_size) {
        std::vector<std::complex<double>> diagonal(database_size, std::complex<double>(1.0, 0.0));
        
        // Mark matching positions with -1 phase
        for (int match : matches) {
            if (match < database_size) {
                diagonal[match] = std::complex<double>(-1.0, 0.0);
            }
        }
        
        return diagonal;
    }
    
    /**
     * Calculate optimal number of Grover iterations
     */
    int calculate_optimal_iterations(int total_items, int marked_items) {
        if (marked_items <= 0 || total_items <= 0) {
            return 1;
        }
        
        double ratio = static_cast<double>(total_items) / static_cast<double>(marked_items);
        int iterations = static_cast<int>(std::floor((M_PI / 4.0) * std::sqrt(ratio)));
        
        return std::max(1, iterations);
    }
    
    /**
     * Statistical analysis of measurement results
     */
    std::unordered_map<std::string, double> analyze_measurement_statistics(
        const std::unordered_map<std::string, int>& counts,
        const std::vector<int>& expected_matches,
        int total_shots) {
        
        std::unordered_map<std::string, double> stats;
        
        int total_match_shots = 0;
        int max_count = 0;
        std::string most_frequent_state;
        
        for (const auto& [state, count] : counts) {
            if (count > max_count) {
                max_count = count;
                most_frequent_state = state;
            }
            
            // Check if this state corresponds to a match
            // (This would need position decoding logic)
            total_match_shots += count;
        }
        
        stats["success_probability"] = static_cast<double>(total_match_shots) / total_shots;
        stats["max_amplitude"] = static_cast<double>(max_count) / total_shots;
        stats["entropy"] = calculate_shannon_entropy(counts, total_shots);
        stats["num_unique_states"] = static_cast<double>(counts.size());
        
        return stats;
    }
    
private:
    /**
     * Calculate Shannon entropy of measurement distribution
     */
    double calculate_shannon_entropy(const std::unordered_map<std::string, int>& counts, int total_shots) {
        double entropy = 0.0;
        
        for (const auto& [state, count] : counts) {
            if (count > 0) {
                double probability = static_cast<double>(count) / total_shots;
                entropy -= probability * std::log2(probability);
            }
        }
        
        return entropy;
    }
};

/**
 * Standalone utility functions
 */
namespace utils {
    /**
     * Generate random DNA sequence for testing
     */
    std::string generate_random_dna(int length, int seed = 42) {
        std::srand(seed);
        const char bases[] = {'A', 'T', 'G', 'C'};
        std::string sequence;
        sequence.reserve(length);
        
        for (int i = 0; i < length; ++i) {
            sequence += bases[std::rand() % 4];
        }
        
        return sequence;
    }
    
    /**
     * Validate DNA sequence (only contains A, T, G, C)
     */
    bool is_valid_dna(const std::string& sequence) {
        for (char base : sequence) {
            if (base != 'A' && base != 'T' && base != 'G' && base != 'C') {
                return false;
            }
        }
        return true;
    }
    
    /**
     * Calculate GC content of DNA sequence
     */
    double calculate_gc_content(const std::string& sequence) {
        if (sequence.empty()) return 0.0;
        
        int gc_count = 0;
        for (char base : sequence) {
            if (base == 'G' || base == 'C') {
                gc_count++;
            }
        }
        
        return static_cast<double>(gc_count) / sequence.length();
    }
}

// Python bindings
PYBIND11_MODULE(grover_accelerator, m) {
    m.doc() = "High-performance C++ accelerator for Grover DNA search";
    
    // Main accelerator class
    py::class_<GroverAccelerator>(m, "GroverAccelerator")
        .def(py::init<>())
        .def("encode_positions", &GroverAccelerator::encode_positions,
             "Fast encoding of positions to binary strings",
             py::arg("num_candidates"), py::arg("n_qubits"))
        .def("find_pattern_matches", &GroverAccelerator::find_pattern_matches,
             "High-performance pattern matching",
             py::arg("sequence"), py::arg("pattern"))
        .def("find_pattern_matches_parallel", &GroverAccelerator::find_pattern_matches_parallel,
             "Parallel pattern matching for large sequences",
             py::arg("sequence"), py::arg("pattern"), py::arg("num_threads") = 4)
        .def("build_oracle_diagonal", &GroverAccelerator::build_oracle_diagonal,
             "Fast diagonal matrix construction for oracle",
             py::arg("matches"), py::arg("database_size"))
        .def("calculate_optimal_iterations", &GroverAccelerator::calculate_optimal_iterations,
             "Calculate optimal number of Grover iterations",
             py::arg("total_items"), py::arg("marked_items"))
        .def("analyze_measurement_statistics", &GroverAccelerator::analyze_measurement_statistics,
             "Statistical analysis of measurement results",
             py::arg("counts"), py::arg("expected_matches"), py::arg("total_shots"));
    
    // Utility functions
    auto utils_module = m.def_submodule("utils", "Utility functions for DNA analysis");
    utils_module.def("generate_random_dna", &utils::generate_random_dna,
                     "Generate random DNA sequence for testing",
                     py::arg("length"), py::arg("seed") = 42);
    utils_module.def("is_valid_dna", &utils::is_valid_dna,
                     "Validate DNA sequence");
    utils_module.def("calculate_gc_content", &utils::calculate_gc_content,
                     "Calculate GC content of DNA sequence");
    
    // Constants
    m.attr("DNA_BASES") = py::make_tuple('A', 'T', 'G', 'C');
    m.attr("VERSION") = "1.0.0";
}
