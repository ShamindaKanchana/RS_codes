"""
DNA-specific Reed-Solomon decoder with file I/O support
"""
import sys
import os
import json
import math
import time
from datetime import datetime
from typing import Optional, Tuple, Dict, List, Generator, BinaryIO, Union

# Add parent directory to path to import RS code modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'RS_codes_main'))
from decode import rs_correct_msg, rs_find_error_locator, rs_find_errors
from init_tables import init_tables
from gf_operations import set_gf_tables, gf_pow, gf_poly_eval

from dna_utils import dna_to_symbols, symbols_to_dna, validate_dna_sequence

class DNAReedSolomonDecoder:
    def __init__(self, n: int = 255, k: int = 223):
        """
        Initialize DNA-specific Reed-Solomon decoder
        
        Args:
            n: codeword length (must be less than 256 for GF(256))
            k: message length (must be less than n)
            
        Raises:
            ValueError: If n >= 256 or k >= n
        """
        if n >= 256:
            raise ValueError("n must be less than 256 for GF(256)")
        if k >= n:
            raise ValueError("k must be less than n")
            
        self.n = n
        self.k = k
        self.prim = 0x11d  # Primitive polynomial for GF(256)
        
        # Initialize Galois Field tables
        gf_exp, gf_log = init_tables(self.prim)
        set_gf_tables(gf_exp, gf_log)
        
        # Performance optimization
        self._chunk_size = k  # Size of each data chunk
        self._ecc_size = n - k  # Size of ECC per chunk

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

    def process_large_file(self, input_file: str, output_file: str, mode: str = 'encode',
                         chunk_size: Optional[int] = None, 
                         show_progress: bool = True) -> Dict[str, Union[int, float, str]]:
        """
        Process large files with streaming support for memory efficiency.
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            mode: 'encode' or 'decode'
            chunk_size: Size of each chunk in bytes (default: self.k for encode, self.n for decode)
            show_progress: Whether to show progress bar
            
        Returns:
            Dict with processing statistics
            
        Raises:
            ValueError: For invalid mode or file operations
        """
        if mode not in ('encode', 'decode'):
            raise ValueError("Mode must be 'encode' or 'decode'")
            
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
            
        chunk_size = chunk_size or (self.k if mode == 'encode' else self.n)
        file_size = os.path.getsize(input_file)
        
        # Calculate total chunks (rounded up)
        total_chunks = (file_size + chunk_size - 1) // chunk_size
        
        stats = {
            'start_time': datetime.now(),
            'file_size': file_size,
            'chunk_size': chunk_size,
            'total_chunks': total_chunks,
            'processed_chunks': 0,
            'errors_corrected': 0,
            'mode': mode
        }
        
        # Create parent directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)) or '.', exist_ok=True)
        
        try:
            with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
                start_time = time.time()
                last_print = 0
                processed_bytes = 0
                
                while True:
                    chunk = f_in.read(chunk_size)
                    if not chunk:
                        break
                        
                    try:
                        if mode == 'encode':
                            # For encoding, convert bytes to DNA and encode
                            dna_chunk = self._bytes_to_dna(chunk)
                            encoded_dna, ecc = self.encode(dna_chunk)
                            # Write both data and ECC
                            f_out.write(encoded_dna.encode('utf-8'))
                            f_out.write(self._ecc_to_bytes(ecc))
                        else:
                            # For decoding, separate data and ECC
                            data_part = chunk[:self.k]
                            ecc_part = chunk[self.k:self.n]
                            dna_chunk = self._bytes_to_dna(data_part)
                            ecc = self._bytes_to_ecc(ecc_part)
                            
                            # Decode with error correction
                            corrected_dna, num_errors, _ = self.decode_with_error_tracking(
                                dna_chunk, ecc, save_to_files=False
                            )
                            stats['errors_corrected'] += num_errors
                            
                            # Convert back to bytes and write
                            f_out.write(self._dna_to_bytes(corrected_dna))
                            
                    except Exception as e:
                        # Log error but continue with next chunk
                        print(f"Error processing chunk: {str(e)}")
                        continue
                        
                    stats['processed_chunks'] += 1
                    processed_bytes += len(chunk)
                    
                    # Show progress every second
                    current_time = time.time()
                    if show_progress and (current_time - last_print) >= 1.0:
                        percent = (processed_bytes / file_size) * 100
                        elapsed = current_time - start_time
                        speed = processed_bytes / (1024 * 1024) / elapsed if elapsed > 0 else 0
                        print(f"\rProgress: {percent:.1f}% | "
                              f"Speed: {speed:.2f} MB/s | "
                              f"Processed: {processed_bytes / (1024*1024):.2f} MB", 
                              end='', flush=True)
                        last_print = current_time
                
                if show_progress:
                    print()  # New line after progress
                
        except Exception as e:
            raise RuntimeError(f"Error processing file: {str(e)}")
            
        stats['end_time'] = datetime.now()
        stats['processing_time'] = (stats['end_time'] - stats['start_time']).total_seconds()
        stats['avg_speed'] = file_size / (stats['processing_time'] or 1)  # bytes per second
        
        return stats
    
    def _bytes_to_dna(self, data: bytes) -> str:
        """Convert bytes to DNA sequence (2 bits per base)."""
        dna = []
        base_map = {0: 'A', 1: 'C', 2: 'G', 3: 'T'}
        
        for byte in data:
            # Process 4 bases per byte (2 bits per base)
            for i in range(0, 8, 2):
                # Extract 2 bits and map to DNA base
                bits = (byte >> (6 - i)) & 0b11
                dna.append(base_map[bits])
                
        return ''.join(dna)
    
    def _dna_to_bytes(self, dna: str) -> bytes:
        """Convert DNA sequence back to bytes."""
        byte_array = bytearray()
        base_map = {'A': 0, 'C': 1, 'G': 2, 'T': 3}
        
        # Process DNA in groups of 4 bases (1 byte)
        for i in range(0, len(dna), 4):
            chunk = dna[i:i+4]
            byte = 0
            
            for j, base in enumerate(chunk):
                # Shift and add each base (2 bits)
                byte = (byte << 2) | base_map.get(base, 0)
                
            # Pad with zeros if needed
            byte <<= (4 - len(chunk)) * 2
            byte_array.append(byte)
            
        return bytes(byte_array)
    
    def _ecc_to_bytes(self, ecc: List[int]) -> bytes:
        """Convert ECC symbols to bytes."""
        return bytes(ecc)
    
    def _bytes_to_ecc(self, data: bytes) -> List[int]:
        """Convert bytes back to ECC symbols."""
        return list(data)
    
    def save_to_file(self, data, filename, output_dir='output'):
        """
        Save data to a file in the specified directory
        
        Args:
            data: Data to save (can be string or dictionary)
            filename: Name of the file to save
            output_dir: Directory to save the file in (default: 'output')
            
        Returns:
            str: Path to the saved file
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"{os.path.splitext(filename)[0]}_{timestamp}"
        
        # Handle different data types
        if isinstance(data, dict):
            filepath = os.path.join(output_dir, f"{base_name}.json")
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            filepath = os.path.join(output_dir, f"{base_name}.txt")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(data))
                
        return filepath

    def decode_with_error_tracking(self, received_dna, ecc_symbols, known_erasure_positions=None, save_to_files=False):
        """
        Decode and correct errors in a received DNA sequence with enhanced error tracking
        
        Args:
            received_dna: The received DNA sequence
            ecc_symbols: The ECC symbols from encoding
            known_erasure_positions: List of known error positions (optional)
            save_to_files: If True, saves input/output to files (default: False)
        
        Returns:
            tuple: (corrected_dna, num_errors_corrected, error_details, file_paths)
                  file_paths is a dict containing paths to saved files if save_to_files=True
        """
        file_paths = {}
        
        if save_to_files:
            # Save the received DNA and ECC symbols
            input_data = {
                'received_dna': received_dna,
                'ecc_symbols': ecc_symbols,
                'timestamp': datetime.now().isoformat(),
                'code_parameters': {
                    'n': self.n,
                    'k': self.k,
                    'ecc_symbols_count': len(ecc_symbols)
                }
            }
            file_paths['input'] = self.save_to_file(input_data, 'decoder_input.json')
            file_paths['received_dna'] = self.save_to_file(received_dna, 'received_dna.txt')
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
            'max_correctable_errors': (self.n - self.k) // 2,
            'error_positions': [],
            'error_correction_status': 'success'
        }
        
        try:
            # Compute syndromes
            syndromes = compute_syndromes(full_received, self.n - self.k)
            error_details['syndrome_vector'] = syndromes
            
            # Check if there are errors
            if all(s == 0 for s in syndromes[1:]):  # Skip first 0
                error_details['num_errors_detected'] = 0
                return (received_dna, 0, error_details)
            
            # Find error locator polynomial
            error_locator = rs_find_error_locator(syndromes[1:], erase_pos=known_erasure_positions or [])
            error_details['error_locator_polynomial'] = error_locator
            
            # Find error positions
            error_positions = rs_find_errors(error_locator, self.n)
            error_details['error_positions'] = error_positions
            
            # Count actual errors
            error_details['num_errors_detected'] = len(error_positions)
            
            # Correct errors
            corrected_msg, corrected_ecc = rs_correct_msg(
                full_received, 
                self.n - self.k,
                erase_pos=known_erasure_positions or []
            )
            
            # Convert corrected message back to DNA
            corrected_dna = symbols_to_dna(corrected_msg)
            
            if save_to_files:
                # Save successful decoding results
                result_data = {
                    'original_sequence': received_dna,
                    'corrected_sequence': corrected_dna,
                    'num_errors_corrected': len(error_positions),
                    'error_positions': error_positions,
                    'timestamp': datetime.now().isoformat()
                }
                file_paths['decoding_result'] = self.save_to_file(result_data, 'decoding_result.json')
                file_paths['corrected_sequence'] = self.save_to_file(corrected_dna, 'corrected_sequence.txt')
                
            return (corrected_dna, len(error_positions), error_details, file_paths if save_to_files else {})
        
        except Exception as e:
            error_details['error_correction_status'] = 'failed'
            error_details['error_message'] = f"Decoding failed: {str(e)}"
            
            # Try partial recovery
            corrected_dna = symbols_to_dna(received_symbols)
            
            if save_to_files:
                # Save error details and partial recovery
                error_details['partial_recovery'] = True
                error_details['recovered_sequence'] = corrected_dna
                file_paths['error_details'] = self.save_to_file(error_details, 'decoder_error_details.json')
                file_paths['recovered_sequence'] = self.save_to_file(corrected_dna, 'recovered_sequence.txt')
                
            return (corrected_dna, 0, error_details, file_paths if save_to_files else {})

def compute_syndromes(received_symbols, num_ecc_symbols):
    """Compute syndrome vector for error detection"""
    # Diagnostic logging
    print(f"DEBUG: Calculating syndromes")
    print(f"DEBUG: Message length: {len(received_symbols)}")
    print(f"DEBUG: Number of error correcting symbols: {num_ecc_symbols}")
    
    synd = [0] * num_ecc_symbols
    
    # Compute syndromes using Galois Field arithmetic
    for i in range(num_ecc_symbols):
        alpha = gf_pow(2, i)
        synd[i] = gf_poly_eval(received_symbols, alpha)
        
        # Ensure result is within GF(256)
        synd[i] = synd[i] % 256
        
        # Detailed syndrome computation logging
        print(f"DEBUG: Syndrome[{i}] = {synd[i]}")
    
    # Pad with zero for mathematical precision
    result = [0] + synd
    
    # Syndrome analysis
    print(f"DEBUG: Full syndrome vector: {result}")
    print(f"DEBUG: Non-zero syndrome count: {len([x for x in result if x != 0])}")
    
    return result
