from reed_solomon_dna import rs_encode_msg, rs_correct_msg  # Assuming you saved the code as reed_solomon_dna.py

# 1. Implement your chosen DNA encoding/decoding algorithm
def dna_encode(dna_sequence):
    """Encodes a DNA sequence into a list of numbers."""
    # Replace this with your actual encoding algorithm
    mapping = {'A': 0, 'T': 1, 'G': 2, 'C': 3}
    return [mapping[nucleotide] for nucleotide in dna_sequence]

def dna_decode(numeric_sequence):
    """Decodes a list of numbers back into a DNA sequence."""
    # Replace this with your actual decoding algorithm
    reverse_mapping = {0: 'A', 1: 'T', 2: 'G', 3: 'C'}
    return ''.join([reverse_mapping[num] for num in numeric_sequence])

# 2. Example Usage:
dna_sequence = "ATGCATGC"
ecc_symbols = 10

# Encode DNA to numbers
numeric_sequence = dna_encode(dna_sequence)

# Encode with Reed-Solomon
encoded_message = rs_encode_msg(numeric_sequence, ecc_symbols)

# Simulate Errors (optional)
encoded_message[2] = 99

# Decode with Reed-Solomon
decoded_message, corrected_errors = rs_correct_msg(encoded_message, ecc_symbols)

# Decode numbers back to DNA
decoded_dna = dna_decode(decoded_message)

print("Original DNA:", dna_sequence)
print("Decoded DNA:", decoded_dna)
print("Errors Corrected:", corrected_errors)
