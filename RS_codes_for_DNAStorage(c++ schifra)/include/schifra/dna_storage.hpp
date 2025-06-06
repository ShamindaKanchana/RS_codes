#ifndef SCHIFRA_DNA_STORAGE_HPP
#define SCHIFRA_DNA_STORAGE_HPP

#include <cstddef>
#include <string>
#include <vector>
#include <array>
#include <stdexcept>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <memory>
#include <unordered_map>
#include <functional>
#include <chrono>
#include <cstdint>
#include <algorithm>
#include <cctype>

// Schifra library includes
#include "schifra/core/galois_field/field.hpp"
#include "schifra/core/galois_field/polynomial.hpp"
#include "schifra/reed_solomon/schifra_sequential_root_generator_polynomial_creator.hpp"
#include "schifra/reed_solomon/schifra_reed_solomon_encoder.hpp"
#include "schifra/reed_solomon/schifra_reed_solomon_decoder.hpp"
#include "schifra/reed_solomon/schifra_reed_solomon_block.hpp"

namespace schifra {

// Forward declarations
namespace galois {
    class field;
    class field_polynomial;
    typedef int field_symbol;
}

namespace reed_solomon {
    template <std::size_t code_length, std::size_t fec_length, std::size_t data_length>
    class encoder;
    
    template <std::size_t code_length, std::size_t fec_length, std::size_t data_length>
    class decoder;
    
    template <std::size_t code_length, std::size_t fec_length, std::size_t data_length>
    struct block;
}

/**
 * @class dna_storage
 * @brief A class for encoding and decoding data into DNA sequences using Reed-Solomon codes.
 * 
 * @tparam CodeLength Total length of the Reed-Solomon code (n).
 * @tparam FecLength Length of the error correction code (n - k).
 * @tparam DataLength Length of the data portion (k).
 */
template <std::size_t CodeLength, std::size_t FecLength, std::size_t DataLength = CodeLength - FecLength>
class dna_storage {
    static_assert(CodeLength > FecLength, "CodeLength must be greater than FecLength");
    static_assert(CodeLength - FecLength == DataLength, "CodeLength - FecLength must equal DataLength");
    static_assert(CodeLength <= 15, "CodeLength must be <= 15 for GF(2^4)");
    
public:
    // Statistics structure for file operations
    struct process_stats {
        std::size_t total_chunks = 0;
        std::size_t processed_chunks = 0;
        std::size_t errors_corrected = 0;
        double processing_time = 0.0;
        std::size_t input_size = 0;
        std::size_t output_size = 0;
        std::string status = "not_started";
        
        std::string to_string() const {
            std::ostringstream ss;
            ss << "Process Statistics:\n"
               << "  Status: " << status << "\n"
               << "  Total chunks: " << total_chunks << "\n"
               << "  Errors corrected: " << errors_corrected << "\n"
               << "  Processing time: " << std::fixed << std::setprecision(2) 
               << processing_time << " seconds\n"
               << "  Processing speed: " 
               << (input_size / (1024.0 * 1024.0 * (processing_time > 0 ? processing_time : 1))) 
               << " MB/s";
            return ss.str();
        }
    };

    // Constructor
    dna_storage() {
        // Parameters for RS(15,11) over GF(2^4)
        const std::size_t field_descriptor = 4;
        const std::size_t generator_polynomial_index = 0;
        const std::size_t generator_polynomial_root_count = 4;

        // Instantiate Galois field for GF(2^4) with Schifra's primitive polynomial
        field_ = std::make_unique<schifra::galois::field>(
            field_descriptor,
            schifra::galois::primitive_polynomial_size01,
            schifra::galois::primitive_polynomial01);

        // Create generator polynomial
        generator_polynomial_ = std::make_unique<schifra::galois::field_polynomial>(*field_);
        if (!schifra::make_sequential_root_generator_polynomial(
                *field_,
                generator_polynomial_index,
                generator_polynomial_root_count,
                *generator_polynomial_)) {
            throw std::runtime_error("Failed to create sequential root generator");
        }
    }
    
    ~dna_storage() = default;
    
    // Disable copy and move
    dna_storage(const dna_storage&) = delete;
    dna_storage& operator=(const dna_storage&) = delete;
    dna_storage(dna_storage&&) = delete;
    dna_storage& operator=(dna_storage&&) = delete;

    // Encode a DNA sequence with error correction
    std::pair<std::string, std::vector<std::uint8_t>> encode(const std::string& dna_sequence) {
        if (!validate_dna(dna_sequence)) {
            throw std::invalid_argument("Invalid DNA sequence: must contain only A, C, G, T characters");
        }
        if (dna_sequence.length() != DataLength) {
            throw std::invalid_argument("DNA sequence length must be exactly " + std::to_string(DataLength) + " characters");
        }
        // Convert DNA to symbols (A=0, C=1, G=2, T=3)
        std::vector<std::uint8_t> symbols = dna_to_symbols(dna_sequence);
        // Create generator polynomial
        schifra::galois::field_polynomial generator_poly(*field_);
        if (!schifra::make_sequential_root_generator_polynomial(*field_, 1, FecLength, generator_poly)) {
            throw std::runtime_error("Failed to create generator polynomial");
        }
        // Create encoder
        typedef schifra::reed_solomon::encoder<15, 4> encoder_t;
        schifra::reed_solomon::block<15, 4> block;
        encoder_t rs_encoder(*field_, generator_poly);
        // Copy data to block.data[0..DataLength-1]
        for (std::size_t i = 0; i < DataLength; ++i) {
            block.data[i] = static_cast<schifra::galois::field_symbol>(symbols[i]);
        }
        // Zero the ECC portion
        for (std::size_t i = DataLength; i < CodeLength; ++i) {
            block.data[i] = 0;
        }
        // Encode the data
        bool encode_ok = rs_encoder.encode(block);
        std::cout << "Encode returned: " << encode_ok << std::endl;
        if (!encode_ok) {
            throw std::runtime_error("Reed-Solomon encoding failed");
        }
        // Debug print: Print block contents after encoding
        std::cout << "Block after encoding: ";
        for (std::size_t i = 0; i < CodeLength; ++i) {
            std::cout << std::hex << std::setw(2) << std::setfill('0') << (int)block.data[i] << " ";
        }
        std::cout << std::dec << std::endl;
        // Extract FEC symbols (as bytes) from block.data[DataLength..CodeLength-1]
        std::vector<std::uint8_t> ecc_symbols(FecLength);
        for (std::size_t i = 0; i < FecLength; ++i) {
            ecc_symbols[i] = static_cast<std::uint8_t>(block.data[DataLength + i]);
        }
        // Return only the original data as DNA, ECC as bytes
        return {dna_sequence, ecc_symbols};
    }
    
    // Decode a DNA sequence with error correction
    std::string decode(const std::string& dna_sequence, const std::vector<std::uint8_t>& ecc_symbols) {
        if (!validate_dna(dna_sequence)) {
            throw std::invalid_argument("Invalid DNA sequence: must contain only A, C, G, T characters");
        }
        if (dna_sequence.length() != DataLength) {
            throw std::invalid_argument("DNA sequence length must be exactly " + std::to_string(DataLength) + " characters");
        }
        if (ecc_symbols.size() != FecLength) {
            throw std::invalid_argument("ECC symbols length must be exactly " + std::to_string(FecLength) + " symbols");
        }
        // Convert DNA to symbols
        std::vector<std::uint8_t> symbols = dna_to_symbols(dna_sequence);
        // Create generator polynomial
        schifra::galois::field_polynomial generator_poly(*field_);
        if (!schifra::make_sequential_root_generator_polynomial(*field_, 1, FecLength, generator_poly)) {
            throw std::runtime_error("Failed to create generator polynomial");
        }
        // Create decoder
        schifra::reed_solomon::block<15, 4> block;
        // Copy data to block.data[0..DataLength-1]
        for (std::size_t i = 0; i < DataLength; ++i) {
            block.data[i] = static_cast<schifra::galois::field_symbol>(symbols[i]);
        }
        // Copy FEC symbols to block.data[DataLength..CodeLength-1]
        for (std::size_t i = 0; i < FecLength; ++i) {
            block.data[DataLength + i] = static_cast<schifra::galois::field_symbol>(ecc_symbols[i]);
        }
        // Debug print: Print block contents before decoding
        std::cout << "Block before decoding: ";
        for (std::size_t i = 0; i < CodeLength; ++i) {
            std::cout << std::hex << std::setw(2) << std::setfill('0') << (int)block.data[i] << " ";
        }
        std::cout << std::dec << std::endl;
        // Decode the data
        schifra::reed_solomon::decoder<15, 4> rs_decoder(*field_, 1);
        if (!rs_decoder.decode(block)) {
            throw std::runtime_error("Reed-Solomon decoding failed");
        }
        // Convert symbols back to DNA (only the data portion)
        std::string decoded_dna = symbols_to_dna(std::vector<std::uint8_t>(block.data, block.data + DataLength));
        return decoded_dna;
    }

    // Process a file (encode or decode)
    process_stats process_file(
        const std::string& input_path,
        const std::string& output_path,
        bool encode_mode,
        std::function<void(double, const std::string&)> progress_callback = nullptr
    );

    // Get the code parameters
    static constexpr std::size_t code_length() { return CodeLength; }
    static constexpr std::size_t fec_length() { return FecLength; }
    static constexpr std::size_t data_length() { return DataLength; }

private:
    // Convert DNA string to symbol vector
    std::vector<std::uint8_t> dna_to_symbols(const std::string& dna_sequence) const {
        std::vector<std::uint8_t> symbols;
        symbols.reserve(dna_sequence.size());
        
        for (char c : dna_sequence) {
            char upper_c = std::toupper(static_cast<unsigned char>(c));
            auto it = dna_to_symbol_.find(upper_c);
            if (it != dna_to_symbol_.end()) {
                symbols.push_back(it->second);
            } else {
                throw std::runtime_error("Invalid DNA character: " + std::string(1, c));
            }
        }
        
        return symbols;
    }
    
    std::string symbols_to_dna(const std::vector<std::uint8_t>& symbols) const {
        std::string dna_sequence;
        dna_sequence.reserve(symbols.size());
        
        for (uint8_t symbol : symbols) {
            auto it = symbol_to_dna_.find(symbol);
            if (it != symbol_to_dna_.end()) {
                dna_sequence.push_back(it->second);
            } else {
                throw std::runtime_error("Invalid symbol value: " + std::to_string(symbol));
            }
        }
        
        return dna_sequence;
    }

    // Validate DNA string (only contains ACGTacgt)
    bool validate_dna(const std::string& dna) const {
        if (dna.empty()) {
            return false;
        }
        
        return std::all_of(dna.begin(), dna.end(), [](char c) {
            return dna_to_symbol_.find(std::toupper(static_cast<unsigned char>(c))) != dna_to_symbol_.end();
        });
    }
    
    // Get current timestamp for logging
    std::string get_timestamp() const {
        auto now = std::chrono::system_clock::now();
        auto in_time_t = std::chrono::system_clock::to_time_t(now);
        
        std::stringstream ss;
        ss << std::put_time(std::localtime(&in_time_t), "%Y-%m-%d %H:%M:%S");
        return ss.str();
    }

    // Galois field for Reed-Solomon operations (GF(2^4))
    std::unique_ptr<schifra::galois::field> field_;
    std::unique_ptr<schifra::galois::field_polynomial> generator_polynomial_;
    
    // DNA to symbol mapping
    static const std::unordered_map<char, std::uint8_t> dna_to_symbol_;
    static const std::unordered_map<std::uint8_t, char> symbol_to_dna_;
    
    // Initialize DNA to symbol mapping
    static std::unordered_map<char, std::uint8_t> init_dna_to_symbol() {
        return {
            {'A', 0}, {'a', 0},
            {'C', 1}, {'c', 1},
            {'G', 2}, {'g', 2},
            {'T', 3}, {'t', 3}
        };
    }
    
    // Initialize symbol to DNA mapping (uppercase only)
    static std::unordered_map<std::uint8_t, char> init_symbol_to_dna() {
        return {
            {0, 'A'},
            {1, 'C'},
            {2, 'G'},
            {3, 'T'}
        };
    }
};

// Initialize static members
template <std::size_t CodeLength, std::size_t FecLength, std::size_t DataLength>
const std::unordered_map<char, std::uint8_t> 
dna_storage<CodeLength, FecLength, DataLength>::dna_to_symbol_ = 
    dna_storage<CodeLength, FecLength, DataLength>::init_dna_to_symbol();

template <std::size_t CodeLength, std::size_t FecLength, std::size_t DataLength>
const std::unordered_map<std::uint8_t, char> 
dna_storage<CodeLength, FecLength, DataLength>::symbol_to_dna_ = 
    dna_storage<CodeLength, FecLength, DataLength>::init_symbol_to_dna();

} // namespace schifra

#endif // SCHIFRA_DNA_STORAGE_HPP