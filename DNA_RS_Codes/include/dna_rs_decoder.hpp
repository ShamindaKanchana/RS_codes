#pragma once

#include <schifra_galois_field.hpp>
#include <schifra_galois_field_polynomial.hpp>
#include <schifra_sequential_root_generator_polynomial_creator.hpp>
#include <schifra_reed_solomon_decoder.hpp>
#include <schifra_reed_solomon_block.hpp>
#include <schifra_reed_solomon_util.hpp>

#include "dna_utils.hpp"

namespace dna {
    class DNAReedSolomonDecoder {
    public:
        DNAReedSolomonDecoder(std::size_t n, std::size_t k);
        
        std::string decode(const std::string& corrupted_dna, const std::vector<uint8_t>& ecc_symbols);
        
    private:
        std::size_t n_;  // Total length (data + ECC)
        std::size_t k_;  // Data length
        std::size_t t_;  // Number of errors that can be corrected
        
        schifra::galois::field field_;
        std::unique_ptr<schifra::reed_solomon::decoder<255, 223>> decoder_;
    };
}
