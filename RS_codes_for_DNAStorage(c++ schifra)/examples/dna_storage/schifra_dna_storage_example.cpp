/*
 *   schifra_dna_storage_example.cpp - Example of using Schifra's DNA Storage
 *   
 *   This example demonstrates how to use the DNA storage system to encode and decode
 *   DNA sequences with error correction using Reed-Solomon codes.
 *
 *   Copyright (C) 2025 Schifra Project
 *   
 *   This program is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <iostream>
#include <iomanip>
#include <fstream>
#include <string>
#include <vector>
#include <cstdint>

#include "schifra/dna_storage.hpp"

// Define the Reed-Solomon code parameters for this example
// Using RS(15,11) which can correct up to 2 symbol errors
using dna_storage_type = schifra::dna_storage<15, 4>;  // n=15, k=11, t=2

void print_help() {
    std::cout << "Schifra DNA Storage Example\n"
              << "Usage: schifra_dna_storage_example <command>\n"
              << "\nCommands:\n"
              << "  encode <input_file> <output_file>  Encode a file with DNA storage\n"
              << "  decode <input_file> <output_file>  Decode a file with DNA storage\n"
              << "  example                           Run a simple example\n";
}

void run_example() {
    std::cout << "=== Schifra DNA Storage Example ===\n\n";
    
    try {
        // Initialize DNA storage with RS(15,11) parameters
        dna_storage_type dna_storage;
        
        std::string original = "ACGTACGTACG";
        std::cout << "Original DNA: " << original << "\n";
        
        // Encode the DNA sequence
        auto [encoded_dna, ecc] = dna_storage.encode(original);
        std::cout << "Encoded DNA: " << encoded_dna << "\n";
        std::cout << "ECC (" << ecc.size() << " symbols): ";
        for (auto b : ecc) {
            std::cout << std::hex << std::setw(2) << std::setfill('0') << (int)b << " ";
        }
        std::cout << std::dec << "\n";
        
        // Introduce some errors
        std::string corrupted = encoded_dna;
        if (corrupted.length() > 2) {
            corrupted[1] = (corrupted[1] == 'A') ? 'C' : 'A';  // Flip a base
            std::cout << "Corrupted DNA: " << corrupted << " (introduced error at position 1)\n";
        }
        
        // Decode and correct errors
        std::string decoded = dna_storage.decode(corrupted, ecc);
        std::cout << "Decoded DNA: " << decoded << "\n";
        
        std::cout << "\nVerification: " 
                  << (original == decoded ? "SUCCESS" : "FAILED") 
                  << "\n";
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }
}

void process_file(const std::string& input_file, 
                  const std::string& output_file,
                  bool encode_mode) {
    
    std::cout << (encode_mode ? "Encoding" : "Decoding") 
              << " file " << input_file 
              << " -> " << output_file << "\n";
    
    try {
        dna_storage_type dna_storage;
        
        auto progress_callback = [](double progress, const std::string& message) {
            std::cout << "\r" << message << " " 
                     << std::fixed << std::setprecision(1) 
                     << (progress * 100.0) << "%" << std::flush;
        };
        
        auto stats = dna_storage.process_file(
            input_file, 
            output_file, 
            encode_mode,
            progress_callback
        );
        
        std::cout << "\n" << stats.to_string() << "\n";
        
    } catch (const std::exception& e) {
        std::cerr << "\nError: " << e.what() << std::endl;
        std::exit(1);
    }
}

int main(int argc, char* argv[]) {
    // Default parameters
    std::size_t n = 255;
    std::size_t k = 223;
    
    // Parse command line arguments
    if (argc < 2) {
        print_help();
        return 1;
    }
    
    std::string command = argv[1];
    
    // Parse options
    for (int i = 2; i < argc - 1; ++i) {
        std::string arg = argv[i];
        if (arg == "-n" && i + 1 < argc) {
            n = std::stoul(argv[++i]);
        } else if (arg == "-k" && i + 1 < argc) {
            k = std::stoul(argv[++i]);
        }
    }
    
    if (command == "example") {
        run_example();
    } else if (command == "encode" || command == "decode") {
        if (argc < 4) {
            std::cerr << "Error: Missing input/output file arguments\n";
            print_help();
            return 1;
        }
        
        std::string input_file = argv[2];
        std::string output_file = argv[3];
        
        process_file(input_file, output_file, command == "encode");
    } else {
        std::cerr << "Error: Unknown command '" << command << "'\n";
        print_help();
        return 1;
    }
    
    return 0;
}
