/*
   schifra_dna_storage.cpp - DNA Storage Implementation
   
   This file implements the DNA storage system that provides error correction
   for DNA sequences using Reed-Solomon codes.
   
   Copyright (C) 2025 Schifra Project
*/

#include "schifra/dna_storage.hpp"

namespace schifra {

// Explicit template instantiations for common Reed-Solomon codes
template class dna_storage<15, 4, 11>;    // RS(15, 11) - For testing

} // namespace schifra
