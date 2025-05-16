"""
Utility functions for DNA-based Reed-Solomon error correction
"""

# DNA nucleotide mapping to numerical values
DNA_TO_INT = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
INT_TO_DNA = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}

def dna_to_symbols(dna_sequence):
    """Convert DNA sequence to numerical symbols"""
    return [DNA_TO_INT[base] for base in dna_sequence.upper()]

def symbols_to_dna(symbols):
    """Convert numerical symbols back to DNA sequence"""
    # Use modulo to map symbols to 0-3 range
    return ''.join(INT_TO_DNA[symbol % 4] for symbol in symbols)

def validate_dna_sequence(sequence):
    """Validate that a sequence contains only valid DNA bases"""
    valid_bases = set('ACGT')
    return all(base.upper() in valid_bases for base in sequence)

def chunk_dna_sequence(sequence, chunk_size):
    """Split DNA sequence into chunks for processing"""
    return [sequence[i:i + chunk_size] for i in range(0, len(sequence), chunk_size)]
