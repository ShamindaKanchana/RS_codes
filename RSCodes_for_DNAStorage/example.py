"""
Example usage of DNA-specific Reed-Solomon error correction
"""
from dna_rs_encoder import DNAReedSolomonEncoder
from dna_rs_decoder import DNAReedSolomonDecoder

def main():
    # Example DNA sequence
    dna_sequence = "ATCGATCGTAGCTACG"
    
    # Initialize encoder and decoder with custom parameters
    # Using smaller values for demonstration
    n, k = 30, 20  # n-k = 10 ECC symbols
    encoder = DNAReedSolomonEncoder(n=n, k=k)
    decoder = DNAReedSolomonDecoder(n=n, k=k)
    
    # Encode the DNA sequence
    encoded_dna, ecc_symbols = encoder.encode(dna_sequence)
    print(f"Original DNA sequence: {dna_sequence}")
    print(f"Encoded DNA (with ECC): {encoded_dna}")
    print(f"ECC symbols: {ecc_symbols}")
    
    # Simulate errors in the DNA sequence (changing some bases)
    corrupted_dna = list(encoded_dna)
    corrupted_dna[1] = 'C'  # Change first base
    corrupted_dna[5] = 'G'  # Change sixth base
    corrupted_dna[9] = 'T'  # Change tenth base
    corrupted_dna[10] = 'A' 
    corrupted_dna = ''.join(corrupted_dna)
    print(f"Corrupted DNA: {corrupted_dna}")
    
    # Decode and correct errors
    corrected_dna = decoder.decode(corrupted_dna, ecc_symbols)
    print(f"Corrected DNA: {corrected_dna}")
    
    # Extract original data (using length of original sequence)
    original_data = corrected_dna[:len(dna_sequence)]
    print(f"Extracted original data: {original_data}")
    
    # Verify correction and data extraction
    print(f"Correction successful (compared to encoded): {corrected_dna == encoded_dna}")
    print(f"Original sequence preserved: {original_data == dna_sequence}")

if __name__ == "__main__":
    main()
