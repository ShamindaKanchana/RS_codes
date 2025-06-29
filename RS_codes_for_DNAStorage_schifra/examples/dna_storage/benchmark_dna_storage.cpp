#include <iostream>
#include <vector>
#include <chrono>
#include <omp.h>
#include "dna_storage.hpp"

void run_benchmark(const std::string& sequence, int max_threads) {
    using namespace std::chrono;
    
    std::cout << "Sequence length: " << sequence.length() << " bases\n";
    std::cout << "Threads\tTime(ms)\tSpeedup\n";
    
    // Test different thread counts
    for (int t = 1; t <= max_threads; t++) {
        omp_set_num_threads(t);
        
        // Warm-up run
        process_dna_sequence_parallel(sequence, 1);
        
        // Timed runs
        auto start = high_resolution_clock::now();
        for (int i = 0; i < 10; i++) {  // Multiple runs for stable measurements
            process_dna_sequence_parallel(sequence, 1);
        }
        auto end = high_resolution_clock::now();
        
        auto duration = duration_cast<milliseconds>(end - start).count() / 10.0;
        double speedup = (t == 1) ? 1.0 : 
                        (duration / (double)duration_1thread) * t;
        
        if (t == 1) duration_1thread = duration;
        
        std::cout << t << "\t" << duration << " ms\t" 
                 << (t == 1 ? 1.0 : speedup) << "x\n";
    }
}

int main() {
    // Generate test sequences of different sizes
    std::vector<std::string> test_sequences = {
        generate_random_dna(1000),    // 1KB
        generate_random_dna(10000),   // 10KB
        generate_random_dna(100000)   // 100KB
    };
    
    const int max_threads = omp_get_max_threads();
    std::cout << "System supports up to " << max_threads << " threads\n";
    
    for (const auto& seq : test_sequences) {
        std::cout << "\n=== Benchmarking Sequence ===" << std::endl;
        run_benchmark(seq, max_threads);
    }
    
    return 0;
}