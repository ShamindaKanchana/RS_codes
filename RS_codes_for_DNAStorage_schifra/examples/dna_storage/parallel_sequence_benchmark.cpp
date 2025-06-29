/*
 * Parallel DNA Sequence Benchmarking with Schifra Reed-Solomon (15,11)
 * Features:
 * - Multi-threaded processing with OpenMP
 * - Comprehensive benchmarking with warmup runs
 * - Thread scaling analysis
 * - Error injection and correction tracking
 * - Memory-efficient processing
 */

#include <iostream>
#include <string>
#include <vector>
#include <random>
#include <chrono>
#include <iomanip>
#include <cassert>
#include <numeric>
#include <algorithm>
#include <omp.h>
#include <atomic>
#include <thread>
#include <unistd.h>
#include <fstream>
#include <sstream>
#include "../../include/schifra/dna_storage.hpp"

// Using RS(15,11) which can correct up to 2 symbol errors
constexpr size_t BLOCK_SIZE = 11;  // k = 11
constexpr size_t CODE_LENGTH = 15;  // n = 15
constexpr size_t ECC_SYMBOLS = CODE_LENGTH - BLOCK_SIZE;  // 4 ECC symbols

using dna_storage_type = schifra::dna_storage<CODE_LENGTH, ECC_SYMBOLS, BLOCK_SIZE>;

// Structure to store benchmarking results
struct BenchmarkResult {
    size_t total_blocks = 0;
    size_t total_errors_introduced = 0;
    size_t total_errors_corrected = 0;
    double total_encoding_time = 0.0;    // in milliseconds
    double total_decoding_time = 0.0;     // in milliseconds
    double total_processing_time = 0.0;   // in milliseconds
    double throughput = 0.0;              // in MB/s
    int num_threads = 1;
    size_t sequence_length = 0;
    
    // Calculate error correction rate
    double error_correction_rate() const {
        return (total_errors_introduced > 0) ? 
               (static_cast<double>(total_errors_corrected) / total_errors_introduced) : 1.0;
    }
    
    // Calculate average block processing time
    double avg_block_processing_time() const {
        return (total_blocks > 0) ? (total_processing_time / total_blocks) : 0.0;
    }
};

// Structure to store block processing statistics with cache alignment
struct alignas(64) BlockStats {
    size_t errors_introduced = 0;
    size_t errors_corrected = 0;
    double encoding_time = 0.0;   // in milliseconds
    double decoding_time = 0.0;    // in milliseconds
    char padding[64 - (2 * sizeof(size_t) + 2 * sizeof(double)) % 64];
};

// Function to split a string into chunks of specified size
std::vector<std::string> split_into_blocks(const std::string& input, size_t block_size) {
    std::vector<std::string> blocks;
    for (size_t i = 0; i < input.length(); i += block_size) {
        blocks.push_back(input.substr(i, block_size));
    }
    return blocks;
}

// Function to pad the last block if needed
std::string pad_block(std::string block, size_t target_size) {
    if (block.size() >= target_size) return block;
    block.append(target_size - block.size(), 'A'); // 'A' is a valid DNA base
    return block;
}

// Thread-safe function to introduce random errors into a DNA sequence
std::string introduce_errors(const std::string& sequence, size_t error_count) {
    if (error_count == 0) return sequence;
    
    std::string corrupted = sequence;
    thread_local std::random_device rd;
    thread_local std::mt19937 gen(rd());
    std::uniform_int_distribution<> pos_dist(0, sequence.length() - 1);
    std::string bases = "ACGT";
    
    for (size_t i = 0; i < error_count; ++i) {
        size_t pos = pos_dist(gen);
        char original = corrupted[pos];
        char new_base;
        
        // Ensure we pick a different base
        do {
            new_base = bases[gen() % 4];
        } while (new_base == original);
        
        corrupted[pos] = new_base;
    }
    
    return corrupted;
}

// Process DNA sequence with benchmarking
BenchmarkResult process_dna_sequence_benchmark(const std::string& input_sequence, 
                                             size_t errors_per_block,
                                             int num_threads = 0) {
    BenchmarkResult result;
    result.sequence_length = input_sequence.length();
    
    // Set number of threads if specified
    if (num_threads > 0) {
        omp_set_num_threads(num_threads);
    }
    
    // Get actual number of threads being used
    #pragma omp parallel
    {
        #pragma omp master
        result.num_threads = omp_get_num_threads();
    }
    
    auto start_total = std::chrono::high_resolution_clock::now();
    
    // Split into blocks and prepare storage
    std::vector<std::string> blocks = split_into_blocks(input_sequence, BLOCK_SIZE);
    result.total_blocks = blocks.size();
    std::vector<std::string> decoded_blocks(blocks.size());
    std::vector<BlockStats> block_stats(blocks.size());
    
    // Process blocks in parallel
    #pragma omp parallel for schedule(static)
    for (size_t i = 0; i < blocks.size(); ++i) {
        try {
            dna_storage_type dna_storage;
            BlockStats stats;
            
            // Pad block if needed
            std::string original_block = blocks[i];
            if (original_block.size() < BLOCK_SIZE) {
                original_block = pad_block(original_block, BLOCK_SIZE);
            }
            
            // Encode
            auto encode_start = std::chrono::high_resolution_clock::now();
            auto [encoded_dna, ecc] = dna_storage.encode(original_block);
            auto encode_end = std::chrono::high_resolution_clock::now();
            
            // Introduce errors
            size_t max_errors = ECC_SYMBOLS / 2;
            size_t errors_to_introduce = std::min(errors_per_block, max_errors);
            std::string corrupted = introduce_errors(encoded_dna, errors_to_introduce);
            
            // Decode
            auto decode_start = std::chrono::high_resolution_clock::now();
            std::string corrected = dna_storage.decode(corrupted, ecc);
            auto decode_end = std::chrono::high_resolution_clock::now();
            
            // Update stats
            stats.encoding_time = std::chrono::duration<double, std::milli>(
                encode_end - encode_start).count();
            stats.decoding_time = std::chrono::duration<double, std::milli>(
                decode_end - decode_start).count();
            stats.errors_introduced = errors_to_introduce;
            
            // Count corrected errors
            for (size_t j = 0; j < std::min(corrupted.size(), corrected.size()); ++j) {
                if (corrupted[j] != corrected[j]) {
                    stats.errors_corrected++;
                }
            }
            
            // Store results
            block_stats[i] = stats;
            decoded_blocks[i] = corrected.substr(0, blocks[i].size());
            
        } catch (const std::exception& e) {
            // Handle error for this block
            #pragma omp critical
            std::cerr << "Error processing block: " << e.what() << std::endl;
        }
    }
    
    // Aggregate results
    for (const auto& stats : block_stats) {
        result.total_errors_introduced += stats.errors_introduced;
        result.total_errors_corrected += stats.errors_corrected;
        result.total_encoding_time += stats.encoding_time;
        result.total_decoding_time += stats.decoding_time;
    }
    
    // Calculate total processing time and throughput
    auto end_total = std::chrono::high_resolution_clock::now();
    result.total_processing_time = std::chrono::duration<double, std::milli>(
        end_total - start_total).count();
    
    // Calculate throughput in MB/s (1 base = 1 byte)
    result.throughput = (input_sequence.length() / (1024.0 * 1024.0)) / 
                       (result.total_processing_time / 1000.0);
    
    return result;
}

// Function to print benchmark results
void print_benchmark_results(const BenchmarkResult& result, const std::string& label = "") {
    if (!label.empty()) {
        std::cout << "\n=== " << label << " ===" << std::endl;
    }
    
    std::cout << "Benchmark Results:" << std::endl;
    std::cout << "-----------------" << std::endl;
    std::cout << "Sequence length:           " << result.sequence_length << " bases" << std::endl;
    std::cout << "Threads used:              " << result.num_threads << std::endl;
    std::cout << "Total blocks processed:    " << result.total_blocks << std::endl;
    std::cout << "Total errors introduced:   " << result.total_errors_introduced << std::endl;
    std::cout << "Total errors corrected:    " << result.total_errors_corrected << std::endl;
    std::cout << "Error correction rate:     " << std::fixed << std::setprecision(2) 
              << (result.error_correction_rate() * 100.0) << "%" << std::endl;
    std::cout << "Total encoding time:       " << std::fixed << std::setprecision(2) 
              << result.total_encoding_time << " ms" << std::endl;
    std::cout << "Total decoding time:       " << std::fixed << std::setprecision(2) 
              << result.total_decoding_time << " ms" << std::endl;
    std::cout << "Total processing time:     " << std::fixed << std::setprecision(2) 
              << result.total_processing_time << " ms" << std::endl;
    std::cout << "Avg block processing time: " << std::fixed << std::setprecision(4) 
              << result.avg_block_processing_time() << " ms/block" << std::endl;
    std::cout << "Throughput:                " << std::fixed << std::setprecision(2) 
              << result.throughput << " MB/s" << std::endl;
}

// Function to run a single benchmark case with warmup and multiple runs
BenchmarkResult run_benchmark_case(const std::string& sequence, 
                                 size_t errors_per_block,
                                 int num_threads,
                                 const std::string& label = "") {
    const int WARMUP_RUNS = 1;
    const int BENCHMARK_RUNS = 3;
    
    BenchmarkResult best_result;
    double best_time = std::numeric_limits<double>::max();
    
    // Warmup runs
    for (int i = 0; i < WARMUP_RUNS; ++i) {
        (void)process_dna_sequence_benchmark(sequence, errors_per_block, num_threads);
    }
    
    // Benchmark runs
    for (int run = 0; run < BENCHMARK_RUNS; ++run) {
        auto start = std::chrono::high_resolution_clock::now();
        BenchmarkResult result = process_dna_sequence_benchmark(
            sequence, errors_per_block, num_threads);
        auto end = std::chrono::high_resolution_clock::now();
        
        double total_time = std::chrono::duration<double, std::milli>(end - start).count();
        
        if (total_time < best_time) {
            best_time = total_time;
            best_result = result;
        }
        
        // Small delay between runs
        if (run < BENCHMARK_RUNS - 1) {
            std::this_thread::sleep_for(std::chrono::milliseconds(50));
        }
    }
    
    return best_result;
}

// Function to run scaling benchmark with different thread counts
void run_scaling_benchmark(const std::string& sequence, size_t errors_per_block) {
    std::cout << "\n=== Scaling Benchmark ===" << std::endl;
    std::cout << "Sequence length: " << sequence.length() << " bases" << std::endl;
    std::cout << "Errors per block: " << errors_per_block << std::endl;
    
    int max_threads = omp_get_max_threads();
    std::cout << "Available threads: " << max_threads << std::endl;
    
    // Test with different thread counts
    std::vector<int> thread_counts;
    for (int t = 1; t <= max_threads; t *= 2) {
        if (t <= max_threads) thread_counts.push_back(t);
    }
    if (thread_counts.empty() || thread_counts.back() != max_threads) {
        thread_counts.push_back(max_threads);
    }
    
    // Run benchmarks for each thread count
    for (int t : thread_counts) {
        std::string label = std::to_string(t) + " thread" + (t > 1 ? "s" : "");
        auto result = run_benchmark_case(sequence, errors_per_block, t, label);
        print_benchmark_results(result, label);
    }
}

// Function to generate a random DNA sequence
std::string generate_random_dna(size_t length) {
    const std::string bases = "ACGT";
    std::string result;
    result.reserve(length);
    
    thread_local std::random_device rd;
    thread_local std::mt19937 gen(rd());
    std::uniform_int_distribution<> dist(0, 3);
    
    for (size_t i = 0; i < length; ++i) {
        result += bases[dist(gen)];
    }
    
    return result;
}

// Function to run comprehensive tests
void run_comprehensive_benchmarks() {
    std::cout << "=== DNA Storage with Reed-Solomon (15,11) Benchmark ===" << std::endl;
    
    // Test with different sequence lengths (in bases)
    std::vector<size_t> test_lengths = {
        10000,     // 10KB
        100000,    // 100KB
        1000000,   // 1MB
        10000000   // 10MB
    };
    
    // Test with different error rates (errors per block)
    std::vector<size_t> error_rates = {0, 1, 2};
    
    for (size_t len : test_lengths) {
        std::cout << "\n=== Testing with " << len << " bases (" 
                 << (len / 1024.0) << " KB) ===" << std::endl;
        
        // Generate random DNA sequence
        std::cout << "Generating random DNA sequence..." << std::endl;
        std::string sequence = generate_random_dna(len);
        
        for (size_t errors : error_rates) {
            std::cout << "\n=== Testing with " << errors << " error" 
                     << (errors != 1 ? "s" : "") << " per block ===" << std::endl;
            
            // Run with all available threads
            auto result = run_benchmark_case(sequence, errors, 0, "Optimal Threads");
            print_benchmark_results(result);
            
            // Run scaling benchmark for larger sequences
            if (len >= 100000) {
                run_scaling_benchmark(sequence, errors);
            }
        }
    }
}

int main(int argc, char* argv[]) {
    try {
        // Print system and OpenMP information
        std::cout << "=== System Information ===" << std::endl;
        std::cout << "CPU Cores: " << sysconf(_SC_NPROCESSORS_ONLN) << std::endl;
        #ifdef _OPENMP
            std::cout << "OpenMP Version: " << _OPENMP / 100 << "." << _OPENMP % 100 << std::endl;
        #else
            std::cout << "OpenMP is NOT enabled!" << std::endl;
            return 1;
        #endif
        
        // Configure OpenMP
        omp_set_dynamic(0);  // Disable dynamic adjustment of threads
        
        // Run comprehensive benchmarks
        run_comprehensive_benchmarks();
        
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "\n❌ ERROR: " << e.what() << std::endl;
        return 1;
    }
}
