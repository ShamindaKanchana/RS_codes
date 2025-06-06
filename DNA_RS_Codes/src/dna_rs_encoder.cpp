#include "dna_rs_encoder.hpp"
#include <cstring>

namespace dna {
    DNAReedSolomonEncoder::DNAReedSolomonEncoder(std::size_t n, std::size_t k)
        : n_(n), k_(k), t_((n - k) / 2),
          field_(8, schifra::galois::primitive_polynomial_size06,
                schifra::galois::primitive_polynomial06),
          generator_polynomial_(field_) {
        
        // Create the generator polynomial
        if (!schifra::make_sequential_root_generator_polynomial(field_,
                                                               120,
                                                               2 * t_,
                                                               generator_polynomial_)) {
            throw std::runtime_error("Failed to create generator polynomial");
        }
        
        // Create encoder
        encoder_ = std::make_unique<schifra::reed_solomon::encoder<255, 223>>(field_, generator_polynomial_);
    }
    
    std::pair<std::string, std::vector<uint8_t>> DNAReedSolomonEncoder::encode(const std::string& dna) {
        if (!is_valid_dna(dna)) {
            throw std::invalid_argument("Invalid DNA sequence");
        }
        
        // Convert DNA to binary
        std::vector<uint8_t> binary_data = dna_to_binary(dna);
        
        // Create RS block
        schifra::reed_solomon::block<255, 223> block;
        
        // Pad the data to match the block size
        std::vector<uint8_t> padded_data(binary_data);
        padded_data.resize(k_, 0);  // Pad with zeros
        
        // Copy padded data to block
        memcpy(&block[0], padded_data.data(), k_);
        
        // Encode
        if (!encoder_->encode(block)) {
            throw std::runtime_error("Encoding failed");
        }
        
        // Extract encoded data and ECC symbols
        std::vector<uint8_t> encoded_data(&block[0], &block[k_]);
        std::vector<uint8_t> ecc_symbols(&block[k_], &block[n_]);
        
        // Convert encoded data back to DNA
        std::string encoded_dna = binary_to_dna(encoded_data);
        
        return {encoded_dna, ecc_symbols};
    }
}
