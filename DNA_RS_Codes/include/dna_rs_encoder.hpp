#pragma once

#include <string>
#include <vector>
#include <memory>
#include <stdexcept>

#include <schifra_galois_field.hpp>
#include <schifra_galois_field_polynomial.hpp>
#include <schifra_sequential_root_generator_polynomial_creator.hpp>
#include <schifra_reed_solomon_encoder.hpp>
#include <schifra_reed_solomon_block.hpp>
#include <schifra_reed_solomon_util.hpp>

#include "dna_utils.hpp"

namespace dna {
    class DNAReedSolomonEncoder {
    public:
        DNAReedSolomonEncoder(std::size_t n, std::size_t k);
        
        std::pair<std::string, std::vector<uint8_t>> encode(const std::string& dna);
        
    private:
        std::size_t n_;  // Total length (data + ECC)
        std::size_t k_;  // Data length
        std::size_t t_;  // Number of errors that can be corrected
        
        schifra::galois::field field_;
        schifra::galois::field_polynomial generator_polynomial_;
        std::unique_ptr<schifra::reed_solomon::encoder<255, 223>> encoder_;
    };
}
