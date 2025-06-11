#include <iostream>
#include <string>
#include <cassert>
#include "../../src/dna_storage_cuda.cu"

void run_parallel_test() {
    std::cout << "=== Testing Parallel Schifra DNA Storage ===\n\n";
    
    try {
        // Initialize parallel DNA storage
        ParallelDNAStorage parallel_storage;
        
        // Create a longer test sequence (multiple of k=11)
        std::string original = "ACGTACGTACG"  // First chunk
                             "TGCATGCATGC"    // Second chunk
                             "GATCGATCGAT"    // Third chunk
                             "CTAGCTAGCTA";   // Fourth chunk
        
        std::cout << "Original DNA sequence: " << original << "\n";
        std::cout << "Length: " << original.length() << " bases\n";
        std::cout << "Number of chunks: " << original.length() / 11 << "\n\n";
        
        // Process in parallel
        std::string processed = parallel_storage.processParallel(original);
        
        std::cout << "Processed DNA sequence: " << processed << "\n";
        
        // Verify the processed sequence matches the original
        if (original == processed) {
            std::cout << "\n✅ Test PASSED: Parallel processing successful\n";
        } else {
            std::cout << "\n❌ Test FAILED: Parallel processing failed\n";
            std::cout << "Expected: " << original << "\n";
            std::cout << "Got:      " << processed << "\n";
        }
        
    } catch (const std::exception& e) {
        std::cerr << "\n❌ ERROR: " << e.what() << std::endl;
    }
}

int main() {
    run_parallel_test();
    return 0;
} 