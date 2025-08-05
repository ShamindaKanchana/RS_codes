/*
 * Benchmark for Schifra DNA Storage with RS(15,11) over GF(16)
 */

#include <iostream>
#include <string>
#include <chrono>
#include <vector>
#include <numeric>
#include <iomanip>
#include <cmath>
#include "schifra/dna_storage.hpp"

using namespace std::chrono;
using dna_storage_type = schifra::dna_storage<15, 4, 11>;  // RS(15,11) over GF(16)

struct BenchmarkResult {
    double encode_time_us;
    double decode_time_us;
    bool success;
};

BenchmarkResult run_benchmark() {
    BenchmarkResult result;
    dna_storage_type dna_storage;
    std::string original = "ACGTACGTACG";  // 11 bases
    
    // Time encoding
    auto start = high_resolution_clock::now();
    auto [encoded_dna, ecc] = dna_storage.encode(original);
    auto encode_time = duration_cast<nanoseconds>(high_resolution_clock::now() - start);
    
    // Corrupt the sequence (2 errors)
    std::string corrupted = encoded_dna;
    corrupted[1] = (corrupted[1] == 'A') ? 'C' : 'A';
    corrupted[5] = (corrupted[5] == 'G') ? 'T' : 'G';
    
    // Time decoding
    start = high_resolution_clock::now();
    std::string corrected = dna_storage.decode(corrupted, ecc);
    auto decode_time = duration_cast<nanoseconds>(high_resolution_clock::now() - start);
    
    // Store results
    result.encode_time_us = encode_time.count() / 1000.0;  // ns to μs
    result.decode_time_us = decode_time.count() / 1000.0;  // ns to μs
    result.success = (corrected == encoded_dna);
    
    return result;
}

int main() {
    const int warmup_runs = 100;
    const int benchmark_runs = 1000;
    
    std::cout << "=== Schifra DNA Storage Benchmark (RS(15,11) over GF(16)) ===\n\n";
    std::cout << "Warming up..." << std::endl;
    
    // Warmup
    for (int i = 0; i < warmup_runs; ++i) {
        run_benchmark();
    }
    
    std::cout << "Running benchmark (" << benchmark_runs << " iterations)...\n";
    
    std::vector<double> encode_times;
    std::vector<double> decode_times;
    int success_count = 0;
    
    // Run benchmark
    for (int i = 0; i < benchmark_runs; ++i) {
        auto result = run_benchmark();
        encode_times.push_back(result.encode_time_us);
        decode_times.push_back(result.decode_time_us);
        if (result.success) success_count++;
    }
    
    // Calculate statistics
    auto avg_encode = std::accumulate(encode_times.begin(), encode_times.end(), 0.0) / benchmark_runs;
    auto avg_decode = std::accumulate(decode_times.begin(), decode_times.end(), 0.0) / benchmark_runs;
    
    // Find min/max
    auto min_encode = *std::min_element(encode_times.begin(), encode_times.end());
    auto max_encode = *std::max_element(encode_times.begin(), encode_times.end());
    auto min_decode = *std::min_element(decode_times.begin(), decode_times.end());
    auto max_decode = *std::max_element(decode_times.begin(), decode_times.end());
    
    // Calculate standard deviation
    double encode_var = 0.0;
    double decode_var = 0.0;
    for (int i = 0; i < benchmark_runs; ++i) {
        encode_var += (encode_times[i] - avg_encode) * (encode_times[i] - avg_encode);
        decode_var += (decode_times[i] - avg_decode) * (decode_times[i] - avg_decode);
    }
    encode_var /= benchmark_runs;
    decode_var /= benchmark_runs;
    double encode_stddev = std::sqrt(encode_var);
    double decode_stddev = std::sqrt(decode_var);
    
    // Print results
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "\n--- Benchmark Results ---\n";
    std::cout << "Total runs: " << benchmark_runs << "\n";
    std::cout << "Success rate: " << (success_count * 100.0 / benchmark_runs) << "%\n\n";
    
    std::cout << "Encode (μs):\n";
    std::cout << "  Avg: " << avg_encode << " ± " << encode_stddev << "\n";
    std::cout << "  Min: " << min_encode << "\n";
    std::cout << "  Max: " << max_encode << "\n\n";
    
    std::cout << "Decode (μs):\n";
    std::cout << "  Avg: " << avg_decode << " ± " << decode_stddev << "\n";
    std::cout << "  Min: " << min_decode << "\n";
    std::cout << "  Max: " << max_decode << "\n\n";
    
    std::cout << "Total time per operation (μs):\n";
    std::cout << "  Avg: " << (avg_encode + avg_decode) << "\n";
    
    return 0;
}
