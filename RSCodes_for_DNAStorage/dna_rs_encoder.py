"""
DNA-specific Reed-Solomon encoder
"""
import sys
import os

# Add parent directory to path to import RS code modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'RS_codes_main'))
from encode import rs_encode_msg
from init_tables import init_tables
from gf_operations import set_gf_tables

from dna_utils import dna_to_symbols, symbols_to_dna, validate_dna_sequence, chunk_dna_sequence

class DNAReedSolomonEncoder:
    def __init__(self, n=255, k=223):
        """
        Initialize DNA-specific Reed-Solomon encoder
        n: codeword length (must be less than 256 for GF(256))
        k: message length (must be less than n)
        """
        self.n = n
        self.k = k
        self.prim = 0x11d  # Primitive polynomial for GF(256)
        
        # Initialize Galois Field tables
        gf_exp, gf_log = init_tables(self.prim)
        set_gf_tables(gf_exp, gf_log)

    def encode(self, dna_sequence):
        """
        Encode a DNA sequence using Reed-Solomon
        Returns: (encoded_sequence, ecc_symbols)
        """
        if not validate_dna_sequence(dna_sequence):
            raise ValueError("Invalid DNA sequence. Must contain only A, C, G, T")

        # Convert DNA to numerical symbols
        message_symbols = dna_to_symbols(dna_sequence)
        
        # Ensure message length matches k
        if len(message_symbols) > self.k:
            raise ValueError(f"DNA sequence too long. Maximum length is {self.k}")
        
        # Pad message if needed
        while len(message_symbols) < self.k:
            message_symbols.append(0)  # Pad with 'A's
        
        # Encode using RS
        encoded = rs_encode_msg(message_symbols, self.n - self.k)
        
        # Split into message and ECC parts
        message_part = encoded[:self.k]
        ecc_part = encoded[self.k:]
        
        # Convert message part back to DNA
        encoded_dna = symbols_to_dna(message_part)
        
        return encoded_dna, ecc_part
