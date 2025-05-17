import random
import time
import os
from dna_utils import symbols_to_dna, dna_to_symbols

from dna_rs_encoder import DNAReedSolomonEncoder
from dna_rs_decoder import DNAReedSolomonDecoder

def generate_random_dna_file(filename: str, size_mb: float):
    """Generate a random DNA file of specified size in MB"""
    total_bytes = int(size_mb * 1024 * 1024)
    
    with open(filename, 'w') as f:
        # Generate random DNA sequence
        dna_sequence = ''.join(random.choice('ACGT') for _ in range(total_bytes))
        f.write(dna_sequence)
    
    print(f"Generated DNA file: {filename} (Size: {size_mb} MB)")

def introduce_random_errors(dna: str, error_rate: float) -> str:
    """Introduce random errors in DNA sequence with more controlled error distribution"""
    dna_list = list(dna)
    num_errors = int(len(dna) * error_rate)
    
    # Use a more deterministic error introduction method
    error_positions = random.sample(range(len(dna)), num_errors)
    
    for pos in error_positions:
        # Get all possible bases except the current one
        possible_bases = list(set('ACGT') - {dna_list[pos]})
        # Replace with a random different base
        dna_list[pos] = random.choice(possible_bases)
    
    return ''.join(dna_list)

def encode_large_file(input_data: str, n: int = 255, k: int = 223) -> tuple:
    """Encode a large file by splitting into chunks"""
    encoder = DNAReedSolomonEncoder(n=n, k=k)
    
    # Ensure each chunk is exactly k characters long
    chunks = []
    for i in range(0, len(input_data), k):
        chunk = input_data[i:i+k]
        
        # Pad the last chunk if it's shorter than k
        if len(chunk) < k:
            chunk = chunk.ljust(k, 'A')
        
        chunks.append(chunk)
    
    # Encode each chunk
    encoded_chunks = []
    ecc_symbols_list = []
    
    for chunk in chunks:
        # Encode the chunk
        encoded_chunk, ecc_symbols = encoder.encode(chunk)
        
        # Full codeword is the encoded chunk + ECC symbols converted to DNA
        full_codeword = encoded_chunk + symbols_to_dna(ecc_symbols)
        
        encoded_chunks.append(full_codeword)
        ecc_symbols_list.append(ecc_symbols)
    
    return ''.join(encoded_chunks), ecc_symbols_list

def decode_large_file(encoded_data: str, ecc_symbols_list: list, n: int = 255, k: int = 223) -> tuple:
    """
    Decode a large file with enhanced error tracking and correction
    
    Returns:
    - Decoded data
    - Error correction statistics
    """
    decoder = DNAReedSolomonDecoder(n=n, k=k)
    
    # Split encoded data into full codewords (including ECC)
    encoded_chunks = [encoded_data[i:i+n] for i in range(0, len(encoded_data), n)]
    
    # Decode each chunk with detailed error tracking
    decoded_chunks = []
    error_stats = {
        'total_chunks': len(encoded_chunks),
        'successfully_decoded_chunks': 0,
        'failed_chunks': 0,
        'total_errors_corrected': 0,
        'total_errors_detected': 0,
        'chunk_error_details': []
    }
    
    for i, (encoded_chunk, ecc_symbols) in enumerate(zip(encoded_chunks, ecc_symbols_list)):
        try:
            # Attempt to decode with enhanced error tracking
            decoded_chunk, errors_corrected, error_details = decoder.decode_with_error_tracking(
                encoded_chunk[:k], 
                ecc_symbols
            )
            
            decoded_chunks.append(decoded_chunk)
            error_stats['successfully_decoded_chunks'] += 1
            error_stats['total_errors_corrected'] += errors_corrected
            error_stats['total_errors_detected'] += error_details.get('num_errors_detected', 0)
            
            # Log detailed error information
            error_stats['chunk_error_details'].append({
                'chunk_index': i,
                'errors_corrected': errors_corrected,
                'errors_detected': error_details.get('num_errors_detected', 0),
                'syndrome_vector': error_details.get('syndrome_vector', []),
                'status': 'success'
            })
        
        except Exception as e:
            # More detailed error handling
            print(f"Decoding error for chunk {i}: {e}")
            error_stats['failed_chunks'] += 1
            
            # Log detailed error information
            error_stats['chunk_error_details'].append({
                'chunk_index': i,
                'errors_corrected': 0,
                'status': 'failed',
                'error_message': str(e)
            })
            
            # Fallback strategy: try partial decoding or use a recovery mechanism
            try:
                # Attempt partial recovery or use original chunk with warning
                partial_decoded = encoded_chunk[:k]
                decoded_chunks.append(partial_decoded)
                print(f"Warning: Partial recovery for chunk {i}")
            except Exception:
                # If all recovery fails, insert a placeholder
                decoded_chunks.append('X' * k)
    
    # Remove padding from the last chunk
    decoded_data = ''.join(decoded_chunks).rstrip('A')
    
    # Calculate error correction percentage
    error_stats['error_correction_rate'] = (error_stats['successfully_decoded_chunks'] / error_stats['total_chunks']) * 100
    
    return decoded_data, error_stats

def main(verbose: bool = True):
    # Parameters
    n = 255  # Codeword length
    k = 223  # Message length
    dna_size_mb = 1  # Size in MB
    error_rate = 0.01  # 1% error rate
    
    # Create docs directory if it doesn't exist
    os.makedirs('docs', exist_ok=True)
    
    # File paths
    input_file = 'docs/dna_input.txt'
    encoded_file = 'docs/dna_encoded.txt'
    ecc_file = 'docs/dna_ecc.txt'
    corrupted_file = 'docs/dna_corrupted.txt'
    corrected_file = 'docs/dna_corrected.txt'
    
    # Optional logging
    def log(message):
        if verbose:
            print(message)
    
    log("\nGenerating DNA sequence...")
    # Generate random DNA file
    generate_random_dna_file(input_file, dna_size_mb)
    
    # Read input file
    with open(input_file, 'r') as f:
        input_data = f.read()
    
    # Encode
    log("\nEncoding DNA sequence...")
    encode_start = time.time()
    encoded_data, ecc_symbols = encode_large_file(input_data, n, k)
    encode_time = time.time() - encode_start
    log(f"Encoding completed in {encode_time:.2f} seconds")
    
    # Write encoded data and ECC
    with open(encoded_file, 'w') as f:
        f.write(encoded_data)
    with open(ecc_file, 'w') as f:
        for symbols in ecc_symbols:
            f.write(''.join(map(str, symbols)) + '\n')
    
    # Introduce errors
    log("\nIntroducing random errors...")
    corrupted_data = introduce_random_errors(encoded_data, error_rate)
    with open(corrupted_file, 'w') as f:
        f.write(corrupted_data)
    
    # Decode and correct
    log("\nDecoding and correcting errors...")
    decode_start = time.time()
    try:
        corrected_data, error_stats = decode_large_file(corrupted_data, ecc_symbols, n, k)
        decode_time = time.time() - decode_start
        log(f"Decoding completed in {decode_time:.2f} seconds")
        
        # Write corrected data
        with open(corrected_file, 'w') as f:
            f.write(corrected_data)
        
        # Detailed error correction reporting
        print("\nError Correction Statistics:")
        print(f"Total Chunks: {error_stats['total_chunks']}")
        print(f"Successfully Decoded Chunks: {error_stats['successfully_decoded_chunks']}")
        print(f"Failed Chunks: {error_stats['failed_chunks']}")
        print(f"Total Errors Detected: {error_stats['total_errors_detected']}")
        print(f"Total Errors Corrected: {error_stats['total_errors_corrected']}")
        print(f"Error Correction Rate: {error_stats['error_correction_rate']:.2f}%")
        
        # Detailed chunk error information
        print("\nChunk Error Details:")
        for detail in error_stats['chunk_error_details'][:10]:  # Show first 10 chunks
            print(f"Chunk {detail['chunk_index']}: {detail}")
        
        # Verification
        print("\nVerification:")
        print(f"Original data length: {len(input_data)}")
        print(f"Corrected data length: {len(corrected_data)}")
        print(f"Data matches: {input_data == corrected_data}")
    
    except Exception as e:
        print(f"Decoding failed: {e}")
    
    # Results
    print(f"\nProcessing Summary:")
    print(f"File Size: {dna_size_mb} MB")
    print(f"Total processing time: {encode_time + decode_time:.2f} seconds")

if __name__ == "__main__":
    main(verbose=True)  # Set to False for less detailed logging
