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

    def decode_with_error_tracking(self, received_dna, ecc_symbols, known_erasure_positions=None):
        """
        Decode and correct errors in a received DNA sequence with enhanced error tracking
        
        Args:
            received_dna: The received DNA sequence
            ecc_symbols: The ECC symbols from encoding
            known_erasure_positions: List of known error positions (optional)
        
        Returns:
            tuple: (corrected_dna, num_errors_corrected, error_details)
        """
        if not validate_dna_sequence(received_dna):
            raise ValueError("Invalid DNA sequence. Must contain only A, C, G, T")

        # Convert DNA to numerical symbols
        received_symbols = dna_to_symbols(received_dna)
        
        # Combine received message and ECC
        full_received = received_symbols + ecc_symbols
        
        # Original received symbols for error tracking
        original_received = full_received.copy()
        
        # Error tracking dictionary
        error_details = {
            'syndrome_vector': None,
            'error_locator_polynomial': None,
            'num_errors_detected': 0,
            'max_correctable_errors': self.n - self.k // 2
        }
        
        try:
            # Compute syndromes
            syndromes = compute_syndromes(full_received, self.n - self.k)
            error_details['syndrome_vector'] = syndromes
            
            # Check if there are errors
            non_zero_syndromes = [s for s in syndromes if s != 0]
            error_details['num_errors_detected'] = len(non_zero_syndromes)
            
            # Correct errors
            corrected_msg, corrected_ecc = rs_correct_msg(
                full_received, 
                self.n - self.k,
                known_erasure_positions
            )
            
            # Count number of errors corrected
            num_errors_corrected = sum(
                1 for orig, corr in zip(original_received, full_received) 
                if orig != corr
            )
            
            # Validate correction
            if num_errors_corrected > error_details['max_correctable_errors']:
                raise ValueError(f"Errors exceed maximum correctable limit: {num_errors_corrected}")
            
            # Convert corrected symbols back to DNA
            corrected_dna = symbols_to_dna(corrected_msg)
            
            return corrected_dna, num_errors_corrected, error_details
        
        except Exception as e:
            # Detailed error logging
            error_details['error_message'] = str(e)
            raise ValueError(f"Decoding failed: {e}")

def compute_syndromes(received_symbols, num_ecc_symbols):
    """
    Compute syndrome vector for error detection
    
    Args:
        received_symbols: Received message symbols
        num_ecc_symbols: Number of error correction symbols
    
    Returns:
        List of syndrome values
    """
    syndromes = [0] * (num_ecc_symbols + 1)
    for i in range(1, num_ecc_symbols + 1):
        syndrome = 0
        for j, symbol in enumerate(received_symbols):
            syndrome ^= symbol * pow(i, j)
        syndromes[i] = syndrome
    
    return syndromes
