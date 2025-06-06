#pragma once

#include <string>
#include <vector>
#include <stdexcept>
#include <cstdint>

namespace dna {
    // DNA base to number mapping
    constexpr char BASE_TO_NUM[4] = {'A', 'C', 'G', 'T'};
    
    // Number to DNA base mapping
    constexpr char NUM_TO_BASE[4] = {'A', 'C', 'G', 'T'};
    
    // Convert DNA sequence to binary representation
    std::vector<uint8_t> dna_to_binary(const std::string& dna);
    
    // Convert binary representation back to DNA sequence
    std::string binary_to_dna(const std::vector<uint8_t>& binary);
    
    // Validate DNA sequence
    bool is_valid_dna(const std::string& dna);
    
    // Convert DNA base to number (0-3)
    uint8_t base_to_num(char base);
    
    // Convert number (0-3) to DNA base
    char num_to_base(uint8_t num);
}
