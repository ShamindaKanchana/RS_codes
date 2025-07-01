#include <iostream>
#include <string>
#include <vector>
#include <random>
#include <chrono>
#include <iomanip>
#include <algorithm>
#include <omp.h>
#include "schifra/dna_storage.hpp"

// Using RS(15,11) which can correct up to 2 symbol errors
constexpr size_t BLOCK_SIZE = 11;  // k = 11
constexpr size_t CODE_LENGTH = 15;  // n = 15
constexpr size_t ECC_SYMBOLS = CODE_LENGTH - BLOCK_SIZE;  // 4 ECC symbols

using dna_storage_type = schifra::dna_storage<CODE_LENGTH, ECC_SYMBOLS, BLOCK_SIZE>;

// Function to split a string into chunks of specified size
std::vector<std::string> split_into_blocks(const std::string& input, size_t block_size) {
    std::vector<std::string> blocks;
    if (input.empty()) return blocks;
    for (size_t i = 0; i < input.length(); i += block_size) {
        blocks.push_back(input.substr(i, block_size));
    }
    return blocks;
}

// Function to generate random DNA sequence
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

// Function to introduce random errors into a DNA sequence
std::string introduce_errors(const std::string& sequence, size_t error_count) {
    if (error_count == 0 || sequence.empty()) return sequence;
    
    std::string corrupted = sequence;
    thread_local std::random_device rd;
    thread_local std::mt19937 gen(rd());
    std::uniform_int_distribution<> pos_dist(0, sequence.length() - 1);
    std::string bases = "ACGT";
    
    for (size_t i = 0; i < error_count; ++i) {
        size_t pos = pos_dist(gen);
        char original = corrupted[pos];
        char new_base;
        
        do {
            new_base = bases[gen() % 4];
        } while (new_base == original);
        
        corrupted[pos] = new_base;
    }
    
    return corrupted;
}

// Function to pad a block to the required size
std::string pad_block(std::string block, size_t target_size) {
    if (block.size() >= target_size) return block;
    block.append(target_size - block.size(), 'A');
    return block;
}

// Function to process blocks in parallel
void process_blocks_parallel(const std::vector<std::string>& blocks, 
                           std::vector<std::string>& decoded_blocks,
                           size_t errors_per_block,
                           int num_threads) {
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel for schedule(dynamic)
    for (size_t i = 0; i < blocks.size(); ++i) {
        try {
            dna_storage_type dna_storage;
            std::string block = blocks[i];
            bool is_last_block = (i == blocks.size() - 1);
            
            // Pad the block if it's too short
            if (block.size() < BLOCK_SIZE) {
                block = pad_block(block, BLOCK_SIZE);
            }
            
            auto [encoded_dna, ecc] = dna_storage.encode(block);
            std::string corrupted = introduce_errors(encoded_dna, errors_per_block);
            std::string decoded = dna_storage.decode(corrupted, ecc);
            
            // Remove padding if this was the last block and it was padded
            if (is_last_block && blocks[i].size() < BLOCK_SIZE) {
                decoded = decoded.substr(0, blocks[i].size());
            }
            
            decoded_blocks[i] = decoded;
        } catch (const std::exception& e) {
            std::cerr << "Error processing block " << i << ": " << e.what() << std::endl;
            decoded_blocks[i] = "";
        }
    }
}

struct BenchmarkResult {
    size_t size_mb;
    std::vector<int> thread_counts;
    std::vector<double> speedups;
    std::vector<long long> times_ms;
};

void run_benchmark(size_t sequence_size_mb, BenchmarkResult& result) {
    const size_t SEQUENCE_SIZE = sequence_size_mb * 1024 * 1024;
    const size_t ERRORS_PER_BLOCK = 1;
    const std::vector<int> thread_counts = {1, 2, 4, 8};
    
    result.size_mb = sequence_size_mb;
    result.thread_counts = thread_counts;
    result.speedups.clear();
    result.times_ms.clear();
    
    std::cout << "\n=== Benchmarking " << sequence_size_mb << "MB of data ===\n";
    
    std::cout << "Generating test data..." << std::endl;
    std::string dna_sequence = generate_random_dna(SEQUENCE_SIZE);
    auto blocks = split_into_blocks(dna_sequence, BLOCK_SIZE);
    std::vector<std::string> decoded_blocks(blocks.size());
    
    // Ensure the last block is properly padded if needed
    if (!blocks.empty() && blocks.back().size() < BLOCK_SIZE) {
        blocks.back() = pad_block(blocks.back(), BLOCK_SIZE);
    }
    
    // Warm-up run
    std::cout << "Warming up..." << std::endl;
    process_blocks_parallel(blocks, decoded_blocks, ERRORS_PER_BLOCK, 1);
    
    // Benchmark different thread counts
    std::cout << "Threads\tTime(ms)\tSpeedup\n";
    std::cout << "-------\t--------\t-------\n";
    
    double base_time = 0.0;
    
    for (int threads : thread_counts) {
        // Clear previous results
        std::fill(decoded_blocks.begin(), decoded_blocks.end(), "");
        
        auto start = std::chrono::high_resolution_clock::now();
        process_blocks_parallel(blocks, decoded_blocks, ERRORS_PER_BLOCK, threads);
        auto end = std::chrono::high_resolution_clock::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
        double speedup = (base_time > 0) ? (base_time / duration) : 1.0;
        
        if (threads == 1) {
            base_time = static_cast<double>(duration);
        }
        
        std::cout << threads << "\t" 
                 << duration << "\t\t"
                 << std::fixed << std::setprecision(2) << speedup << "x\n";
                 
        result.speedups.push_back(speedup);
        result.times_ms.push_back(duration);
    }
}

int main() {
    std::vector<size_t> test_sizes_mb = {10, 15, 20, 25};
    std::vector<BenchmarkResult> all_results;
    
    for (size_t size_mb : test_sizes_mb) {
        BenchmarkResult result;
        run_benchmark(size_mb, result);
        all_results.push_back(result);
        
        // Save results to a file for plotting
        std::ofstream outfile("benchmark_results_" + std::to_string(size_mb) + "MB.txt");
        outfile << "Threads\tTime(ms)\tSpeedup\n";
        for (size_t i = 0; i < result.thread_counts.size(); ++i) {
            outfile << result.thread_counts[i] << "\t"
                   << result.times_ms[i] << "\t"
                   << std::fixed << std::setprecision(2) << result.speedups[i] << "x\n";
        }
    }
    
    return 0;
}