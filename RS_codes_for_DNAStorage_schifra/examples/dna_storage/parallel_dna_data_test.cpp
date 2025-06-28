/*
 * Parallel block-wise processing of large DNA sequences using Schifra Reed-Solomon
 * RS(15,11) code that can correct up to 2 symbol errors per block
 * Parallelized with OpenMP for improved performance
 */

#include <iostream>
#include <string>
#include <vector>
#include <random>
#include <chrono>
#include <iomanip>
#include <cassert>
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

// Function to process a single block
bool process_block(const std::string& original_block, 
                  const std::vector<unsigned char>& original_ecc,
                  size_t error_count,
                  std::string& decoded_sequence) {
    try {
        dna_storage_type dna_storage;
        
        // Encode the block
        auto [encoded_dna, ecc] = dna_storage.encode(original_block);
        
        // Introduce errors (but ensure we don't exceed the maximum correctable errors)
        size_t max_errors = ECC_SYMBOLS / 2;  // RS can correct t = (n-k)/2 errors
        size_t errors_to_introduce = std::min(error_count, max_errors);
        std::string corrupted = introduce_errors(encoded_dna, errors_to_introduce);
        
        // Decode and correct errors
        std::string corrected = dna_storage.decode(corrupted, ecc);
        
        // Store the decoded block (without ECC symbols)
        decoded_sequence = corrected.substr(0, original_block.size());
        
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Error processing block: " << e.what() << std::endl;
        return false;
    }
}

// Function to process the entire DNA sequence in parallel
bool process_dna_sequence(const std::string& input_sequence, 
                         size_t errors_per_block,
                         std::string& output_sequence) {
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // Split into blocks
    auto blocks = split_into_blocks(input_sequence, BLOCK_SIZE);
    std::vector<std::string> decoded_blocks(blocks.size()); // Pre-allocate for thread safety
    
    bool all_blocks_processed = true;
    
    // Parallelize block processing
    #pragma omp parallel for shared(blocks, decoded_blocks, all_blocks_processed, errors_per_block)
    for (size_t i = 0; i < blocks.size(); ++i) {
        std::string original_block = blocks[i];
        bool is_last_block = (i == blocks.size() - 1);
        
        // Pad the last block if needed
        if (is_last_block && original_block.size() < BLOCK_SIZE) {
            original_block = pad_block(original_block, BLOCK_SIZE);
        }
        
        // Process the block
        std::string decoded_block;
        bool success = process_block(original_block, {}, errors_per_block, decoded_block);
        
        if (!success) {
            #pragma omp critical
            all_blocks_processed = false; // Thread-safe update
            continue;
        }
        
        // Remove padding from the last block
        if (is_last_block && blocks[i].size() < BLOCK_SIZE) {
            decoded_block = remove_padding(decoded_block, blocks[i].size());
        }
        
        // Store in pre-allocated vector to maintain order
        decoded_blocks[i] = decoded_block;
    }
    
    // Early exit if any block failed
    if (!all_blocks_processed) {
        output_sequence.clear();
        return false;
    }
    
    // Combine all blocks
    output_sequence.clear();
    output_sequence.reserve(input_sequence.size()); // Optimize concatenation
    for (const auto& block : decoded_blocks) {
        output_sequence += block;
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
    
    return all_blocks_processed;
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
    std::cout << "=== Schifra DNA Storage - Parallel Block-wise Processing Test ===\n";
    std::cout << "Using " << omp_get_max_threads() << " threads\n\n";
    
    // Test cases
    struct TestCase {
        std::string name;
        std::string sequence;
        size_t errors_per_block;
    };
    
    // Generate a large random DNA sequence (10,000 bases)
    std::string large_sequence = generate_random_dna(10000);
    
    std::vector<TestCase> test_cases = {
        {"Exact multiple of block size (22 chars)", generate_random_dna(22), 1},
        {"One less than multiple of block size (21 chars)", generate_random_dna(21), 1},
        {"Large sequence (10,000 chars)", large_sequence, 1},
        {"Edge case: single base", "A", 0},
        {"Edge case: empty string", "", 0}
    };
    
    for (const auto& test_case : test_cases) {
        std::cout << "\n\n=== Test: " << test_case.name << " ===\n";
        std::cout << "Input length: " << test_case.sequence.length() << " bases\n";
        std::cout << "Errors per block: " << test_case.errors_per_block << "\n";
        
        std::string decoded_sequence;
        bool success = process_dna_sequence(
            test_case.sequence, 
            test_case.errors_per_block,
            decoded_sequence
        );
        
        if (!success) {
            std::cout << "❌ Test failed during processing\n";
            continue;
        }
        
        // Verify the decoded sequence matches the original
        if (test_case.sequence == decoded_sequence) {
            std::cout << "✅ Test passed: Decoded sequence matches original\n";
        } else {
            float error_rate = calculate_error_rate(test_case.sequence, decoded_sequence);
            std::cout << "❌ Test failed: Decoded sequence does not match original\n";
            std::cout << "   Error rate: " << std::fixed << std::setprecision(2) 
                      << error_rate << "%\n";
            
            // Print first 20 characters where they differ
            size_t diff_pos = 0;
            while (diff_pos < test_case.sequence.length() && 
                   diff_pos < decoded_sequence.length() &&
                   test_case.sequence[diff_pos] == decoded_sequence[diff_pos]) {
                ++diff_pos;
            }
            
            if (diff_pos < test_case.sequence.length()) {
                size_t start = (diff_pos > 10) ? diff_pos - 10 : 0;
                size_t end = std::min(diff_pos + 10, test_case.sequence.length());
                
                std::cout << "   First difference around position " << diff_pos << ":\n";
                std::cout << "   Original: ..." << test_case.sequence.substr(start, end - start) << "...\n";
                std::cout << "   Decoded : ..." << decoded_sequence.substr(start, end - start) << "...\n";
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