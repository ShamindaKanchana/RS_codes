// large_dna_test.cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <random>
#include <chrono>
#include <algorithm>
#include <iomanip>
#include "schifra/dna_storage.hpp"

using dna_storage_type = schifra::dna_storage<15, 4, 11>;  // RS(15,11)

// Generate random DNA sequence of given length
std::string generate_random_dna(size_t length) {
    static const char dna_bases[] = {'A', 'C', 'G', 'T'};
    static std::random_device rd;
    static std::mt19937 gen(rd());
    static std::uniform_int_distribution<> dis(0, 3);
    
    std::string result;
    result.reserve(length);
    for (size_t i = 0; i < length; ++i) {
        result += dna_bases[dis(gen)];
    }
    return result;
}

// Add exactly 2 substitution errors per block
void add_errors(std::string& dna_block) {
    static std::random_device rd;
    static std::mt19937 gen(rd());
    static std::uniform_int_distribution<> pos_dis(0, 10);
    static std::uniform_int_distribution<> base_dis(0, 2);
    
    // Ensure we have exactly 11 bases
    if (dna_block.length() != 11) return;
    
    // Choose 2 distinct positions
    int pos1 = pos_dis(gen);
    int pos2;
    do {
        pos2 = pos_dis(gen);
    } while (pos2 == pos1);
    
    // Generate different bases
    auto get_different_base = [](char original) {
        static const std::string bases = "ACGT";
        std::string other_bases;
        for (char b : bases) {
            if (b != original) other_bases += b;
        }
        return other_bases[std::rand() % 3];
    };
    
    dna_block[pos1] = get_different_base(dna_block[pos1]);
    dna_block[pos2] = get_different_base(dna_block[pos2]);
}

// Process large DNA sequence
void process_large_dna(const std::string& input_dna, bool inject_errors = true) {
    const size_t BLOCK_SIZE = 11;
    size_t original_length = input_dna.length();
    size_t padded_length = ((original_length + BLOCK_SIZE - 1) / BLOCK_SIZE) * BLOCK_SIZE;
    
    // Pad input if needed
    std::string padded_input = input_dna;
    if (padded_length > original_length) {
        padded_input.append(padded_length - original_length, 'N');  // 'N' for padding
    }
    
    dna_storage_type encoder;
    size_t num_blocks = padded_length / BLOCK_SIZE;
    
    // Statistics
    size_t total_errors_injected = 0;
    size_t total_errors_corrected = 0;
    size_t total_blocks = 0;
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // Process blocks in parallel
    #pragma omp parallel for reduction(+:total_errors_injected, total_errors_corrected, total_blocks)
    for (size_t i = 0; i < num_blocks; ++i) {
        std::string block = padded_input.substr(i * BLOCK_SIZE, BLOCK_SIZE);
        std::string original_block = block;
        
        // Encode
        auto [encoded_dna, ecc] = encoder.encode(block);
        
        // Inject errors
        if (inject_errors) {
            add_errors(encoded_dna);
            total_errors_injected += 2;  // We inject exactly 2 errors per block
        }
        
        // Decode
        try {
            std::string decoded = encoder.decode(encoded_dna, ecc);
            
            // Count corrected errors
            for (size_t j = 0; j < BLOCK_SIZE; ++j) {
                if (original_block[j] != 'N' &&  // Don't count padding
                    decoded[j] != original_block[j]) {
                    #pragma omp atomic
                    total_errors_corrected++;
                }
            }
        } catch (const std::exception& e) {
            #pragma omp critical
            std::cerr << "Error in block " << i << ": " << e.what() << std::endl;
        }
        
        #pragma omp atomic
        total_blocks++;
        
        // Progress reporting
        if (total_blocks % 1000 == 0) {
            #pragma omp critical
            {
                auto now = std::chrono::high_resolution_clock::now();
                auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time).count() / 1000.0;
                double blocks_per_sec = total_blocks / elapsed;
                std::cout << "\rProcessed " << total_blocks << " blocks (" 
                          << std::fixed << std::setprecision(1) << blocks_per_sec << " blocks/s)";
                std::cout.flush();
            }
        }
    }
    
    // Print summary
    auto end_time = std::chrono::high_resolution_clock::now();
    double total_seconds = std::chrono::duration<double>(end_time - start_time).count();
    
    std::cout << "\n\n=== Processing Complete ===\n";
    std::cout << "Total blocks processed: " << total_blocks << "\n";
    std::cout << "Original length: " << original_length << " bases\n";
    std::cout << "Padded length: " << padded_length << " bases\n";
    std::cout << "Total errors injected: " << total_errors_injected << "\n";
    std::cout << "Total errors corrected: " << total_errors_corrected << "\n";
    std::cout << "Processing time: " << total_seconds << " seconds\n";
    std::cout << "Throughput: " 
              << (padded_length / (1024.0 * 1024.0)) / total_seconds 
              << " MB/s\n";
}

int main(int argc, char* argv[]) {
    if (argc != 2 && argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <sequence_length> [no_errors]\n";
        std::cerr << "Example: " << argv[0] << " 1000000\n";
        return 1;
    }
    
    size_t sequence_length = std::stoull(argv[1]);
    bool inject_errors = (argc == 2);  // Default: inject errors
    
    // Generate or load your DNA sequence
    std::cout << "Generating random DNA sequence of length " << sequence_length << "...\n";
    std::string dna_sequence = generate_random_dna(sequence_length);
    
    // Process the sequence
    process_large_dna(dna_sequence, inject_errors);
    
    return 0;
}