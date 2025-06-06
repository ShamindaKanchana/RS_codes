#include "dna_rs_decoder.hpp"
#include <cstring>

namespace dna {
    DNAReedSolomonDecoder::DNAReedSolomonDecoder(std::size_t n, std::size_t k)
        : n_(n), k_(k), t_((n - k) / 2),
          field_(8, schifra::galois::primitive_polynomial_size06,
                schifra::galois::primitive_polynomial06) {
        
        // Create decoder
        decoder_ = std::make_unique<schifra::reed_solomon::decoder<255, 223>>(field_, 120);
    }
    
    std::string DNAReedSolomonDecoder::decode(const std::string& corrupted_dna, const std::vector<uint8_t>& ecc_symbols) {
        if (!is_valid_dna(corrupted_dna)) {
            throw std::invalid_argument("Invalid DNA sequence");
        }
        
        // Convert corrupted DNA to binary
        std::vector<uint8_t> binary_data = dna_to_binary(corrupted_dna);
        
        // Create RS block
        schifra::reed_solomon::block<255, 223> block;
        
        // Copy corrupted data and ECC symbols to block
        memcpy(&block[0], binary_data.data(), k_);
        memcpy(&block[k_], ecc_symbols.data(), n_ - k_);
        
        // Decode
        if (!decoder_->decode(block)) {
            throw std::runtime_error("Decoding failed");
        }
        
        // Extract corrected data
        std::vector<uint8_t> corrected_data(&block[0], &block[k_]);
        
        // Convert back to DNA
        return binary_to_dna(corrected_data);
    }
}
