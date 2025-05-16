"""
DNA-specific Reed-Solomon decoder
"""
import sys
import os

# Add parent directory to path to import RS code modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'RS_codes_main'))
from decode import rs_correct_msg
from init_tables import init_tables
from gf_operations import set_gf_tables

from dna_utils import dna_to_symbols, symbols_to_dna, validate_dna_sequence

class DNAReedSolomonDecoder:
    def __init__(self, n=255, k=223):
        """
        Initialize DNA-specific Reed-Solomon decoder
        n: codeword length (must be less than 256 for GF(256))
        k: message length (must be less than n)
        """
        self.n = n
        self.k = k
        self.prim = 0x11d  # Primitive polynomial for GF(256)
        
        # Initialize Galois Field tables
        gf_exp, gf_log = init_tables(self.prim)
        set_gf_tables(gf_exp, gf_log)

    def decode(self, received_dna, ecc_symbols, known_erasure_positions=None):
        """
        Decode and correct errors in a received DNA sequence
        received_dna: The received DNA sequence
        ecc_symbols: The ECC symbols from encoding
        known_erasure_positions: List of known error positions (optional)
        Returns: corrected DNA sequence
        """
        if not validate_dna_sequence(received_dna):
            raise ValueError("Invalid DNA sequence. Must contain only A, C, G, T")

        # Convert DNA to numerical symbols
        received_symbols = dna_to_symbols(received_dna)
        
        # Combine received message and ECC
        full_received = received_symbols + ecc_symbols
        
        # Correct errors
        corrected_msg, corrected_ecc = rs_correct_msg(
            full_received, 
            self.n - self.k,
            erase_pos=known_erasure_positions or []
        )
        
        # Convert corrected message back to DNA
        corrected_dna = symbols_to_dna(corrected_msg)
        
        return corrected_dna
