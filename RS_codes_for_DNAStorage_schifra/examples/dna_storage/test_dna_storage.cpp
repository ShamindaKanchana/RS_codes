/*
 * Simple test program for Schifra DNA Storage
 */

#include <iostream>
#include <string>
#include <cassert>
#include "schifra/dna_storage.hpp"

// Using RS(15,11) which can correct up to 2 symbol errors
using dna_storage_type = schifra::dna_storage<15, 4, 11>;  // n=15, k=11, t=2

void run_test() {
    std::cout << "=== Testing Schifra DNA Storage ===\n\n";
    
    try {
        // 1. Initialize DNA storage
        dna_storage_type dna_storage;
        
        // 2. Test with a simple DNA sequence
        std::string original = "ACGTACGTACG";  // 11 bases (matches k=11)
        std::cout << "Original DNA: " << original << "\n";
        
        // 3. Encode the DNA sequence
        auto [encoded_dna, ecc] = dna_storage.encode(original);
        std::cout << "Encoded DNA (data only): " << encoded_dna << "\n";
        
        // 4. Print ECC symbols
        std::cout << "ECC (" << ecc.size() << " symbols): ";
        for (auto b : ecc) {
            std::cout << std::hex << std::setw(2) << std::setfill('0') 
                     << (int)b << " ";
        }
        std::cout << std::dec << "\n";
        
        // 5. Test error-free decoding
        std::string decoded = dna_storage.decode(encoded_dna, ecc);
        std::cout << "Decoded DNA: " << decoded << "\n";
        
        // 6. Verify the decoded sequence matches the original
        if (original == decoded) {
            std::cout << "\n✅ Test 1/2 PASSED: Error-free decoding successful\n";
        } else {
            std::cout << "\n❌ Test 1/2 FAILED: Error-free decoding failed\n";
            return;
        }
        
        // 7. Test error correction
        std::string corrupted = encoded_dna;
        // Introduce two errors at different positions
        corrupted[1] = (corrupted[1] == 'A') ? 'C' : 'A';  // First error
        corrupted[5] = (corrupted[5] == 'G') ? 'T' : 'G';  // Second error
        
        std::cout << "\nCorrupted DNA: " << corrupted << " (introduced 2 errors)\n";
        
        // Try to decode and correct the errors
        std::string corrected = dna_storage.decode(corrupted, ecc);
        std::cout << "Corrected DNA: " << corrected << "\n";
        
        // Verify if the errors were corrected
        if (original == corrected) {
            std::cout << "\n✅ Test 2/2 PASSED: Error correction successful\n";
        } else {
            std::cout << "\n❌ Test 2/2 FAILED: Error correction failed\n";
            std::cout << "Expected: " << original << "\n";
            std::cout << "Got:      " << corrected << "\n";
        }
        
    } catch (const std::exception& e) {
        std::cerr << "\n❌ ERROR: " << e.what() << std::endl;
    }
}

int main() {
    run_test();
    return 0;
}
