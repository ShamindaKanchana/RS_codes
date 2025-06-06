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

def encode_large_file(input_data: str, n: int = 30, k: int = 20) -> tuple:
    """Encode a large file by splitting into chunks"""
    encoder = DNAReedSolomonEncoder(n=n, k=k)
    
    # Process in chunks of size k
    chunks = []
    for i in range(0, len(input_data), k):
        chunk = input_data[i:i+k]
        
        # Pad last chunk if needed
        if len(chunk) < k:
            chunk = chunk.ljust(k, 'A')
        
        chunks.append(chunk)
    
    # Encode each chunk
    encoded_chunks = []
    
    for chunk in chunks:
        # Encode the chunk
        encoded_chunk, ecc_symbols = encoder.encode(chunk)
        
        # Convert ECC symbols to DNA and append to encoded chunk
        ecc_dna = symbols_to_dna(ecc_symbols)
        full_codeword = encoded_chunk + ecc_dna
        
        encoded_chunks.append(full_codeword)
    
    # Combine encoded chunks
    return ''.join(encoded_chunks)

def decode_large_file(encoded_data: str, n: int = 30, k: int = 20) -> tuple:
    """
    Decode a large file with enhanced error tracking and correction
    
    Returns:
    - Decoded data
    - Error correction statistics
    """
    decoder = DNAReedSolomonDecoder(n=n, k=k)
    
    # Calculate number of chunks
    chunk_size = n
    num_chunks = len(encoded_data) // chunk_size
    
    # Decode each chunk with detailed error tracking
    decoded_chunks = []
    error_stats = {
        'total_chunks': num_chunks,
        'successfully_decoded_chunks': 0,
        'failed_chunks': 0,
        'total_errors_detected': 0,
        'chunk_error_details': []
    }
    
    for i in range(num_chunks):
        try:
            # Get the full codeword (message + ECC)
            full_codeword = encoded_data[i*chunk_size:(i+1)*chunk_size]
            
            # Split into message and ECC parts
            message_part = full_codeword[:k]
            ecc_part = full_codeword[k:]
            
            # Convert ECC part back to symbols
            ecc_symbols = dna_to_symbols(ecc_part)
            
            # Decode with error tracking
            corrected_chunk, errors_corrected, error_details = decoder.decode_with_error_tracking(
                message_part,
                ecc_symbols
            )
            
            decoded_chunks.append(corrected_chunk)
            error_stats['successfully_decoded_chunks'] += 1
            error_stats['total_errors_detected'] += error_details.get('num_errors_detected', 0)
            
            # Log detailed error information
            error_stats['chunk_error_details'].append({
                'chunk_index': i,
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
                'status': 'failed',
                'error_message': str(e)
            })
            
            # Fallback strategy: try partial decoding or use a recovery mechanism
            try:
                # Attempt partial recovery
                message_part = encoded_data[i*chunk_size:(i+1)*chunk_size][:k]
                decoded_chunks.append(message_part)
                print(f"Warning: Partial recovery for chunk {i}")
            except Exception:
                # If all recovery fails, insert a placeholder
                decoded_chunks.append('X' * k)
    
    # Combine decoded chunks
    decoded_data = ''.join(decoded_chunks)
    
    return decoded_data, error_stats

def main(verbose: bool = True):
    # Parameters optimized for DNA storage
    n = 30  # Codeword length (total length including ECC)
    k = 20  # Message length (original data length)
    dna_size_mb = 0.0004  # Size in MB
    error_rate = 0.01  # 1% error rate
    
    # Create docs directory if it doesn't exist
    os.makedirs('docs', exist_ok=True)
    
    # File paths
    input_file = 'docs/dna_input6.txt'
    encoded_file = 'docs/dna_encoded6.txt'
    ecc_file = 'docs/dna_ecc6.txt'
    corrupted_file = 'docs/dna_corrupted6.txt'
    corrected_file = 'docs/dna_corrected6.txt'
    
    # Optional logging
    def log(message):
        if verbose:
            print(message)
    
    # Process files with cleaner output
    print("""
=== DNA Error Correction Process ===
""")
    
    # 1. Generate DNA sequence
    log("\n1. Generating DNA sequence...")
    generate_random_dna_file(input_file, dna_size_mb)
    
    # 2. Read input file
    with open(input_file, 'r') as f:
        input_data = f.read()
    
    # 3. Encode DNA sequence
    log("\n2. Encoding DNA sequence...")
    encode_start = time.time()
    encoded_data = encode_large_file(input_data, n, k)
    encode_time = time.time() - encode_start
    log(f"Encoding completed in {encode_time:.2f} seconds")
    
    # 4. Write encoded data
    with open(encoded_file, 'w') as f:
        f.write(encoded_data)
    
    # 5. Introduce errors in original data before encoding
    log("\n3. Introducing random errors in original data...")
    corrupted_input = introduce_random_errors(input_data, error_rate)
    with open(corrupted_file, 'w') as f:
        f.write(corrupted_input)
    
    # Encode corrupted data
    log("\n4. Encoding corrupted data...")
    corrupted_encoded = encode_large_file(corrupted_input, n, k)
    
    # 6. Decode and correct
    log("\n5. Decoding and correcting errors...")
    decode_start = time.time()
    try:
        corrected_data, error_stats = decode_large_file(corrupted_encoded, n, k)
        decode_time = time.time() - decode_start
        log(f"Decoding completed in {decode_time:.2f} seconds")
        
        # Write corrected data
        with open(corrected_file, 'w') as f:
            f.write(corrected_data)
        
        # === Results Summary ===
        print("\n=== Results Summary ===")
        print(f"\nFile Size: {dna_size_mb} MB")
        print(f"Total processing time: {encode_time + decode_time:.2f} seconds")
        
        # === Data Verification ===
        print("\n=== Data Verification ===")
        print(f"Original data length: {len(input_data)}")
        print(f"Corrected data length: {len(corrected_data)}")
        print(f"Data matches: {input_data == corrected_data}")
        
        # Calculate correction statistics
        chunks_with_errors = sum(1 for detail in error_stats['chunk_error_details'] 
                               if detail.get('errors_detected', 0) > 0)
        total_errors_detected = sum(detail.get('errors_detected', 0) 
                                  for detail in error_stats['chunk_error_details'])
        
        print("\n=== Correction Statistics ===")
        print(f"Chunks processed: {error_stats['total_chunks']}")
        print(f"Chunks with errors: {chunks_with_errors}")
        print(f"Total errors detected: {total_errors_detected}")
        print(f"Successfully decoded chunks: {error_stats['successfully_decoded_chunks']}")
        print(f"Failed chunks: {error_stats['failed_chunks']}")
        
        # === Symbol Verification ===
        print("\n=== Symbol Verification ===")
        symbol_matches = sum(1 for a, b in zip(input_data, corrected_data) if a == b)
        total_symbols = min(len(input_data), len(corrected_data))
        symbol_match_rate = (symbol_matches / total_symbols) * 100
        
        print(f"Symbols matched: {symbol_matches} out of {total_symbols}")
        print(f"Symbol match rate: {symbol_match_rate:.2f}%")
        
        # === Detailed Error Analysis ===
        print("\n=== Detailed Error Analysis ===")
        symbol_errors = []
        for i, (original, corrected) in enumerate(zip(input_data, corrected_data)):
            if original != corrected:
                symbol_errors.append({
                    'position': i,
                    'original': original,
                    'corrected': corrected,
                    'chunk': i // k
                })
        
        if symbol_errors:
            print(f"Total symbol errors: {len(symbol_errors)}")
            print("\nFirst 5 symbol errors:")
            for error in symbol_errors[:5]:
                print(f"Position {error['position']} in chunk {error['chunk']}:")
                print(f"  Original: {error['original']}")
                print(f"  Corrected: {error['corrected']}")
        else:
            print("No symbol errors found!")
            
    except Exception as e:
        print(f"\nError: {e}")
    
    print("\n=== Process Complete ===")

if __name__ == "__main__":
    main(verbose=True)  # Set to False for less detailed logging
