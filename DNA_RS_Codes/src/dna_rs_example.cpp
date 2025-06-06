#include <iostream>
#include <string>
#include <vector>

#include "dna_utils.hpp"
#include "dna_rs_encoder.hpp"
#include "dna_rs_decoder.hpp"

int main() {
    try {
        // Example DNA sequence
        std::string dna_sequence = "ATCGATCGTAGCTACG";
        
        // Initialize encoder and decoder with custom parameters
        // Using smaller values for demonstration
        std::size_t n = 30;  // Total length (data + ECC)
        std::size_t k = 20;  // Data length
        
        // Create encoder and decoder
        dna::DNAReedSolomonEncoder encoder(n, k);
        dna::DNAReedSolomonDecoder decoder(n, k);
        
        // Encode the DNA sequence
        auto result = encoder.encode(dna_sequence);
        std::string encoded_dna = std::get<0>(result);
        std::vector<uint8_t> ecc_symbols = std::get<1>(result);
        
        std::cout << "Original DNA sequence: " << dna_sequence << "\n";
        std::cout << "Encoded DNA (with ECC): " << encoded_dna << "\n";
        
        // Simulate errors in the DNA sequence
        std::string corrupted_dna = encoded_dna;
        
        // Introduce errors at specific positions
        if (corrupted_dna.size() > 1) corrupted_dna[1] = 'C';  // Change second base
        if (corrupted_dna.size() > 5) corrupted_dna[5] = 'G';  // Change sixth base
        if (corrupted_dna.size() > 9) corrupted_dna[9] = 'T';  // Change tenth base
        if (corrupted_dna.size() > 10) corrupted_dna[10] = 'A'; // Change eleventh base
        
        std::cout << "Corrupted DNA: " << corrupted_dna << "\n";
        
        // Decode and correct errors
        std::string corrected_dna = decoder.decode(corrupted_dna, ecc_symbols);
        std::cout << "Corrected DNA: " << corrected_dna << "\n";
        
        // Extract original data
        std::string original_data = corrected_dna.substr(0, dna_sequence.size());
        std::cout << "Extracted original data: " << original_data << "\n";
        
        // Verify correction and data extraction
        std::cout << "Correction successful (compared to encoded): " 
                  << (corrected_dna == encoded_dna) << "\n";
        std::cout << "Original sequence preserved: " 
                  << (original_data == dna_sequence) << "\n";
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    
    return 0;
}
