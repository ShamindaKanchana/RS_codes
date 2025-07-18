/*
 * Parallel vs Sequential DNA Sequence Processing Comparison
 * Uses Schifra Reed-Solomon RS(15,11) code
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
 
 // Test case structure
 struct TestCase {
     std::string name;
     std::string sequence;
     size_t errors_per_block;
 };
 
 // Function declarations
 std::vector<std::string> split_into_blocks(const std::string& input, size_t block_size);
 std::string pad_block(std::string block, size_t target_size);
 std::string remove_padding(const std::string& block, size_t original_size);
 std::string introduce_errors(const std::string& sequence, size_t error_count);
 bool process_block(const std::string& original_block, 
                   const std::vector<unsigned char>& original_ecc,
                   size_t error_count,
                   std::string& decoded_sequence);
 bool process_dna_sequence(const std::string& input_sequence, 
                          size_t errors_per_block,
                          std::string& output_sequence);
 bool process_dna_sequence_parallel(const std::string& input_sequence, 
                                   size_t errors_per_block,
                                   std::string& output_sequence);
 std::string generate_random_dna(size_t length);
 float calculate_error_rate(const std::string& original, const std::string& decoded);
 
 // Function to split a string into chunks of specified size
 std::vector<std::string> split_into_blocks(const std::string& input, size_t block_size) {
     std::vector<std::string> blocks;
     if (input.empty()) return blocks; // Handle empty string
     for (size_t i = 0; i < input.length(); i += block_size) {
         blocks.push_back(input.substr(i, block_size));
     }
     return blocks;
 }
 
 // Function to pad the last block if needed
 std::string pad_block(std::string block, size_t target_size) {
     if (block.size() >= target_size) return block;
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
 
 // Function to process a single block
 bool process_block(const std::string& original_block, 
                   const std::vector<unsigned char>& original_ecc,
                   size_t error_count,
                   std::string& decoded_sequence) {
     try {
         dna_storage_type dna_storage;
         auto [encoded_dna, ecc] = dna_storage.encode(original_block);
         size_t max_errors = ECC_SYMBOLS / 2;  // t = (n-k)/2 = 2
         size_t errors_to_introduce = std::min(error_count, max_errors);
         std::string corrupted = introduce_errors(encoded_dna, errors_to_introduce);
         std::string corrected = dna_storage.decode(corrupted, ecc);
         decoded_sequence = corrected.substr(0, original_block.size());
         return true;
     } catch (const std::exception& e) {
         #pragma omp critical
         std::cerr << "Error processing block: " << e.what() << std::endl;
         return false;
     }
 }
 
 // Sequential version of DNA sequence processing
 bool process_dna_sequence(const std::string& input_sequence, 
                          size_t errors_per_block,
                          std::string& output_sequence) {
     auto start_time = std::chrono::high_resolution_clock::now();
     
     auto blocks = split_into_blocks(input_sequence, BLOCK_SIZE);
     std::vector<std::string> decoded_blocks(blocks.size());
     bool all_blocks_processed = true;
     
     for (size_t i = 0; i < blocks.size(); ++i) {
         std::string original_block = blocks[i];
         bool is_last_block = (i == blocks.size() - 1);
         
         if (is_last_block && original_block.size() < BLOCK_SIZE) {
             original_block = pad_block(original_block, BLOCK_SIZE);
         }
         
         if (!process_block(original_block, {}, errors_per_block, decoded_blocks[i])) {
             all_blocks_processed = false;
             break;
         }
         
         if (is_last_block && blocks[i].size() < BLOCK_SIZE) {
             decoded_blocks[i] = remove_padding(decoded_blocks[i], blocks[i].size());
         }
     }
     
     output_sequence.clear();
     if (all_blocks_processed) {
         output_sequence.reserve(input_sequence.size());
         for (const auto& block : decoded_blocks) {
             output_sequence += block;
         }
     }
     
     auto end_time = std::chrono::high_resolution_clock::now();
     auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
     std::cout << "Processed " << blocks.size() << " blocks sequentially in " 
               << duration.count() << " ms" << std::endl;
     
     return all_blocks_processed;
 }
 
 // Parallel version of DNA sequence processing
 bool process_dna_sequence_parallel(const std::string& input_sequence, 
                                   size_t errors_per_block,
                                   std::string& output_sequence) {
     auto start_time = std::chrono::high_resolution_clock::now();
     
     auto blocks = split_into_blocks(input_sequence, BLOCK_SIZE);
     std::vector<std::string> decoded_blocks(blocks.size());
     bool all_blocks_processed = true;
     
     #pragma omp parallel for schedule(dynamic)
     for (size_t i = 0; i < blocks.size(); ++i) {
         std::string original_block = blocks[i];
         bool is_last_block = (i == blocks.size() - 1);
         
         if (is_last_block && original_block.size() < BLOCK_SIZE) {
             original_block = pad_block(original_block, BLOCK_SIZE);
         }
         
         std::string decoded_block;
         if (!process_block(original_block, {}, errors_per_block, decoded_block)) {
             #pragma omp critical
             all_blocks_processed = false;
             continue;
         }
         
         if (is_last_block && blocks[i].size() < BLOCK_SIZE) {
             decoded_block = remove_padding(decoded_block, blocks[i].size());
         }
         
         decoded_blocks[i] = decoded_block;
     }
     
     output_sequence.clear();
     if (all_blocks_processed) {
         output_sequence.reserve(input_sequence.size());
         for (const auto& block : decoded_blocks) {
             output_sequence += block;
         }
     }
     
     auto end_time = std::chrono::high_resolution_clock::now();
     auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
     std::cout << "Processed " << blocks.size() << " blocks in parallel in " 
               << duration.count() << " ms" << std::endl;
     
     return all_blocks_processed;
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
 
 // Function to calculate error rate between two sequences
 float calculate_error_rate(const std::string& original, const std::string& decoded) {
     if (original.length() != decoded.length()) {
         return -1.0f;
     }
     
     size_t errors = 0;
     for (size_t i = 0; i < original.length(); ++i) {
         if (original[i] != decoded[i]) {
             ++errors;
         }
     }
     
     return (static_cast<float>(errors) / original.length()) * 100.0f;
 }
 
 // Function to run a single test case
 void run_test_case(const TestCase& test_case) {
     std::cout << "\n\n=== Test: " << test_case.name << " ===\n";
     std::cout << "Input length: " << test_case.sequence.length() << " bases\n";
     std::cout << "Errors per block: " << test_case.errors_per_block << "\n";
 
     // Sequential
     std::string seq_sequential;
     auto start_seq = std::chrono::high_resolution_clock::now();
     bool success_seq = process_dna_sequence(test_case.sequence, test_case.errors_per_block, seq_sequential);
     auto end_seq = std::chrono::high_resolution_clock::now();
     auto duration_seq = std::chrono::duration_cast<std::chrono::milliseconds>(end_seq - start_seq).count();
 
     // Parallel
     std::string seq_parallel;
     auto start_par = std::chrono::high_resolution_clock::now();
     bool success_par = process_dna_sequence_parallel(test_case.sequence, test_case.errors_per_block, seq_parallel);
     auto end_par = std::chrono::high_resolution_clock::now();
     auto duration_par = std::chrono::duration_cast<std::chrono::milliseconds>(end_par - start_par).count();
 
     // Verify same output
     bool same_output = (seq_sequential == seq_parallel && success_seq == success_par);
     float speedup = (duration_par > 0) ? static_cast<float>(duration_seq) / duration_par : 0.0f;
 
     // Report results
     std::cout << "Sequential time: " << duration_seq << " ms\n";
     std::cout << "Parallel time: " << duration_par << " ms\n";
     std::cout << "Speedup: " << std::fixed << std::setprecision(2) << speedup << "x\n";
     if (success_seq && same_output) {
         std::cout << "✅ Test passed: Outputs match\n";
     } else {
         std::cout << "❌ Test failed: Outputs differ or processing failed\n";
         if (!same_output) {
             float error_rate = calculate_error_rate(seq_sequential, seq_parallel);
             std::cout << "   Error rate: " << std::fixed << std::setprecision(2) << error_rate << "%\n";
         }
     }
 }
 
 // Function to run all test cases
 void run_tests() {
     std::cout << "=== Schifra DNA Storage - Large Sequence Performance Test ===\n\n";
    
     // Test different large sequence sizes
     const size_t KB = 1024;
     const size_t MB = 1024 * KB;
    
     std::vector<TestCase> test_cases = {
         // Medium size sequences
         {"Medium sequence (10KB)", generate_random_dna(10 * KB), 1},
         {"Medium sequence (100KB)", generate_random_dna(100 * KB), 1},
        
         // Large sequences
         {"Large sequence (1MB)", generate_random_dna(1 * MB), 1},
         {"Large sequence (5MB)", generate_random_dna(5 * MB), 1},
        
         // Test with different error rates
         {"Large sequence with no errors (1MB)", generate_random_dna(1 * MB), 0},
         {"Large sequence with max errors (1MB)", generate_random_dna(1 * MB), ECC_SYMBOLS / 2}
     };
    
     for (const auto& test_case : test_cases) {
         run_test_case(test_case);
     }
 }
 
 // Main function
 int main() {
     try {
         // Set number of threads (optional, adjust based on system)
         omp_set_num_threads(4); // Example: Use 4 threads
         run_tests();
         return 0;
     } catch (const std::exception& e) {
         std::cerr << "\n❌ ERROR: " << e.what() << std::endl;
         return 1;
     }
 }