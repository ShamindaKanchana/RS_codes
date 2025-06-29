/*
 * Parallel block-wise processing of large DNA sequences using Schifra Reed-Solomon
 * RS(15,11) code that can correct up to 2 symbol errors per block
 * Parallelized with OpenMP for improved performance
 * 
 * Enhanced with benchmarking capabilities for performance analysis
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

// Structure to store block processing statistics
struct BlockStats {
    size_t errors_introduced = 0;
    size_t errors_corrected = 0;
    double encoding_time = 0.0;   // in milliseconds
    double decoding_time = 0.0;    // in milliseconds
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
    
    // Use 'A' as padding character (must be a valid DNA base: A, C, G, or T)
    block.append(target_size - block.size(), 'A');
    return block;
}

// Function to remove padding from the last block
std::string remove_padding(const std::string& block, size_t original_size) {
    if (block.size() <= original_size) return block;
    return block.substr(0, original_size);
}

// Thread-safe function to introduce random errors into a DNA sequence
std::string introduce_errors(const std::string& sequence, size_t error_count) {
    if (error_count == 0) return sequence;
    
    std::string corrupted = sequence;
    
    // Thread-local random number generation
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

// Function to process a single block with timing and error tracking
BlockStats process_block(const std::string& original_block, 
                       const std::vector<unsigned char>& original_ecc,
                       size_t error_count,
                       std::string& decoded_sequence) {
    BlockStats stats;
    auto start_total = std::chrono::high_resolution_clock::now();
    
    try {
        dna_storage_type dna_storage;
        
        // Time encoding
        auto encode_start = std::chrono::high_resolution_clock::now();
        auto [encoded_dna, ecc] = dna_storage.encode(original_block);
        auto encode_end = std::chrono::high_resolution_clock::now();
        stats.encoding_time = std::chrono::duration<double, std::milli>(encode_end - encode_start).count();
        
        // Introduce errors (but ensure we don't exceed the maximum correctable errors)
        size_t max_errors = ECC_SYMBOLS / 2;  // RS can correct t = (n-k)/2 errors
        size_t errors_to_introduce = std::min(error_count, max_errors);
        std::string corrupted = introduce_errors(encoded_dna, errors_to_introduce);
        stats.errors_introduced = errors_to_introduce;
        
        // Time decoding
        auto decode_start = std::chrono::high_resolution_clock::now();
        std::string corrected = dna_storage.decode(corrupted, ecc);
        auto decode_end = std::chrono::high_resolution_clock::now();
        stats.decoding_time = std::chrono::duration<double, std::milli>(decode_end - decode_start).count();
        
        // Store the decoded block (without ECC symbols)
        if (corrected.size() >= original_block.size()) {
            decoded_sequence = corrected.substr(0, original_block.size());
        } else {
            // If the corrected sequence is shorter, pad it with 'A's
            decoded_sequence = corrected;
            decoded_sequence.append(original_block.size() - corrected.size(), 'A');
        }
        
        // Count corrected errors by comparing corrupted vs corrected
        size_t corrected_errors = 0;
        for (size_t i = 0; i < std::min(corrupted.size(), corrected.size()); ++i) {
            if (corrupted[i] != corrected[i]) {
                corrected_errors++;
            }
        }
        stats.errors_corrected = corrected_errors;
        
        // Debug output for the first few blocks
        static std::atomic<int> block_counter{0};
        int block_num = block_counter++;
        if (block_num < 3) {  // Only show first 3 blocks for debugging
            std::cout << "Block " << block_num << " - "
                      << "Introduced: " << stats.errors_introduced << " errors, "
                      << "Corrected: " << stats.errors_corrected << " errors\n"
                      << "  Original: " << original_block.substr(0, 10) << (original_block.size() > 10 ? "..." : "") << "\n"
                      << "  Corrupt:  " << corrupted.substr(0, 10) << (corrupted.size() > 10 ? "..." : "") << "\n"
                      << "  Corrected:" << corrected.substr(0, 10) << (corrected.size() > 10 ? "..." : "") << "\n";
        }
        
    } catch (const std::exception& e) {
        std::cerr << "Error processing block: " << e.what() << std::endl;
        // Return empty decoded sequence on error
        decoded_sequence = std::string(original_block.size(), 'N');
    }
    
    return stats;
}

// Function to process the entire DNA sequence in parallel with benchmarking
BenchmarkResult process_dna_sequence(const std::string& input_sequence, 
                                   size_t errors_per_block,
                                   std::string& output_sequence,
                                   int num_threads = 0) {
    auto start_time = std::chrono::high_resolution_clock::now();
    BenchmarkResult result;
    auto start_total = std::chrono::high_resolution_clock::now();
    
    // Set number of threads if specified
    if (num_threads > 0) {
        omp_set_num_threads(num_threads);
    }
    
    // Split the input into blocks
    std::vector<std::string> blocks = split_into_blocks(input_sequence, BLOCK_SIZE);
    result.total_blocks = blocks.size();
    
    // Pad the last block if needed
    if (!blocks.empty() && blocks.back().size() < BLOCK_SIZE) {
        blocks.back() = pad_block(blocks.back(), BLOCK_SIZE);
    }
    
    // Process blocks in parallel
    std::vector<std::string> decoded_blocks(blocks.size());
    std::vector<BlockStats> block_stats(blocks.size());
    
    #pragma omp parallel for
    for (size_t i = 0; i < blocks.size(); ++i) {
        std::string original_block = blocks[i];
        bool is_last_block = (i == blocks.size() - 1);
        
        // Pad the last block if needed
        if (is_last_block && original_block.size() < BLOCK_SIZE) {
            original_block = pad_block(original_block, BLOCK_SIZE);
        }
        
        // Process the block
        block_stats[i] = process_block(blocks[i], {}, errors_per_block, decoded_blocks[i]);
    }
    
    // Combine block statistics
    for (const auto& stats : block_stats) {
        result.total_errors_introduced += stats.errors_introduced;
        result.total_errors_corrected += stats.errors_corrected;
        result.total_encoding_time += stats.encoding_time;
        result.total_decoding_time += stats.decoding_time;
    }
    
    // Calculate total processing time
    auto end_total = std::chrono::high_resolution_clock::now();
    result.total_processing_time = std::chrono::duration<double, std::milli>(end_total - start_total).count();
    
    // Calculate throughput
    size_t total_bases = input_sequence.length();
    double total_milliseconds = result.total_processing_time;
    result.throughput = (total_bases / 1024.0 / 1024.0) / (total_milliseconds / 1000.0);
    
    // Combine all blocks, removing padding from the last block
    output_sequence.clear();
    output_sequence.reserve(input_sequence.size()); // Optimize concatenation
    
    for (size_t i = 0; i < decoded_blocks.size(); ++i) {
        if (i == decoded_blocks.size() - 1) {
            // For the last block, only take the original size
            size_t original_size = input_sequence.length() % BLOCK_SIZE;
            if (original_size == 0) original_size = BLOCK_SIZE;
            output_sequence += decoded_blocks[i].substr(0, original_size);
        } else {
            output_sequence += decoded_blocks[i];
        }
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    
    #pragma omp parallel
    #pragma omp master
    {
        std::cout << "Processed " << blocks.size() << " blocks using " 
                  << omp_get_num_threads() << " threads in " 
                  << duration.count() << " ms" << std::endl;
    }
    
    return result;
}

// Function to print benchmark results
void print_benchmark_results(const BenchmarkResult& result, const std::string& label = "") {
    if (!label.empty()) {
        std::cout << "\n=== " << label << " ===" << std::endl;
    }
    
    std::cout << "Benchmark Results:" << std::endl;
    std::cout << "-----------------" << std::endl;
    std::cout << "Total blocks processed:       " << result.total_blocks << std::endl;
    std::cout << "Total errors introduced:      " << result.total_errors_introduced << std::endl;
    std::cout << "Total errors corrected:       " << result.total_errors_corrected << std::endl;
    std::cout << "Error correction rate:        " << std::fixed << std::setprecision(2) 
              << (result.error_correction_rate() * 100.0) << "%" << std::endl;
    std::cout << "Total encoding time:          " << std::fixed << std::setprecision(2) 
              << result.total_encoding_time << " ms" << std::endl;
    std::cout << "Total decoding time:          " << std::fixed << std::setprecision(2) 
              << result.total_decoding_time << " ms" << std::endl;
    std::cout << "Total processing time:        " << std::fixed << std::setprecision(2) 
              << result.total_processing_time << " ms" << std::endl;
    std::cout << "Average block processing time: " << std::fixed << std::setprecision(4) 
              << result.avg_block_processing_time() << " ms/block" << std::endl;
    std::cout << "Throughput:                   " << std::fixed << std::setprecision(2) 
              << result.throughput << " MB/s" << std::endl;
    std::cout << std::endl;
}

// Function to run a single benchmark case
void run_benchmark_case(const std::string& sequence, size_t errors_per_block, 
                       const std::string& label = "", int num_threads = 0) {
    std::string decoded;
    auto start = std::chrono::high_resolution_clock::now();
    
    BenchmarkResult result = process_dna_sequence(sequence, errors_per_block, decoded, num_threads);
    
    auto end = std::chrono::high_resolution_clock::now();
    double total_time = std::chrono::duration<double, std::milli>(end - start).count();
    
    std::string test_label = label;
    if (test_label.empty()) {
        test_label = "Test with " + std::to_string(sequence.length()) + " bases";
        if (num_threads > 0) {
            test_label += " (" + std::to_string(num_threads) + " threads)";
        }
    }
    
    print_benchmark_results(result, test_label);
    
    // Verify the decoding
    if (sequence == decoded) {
        std::cout << "✓ Decoding successful - Output matches input" << std::endl;
    } else {
        std::cerr << "✗ Decoding failed - Output does not match input" << std::endl;
        std::cerr << "  Original length: " << sequence.length() << std::endl;
        std::cerr << "  Decoded length:  " << decoded.length() << std::endl;
        
        // Find first mismatch
        size_t mismatch_pos = 0;
        size_t min_len = std::min(sequence.length(), decoded.length());
        while (mismatch_pos < min_len && sequence[mismatch_pos] == decoded[mismatch_pos]) {
            mismatch_pos++;
        }
        
        if (mismatch_pos < min_len) {
            size_t start_pos = (mismatch_pos > 10) ? mismatch_pos - 10 : 0;
            size_t end_pos = std::min(mismatch_pos + 10, min_len);
            
            std::cerr << "  First mismatch at position " << mismatch_pos << ":" << std::endl;
            std::cerr << "  Original: ..." << sequence.substr(start_pos, end_pos - start_pos) << "..." << std::endl;
            std::cerr << "  Decoded:  ..." << decoded.substr(start_pos, end_pos - start_pos) << "..." << std::endl;
        }
    }
    
    std::cout << std::string(60, '=') << std::endl;
}

// Function to run a scaling benchmark with different thread counts
void run_scaling_benchmark(const std::string& sequence, size_t errors_per_block) {
    std::cout << "\n=== Scaling Benchmark ===" << std::endl;
    std::cout << "Sequence length: " << sequence.length() << " bases" << std::endl;
    std::cout << "Errors per block: " << errors_per_block << std::endl;
    
    int max_threads = omp_get_max_threads();
    std::cout << "Available threads: " << max_threads << std::endl;
    
    // Warm-up run - don't check the result, just run it
    std::string dummy_decoded;
    (void)process_dna_sequence(sequence, errors_per_block, dummy_decoded, 1);
    
    // Test with different thread counts
    for (int t = 1; t <= max_threads; t++) {
        std::string label = "Threads: " + std::to_string(t);
        run_benchmark_case(sequence, errors_per_block, label, t);
    }
}

// Function to generate a random DNA sequence
std::string generate_random_dna(size_t length) {
    const std::string bases = "ACGT";
    std::string result;
    result.reserve(length);
    
    // Thread-safe random number generation
    thread_local std::random_device rd;
    thread_local std::mt19937 gen(rd());
    std::uniform_int_distribution<> dist(0, 3);
    
    for (size_t i = 0; i < length; ++i) {
        result += bases[dist(gen)];
    }
    
    return result;
}

// Function to calculate error rate between two sequences
float calculate_error_rate(const std::string& original, const std::string& decoded) {
    if (original.length() != decoded.length()) {
        return -1.0f; // Error: sequences have different lengths
    }
    
    size_t errors = 0;
    #pragma omp parallel for reduction(+:errors)
    for (size_t i = 0; i < original.length(); ++i) {
        if (original[i] != decoded[i]) {
            ++errors;
        }
    }
    
    return (static_cast<float>(errors) / original.length()) * 100.0f;
}

void run_tests() {
    std::cout << "=== DNA Storage with Reed-Solomon (15,11) Benchmark ===" << std::endl;
    
    // Test with different sequence lengths
    std::vector<size_t> test_lengths = {1000, 10000, 100000};  // 1KB, 10KB, 100KB
    
    for (size_t len : test_lengths) {
        std::cout << "\n\n=== Testing with " << len << " bases (" 
                  << (len / 1024.0) << " KB) ===" << std::endl;
        
        // Generate random DNA sequence
        std::cout << "Generating random DNA sequence..." << std::endl;
        std::string original_sequence = generate_random_dna(len);
        
        // Test with different error counts (up to max correctable errors)
        for (size_t errors = 1; errors <= 2; ++errors) {
            std::cout << "\n=== Testing with " << errors << " error" 
                     << (errors > 1 ? "s" : "") << " per block ===" << std::endl;
            
            // Run single-threaded test
            run_benchmark_case(original_sequence, errors, "Single-threaded", 1);
            
            // Run multi-threaded test
            run_benchmark_case(original_sequence, errors, "Multi-threaded");
            
            // Run scaling benchmark (test with different thread counts)
            if (len >= 10000) {  // Only run scaling test for larger sequences
                run_scaling_benchmark(original_sequence, errors);
            }
        }
    }
}

int main() {
    try {
        // Use all available threads
        omp_set_num_threads(omp_get_max_threads());
        
        run_tests();
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "\n❌ ERROR: " << e.what() << std::endl;
        return 1;
    }
}