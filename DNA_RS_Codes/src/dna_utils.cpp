#include "dna_utils.hpp"

namespace dna {
    bool is_valid_dna(const std::string& dna) {
        for (char base : dna) {
            if (base != 'A' && base != 'C' && base != 'G' && base != 'T') {
                return false;
            }
        }
        return true;
    }

    uint8_t base_to_num(char base) {
        switch (base) {
            case 'A': return 0;
            case 'C': return 1;
            case 'G': return 2;
            case 'T': return 3;
            default: throw std::invalid_argument("Invalid DNA base");
        }
    }

    char num_to_base(uint8_t num) {
        if (num > 3) {
            throw std::invalid_argument("Invalid number for DNA base");
        }
        return NUM_TO_BASE[num];
    }

    std::vector<uint8_t> dna_to_binary(const std::string& dna) {
        if (!is_valid_dna(dna)) {
            throw std::invalid_argument("Invalid DNA sequence");
        }
        
        std::vector<uint8_t> binary;
        for (char base : dna) {
            binary.push_back(base_to_num(base));
        }
        return binary;
    }

    std::string binary_to_dna(const std::vector<uint8_t>& binary) {
        std::string dna;
        for (uint8_t num : binary) {
            if (num > 3) throw std::invalid_argument("Invalid binary value");
            dna.push_back(num_to_base(num));
        }
        return dna;
    }
}
